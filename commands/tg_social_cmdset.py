# coding=utf-8
from commands.command import Command
from evennia import CmdSet
from typeclasses.characters import RecogError
from utils.tg_search_and_emote_regexes import *
from world.rpsystem import send_emote, parse_sdescs_and_recogs, EmoteError, LanguageError


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
            self.caller.msg("Cosa vuoi esprimere?")
        else:
            # we also include ourselves here.
            targets = self.caller.location.contents_get(exclude=self.caller) + [self.caller]
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

        # call hook on location
        speech = caller.location.at_before_say(speech)

        # this is : and a space
        intermediary = ": "
        if self.espr:
            intermediary = " {espr}: ".format(espr=self.espr)

        # main "others" objs da cui prendere per le varaibili. è il  candidates di parse_sdesc
        feed_obj_candidates = caller.location.contents_get(exclude=caller)

        try:
            if not self.receiver:
                speech_self = "{sp_dc}{intermediary}\'{speech}\'".format(speech=speech,
                                                                         intermediary=intermediary,
                                                                         sp_dc="spieghi" if spiega else "dici")

                speech_all = " /me {sp_dc}{intermediary}\'{speech}\'".format(speech=speech,
                                                                             intermediary=intermediary,
                                                                             sp_dc="spiega" if spiega else "dice")

                speech_to_self = send_emote(caller, [caller], speech_self, candidates=feed_obj_candidates,
                                            anonymous_add=None, return_emote=True)[0]

                speech_all = send_emote(caller, feed_obj_candidates, speech_all, candidates=feed_obj_candidates,
                                        anonymous_add=None, return_emote=True)

                seq = zip([caller] + feed_obj_candidates, [speech_to_self] + speech_all)

            else:
                prefixed_rec = PREFIX + self.receiver

                receiver_obj = parse_sdescs_and_recogs(caller, feed_obj_candidates + [caller], prefixed_rec,
                                                       search_mode=True)

                if not receiver_obj:
                    caller.msg("A chi vuoi dirlo scusa?")
                    return

                temp = "spiega" if spiega else "dice"

                if receiver_obj != caller:
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
                    speech_to_self = send_emote(caller, [caller], speech_to_self,
                                                candidates=feed_obj_candidates, anonymous_add=None,
                                                return_emote=True)[0]

                    speech_to_rec = send_emote(caller, [receiver_obj], speech_to_rec,
                                               candidates=feed_obj_candidates, anonymous_add=None,
                                               return_emote=True)[0]

                    other_listener = [x for x in feed_obj_candidates if
                                      x != receiver_obj]  # quindi senza caller e receiver_obj

                    speech_to_others = send_emote(caller, other_listener, speech_to_others,
                                                  candidates=feed_obj_candidates, anonymous_add=None,
                                                  return_emote=True)

                    seq = zip([caller, receiver_obj] + other_listener,
                              [speech_to_self, speech_to_rec] + speech_to_others)

                else:
                    speech_to_self = "{sp_dc} a te stesso{intermediary}\'{speech}\'".format(speech=speech,
                                                                                            intermediary=intermediary,
                                                                                            sp_dc="spieghi" if spiega else "dici")
                    speech_to_others = "/me {sp_dc} a se stesso{intermediary}\'{speech}\'".format(speech=speech,
                                                                                                  intermediary=intermediary,
                                                                                                  sp_dc=temp)
                    speech_to_self = send_emote(caller, [caller], speech_to_self,
                                                candidates=feed_obj_candidates, anonymous_add=None,
                                                return_emote=True)[0]

                    speech_to_others = send_emote(caller, feed_obj_candidates, speech_to_others,
                                                  candidates=feed_obj_candidates, anonymous_add=None,
                                                  return_emote=True)

                    seq = zip([caller] + feed_obj_candidates, [speech_to_self] + speech_to_others)

        except (EmoteError, LanguageError) as err:
            caller.msg("%s" % err)
            return

        for rec, txt in seq:
            rec.msg(txt.strip().capitalize())


class CmdPose(Command):  # set current pose and default pose
    """
    Set a static pose

    Usage:
        | <pose>
        | default <pose>
        | reset
        | obj = <pose>
        | default obj = <pose>
        | reset obj =

    Examples:
        | appggiato spalle ad un albero è qui
        | is talking to the barkeep.
        | box = is sitting on the floor.

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
        """Create the pose"""
        caller = self.caller
        pose = self.args
        target = self.target
        if not pose and not self.reset:
            caller.msg("Usage: | <pose-text> OR | obj = <pose-text>")
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
            caller.msg("Non puoi su %s." % target.key)
            return

        target_name = target.sdesc.get() if hasattr(target, "sdesc") else target.key
        # set the pose
        if self.reset:
            pose = target.db.pose_default
            target.db.pose = pose
        elif self.default:
            target.db.pose_default = pose
            caller.msg("La posa ora è: '%s %s'." % (target_name, pose))
            return
        else:
            # set the pose. We do one-time ref->sdesc mapping here.
            parsed, mapping = parse_sdescs_and_recogs(caller, caller.location.contents, pose)
            mapping = dict((ref, obj.sdesc.get() if hasattr(obj, "sdesc") else obj.key)
                           for ref, obj in mapping.iteritems())
            pose = parsed.format(**mapping)

            if len(target_name) + len(pose) > 60:
                caller.msg("Posa '%s' troppo lunga." % pose)
                return

            target.db.pose = pose

        caller.msg("Gli altri leggeranno '%s %s'." % (target_name, pose))


class CmdRecog(Command):  # assign personal alias to object in room
    """
    Recognize another person in the same room.

    Usage:
      recog sdesc as alias
      forget alias

    Example:
        recog <qualcuno> <come>
        forget <qualcuno>

    This will assign a personal alias for a person, or
    forget said alias.

    """
    key = "ricorda"
    aliases = ["dimentica"]

    def parse(self):
        """Parse for the sdesc as alias structure"""

        self.args = self.args.strip()
        temp = self.args.split(" ")
        if len(temp) >= 2:
            self.chi, self.come = temp[:2]
        else:
            self.chi, self.come = self.args, ""

    def func(self):
        """Assign the recog"""
        caller = self.caller
        if not self.args or (self.cmdstring == "ricorda" and not self.come):
            caller.msg("Usage: ricorda <pg> <alias> oppure dimentica <alias>")
            return

        target = self.chi
        prefixed_sdesc = target if target.startswith(PREFIX) else PREFIX + target
        candidates = caller.location.contents_get(exclude=caller)
        obj = parse_sdescs_and_recogs(caller, candidates, prefixed_sdesc, search_mode=True)
        # handle 0, 1 and >1 matches
        if not obj:
            caller.msg("Non ti ricordi di nessuno come %s" % target)
        else:
            if not obj.access(self.obj, "enable_recog", default=True):
                # don't apply recog if object doesn't allow it (e.g. by being masked).
                caller.msg("è un viso tropp comune...")
                return
            if self.cmdstring == "dimentica":
                # remove existing recog
                if caller.recog.remove(obj):
                    caller.msg("Ti dimentichi di %s" % self.chi)
                else:
                    caller.msg("Non ti ricordi di %s" % self.chi)
            else:
                sdesc = obj.sdesc.get() if hasattr(obj, "sdesc") else obj.key
                try:
                    alias = self.come.rstrip(".?!")
                    alias = caller.recog.add(obj, alias)
                except RecogError as err:
                    caller.msg(err)
                    return
                caller.msg("Ti ricorderai di |w%s|n come |w%s|n." % (sdesc, alias))


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
