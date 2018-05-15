# coding=utf-8
"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import ansi
from evennia.utils import logger, lazy_property
from typeclasses.defaults.default_characters import Character
from utils.tg_search_and_emote_regexes import *
from world.traits_handler import TraitHandler


class RecogError(Exception):
    pass


class RecogHandler(object):
    """
    This handler manages the recognition mapping
    of an Object.

    The handler stores data in Attributes as dictionaries of
    the following names:

        _recog_ref2recog
        _recog_obj2recog
        _recog_obj2regex

    """

    def __init__(self, obj):
        """
        Initialize the handler

        Args:
            obj (Object): The entity on which this handler is stored.

        """
        self.obj = obj
        # mappings
        self.obj2recog = {}
        self._cache()

    def _cache(self):
        """
        Load data to handler cache
        """
        obj2recog = self.obj.attributes.get("_recog_obj2recog", default={})

        self.obj2recog = dict((obj, recog)
                              for obj, recog in obj2recog.items() if obj)

    def add(self, obj, recog, max_length=60):
        """
        Assign a custom recog (nick) to the given object.

        Args:
            obj (Object): The object ot associate with the recog
                string. This is usually determined from the sdesc in the
                room by a call to parse_sdescs_and_recogs, but can also be
                given.
            recog (str): The replacement string to use with this object.
            max_length (int, optional): The max length of the recog string.

        Returns:
            recog (str): The (possibly cleaned up) recog string actually set.

        Raises:
            SdescError: When recog could not be set or sdesc longer
                than `max_length`.

        """
        if not obj.access(self.obj, "enable_recog", default=True):
            raise RecogError("This person is unrecognizeable.")

        # strip emote components from recog
        recog = RE_REF.sub(
            r"\1", RE_REF_LANG.sub(
                r"\1", RE_SELF_REF.sub(
                    r"", RE_LANGUAGE.sub(
                        r"", RE_OBJ_REF_START.sub(r"", recog)))))

        # make an recog clean of ANSI codes
        cleaned_recog = ansi.strip_ansi(recog)

        if not cleaned_recog:
            raise RecogError("Recog string cannot be empty.")

        if len(cleaned_recog) > max_length:
            raise RecogError(
                "Recog string cannot be longer than %i chars (was %i chars)" % (max_length, len(cleaned_recog)))

        self.obj.attributes.get("_recog_obj2recog", default={})[obj] = recog
        # local caching
        self.obj2recog[obj] = recog
        return recog

    def get(self, obj, default=None):
        """
        Get recog replacement string, if one exists, otherwise
        get sdesc and as a last resort, the object's key.

        Args:
            obj (Object): The object, whose sdesc to replace
        Returns:
            recog (str): The replacement string to use.

        Notes:
            This method will respect a "enable_recog" lock set on
            `obj` (True by default) in order to turn off recog
            mechanism. This is useful for adding masks/hoods etc.
        """
        if obj.access(self.obj, "enable_recog", default=True):
            # check an eventual recog_masked lock on the object
            # to avoid revealing masked characters. If lock
            # does not exist, pass automatically.
            if not default:
                return self.obj2recog.get(obj, obj.sdesc.get() if hasattr(obj, "sdesc") else obj.key)
            else:
                return self.obj2recog.get(obj, default)
        else:
            # recog_mask log not passed, disable recog
            if default:
                return default
            else:
                return obj.sdesc.get() if hasattr(obj, "sdesc") else obj.key

    def remove(self, obj):
        """
        Clear recog for a given object.

        Args:
            obj (Object): The object for which to remove recog.
        """
        ret_flag = False
        if obj in self.obj2recog:
            del self.obj.db._recog_obj2recog[obj]
            ret_flag = True
        self._cache()
        return ret_flag


class SdescHandler(object):
    obj = None

    def __init__(self, obj):
        self.obj = obj
        self.sdesc = ""
        self._cache()

    def _cache(self):
        self.sdesc = self.obj.attributes.get("sdesc", "")

    def add(self, sdesc, ):
        self.obj.attributes.add("sdesc", sdesc)
        self.sdesc = sdesc

    def get(self):
        return self.sdesc


