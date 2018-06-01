# coding=utf-8
from commands.command import Command
from evennia import CmdSet
from evennia.utils import inherits_from
from typeclasses.combat_handler import CombatHandler
from world.rpsystem import parse_sdescs_and_recogs


class CmdInitiateAttack(Command):
    """
    initiate combat against an enemy
    Usage:
      attack <target>
    Begins or joins turn-based combat against the given enemy.
    """
    key = 'attack'
    aliases = ['att']
    locks = 'cmd:not in_combat()'
    help_category = 'combat'

    def parse(self):
        self.args = self.args.strip()

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: attack <target>")
            return

        target = parse_sdescs_and_recogs(caller, caller.location.contents_get(exclude=caller), self.args,
                                         search_mode=True)

        if not target:
            caller.msg("Non sai dove trovare {}".format(self.args))
            return

        # for combat against yourself
        if target.id == caller.id:
            caller.msg("Ti colpisci in testa.")
            return

        if not inherits_from(target, 'typeclasses.characters.Character'):
            caller.msg("Non puoi attaccare {target}.".format(target=target.get_display_name(caller)))
            return

        if target.ndb.no_attack:
            caller.msg("Non puoi attaccare {target} ora.".format(target=target.get_display_name(caller)))
            return

        if caller.location.tags.get('no_attack', None, category='flags'):
            caller.msg("Non puoi attaccare qui.")
            return

        # set up combat
        if target.ndb.combat_handler:
            # target is already in combat - join it
            target.ndb.combat_handler.join_combat(caller, target)
        else:
            # create a new combat handler
            ch = CombatHandler()
            ch.start_combat(caller, target)

            # aggiungo i cmdset al pg
            caller.ndb.combat_handler = ch
            target.ndb.combat_handler = ch

            # questo fa partire i timer su entrambi i pg
            caller.at_combat_start(target)
            target.at_combat_start(caller)

        for char in ch.characters.values():
            char.execute_cmd("look")

        caller.msg("attacchi {target}!".format(target=target.get_display_name(caller)))
        target.msg("{actor} ti attacca!".format(actor=caller.get_display_name(target)))
        for anything in caller.location.contents_get(exclude=(caller, target,)):
            anything.msg("{actor} attacca {target}!".format(actor=caller.get_display_name(anything),
                                                            target=target.get_display_name(anything)))


class TGCombatCmdSet(CmdSet):
    """
    Mix-in for adding rp-commands to default cmdset.
    """

    def at_cmdset_creation(self):
        self.add(CmdInitiateAttack())
