from commands.command import Command
from evennia import CmdSet
from typeclasses.characters import RecogError
from utils.tg_search_and_emote_regexes import *
from world.rpsystem import send_emote, parse_sdescs_and_recogs


class CmdEmote(Command):  # replaces the main emote
    """
    Emote an action, allowing dynamic replacement of
    text in the emote.

    Usage:
      emote text

    Example:
      espr /me looks around.
      espr With a flurry /me attacks /tall man with his sword.
      espr "Hello", /me says.

    Describes an event in the world. This allows the use of /ref
    markers to replace with the short descriptions or recognized
    strings of objects in the same room. These will be translated to
    emotes to match each person seeing it. Use "..." for saying
    things and langcode"..." without spaces to say something in
    a different language.

    """
    key = "espr"
    aliases = [":"]
    locks = "cmd:all()"

    def parse(self):
        self.args = self.args.strip()
        self.emote = self.args

    def func(self):
        """Perform the emote."""
        emote = self.emote
        if not emote:
            self.caller.msg("What do you want to do?")
        else:
            # we also include ourselves here.
            targets = self.caller.location.contents
            if not emote.endswith((".", "?", "!")):  # If emote is not punctuated,
                emote = "%s." % emote  # add a full-stop for good measure.
            send_emote(self.caller, targets, emote, anonymous_add='first')


class CmdSay(Command):  # replaces standard say
    """
    speak as your character

    Usage:
      say <message>

    """

    key = "di"
    aliases = []
    locks = "cmd:all()"

    def parse(self):
        self.args = self.args.strip()
        self.espr = ""
        if "|" in self.args:
            self.args, self.espr = self.args.split("|")
            self.args = self.args.strip()
            self.espr = self.espr.strip()
        if ":" not in self.args:
            self.speech = self.args
            self.receiver = ""
        else:
            self.receiver, self.speech = self.args.split(":")
            self.receiver = self.receiver.strip()
            self.speech = self.speech.strip()

    def func(self):
        "Run the say command"

        caller = self.caller

        if not self.speech:
            caller.msg("Cosa vuoi dire?")
            return

        speech = self.speech
        spiega = speech[-1] == ":"

        if not spiega and speech[-1] not in ["?", "!", ".", ":"]:
            speech = "{}.".format(speech)

        speech = caller.location.at_before_say(speech)
        # this is : and a space
        intermediary = ": "
        if self.espr:
            intermediary = " {espr}: ".format(espr=self.espr)

        if not self.receiver:
            # calling the speech hook on the location
            # preparing the speech with sdesc/speech parsing.
            speech_self = "{sp_dc}{intermediary}\'{speech}\'".format(speech=speech, intermediary=intermediary,
                                                                     sp_dc="spieghi" if spiega else "dici")

            speech_all = " /me {sp_dc}{intermediary}\'{speech}\'".format(speech=speech, intermediary=intermediary,
                                                                         sp_dc="spiega" if spiega else "dice")

            other_candidates = [x for x in caller.location.contents_get(exclude=caller)]
            speech_all = send_emote(caller, other_candidates, speech_all, anonymous_add=None, return_emote=True)
            speech_to_self = send_emote(caller, [caller], speech_self, anonymous_add=None, return_emote=True)[0]
            seq = zip([caller] + other_candidates, [speech_to_self] + speech_all)
        else:
            prefixed_rec = PREFIX + self.receiver
            receiver_obj = parse_sdescs_and_recogs(caller, caller.location.contents, prefixed_rec, search_mode=True)

            if not receiver_obj:
                caller.msg("A chi vuoi dirlo scusa?")
                return

            temp = "spiega" if spiega else "dice"

            if receiver_obj == caller:
                speech_to_self = "{sp_dc} a te stesso{intermediary}\'{speech}\'".format(speech=speech,
                                                                                        intermediary=intermediary,
                                                                                        sp_dc="spieghi" if spiega else "dici")
                speech_to_others = "/me {sp_dc} a se stesso{intermediary}\'{speech}\'".format(speech=speech,
                                                                                              intermediary=intermediary,
                                                                                              sp_dc=temp)
                speech_to_self = send_emote(caller, [caller], speech_to_self, anonymous_add=None, return_emote=True)[0]
                other_candidates = caller.location.contents_get(exclude=[caller, receiver_obj])
                speech_to_others = send_emote(caller, other_candidates, speech_to_others, anonymous_add=None,
                                              return_emote=True)
                seq = zip([caller] + other_candidates, [speech_to_self] + speech_to_others)

            else:
                speech_to_self = "{sp_dc} a {receiver}{intermediary}\'{speech}\'".format(speech=speech,
                                                                                         intermediary=intermediary,
                                                                                         receiver=prefixed_rec,
                                                                                         sp_dc="spieghi" if spiega else "dici")

                speech_to_rec = "/me ti {sp_dc}{intermediary}\'{speech}\'".format(speech=speech,
                                                                                  intermediary=intermediary,
                                                                                  sp_dc=temp)
                speech_to_others = "/me {sp_dc} a {receiver}{intermediary}\'{speech}\'".format(speech=speech,
                                                                                               intermediary=intermediary,
                                                                                               receiver=prefixed_rec,
                                                                                               sp_dc=temp)

                speech_to_self = send_emote(caller, [caller], speech_to_self, anonymous_add=None, return_emote=True)[0]
                speech_to_rec = \
                    send_emote(caller, [receiver_obj], speech_to_rec, anonymous_add=None, return_emote=True)[0]
                other_candidates = caller.location.contents_get(exclude=[caller, receiver_obj])
                speech_to_others = send_emote(caller, other_candidates, speech_to_others, anonymous_add=None,
                                              return_emote=True)
                seq = zip([caller, receiver_obj] + other_candidates,
                          [speech_to_self, speech_to_rec] + speech_to_others)

        for rec, txt in seq:
            rec.msg(txt.capitalize().strip())