class TGCharacter(Character):

    def at_object_creation(self):
        self.db.gender = "m"

        self.db.slots = {
            'impugnatura1': None,
            'impugnatura2': None,
            'armatura': None,
        }
        self.db.limbs = (
            ('r_arm', ('impugnatura1',)),
            ('l_arm', ('impugnatura2',)),
            ('corpo', ('armatura',)),
        )

        # defaults
        self.db.altezza = 170
        self.db.aggettivo = ""
        self.db.pose = ""
        self.db.pose_default = "è qui."

        self.db._recog_obj2recog = {}
        self.coordinates = None

    @lazy_property
    def traits(self):
        return TraitHandler(self)

    @lazy_property
    def recog(self):
        return RecogHandler(self)

    @lazy_property
    def sdesc(self):
        return SdescHandler(self)

    @property
    def coordinates(self):
        return self.ndb.coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        self.ndb.coordinates = coordinates

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

    def at_pre_puppet(self, account, session=None, **kwargs):
        """
        Return the character from storage in None location in `at_post_unpuppet`.
        Args:
            account (Account): This is the connecting account.
            session (Session): Session controlling the connection.
        """
        from world.mapengine.map_engine import TGMapEngineFactory
        from django.conf import settings

        map_handler = TGMapEngineFactory().get()
        # mi asicuro di essere in una location valida
        logger.log_info(
            "at_pre_puppet():\nself.location:{}\nself.db.last_valid_area:{}\nself.db.last_valid_coordinates:{}".format(
                self.location, self.db.last_valid_area, self.db.last_valid_coordinates))

        # Ogni volta che mi loggo self.location sarà None, altrimenti può succedere che puppetto qualcuno, e allora
        # in base a dove parto devo stare attento

        if self.location is None:

            if self.db.last_valid_area == settings.WILD_AREA_NAME or map_handler._rooms.contains(
                    self.db.last_valid_coordinates):

                # mi sposto in last_valid_coordinates o in home se fallisco, altrimenti esplodo
                if not map_handler.move_obj(self, self.db.last_valid_coordinates, quiet=True, move_hooks=False):
                    self.location = self.home

            else:
                # se invece l'ultima zona non è la wild uso prelogout_location
                # giusto per ricordarmi la last_valid_area è già coerente non devo aggiornarla
                self.location = self.db.prelogout_location if self.db.prelogout_location else self.home

            if self.location:
                self.location.at_object_receive(self, source_location=None)

        if self.location:
            # aggiorno tutto sapendo che self.location è pronta

            if self.location.coordinates:
                self.db.last_valid_coordinates = self.location.coordinates

            self.db.last_valid_area = self.location.tags.get(category="area")
            self.db.prelogout_location = self.location  # save location again to be sure.
        else:
            account.msg("|r%s non ha una stanza settata e nemmeno una home.|n" % self, session=session)

    def at_post_unpuppet(self, account, session=None, **kwargs):
        """
        We stove away the character when the account goes ooc/logs off,
        otherwise the character object will remain in the room also
        after the account logged off ("headless", so to say).

        Args:
            account (Account): The account object that just disconnected
                from this object.
            session (Session): Session controlling the connection that
                just disconnected.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not self.sessions.count():
            # only remove this char from grid if no sessions control it anymore.
            if self.location:
                from django.conf import settings
                def message(obj, from_obj):
                    obj.msg("%s ha lasciato il gioco." % self.get_display_name(obj), from_obj=from_obj)

                self.location.for_contents(message, exclude=[self], from_obj=self)
                if self.location.coordinates:
                    self.db.last_valid_coordinates = self.location.coordinates

                self.db.prelogout_location = self.location
                self.db.last_valid_area = self.location.tags.get(category="area")

                logger.log_info(
                    "at_post_unpuppet():"
                    "\nlast_valid_coordinates{}\nself.last_valid_area:{}\nself.db.prelogout_location:{}".format(
                        self.db.last_valid_coordinates, self.db.last_valid_area, self.db.prelogout_location))

                self.location = None

    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object.

        Kwargs:
            pose (bool): Include the pose (if available) in the return.

        Returns:
            name (str): A string of the sdesc containing the name of the object,
            if this is defined.
                including the DBREF if this user is privileged to control
                said object.

        Notes:
            The RPCharacter version of this method colors its display to make
            characters stand out from other objects.

        """
        idstr = "(#%s)" % self.id if self.access(looker, access_type='control') else ""
        if looker == self:
            sdesc = self.key
        else:
            try:
                recog = looker.recog.get(self)
            except AttributeError:
                recog = None
            sdesc = recog or self.sdesc.get()

        pose = " %s" % (self.db.pose or "è qui.") if kwargs.get("pose", False) else ""

        return "|c%s|n%s%s" % (sdesc.capitalize() if kwargs.get("capitalize", False) else sdesc, idstr, pose)

    def process_sdesc(self, sdesc, obj, **kwargs):
        """
        Allows to customize how your sdesc is displayed (primarily by
        changing colors).

        Args:
            sdesc (str): The sdesc to display.
            obj (Object): The object to which the adjoining sdesc
                belongs. If this object is equal to yourself, then
                you are viewing yourself (and sdesc is your key).
                This is not used by default.

        Returns:
            sdesc (str): The processed sdesc ready
                for display.

        """
        return "%s" % sdesc

    def process_recog(self, recog, obj, **kwargs):
        """
        Allows to customize how a recog string is displayed.

        Args:
            recog (str): The recog string. It has already been
                translated from the original sdesc at this point.
            obj (Object): The object the recog:ed string belongs to.
                This is not used by default.

        Returns:
            recog (str): The modified recog string.

        """
        return self.process_sdesc(recog, obj)

    def process_language(self, text, speaker, language, **kwargs):
        """
        Allows to process the spoken text, for example
        by obfuscating language based on your and the
        speaker's language skills. Also a good place to
        put coloring.

        Args:
            text (str): The text to process.
            speaker (Object): The object delivering the text.
            language (str): An identifier string for the language.

        Return:
            text (str): The optionally processed text.

        Notes:
            This is designed to work together with a string obfuscator
            such as the `obfuscate_language` or `obfuscate_whisper` in
            the evennia.contrib.rplanguage module.

        """
        return "%s|w%s|n" % ("|W(%s)" % language if language else "", text)

        # from evennia.contrib import rplanguage
        # return "|w%s|n" % rplanguage.obfuscate_language(text, level=1.0)

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
        """
        if not looker:
            return ""
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and
                   con.access(looker, "view"))
        exits, users, things = [], [], []
        for con in visible:
            key = con.get_display_name(looker, pose=True, capitalize=True)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append(key)
            else:
                things.append(key)
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker, pose=False, capitalize=True)
        desc = self.desc
        if desc:
            string += "%s" % desc
        if exits:
            string += "\n|wExits:|n " + ", ".join(exits)
        if users or things:
            string += "\n " + "\n ".join(users + things)
        return string
