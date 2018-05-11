"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""
from evennia import ObjectDB
from evennia.utils import make_iter
from typeclasses.defaults.default_objects import Object
from utils.tg_search_and_emote_regexes import PREFIX, AT_SEARCH_RESULT
from world.rpsystem import parse_sdescs_and_recogs


class TGObject(Object):

    def at_before_move(self, destination, coordinates=None, **kwargs):
        """
        Called just before starting to move this object to
        destination.

        Args:
            destination (Object): The object we are moving to, which can be non for the wild map
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            shouldmove (bool): If we should move or not.

        Notes:
            If this method returns False/None, the move is cancelled
            before it is even started.
        """

        if not destination:
            if not coordinates:
                return False

        # return has_perm(self, destination, "can_move")
        return True

    def search(self, searchdata,
               global_search=False,
               use_nicks=True,
               typeclass=None,
               location=None,
               attribute_name=None,
               quiet=False,
               exact=False,
               candidates=None,
               nofound_string=None,
               multimatch_string=None,
               use_dbref=None):
        """
        Returns an Object matching a search string/condition, taking
        sdescs into account.

        Perform a standard object search in the database, handling
        multiple results and lack thereof gracefully. By default, only
        objects in the current `location` of `self` or its inventory are searched for.

        Args:
            searchdata (str or obj): Primary search criterion. Will be matched
                against `object.key` (with `object.aliases` second) unless
                the keyword attribute_name specifies otherwise.
                **Special strings:**
                - `#<num>`: search by unique dbref. This is always
                   a global search.
                - `me,self`: self-reference to this object
                - `<num>-<string>` - can be used to differentiate
                   between multiple same-named matches
            global_search (bool): Search all objects globally. This is overruled
                by `location` keyword.
            use_nicks (bool): Use nickname-replace (nicktype "object") on `searchdata`.
            typeclass (str or Typeclass, or list of either): Limit search only
                to `Objects` with this typeclass. May be a list of typeclasses
                for a broader search.
            location (Object or list): Specify a location or multiple locations
                to search. Note that this is used to query the *contents* of a
                location and will not match for the location itself -
                if you want that, don't set this or use `candidates` to specify
                exactly which objects should be searched.
            attribute_name (str): Define which property to search. If set, no
                key+alias search will be performed. This can be used
                to search database fields (db_ will be automatically
                appended), and if that fails, it will try to return
                objects having Attributes with this name and value
                equal to searchdata. A special use is to search for
                "key" here if you want to do a key-search without
                including aliases.
            quiet (bool): don't display default error messages - this tells the
                search method that the user wants to handle all errors
                themselves. It also changes the return value type, see
                below.
            exact (bool): if unset (default) - prefers to match to beginning of
                string rather than not matching at all. If set, requires
                exact matching of entire string.
            candidates (list of objects): this is an optional custom list of objects
                to search (filter) between. It is ignored if `global_search`
                is given. If not set, this list will automatically be defined
                to include the location, the contents of location and the
                caller's contents (inventory).
            nofound_string (str):  optional custom string for not-found error message.
            multimatch_string (str): optional custom string for multimatch error header.
            use_dbref (bool or None): If None, only turn off use_dbref if we are of a lower
                permission than Builder. Otherwise, honor the True/False value.

        Returns:
            match (Object, None or list): will return an Object/None if `quiet=False`,
                otherwise it will return a list of 0, 1 or more matches.

        Notes:
            To find Accounts, use eg. `evennia.account_search`. If
            `quiet=False`, error messages will be handled by
            `settings.SEARCH_AT_RESULT` and echoed automatically (on
            error, return will be `None`). If `quiet=True`, the error
            messaging is assumed to be handled by the caller.

        """
        is_string = isinstance(searchdata, basestring)

        if is_string:
            # searchdata is a string; wrap some common self-references
            if searchdata.lower() in ("here",):
                return [self.location] if quiet else self.location
            if searchdata.lower() in ("me", "self",):
                return [self] if quiet else self

        if use_nicks:
            # do nick-replacement on search
            searchdata = self.nicks.nickreplace(searchdata, categories=("object", "account"), include_account=True)

        if (global_search or (is_string and searchdata.startswith("#") and
                              len(searchdata) > 1 and searchdata[1:].isdigit())):
            # only allow exact matching if searching the entire database
            # or unique #dbrefs
            exact = True
        elif candidates is None:
            # no custom candidates given - get them automatically
            if location:
                # location(s) were given
                candidates = []
                for obj in make_iter(location):
                    candidates.extend(obj.contents)
            else:
                # local search. Candidates are taken from
                # self.contents, self.location and
                # self.location.contents
                location = self.location
                candidates = self.contents
                if location:
                    candidates = candidates + [location] + location.contents
                else:
                    # normally we don't need this since we are
                    # included in location.contents
                    candidates.append(self)

        # the sdesc-related substitution
        is_builder = self.locks.check_lockstring(self, "perm(Builder)")
        use_dbref = is_builder if use_dbref is None else use_dbref

        def search_obj(string):
            return ObjectDB.objects.object_search(string,
                                                  attribute_name=attribute_name,
                                                  typeclass=typeclass,
                                                  candidates=candidates,
                                                  exact=exact,
                                                  use_dbref=use_dbref)

        if candidates:
            candidates = parse_sdescs_and_recogs(self, candidates,
                                                 PREFIX + searchdata, search_mode=True)
            results = []
            for candidate in candidates:
                # we search by candidate keys here; this allows full error
                # management and use of all kwargs - we will use searchdata
                # in eventual error reporting later (not their keys). Doing
                # it like this e.g. allows for use of the typeclass kwarg
                # limiter.
                results.extend(search_obj(candidate.key))

            if not results and is_builder:
                # builders get a chance to search only by key+alias
                results = search_obj(searchdata)
        else:
            # global searches / #drefs end up here. Global searches are
            # only done in code, so is controlled, #dbrefs are turned off
            # for non-Builders.
            results = search_obj(searchdata)

        if quiet:
            return results
        return AT_SEARCH_RESULT(results, self, query=searchdata,
                                nofound_string=nofound_string, multimatch_string=multimatch_string)
