# coding=utf-8
"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia.utils import logger

from typeclasses.defaults.default_characters import Character


class TGCharacter(Character):

    def at_object_creation(self):
        self.coordinates = None

    @property
    def coordinates(self):
        return self.ndb.coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        self.ndb.coordinates = coordinates

    def at_before_move(self, destination, coordinates=None, **kwargs):
        """
        Called just before starting to move this object to
        destination.

        Args:
            destination (Object): The object we are moving to, which can be non for the wild map
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            shouldmove (bool): If we should move or not.

        Notes:
            If this method returns False/None, the move is cancelled
            before it is even started.

        """

        if not destination:
            if not coordinates:
                return False

        # return has_perm(self, destination, "can_move")
        return True

    def at_pre_puppet(self, account, session=None, **kwargs):
        """
        Return the character from storage in None location in `at_post_unpuppet`.
        Args:
            account (Account): This is the connecting account.
            session (Session): Session controlling the connection.
        """
        from world.mapengine.map_engine import TGMapEngineFactory
        from django.conf import settings

        map_handler = TGMapEngineFactory().get()
        # mi asicuro di essere in una location valida
        logger.log_info(
            "at_pre_puppet():\nself.location:{}\nself.db.last_valid_area:{}\nself.db.last_valid_coordinates:{}".format(
                self.location, self.db.last_valid_area, self.db.last_valid_coordinates))

        # Ogni volta che mi loggo self.location sarà None, altrimenti può succedere che puppetto qualcuno, e allora
        # in base a dove parto devo stare attento

        if self.location is None:

            if self.db.last_valid_area == settings.WILD_AREA_NAME or map_handler._rooms.contains(
                    self.db.last_valid_coordinates):

                # mi sposto in last_valid_coordinates o in home se fallisco, altrimenti esplodo
                if not map_handler.move_obj(self, self.db.last_valid_coordinates, quiet=True, move_hooks=False):
                    if not self.home:
                        raise RuntimeError
                    self.location = self.home

            else:
                # se invece l'ultima zona non è la wild uso prelogout_location
                # giusto per ricordarmi la last_valid_area è già coerente non devo aggiornarla
                self.location = self.db.prelogout_location if self.db.prelogout_location else self.home

            self.location.at_object_receive(self, source_location=None)

        if self.location:
            # aggiorno tutto sapendo che self.location è pronta

            if self.location.coordinates:
                self.db.last_valid_coordinates = self.location.coordinates

            self.db.last_valid_area = self.location.tags.get(category="area")
            self.db.prelogout_location = self.location  # save location again to be sure.
        else:
            account.msg("|r%s non ha una stanza settata e nemmeno una home.|n" % self, session=session)

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
                from django.conf import settings
                def message(obj, from_obj):
                    obj.msg("%s ha lasciato il gioco." % self.get_display_name(obj), from_obj=from_obj)

                self.location.for_contents(message, exclude=[self], from_obj=self)
                if self.location.coordinates:
                    self.db.last_valid_coordinates = self.location.coordinates

                self.db.prelogout_location = self.location
                self.db.last_valid_area = self.location.tags.get(category="area")

                logger.log_info(
                    "at_post_unpuppet():"
                    "\nlast_valid_coordinates{}\nself.last_valid_area:{}\nself.db.prelogout_location:{}".format(
                        self.db.last_valid_coordinates, self.db.last_valid_area, self.db.prelogout_location))

                self.location = None