class CmdPose(Command):  # set current pose and default pose
    """
    Set a static pose

    Usage:
        pose <pose>
        pose default <pose>
        pose reset
        pose obj = <pose>
        pose default obj = <pose>
        pose reset obj =

    Examples:
        pose leans against the tree
        pose is talking to the barkeep.
        pose box = is sitting on the floor.

    Set a static pose. This is the end of a full sentence that starts
    with your sdesc. If no full stop is given, it will be added
    automatically. The default pose is the pose you get when using
    pose reset. Note that you can use sdescs/recogs to reference
    people in your pose, but these always appear as that person's
    sdesc in the emote, regardless of who is seeing it.

    """
    key = "|"
    aliases = []
    locks = "cmd:all()"

    def parse(self):
        """
        Extract the "default" alternative to the pose.
        """
        args = self.args.strip()
        default = args.startswith("default")
        reset = args.startswith("reset")
        if default:
            args = re.sub(r"^default", "", args)
        if reset:
            args = re.sub(r"^reset", "", args)
        target = None
        if "=" in args:
            target, args = [part.strip() for part in args.split("=", 1)]

        self.target = target
        self.reset = reset
        self.default = default
        self.args = args.strip()

    def func(self):
        "Create the pose"
        caller = self.caller
        pose = self.args
        target = self.target
        if not pose and not self.reset:
            caller.msg("Usage: pose <pose-text> OR pose obj = <pose-text>")
            return

        if not pose.endswith("."):
            pose = "%s." % pose
        if target:
            # affect something else
            target = caller.search(target)
            if not target:
                return
            if not target.access(caller, "edit"):
                caller.msg("You can't pose that.")
                return
        else:
            target = caller

        if not target.attributes.has("pose"):
            caller.msg("%s cannot be posed." % target.key)
            return

        target_name = target.sdesc.get() if hasattr(target, "sdesc") else target.key
        # set the pose
        if self.reset:
            pose = target.db.pose_default
            target.db.pose = pose
        elif self.default:
            target.db.pose_default = pose
            caller.msg("Default pose is now '%s %s'." % (target_name, pose))
            return
        else:
            # set the pose. We do one-time ref->sdesc mapping here.
            parsed, mapping = parse_sdescs_and_recogs(caller, caller.location.contents, pose)
            mapping = dict((ref, obj.sdesc.get() if hasattr(obj, "sdesc") else obj.key)
                           for ref, obj in mapping.iteritems())
            pose = parsed.format(**mapping)

            if len(target_name) + len(pose) > 60:
                caller.msg("Your pose '%s' is too long." % pose)
                return

            target.db.pose = pose

        caller.msg("Pose will read '%s %s'." % (target_name, pose))


