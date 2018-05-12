"""
Roleplaying base system for Evennia

Contribution - Griatch, 2015

This module contains the ContribRPObject, ContribRPRoom and
ContribRPCharacter typeclasses.  If you inherit your
objects/rooms/character from these (or make them the defaults) from
these you will get the following features:

    - Objects/Rooms will get the ability to have poses and will report
    the poses of items inside them (the latter most useful for Rooms).
    - Characters will get poses and also sdescs (short descriptions)
    that will be used instead of their keys. They will gain commands
    for managing recognition (custom sdesc-replacement), masking
    themselves as well as an advanced free-form emote command.

To use, simply import the typclasses you want from this module and use
them to create your objects, or set them to default.

In more detail, This RP base system introduces the following features
to a game, common to many RP-centric games:

    - emote system using director stance emoting (names/sdescs).
        This uses a customizable replacement noun (/me, @ etc) to
        represent you in the emote. You can use /sdesc, /nick, /key or
        /alias to reference objects in the room. You can use any
        number of sdesc sub-parts to differentiate a local sdesc, or
        use /1-sdesc etc to differentiate them. The emote also
        identifies nested says.
    - sdesc obscuration of real character names for use in emotes
        and in any referencing such as object.search().  This relies
        on an SdescHandler `sdesc` being set on the Character and
        makes use of a custom Character.get_display_name hook. If
        sdesc is not set, the character's `key` is used instead. This
        is particularly used in the emoting system.
    - recog system to assign your own nicknames to characters, can then
        be used for referencing. The user may recog a user and assign
        any personal nick to them. This will be shown in descriptions
        and used to reference them. This is making use of the nick
        functionality of Evennia.
    - masks to hide your identity (using a simple lock).
    - pose system to set room-persistent poses, visible in room
        descriptions and when looking at the person/object.  This is a
        simple Attribute that modifies how the characters is viewed when
        in a room as sdesc + pose.
    - in-emote says, including seamless integration with language
        obscuration routine (such as contrib/rplanguage.py)

Examples:

> look
Tavern
The tavern is full of nice people

*A tall man* is standing by the bar.

Above is an example of a player with an sdesc "a tall man". It is also
an example of a static *pose*: The "standing by the bar" has been set
by the player of the tall man, so that people looking at him can tell
at a glance what is going on.

> emote /me looks at /tall and says "Hello!"

I see:
    Griatch looks at Tall man and says "Hello".
Tall man (assuming his name is Tom) sees:
    The godlike figure looks at Tom and says "Hello".

Verbose Installation Instructions:

    1. In typeclasses/character.py:
       Import the `ContribRPCharacter` class:
           `from evennia.contrib.rpsystem import ContribRPCharacter`
       Inherit ContribRPCharacter:
           Change "class Character(DefaultCharacter):" to
           `class Character(ContribRPCharacter):`
       If you have any overriden calls in `at_object_creation(self)`:
           Add `super(Character,self).at_object_creation()` as the top line.
    2. In `typeclasses/rooms.py`:
           Import the `ContribRPRoom` class:
           `from evennia.contrib.rpsystem import ContribRPRoom`
       Inherit `ContribRPRoom`:
           Change `class Room(DefaultRoom):` to
           `class Room(ContribRPRoom):`
    3. In `typeclasses/objects.py`
           Import the `ContribRPObject` class:
           `from evennia.contrib.rpsystem import ContribRPObject`
       Inherit `ContribRPObject`:
           Change `class Object(DefaultObject):` to
           `class Object(ContribRPObject):`
    4. Reload the server (@reload or from console: "evennia reload")
    5. Force typeclass updates as required. Example for your character:
           @type/reset/force me = typeclasses.characters.Character

"""
from evennia.utils import string_partial_matching
from utils.tg_search_and_emote_regexes import *


# ------------------------------------------------------------
# Emote parser
# ------------------------------------------------------------


# the emote parser works in two steps:
#  1) convert the incoming emote into an intermediary
#     form with all object references mapped to ids.
#  2) for every person seeing the emote, parse this
#     intermediary form into the one valid for that char.


class EmoteError(Exception):
    pass


class SdescError(Exception):
    pass


class LanguageError(Exception):
    pass


def _dummy_process(text, *args, **kwargs):
    "Pass-through processor"
    return text


