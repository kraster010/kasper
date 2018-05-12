from commands.command import Command
from evennia import CmdSet


class CmdLook(Command):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Observes your location or objects in your vicinity.
    """
    key = "guarda"
    aliases = ["g", "l", "ls"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def parse(self):
        self.args = self.args.strip()

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("Chi vuoi guardare?")
                return
        else:
            args = self.args
            target = caller.search(args, quiet=True)
            if not target:
                caller.msg("Chi vuoi guardare?")
                return
            target = target[0]

        self.caller.msg(caller.at_look(target))


class TGCharacterCmdSet(CmdSet):
    """
    Mix-in for adding rp-commands to default cmdset.
    """

    def at_cmdset_creation(self):
        self.add(CmdLook())
