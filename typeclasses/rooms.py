# coding=utf-8
"""
Room

Rooms are simple containers that has no location of their own.

"""
from evennia.utils import lazy_property, inherits_from

from typeclasses.defaults.default_rooms import Room
from utils.tg_handlers import TGDescriptionHandler


class TGStaticRoom(Room):

    def at_object_creation(self):
        self.desc = "Una stanza vuota."
        self.coordinates = None

    @property
    def coordinates(self):
        return self.db.coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        self.db.coordinates = coordinates

    @property
    def desc(self):
        return self.__description_handler.get()

    @desc.setter
    def desc(self, description):
        self.__description_handler.add(description)

    def is_deletable(self, exclude=None):
        return False

    @lazy_property
    def __description_handler(self):
        return TGDescriptionHandler(self)


class TGDynamicRoom(Room):

    def at_object_creation(self):
        self.desc = "Una stanza vuota."
        self.coordinates = None

    @property
    def coordinates(self):
        return self.ndb.coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        self.ndb.coordinates = coordinates

    @property
    def desc(self):
        return self.ndb.desc

    @desc.setter
    def desc(self, description):
        self.ndb.desc = description

    @property
    def is_static(self):
        return False

    # il costraint per non essere deletabile è contenere almeno un oggetto diverso da un uscita dinamica
    def is_deletable(self, exclude=None):
        for cont in self.contents_get(exclude=exclude):
            if not inherits_from(cont, "typeclasses.exits.TGDynamicExit"):
                return False
        return True