# emoting mechanisms
def parse_language(speaker, emote):
    """
    Parse the emote for language. This is
    used with a plugin for handling languages.

    Args:
        speaker (Object): The object speaking.
        emote (str): An emote possibly containing
            language references.

    Returns:
        (emote, mapping) (tuple): A tuple where the
            `emote` is the emote string with all says
            (including quotes) replaced with reference
            markers on the form {##n} where n is a running
            number. The `mapping` is a dictionary between
            the markers and a tuple (langname, saytext), where
            langname can be None.
    Raises:
        LanguageError: If an invalid language was specified.

    Notes:
        Note that no errors are raised if the wrong language identifier
        is given.
        This data, together with the identity of the speaker, is
        intended to be used by the "listener" later, since with this
        information the language skill of the speaker can be offset to
        the language skill of the listener to determine how much
        information is actually conveyed.

    """
    # escape mapping syntax on the form {##id} if it exists already in emote,
    # if so it is replaced with just "id".
    emote = RE_REF_LANG.sub(r"\1", emote)

    errors = []
    mapping = {}
    for imatch, say_match in enumerate(reversed(list(RE_LANGUAGE.finditer(emote)))):
        # process matches backwards to be able to replace
        # in-place without messing up indexes for future matches
        # note that saytext includes surrounding "...".
        langname, saytext = say_match.groups()
        istart, iend = say_match.start(), say_match.end()
        # the key is simply the running match in the emote
        key = "##%i" % imatch
        # replace say with ref markers in emote
        emote = emote[:istart] + "{%s}" % key + emote[iend:]
        mapping[key] = (langname, saytext)

    if errors:
        # catch errors and report
        raise LanguageError("\n".join(errors))

    # at this point all says have been replaced with {##nn} markers
    # and mapping maps 1:1 to this.
    return emote, mapping


def parse_sdescs_and_recogs(sender, candidates, string, search_mode=False):
    """
    Read a raw emote and parse it into an intermediary
    format for distributing to all observers.

    Args:
        sender (Object): The object sending the emote. This object's
            recog data will be considered in the parsing.
        candidates (iterable): A list of objects valid for referencing
            in the emote.
        string (str): The string (like an emote) we want to analyze for keywords.
        search_mode (bool, optional): If `True`, the "emote" is a query string
            we want to analyze. If so, the return value is changed.

    Returns:
        (emote, mapping) (tuple): If `search_mode` is `False`
            (default), a tuple where the emote is the emote string, with
            all references replaced with internal-representation {#dbref}
            markers and mapping is a dictionary `{"#dbref":obj, ...}`.
        result (list): If `search_mode` is `True` we are
            performing a search query on `string`, looking for a specific
            object. A list with zero, one or more matches.

    Raises:
        EmoteException: For various ref-matching errors.

    Notes:
        The parser analyzes and should understand the following
        _PREFIX-tagged structures in the emote:
        - self-reference (/me)
        - recogs (any part of it) stored on emoter, matching obj in `candidates`.
        - sdesc (any part of it) from any obj in `candidates`.
        - N-sdesc, N-recog separating multi-matches (1-tall, 2-tall)
        - says, "..." are

    """
    # escape mapping syntax on the form {#id} if it exists already in emote,
    # if so it is replaced with just "id".
    string = RE_REF.sub(r"\1", string)
    # escape loose { } brackets since this will clash with formatting
    string = RE_LEFT_BRACKETS.sub("{{", string)
    string = RE_RIGHT_BRACKETS.sub("}}", string)

    # we now loop over all references and analyze them
    mapping = {}
    errors = []
    obj = None
    nmatches = 0
    for marker_match in reversed(list(RE_OBJ_REF_START.finditer(string))):
        # we scan backwards so we can replace in-situ without messing
        # up later occurrences. Given a marker match, query from
        # start index forward for all candidates.

        # first see if there is a number given (e.g. 1-tall)
        num_identifier, obj_str = marker_match.groups("")  # return "" if no match, rather than None

        if RE_SELF_REF.match(PREFIX + obj_str):
            bestmatches = [sender]
        else:
            bestmatches = [x for x in candidates if string_partial_matching([sender.recog.get(x, "")], obj_str)]
            if not bestmatches:
                bestmatches = [x for x in candidates if
                               string_partial_matching([x.sdesc.get() if hasattr(x, "sdesc") else x.key], obj_str)]

        nmatches = len(bestmatches)

        if not nmatches:
            # no matches
            obj = None
            nmatches = 0
        elif nmatches == 1:
            # an exact match.
            obj = bestmatches[0]
            nmatches = 1
        elif all(bestmatches[0].id == obj.id for obj in bestmatches):
            # multi-match but all matches actually reference the same
            # obj (could happen with clashing recogs + sdescs)
            obj = bestmatches[0]
            nmatches = 1
        else:
            # multi-match.
            # was a numerical identifier given to help us separate the multi-match?
            inum = min(max(0, int(num_identifier) - 1), nmatches - 1) if num_identifier else None
            if inum is not None:
                # A valid inum is given. Use this to separate data.
                obj = bestmatches[inum]
                nmatches = 1
            else:
                # no identifier given - a real multimatch. prendiamo solo il primo risultato
                obj = bestmatches[0]
                nmatches = 1

        if search_mode:
            # single-object search mode. Don't continue loop.
            return obj

        elif nmatches == 0:
            errors.append(EMOTE_NOMATCH_ERROR.format(ref=marker_match.group()))
        else:
            # allora nmatches == 1
            key = "#%i" % obj.id
            string = string[:marker_match.start()] + "{%s}" % key + string[marker_match.end():]
            mapping[key] = obj

    if search_mode:
        # return list of object(s) matching
        if nmatches == 0:
            return None
        else:
            return obj

    if errors:
        # make sure to not let errors through.
        raise EmoteError("\n".join(errors))

    # at this point all references have been replaced with {#xxx} markers and the mapping contains
    # a 1:1 mapping between those inline markers and objects.
    return string, mapping


