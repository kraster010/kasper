# coding=utf-8
"""
Races module.

This module contains data and functions relating to Races and Focuses. Its
public module functions are to be used primarily during the character
creation process.

Classes:

    `Race`: base class for all races
    `Human`: human race class
    `Elf`: elf race class
    `Dwarf`: dwarf race class
    `Focus`: class representing a character's focus; a set of bonuses

Module Functions:

    - `load_race(str)`:

        loads an instance of the named Race class

    - `apply_race(char, race, focus)`:

        have a character "become" a member of the specified race with
        the specified focus
"""


class RaceException(Exception):
    """Base exception class for races module."""

    def __init__(self, msg):
        self.msg = msg


ALL_RACES = ('Umani', 'Elfi')


def load_race(race):
    """Returns an instance of the named race class.

    Args:
        race (str): case-insensitive name of race to load

    Returns:
        (Race): instance of the appropriate subclass of `Race`
    """
    race = race.capitalize()
    if race in ALL_RACES:
        return globals()[race]()
    else:
        raise RaceException("Invalid race specified.")


def apply_race(char, race):
    """Causes a Character to "become" the named race.

    Args:
        char (Character): the character object becoming a member of race
        race (str, Race): the name of the race to apply, or the
        focus (str, Focus): the name of the focus the player has selected
    """
    # if objects are passed in, reload Race and Focus objects
    # by name to ensure we have un-modified versions of them
    if isinstance(race, Race):
        race = race.name

    race = load_race(race)

    # set race and related attributes on the character
    race.apply_to(char)


class Race(object):
    """Base class for race attributes"""

    def __init__(self):
        self.name = ""
        self.maschile = {}
        self.femminile = {}
        self.slots = {
            'impugnatura1': None,
            'impugnatura2': None,
            'armatura': None,
        }
        self.limbs = (
            ('r_arm', ('impugnatura1',)),
            ('l_arm', ('impugnatura2',)),
            ('corpo', ('armatura',)),
        )

        # base traits data
        self.traits = {
            # primary
            'STR': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Forza'},
            'COS': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Costituzione'},
            'DEX': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Destrezza'},
            'INT': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Intelligenza'},
            'CHA': {'type': 'static', 'base': 1, 'mod': 0, 'name': 'Carisma'},

            # secondary
            'PF': {'type': 'gauge', 'base': 0, 'mod': 0, 'name': 'Punti Ferita'},
            'PM': {'type': 'gauge', 'base': 0, 'mod': 0, 'name': 'Punti Movimento'},

            # saves
            'FORT': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Tempra'},
            'REFL': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Riflessi'},
            'WILL': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Volontà'},

            # combat
            'TCP': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Tiro Per Colpire'},
            'CA': {'type': 'static', 'base': 0, 'mod': 0, 'name': 'Classe Armatura'},

            # misc
            'ENC': {'type': 'counter', 'base': 0, 'mod': 0, 'min': 0, 'name': 'Ingombro'},
        }

    def apply_to(self, obj):
        obj.db.slots = self.slots
        obj.db.limbs = self.limbs
        obj.db.race = self.name
        temp = self.race_oa(gender=obj.db.gender)
        obj.db.race_name = temp
        obj.sdesc.add("un %s" % temp.capitalize())
        obj.traits.clear()
        for key, kwargs in self.traits.iteritems():
            obj.traits.add(key, **kwargs)

    def race_oa(self, gender="m", s_or_p="s"):
        return self.femminile[s_or_p] if gender == "f" else self.maschile[s_or_p]


class Umani(Race):
    """Class representing human attributes."""

    def __init__(self):
        super(Umani, self).__init__()
        self.name = "umani"
        self.maschile = dict(s="uomo", p="uomini")
        self.femminile = dict(s="donna", p="donne")
        self.altezza = dict(m=170, f=170)
        # set starting trait values
        self.traits['STR']['base'] = 50
        self.traits['COS']['base'] = 50
        self.traits['DEX']['base'] = 50
        self.traits['INT']['base'] = 50
        self.traits['PM']['base'] = 7

class Elfi(Race):
    """Class representing elf attributes."""

    def __init__(self):
        super(Elfi, self).__init__()
        self.name = "elfi"
        self.maschile = dict(s="elfo", p="elfi")
        self.femminile = dict(s="elfa", p="elfe")
        self.altezza = dict(m=170, f=170)
        # set starting trait values
        self.traits['STR']['base'] = 40
        self.traits['COS']['base'] = 50
        self.traits['DEX']['base'] = 60
        self.traits['INT']['base'] = 50
        self.traits['PM']['base'] = 7
