from evennia.utils import utils

COMBAT_DISTANCES = ['melee', 'reach', 'ranged']
WRESTLING_POSITIONS = ('STANDING', 'CLINCHED', 'TAKE DOWN', 'PINNED')

_ACTIONS_PER_TURN = utils.variable_from_module('world.rulebook', 'ACTIONS_PER_TURN')
_COMBAT_PROMPT = ("|M[|n HP: |g{tr.HP.actual}|n "
                  "|| PM: |y{tr.PM.actual}|n |M]|n")


class CombatHandler(object):
    """
    This implements the combat handler.
    """

    # standard Script hooks
    def __init__(self):
        """Called when script is first created"""
        # store all combatants
        self.characters = {}
        self.targets = {}

    def start_combat(self, f_ch, s_ch):

        location = f_ch.location
        assert location == s_ch.location

        f_k = f_ch.key
        s_k = s_ch.key

        self.characters[f_k] = f_ch
        self.characters[s_k] = s_ch

        self.targets[f_k] = s_k
        self.targets[s_k] = f_k

        f_ch.cmdset.add("commands.tg_combat_cmdset.TGBaseCombatCmdSet")
        f_ch.cmdset.add("commands.tg_combat_cmdset.TGCombatCmdSet")

        s_ch.cmdset.add("commands.tg_combat_cmdset.TGBaseCombatCmdSet")
        s_ch.cmdset.add("commands.tg_combat_cmdset.TGCombatCmdSet")

    def join_combat(self, character, attacked):

        c_k = character.key
        self.characters[c_k] = character
        self.targets[c_k] = attacked

        character.ndb.combat_handler = self

        # parte il timer per il primo giocatore
        character.at_combat_start(attacked)

        character.cmdset.add("commands.tg_combat_cmdset.CombatBaseCmdSet")
        character.cmdset.add("commands.tg_combat_cmdset.CombatCmdSet")

    def cleanup_character(self, character):
        c_k = character.key
        del self.characters[c_k]
        del self.targets[c_k]
        for k, v in self.targets.items():
            if v == c_k:
                del self.targets[k]

        character.at_combat_end()
        del character.ndb.combat_handler

        character.cmdset.remove("commands.combat.CombatCmdSet")
        character.cmdset.remove("commands.combat.CombatBaseCmdSet")

