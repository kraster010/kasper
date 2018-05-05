from typeclasses.defaults.default_objects import Object


class Room(Object):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.


    This is the base room object. It's just like any Object except its
    location is always `None`.
    """

    def basetype_setup(self):
        """
        Simple room setup setting locks to make sure the room
        cannot be picked up.

        """

        super(Room, self).basetype_setup()
        self.locks.add(";".join(["get:false()",
                                 "puppet:false()"]))  # would be weird to puppet a room ...
        self.location = None

    @property
    def map_handler(self):
        return self.ndb.map_handler

    @map_handler.setter
    def map_handler(self, map_engine):
        self.ndb.map_handler = map_engine
