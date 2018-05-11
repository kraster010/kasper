# -*- coding: utf-8 -*-
import random

from django.conf import settings

from evennia import create_script, create_object
from evennia.utils import lazy_property, logger
from resources.terreni_desc import get_room_data
from typeclasses.defaults.default_scripts import Script
from utils.tg_handlers import TGHandlerDict
from world.mapengine.map_utils import load_map_from_file, get_new_coordinates


class TGMapEngineFactory(object):
    _instance = None

    def __init__(self):
        if not TGMapEngineFactory._instance:
            if not TGMapEngine.objects.filter(db_key="map_engine").exists():
                print "creo il map engine."
                TGMapEngineFactory._instance = create_script(TGMapEngine, key="map_engine", persistent=True, obj=None)
            else:
                print "carico il map engine."
                TGMapEngineFactory._instance = TGMapEngine.objects.get(db_key="map_engine")

    def get(self):
        # type: () -> TGMapEngine
        return self._instance


class TGMapEngineRoomHandler(TGHandlerDict):
    def __init__(self, obj):
        super(TGMapEngineRoomHandler, self).__init__(obj, "_active_rooms")

    def remove(self, key):
        if self.contains(key):
            del self.obj.db._active_rooms[key]
            self._cache()
            return True

        return False


class TGMapEngine(Script):
    dynamic_exit_type = "typeclasses.exits.TGDynamicExit"
    dynamic_room_type = "typeclasses.rooms.TGDynamicRoom"
    static_room_type = "typeclasses.rooms.TGStaticRoom"

    default_exits = [("nord", "n"),
                     ("est", "e"),
                     ("sud", "s"),
                     ("ovest", "o")]

    # -------------------- CREAZIONE --------- #

    def at_script_creation(self):
        self.desc = "Gestore di tutta la mappa e movimenti in wild"
        self._init()

    def _init(self):
        self.db._active_rooms = {}
        self.db._inactive_rooms = []
        self.db._garage_exits = []
        self._soft_init()

    def _soft_init(self):
        w, h, map = load_map_from_file()
        self.ndb.static_map = dict(rows=h, cols=w, raw=map)

        for coordinates, room in self._rooms.items():
            if not room:
                self._rooms.remove(coordinates)
                logger.log_info("Rimuovo la stanza [ {} -> {} ] dal map handler.".format(coordinates, room))
            if room.is_deletable():
                self.delete_room(coordinates=coordinates)
                logger.log_info("Rimuovo la stanza [ {} -> {} ] dal map handler.".format(coordinates, room))
                continue
            if not room.is_static:
                self.apply_static_definition(room, coordinates=coordinates)
            room.map_handler = self

    # --------------- GETTER & SETTER ----------- #

    @lazy_property
    def _rooms(self):
        # type: () -> TGMapEngineRoomHandler
        return TGMapEngineRoomHandler(self)

    def get_room(self, coordinates, default=None):
        TGMapEngine.objects.all()[:1].get()
        return self._rooms.get(coordinates, default=default)

    def get_terrain_id(self, coordinates):
        x, y = coordinates
        y = self.map_cols - y - 1
        return self._map_raw[x * self.map_cols + y]

    @property
    def map_rows(self):
        return self.ndb.static_map.get("rows", 0)

    @property
    def map_cols(self):
        return self.ndb.static_map.get("cols", 0)

    @property
    def _map_raw(self):
        return self.ndb.static_map.get("raw", bytearray())

    def is_valid_coordinates(self, coordinates):
        x, y = coordinates
        y = self.map_cols - y - 1
        return 0 <= x < self.map_rows and 0 <= y < self.map_cols

    # ------------------ HOOKS ------------------ #

    def at_start(self, **kwargs):
        """
        Called whenever the script is started, which for persistent
        scripts is at least once every server start. It will also be
        called when starting again after a pause (such as after a
        server reload)

        Args:
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        self._soft_init()

    def at_server_reload(self):
        """
        This hook is called whenever the server is shutting down for
        restart/reboot. If you want to, for example, save
        non-persistent properties across a restart, this is the place
        to do it.
        """
        self._map_save()

    # ------------- UTILITIES ------------- #

    def move_obj(self, obj_to_move, new_coordinates, quiet=False, report_to=None, to_none=False, move_hooks=True,
                 **kwargs):
        """
        Move an object inside the map grid. Its the same as obj_to_move.location = room_at_coordinates(new_coordinates)
        """
        if not obj_to_move:
            return False

        if not report_to:
            report_to = obj_to_move

        if not new_coordinates:
            if to_none:
                # immediately move to None. There can be no hooks called since
                # there is no destination to call them with.
                obj_to_move.location = None
                return True
            report_to.msg("La destinazione non esiste.")
            return False

        if not self.is_valid_coordinates(new_coordinates):
            return False

        # new coordinates potrebbe fare riferimento solo a TGStaticRoom o TGDynamicRoom
        room = self.get_room(new_coordinates)

        # ------------ la room esiste già, si mergiano ----------------- #

        if room:
            if room == obj_to_move.location:
                report_to.msg("Non puoi andare dove sei già!")
                return False

            # Before the move, call eventual pre-commands.
            if move_hooks:
                try:
                    if not obj_to_move.at_before_move(room):
                        return False
                except Exception as err:
                    print "at_before_move(): %s" % err
                    return False

            # salvo old_room
            old_room = obj_to_move.location

            # Call hook on source location
            if move_hooks and old_room:
                try:
                    old_room.at_object_leave(obj_to_move, room)
                except Exception as err:
                    print "at_object_leave(): %s" % err
                    return False

            if not quiet:
                # tell the old room we are leaving
                try:
                    obj_to_move.announce_move_from(room, **kwargs)
                except Exception as err:
                    print "at_announce_move(): %s" % err
                    return False

            # Perform move
            try:
                obj_to_move.location = room
                obj_to_move.coordinates = new_coordinates
                # quando mi sposto in una stanza room statica -> mergio, allora salvo
                if room.is_static:
                    obj_to_move.db.last_valid_coordinates = new_coordinates
                    obj_to_move.db.last_valid_area = room.tags.get(category="area")

            except Exception as err:
                print "location change: %s" % err
                return False

            if not quiet:
                # Tell the new room we are there.
                try:
                    obj_to_move.announce_move_to(old_room, **kwargs)
                except Exception as err:
                    print "announce_move_to(): %s" % err
                    return False

            if move_hooks:
                # Perform eventual extra commands on the receiving location
                # (the object has already arrived at this point)
                try:
                    room.at_object_receive(obj_to_move, old_room)
                except Exception as err:
                    print "at_object_receive(): %s" % err
                    return False

            # Execute eventual extra commands on this object after moving it
            # (usually calling 'look')
            if move_hooks:
                try:
                    obj_to_move.at_after_move(old_room)
                except Exception as err:
                    print "at_after_move(): %s" % err
                    return False

            # mergio le stanze quindi deleto la vecchia se necessaraio
            if old_room and old_room.is_deletable():
                self.delete_room(room=old_room)

            return True

        # -------------------- fine --------------------------- #
        # ----------- La stanza non esiste già ---------------- #

        if move_hooks:
            try:
                if not obj_to_move.at_before_move(None, coordinates=new_coordinates):
                    return False
            except Exception as err:
                print "at_before_move(): %s" % err
                return False

        # salvo old_room
        old_room = obj_to_move.location

        # old_room comunque vada non si  dovrà provare a cancellare da qui in poi.
        # o riutilizzo  old room, o significa che è una stanza che non serve cancellare per is_deletable()

        # ---------- decido se riusare old room o creare una nuova room ------- #

        reused = False
        if not old_room:
            # vengo da None, e aggiorno anche
            room = self._create_dynamic_room(coordinates=new_coordinates, report_to=report_to)
        elif not old_room.is_deletable(exclude=obj_to_move):
            # la creo e non cancello old_room
            room = self._create_dynamic_room(coordinates=new_coordinates, report_to=report_to)
        else:
            reused = True
            # se la coordinata di old room è dentro _active_rooms (ricordati che è pur sempre una dynamic room e non
            # una statica) la devo cancellare e aggiornarla
            self._rooms.remove(old_room.coordinates)
            room = old_room
            self._rooms.add(new_coordinates, room)
            # non serve ricreare le uscite perchè dovrebbero già essere le uscite standard
            # assert [x[0] for x in self.default_exit] == [x.key for x in room.exits]
            # quindi aggiustiamo solo i lock
            for c_exit in room.exits:
                if self.is_valid_coordinates(get_new_coordinates(new_coordinates, c_exit.key)):
                    c_exit.locks.add("traverse:true();view:true()")
                else:
                    c_exit.locks.add("traverse:false();view:false()")

        # da qui in avanti new_coordinates (e quindi room) fa riferimento sicuramente (x costruzione) a ad una stanza dinamica
        self.apply_static_definition(room, new_coordinates)

        # Call hook on source location
        if move_hooks and not reused and old_room:
            # quindi se ho riutilizzato old room non ci entro
            try:
                old_room.at_object_leave(obj_to_move, room)
            except Exception as err:
                print "at_object_leave(): %s" % err
                return False

        if not quiet and not reused:
            # tell the old room we are leaving
            try:
                obj_to_move.announce_move_from(room, **kwargs)
            except Exception as err:
                print "at_announce_move(): %s" % err
                return False

        # Perform move
        try:
            obj_to_move.location = room
            obj_to_move.coordinates = new_coordinates
        except Exception as err:
            print "location change: %s" % err
            return False

        if not quiet:
            # Tell the new room we are there.
            # a questo punto obj_to_move.location è già nella nuova location
            # old room può anche essere vuota
            try:
                obj_to_move.announce_move_to(old_room, **kwargs)
            except Exception as err:
                print "announce_move_to(): %s" % err
                return False

        if move_hooks:
            # Perform eventual extra commands on the receiving location
            # (the object has already arrived at this point)
            try:
                room.at_object_receive(obj_to_move, old_room)
            except Exception as err:
                print "at_object_receive(): %s" % err
                return False

        # Execute eventual extra commands on this object after moving it
        # (usually calling 'look')
        if move_hooks:
            try:
                obj_to_move.at_after_move(old_room)
            except Exception as err:
                print "at_after_move(): %s" % err
                return False

        return True

    @staticmethod
    def _create_room_factory(typeclass, key, report_to=None):
        c_obj = create_object(typeclass=typeclass, key=key, nohome=True, report_to=report_to)
        c_obj.tags.add(settings.WILD_AREA_NAME, category="Area")
        return c_obj

    @staticmethod
    def _create_exit_factory(typeclass, key, aliases, location, destination, report_to=None):
        return create_object(typeclass=typeclass,
                             key=key,
                             aliases=aliases,
                             location=location,
                             destination=destination,
                             report_to=report_to)

    def create_static_room(self, coordinates, area=None, key=None, report_to=None):
        # sta meglio messo qui invece che nei  parametri il  default
        if not key:
            key = "wild_{}_{}".format(coordinates[0], coordinates[1])

        if not area:
            area = self.location.tags.get(category="area")

        if self.get_room(coordinates):
            print "c'è già una stanza in quelle coordinate"
            return False

        # ad una static room non serve applicare room_data quindi la creo, e la torno
        room = TGMapEngine._create_room_factory(typeclass=self.static_room_type, key=key, report_to=report_to)
        room.tags.add(area, category="Area")
        self._rooms.add(coordinates, room)
        return room

    def _create_dynamic_room(self, coordinates, report_to=None):
        try:
            active_room = self.db._inactive_rooms.pop()
        except IndexError:
            # questo è il l'unico punto in cui creo un oggetto di tipo stanza.
            active_room = TGMapEngine._create_room_factory(self.dynamic_room_type,
                                                           key="wild_{}_{}".format(coordinates[0], coordinates[1]),
                                                           report_to=report_to)
            for key, alias in self.default_exits:
                aliases = [alias]
                try:
                    c_exit = self.db._garage_exits.pop()
                    c_exit.location = active_room
                    c_exit.destination = active_room
                    c_exit.key = key
                    c_exit.aliases = aliases
                except IndexError:
                    c_exit = TGMapEngine._create_exit_factory(self.dynamic_exit_type, key, aliases, active_room,
                                                              active_room,
                                                              report_to=report_to)

                    if self.is_valid_coordinates(get_new_coordinates(coordinates, c_exit.key)):
                        c_exit.locks.add("traverse:true();view:true()")
                    else:
                        c_exit.locks.add("traverse:false();view:false()")

        self._rooms.add(coordinates, active_room)
        active_room.map_handler = self

        return active_room

    def _dispose_dynamic_room(self, room, report_to=None):
        missing = {k: v for k, v in self.default_exits}
        for d_exit in room.exits:
            # devo solo togliere la location
            # importante perche per essere una exit devi avere almeno destination settatata
            # quindi la mettiamo solo da parte
            d_e_key = d_exit.key
            if d_e_key not in self.default_exits:
                d_exit.location = None
                self.db._garage_exits.append(d_exit)
            else:
                del missing[d_e_key]

        for key, alias in missing.items():
            aliases = [alias]
            try:
                c_exit = self.db._garage_exits.pop()
                c_exit.location = room
                c_exit.destination = room
                c_exit.key = key
                c_exit.aliases = aliases
            except IndexError:
                TGMapEngine._create_exit_factory(self.dynamic_room_type, key, aliases, room, room,
                                                 report_to=report_to)

        self.db._inactive_rooms.append(room)

    # constraints:
    # do per scontato che la room @ coordinates sia is_deletable()=True
    def delete_room(self, coordinates=None, room=None, report_to=None):
        if room:
            coordinates = room.coordinates

        if not coordinates:
            return False

        if self._rooms.remove(coordinates):
            self._dispose_dynamic_room(room, report_to=report_to)
            return True
        else:
            # allora non è tra gli active_rooms
            # non sono autorizzato a cancellare
            return False

    def apply_static_definition(self, room, coordinates):
        id_terreno = self.get_terrain_id(coordinates=coordinates)
        rd = get_room_data(id_terreno=id_terreno)
        titolo = rd.titolo
        descrizione = random.choice(rd.descrizioni)

        room.desc = descrizione
        room.name = titolo
        room.coordinates = coordinates

    def _reset_map(self):
        # cancello tutte le uscite dinamiche della mappa
        temp = list(self.db._garage_exits)
        for c_exit in temp:
            if c_exit:
                c_exit.delete()
        del self.db._garage_exits

        # cancello tutte le inactive_rooms
        temp = list(self.db._inactive_rooms)
        for room in temp:
            if room:
                room.delete()
        del self.db._inactive_rooms

        # cancello tutte le active_room
        temp = list(self.db._active_rooms)
        for room in temp:
            if room:
                room.delete()
        del self.db._active_rooms

        self._init()

    def _map_save(self):
        """
        Placeholder per salvataggio mappa, può essere la funzione asincrona
        """
        return True
