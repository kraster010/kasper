"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""
from evennia.utils import lazy_property

from typeclasses.defaults.default_objects import Object
from utils.tg_handlers import TGDescriptionHandler


class TGObject(Object):

    @lazy_property
    def __description_handler(self):
        return TGDescriptionHandler(self)

    @property
    def desc(self):
        return self.__description_handler.get()

    @desc.setter
    def desc(self, description):
        self.__description_handler.add(description)
