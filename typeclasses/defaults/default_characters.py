import time

from django.conf import settings

from typeclasses.defaults.default_objects import Object


class Character(Object):
    """
    This implements an Object puppeted by a Session - that is,
    a character avatar controlled by an account.

    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    def basetype_setup(self):
        """
        Setup character-specific security.

        You should normally not need to overload this, but if you do,
        make sure to reproduce at least the two last commands in this
        method (unless you want to fundamentally change how a
        Character object works).

        """
        super(Character, self).basetype_setup()
        self.locks.add(";".join(["get:false()",  # noone can pick up the character
                                 "call:false()"]))  # no commands can be called on character from outside
        # add the default cmdset
        self.cmdset.add_default(settings.CMDSET_CHARACTER, permanent=True)

    def at_after_move(self, source_location, **kwargs):
        """
        We make sure to look around after a move.

        """
        if self.location.access(self, "view"):
            self.msg(self.at_look(self.location))

    def at_pre_puppet(self, account, session=None, **kwargs):
        """
        Return the character from storage in None location in `at_post_unpuppet`.
        Args:
            account (Account): This is the connecting account.
            session (Session): Session controlling the connection.
        """
        if self.location is None:  # Make sure character's location is never None before being puppeted.
            # Return to last location (or home, which should always exist),
            self.location = self.db.prelogout_location if self.db.prelogout_location else self.home
            self.location.at_object_receive(self, None)  # and trigger the location's reception hook.
        if self.location:  # If the character is verified to be somewhere,
            self.db.prelogout_location = self.location  # save location again to be sure.
        else:
            account.msg("|r%s has no location and no home is set.|n" % self, session=session)  # Note to set home.

    def at_post_puppet(self, **kwargs):
        """
        Called just after puppeting has been completed and all
        Account<->Object links have been established.

        Args:
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        Note:
            You can use `self.account` and `self.sessions.get()` to get
            account and sessions at this point; the last entry in the
            list from `self.sessions.get()` is the latest Session
            puppeting this Object.

        """
        self.msg("\nYou become |c%s|n.\n" % self.name)
        self.msg(self.at_look(self.location))

        def message(obj, from_obj):
            obj.msg("%s has entered the game." % self.get_display_name(obj), from_obj=from_obj)

        self.location.for_contents(message, exclude=[self], from_obj=self)

    def at_post_unpuppet(self, account, session=None, **kwargs):
        """
        We stove away the character when the account goes ooc/logs off,
        otherwise the character object will remain in the room also
        after the account logged off ("headless", so to say).

        Args:
            account (Account): The account object that just disconnected
                from this object.
            session (Session): Session controlling the connection that
                just disconnected.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not self.sessions.count():
            # only remove this char from grid if no sessions control it anymore.
            if self.location:
                def message(obj, from_obj):
                    obj.msg("%s has left the game." % self.get_display_name(obj), from_obj=from_obj)

                self.location.for_contents(message, exclude=[self], from_obj=self)
                self.db.prelogout_location = self.location
                self.location = None

    @property
    def idle_time(self):
        """
        Returns the idle time of the least idle session in seconds. If
        no sessions are connected it returns nothing.
        """
        idle = [session.cmd_last_visible for session in self.sessions.all()]
        if idle:
            return time.time() - float(max(idle))
        return None

    @property
    def connection_time(self):
        """
        Returns the maximum connection time of all connected sessions
        in seconds. Returns nothing if there are no sessions.
        """
        conn = [session.conn_time for session in self.sessions.all()]
        if conn:
            return time.time() - float(min(conn))
        return None