def send_emote(sender, receivers, emote, candidates=None, anonymous_add="first", return_emote=False):
    """
    Main access function for distribute an emote.

    Args:
        sender (Object): The one sending the emote.
        receivers (iterable): Receivers of the emote. These
            will also form the basis for which sdescs are
            'valid' to use in the emote.
        emote (str): The raw emote string as input by emoter.
        anonymous_add (str or None, optional): If `sender` is not
            self-referencing in the emote, this will auto-add
            `sender`'s data to the emote. Possible values are
            - None: No auto-add at anonymous emote
            - 'last': Add sender to the end of emote as [sender]
            - 'first': Prepend sender to start of emote.

    """
    if not candidates:
        candidates = receivers  # questo era la  classica chiamata

    emote, obj_mapping = parse_sdescs_and_recogs(sender, candidates, emote)
    emote, language_mapping = parse_language(sender, emote)
    # we escape the object mappings since we'll do the language ones first
    # (the text could have nested object mappings).
    emote = RE_REF.sub(r"{{#\1}}", emote)

    if anonymous_add and not "#%i" % sender.id in obj_mapping:
        # no self-reference in the emote - add to the end
        key = "#%i" % sender.id
        obj_mapping[key] = sender
        if anonymous_add == 'first':
            possessive = "" if emote.startswith('\'') else " "
            emote = "%s%s%s" % ("{{%s}}" % key, possessive, emote)
        else:
            emote = "%s [%s]" % (emote, "{{%s}}" % key)

    # broadcast emote to everyone
    ret = []
    for receiver in receivers:
        # first handle the language mapping, which always produce different keys ##nn
        receiver_lang_mapping = {}
        try:
            process_language = receiver.process_language
        except AttributeError:
            process_language = _dummy_process
        for key, (langname, saytext) in language_mapping.iteritems():
            # color says
            receiver_lang_mapping[key] = process_language(saytext, sender, langname)
        # map the language {##num} markers. This will convert the escaped sdesc markers on
        # the form {{#num}} to {#num} markers ready to sdescmat in the next step.
        sendemote = emote.format(**receiver_lang_mapping)

        # handle sdesc mappings. we make a temporary copy that we can modify
        try:
            process_sdesc = receiver.process_sdesc
        except AttributeError:
            process_sdesc = _dummy_process

        try:
            process_recog = receiver.process_recog
        except AttributeError:
            process_recog = _dummy_process

        try:
            recog_get = receiver.recog.get
            receiver_sdesc_mapping = dict((ref, process_recog(recog_get(obj), obj)) for ref, obj in obj_mapping.items())
        except AttributeError:
            receiver_sdesc_mapping = dict((ref, process_sdesc(obj.sdesc.get(), obj)
            if hasattr(obj, "sdesc") else process_sdesc(obj.key, obj))
                                          for ref, obj in obj_mapping.items())
        # make sure receiver always sees their real name
        rkey = "#%i" % receiver.id
        if rkey in receiver_sdesc_mapping:
            receiver_sdesc_mapping[rkey] = process_sdesc(receiver.key, receiver)

        # do the template replacement of the sdesc/recog {#num} markers
        temp = sendemote.format(**receiver_sdesc_mapping)
        if return_emote:
            ret.append(temp)
        else:
            receiver.msg(temp)

    if return_emote:
        return ret