class CmdRecog(Command):  # assign personal alias to object in room
    """
    Recognize another person in the same room.

    Usage:
      recog sdesc as alias
      forget alias

    Example:
        recog tall man as Griatch
        forget griatch

    This will assign a personal alias for a person, or
    forget said alias.

    """
    key = "recog"
    aliases = ["recognize", "forget"]

    def parse(self):
        "Parse for the sdesc as alias structure"
        if " as " in self.args:
            self.sdesc, self.alias = [part.strip() for part in self.args.split(" as ", 2)]
        elif self.args:
            # try to split by space instead
            try:
                self.sdesc, self.alias = [part.strip() for part in self.args.split(None, 1)]
            except ValueError:
                self.sdesc, self.alias = self.args.strip(), ""

    def func(self):
        "Assign the recog"
        caller = self.caller
        if not self.args:
            caller.msg("Usage: recog <sdesc> as <alias> or forget <alias>")
            return
        sdesc = self.sdesc
        alias = self.alias.rstrip(".?!")
        prefixed_sdesc = sdesc if sdesc.startswith(PREFIX) else PREFIX + sdesc
        candidates = caller.location.contents
        matches = parse_sdescs_and_recogs(caller, candidates, prefixed_sdesc, search_mode=True)
        nmatches = len(matches)
        # handle 0, 1 and >1 matches
        if nmatches == 0:
            caller.msg(EMOTE_NOMATCH_ERROR.format(ref=sdesc))
        elif nmatches > 1:
            reflist = ["%s%s%s (%s%s)" % (inum + 1, NUM_SEP,
                                          RE_PREFIX.sub("", sdesc), caller.recog.get(obj),
                                          " (%s)" % caller.key if caller == obj else "")
                       for inum, obj in enumerate(matches)]
            caller.msg(EMOTE_MULTIMATCH_ERROR.format(ref=sdesc, reflist="\n    ".join(reflist)))
        else:
            obj = matches[0]
            if not obj.access(self.obj, "enable_recog", default=True):
                # don't apply recog if object doesn't allow it (e.g. by being masked).
                caller.msg("Can't recognize someone who is masked.")
                return
            if self.cmdstring == "forget":
                # remove existing recog
                caller.recog.remove(obj)
                caller.msg("%s will now know only '%s'." % (caller.key, obj.recog.get(obj)))
            else:
                sdesc = obj.sdesc.get() if hasattr(obj, "sdesc") else obj.key
                try:
                    alias = caller.recog.add(obj, alias)
                except RecogError as err:
                    caller.msg(err)
                    return
                caller.msg("%s will now remember |w%s|n as |w%s|n." % (caller.key, sdesc, alias))


class CmdMask(Command):
    """
    Wear a mask

    Usage:
        mask <new sdesc>
        unmask

    This will put on a mask to hide your identity. When wearing
    a mask, your sdesc will be replaced by the sdesc you pick and
    people's recognitions of you will be disabled.

    """
    key = "mask"
    aliases = ["unmask"]

    def func(self):
        caller = self.caller
        if self.cmdstring == "mask":
            # wear a mask
            if not self.args:
                caller.msg("Usage: (un)mask sdesc")
                return
            if caller.db.unmasked_sdesc:
                caller.msg("You are already wearing a mask.")
                return
            sdesc = RE_CHAREND.sub("", self.args)
            sdesc = "%s |H[masked]|n" % sdesc
            if len(sdesc) > 60:
                caller.msg("Your masked sdesc is too long.")
                return
            caller.db.unmasked_sdesc = caller.sdesc.get()
            caller.locks.add("enable_recog:false()")
            caller.sdesc.add(sdesc)
            caller.msg("You wear a mask as '%s'." % sdesc)
        else:
            # unmask
            old_sdesc = caller.db.unmasked_sdesc
            if not old_sdesc:
                caller.msg("You are not wearing a mask.")
                return
            del caller.db.unmasked_sdesc
            caller.locks.remove("enable_recog")
            caller.sdesc.add(old_sdesc)
            caller.msg("You remove your mask and are again '%s'." % old_sdesc)


class TGSocialSystemCmdSet(CmdSet):
    """
    Mix-in for adding rp-commands to default cmdset.
    """

    def at_cmdset_creation(self):
        self.add(CmdEmote())
        self.add(CmdSay())
        self.add(CmdPose())
        self.add(CmdRecog())
        self.add(CmdMask())
