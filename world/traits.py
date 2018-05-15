class PrimaryTraits(object):

    def __init__(self):
        # base traits data
        self.traits = {
            # primary
            'STR': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Strength'},
            'PER': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Perception'},
            'INT': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Intelligence'},
            'DEX': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Dexterity'},
            'CHA': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Charisma'},
            'VIT': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Vitality'},
            # magic
            'MAG': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Magic'},
            'BM': {'type': 'gauge', 'base': 0, 'mod': 0, 'min': 0, 'max': 10, 'name': 'Black Mana'},
            'WM': {'type': 'gauge', 'base': 0, 'mod': 0, 'min': 0, 'max': 10, 'name': 'White Mana'},
            # secondary
            'HP': {'type': 'gauge', 'base': 0, 'mod': 0, 'name': 'Health'},
            'SP': {'type': 'gauge', 'base': 0, 'mod': 0, 'name': 'Stamina'},
            # saves
            'FORT': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Fortitude Save'},
            'REFL': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Reflex Save'},
            'WILL': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Will Save'},
            # combat
            'ATKM': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Melee Attack'},
            'ATKR': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Ranged Attack'},
            'ATKU': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Unarmed Attack'},
            'DEF': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Defense'},
            'ACT': {'type': 'counter', 'base': 0, 'mod': 0, 'min': 0, 'name': 'Action Points'},
            'PP': {'type': 'counter', 'base': 0, 'mod': 0, 'min': 0, 'name': 'Power Points'},
            # misc
            'ENC': {'type': 'counter', 'base': 0, 'mod': 0, 'min': 0, 'name': 'Carry Weight'},
            'MV': {'type': 'gauge', 'base': 6, 'mod': 0, 'min': 0, 'name': 'Movement Points'},
            'LV': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Level'},
            'XP': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Experience',
                   'extra': {'level_boundaries': (500, 2000, 4500, 'unlimited')}},
        }
