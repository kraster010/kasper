# -*- coding: utf-8 -*-
"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from typeclasses.defaults.default_exits import Exit
from typeclasses.defaults.default_objects import Object
from world.mapengine.map_utils import get_new_coordinates


class TGStaticExit(Exit):
    """
    Una exit statica è una exit che va posizionata in una room statica
    e può portare ad una stanza statica.

    """
    pass


class TGDynamicExit(Exit):
    """
    Una exit dinamica collega una stanza del map handler con un'altra stanza del maphandler
    """

    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
         This hook is responsible for handling the actual traversal,
        normally by calling
        `traversing_object.move_to(target_location)`. It is normally
        only implemented by Exit objects. If it returns False (usually
        because `move_to` returned False), `at_after_traverse` below
        should not be called and instead `at_failed_traverse` should be
        called.

        Args:
           Args:
            traversing_object (Object): Object traversing us.
            target_location (Object): Where target is going.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        old_room = traversing_object.location
        old_coordinates = old_room.coordinates

        if old_room.map_handler.move_obj(traversing_object,
                                         new_coordinates=get_new_coordinates(old_coordinates, self.key),
                                         report_to=traversing_object):
            self.at_after_traverse(traversing_object, old_room)
        else:
            if self.db.err_traverse:
                # if exit has a better error message, let's use it.
                self.caller.msg(self.db.err_traverse)
            else:
                # No shorthand error message. Call hook.
                self.at_failed_traverse(traversing_object)

    def at_after_traverse(self, traversing_object, source_location, **kwargs):
        """
        Called just after an object successfully used this object to
        traverse to another object (i.e. this object is a type of
        Exit)

        Args:
            traversing_object (Object): The object traversing us.
            source_location (Object): Where `traversing_object` came from.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            The target location should normally be available as `self.destination`.
        """
        pass

    def at_failed_traverse(self, traversing_object, **kwargs):
        """
        Overloads the default hook to implement a simple default error message.

        Args:
            traversing_object (Object): The object that failed traversing us.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            Using the default exits, this hook will not be called if an
            Attribute `err_traverse` is defined - this will in that case be
            read for an error string instead.

        """
        traversing_object.msg("Non puoi andare qui.")

    @property
    def is_static(self):
        return False
