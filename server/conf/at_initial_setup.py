# coding=utf-8
"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""
from django.conf import settings
from evennia import search_object, ObjectDB
from evennia.utils import create, logger

from typeclasses.exits import TGStaticExit, TGDynamicExit
from typeclasses.rooms import TGStaticRoom
from world.mapengine.map_engine import TGMapEngineFactory


def set_playable_character(character, account):
    account.db.FIRST_LOGIN = True
    account.db._playable_characters.append(character)
    account.db._last_puppet = character


def create_test_character(pg_name, home):
    logger.log_info("Creating test charachter {} with home {} ...".format(pg_name, home))

    new_account = create.create_account(pg_name, email="test%s@test.com" % pg_name, password="1234",
                                        typeclass=settings.BASE_ACCOUNT_TYPECLASS,
                                        permissions=settings.PERMISSION_ACCOUNT_DEFAULT)

    new_character = create.create_object(settings.BASE_CHARACTER_TYPECLASS, key=new_account.key, home=home)

    set_playable_character(new_character, new_account)

    # allow only the character itself and the account to puppet this character (and Developers).
    new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Developer) or pperm(Developer)" %
                            (new_character.id, new_account.id))

    # If no description is set, set a default description
    new_character.db.desc = "This is %s." % pg_name

    logger.log_info("Finished test character %s creation." % pg_name)

    return new_character


def costruisci_interno_grotta(grotta_lunare):
    logger.log_info("costruisci_interno_grotta(): inizio creazione interno grotta tutorial ...")

    grotta_lunare_area = grotta_lunare.tags.get(category="area")

    dentro1 = create.create_object(TGStaticRoom, key="Dentro una grotta", nohome=True)
    dentro1.tags.add(grotta_lunare_area, category="area")
    dentro1.desc = "Le pareti rocciose trasudano acqua, ci deve essere dell'acqua più in fondo."
    dentro1.name = "Dentro una grotta"

    dentro2 = create.create_object(TGStaticRoom, key="Una grande voragine", nohome=True)
    dentro2.tags.add(grotta_lunare_area, category="area")
    dentro2.desc = "Impensabile trovare una voragine di tali dimensioni."
    dentro2.name = "Dentro una grotta"

    # collgeo grotta-dentro1
    create.create_object(typeclass=TGStaticExit,
                         key="sud",
                         aliases=["s"],
                         location=grotta_lunare,
                         destination=dentro1,
                         report_to=None)

    create.create_object(typeclass=TGStaticExit,
                         key="nord",
                         aliases=["n"],
                         location=dentro1,
                         destination=grotta_lunare,
                         report_to=None)

    # collgeo dentro1-dentro2
    create.create_object(typeclass=TGStaticExit,
                         key="sud",
                         aliases=["s"],
                         location=dentro1,
                         destination=dentro2,
                         report_to=None)

    create.create_object(typeclass=TGStaticExit,
                         key="nord",
                         aliases=["n"],
                         location=dentro2,
                         destination=dentro1,
                         report_to=None)

    add_starting_exit(grotta_lunare)

    logger.log_info("costruisci_interno_grotta(): fine creazione grotta tutorial ...")


def add_starting_exit(grotta_lunare):
    # ci aggiungo le uscite ovest nord est a grotta_lunare
    create.create_object(typeclass=TGDynamicExit,
                         key="est",
                         aliases=["e"],
                         location=grotta_lunare,
                         destination=grotta_lunare,
                         report_to=None)

    create.create_object(typeclass=TGDynamicExit,
                         key="nord",
                         aliases=["n"],
                         location=grotta_lunare,
                         destination=grotta_lunare,
                         report_to=None)

    create.create_object(typeclass=TGDynamicExit,
                         key="ovest",
                         aliases=["o"],
                         location=grotta_lunare,
                         destination=grotta_lunare,
                         report_to=None)


def at_initial_setup():
    # prendo Limbo e la trasformo (è una stanza di tipo TGStaticRoom se non cambiano le configurazioni di default nuove)
    try:
        grotta_lunare = search_object("#2")[0]
    except ObjectDB.DoesNotExist:
        raise ObjectDB.DoesNotExist("Limbo non esiste")

    grotta_lunare.name = "Grotta Lunare"
    grotta_lunare.desc = "Un luogo quasi buio se non fosse per lievi raggi di luce che arrivano da più lontano."
    grotta_lunare.coordinates = (5, 5)
    map_handler = TGMapEngineFactory().get()
    grotta_lunare.map_handler = map_handler
    grotta_lunare.tags.add("tutorial", category="area")
    costruisci_interno_grotta(grotta_lunare)
    # aggiungo  la grotta_lunare_nella lista delle rooms essendo diciamo un "portale
    logger.log_info("adding {} to map_handler._rooms ...".format(grotta_lunare))
    map_handler._rooms.add(grotta_lunare.coordinates, grotta_lunare)
    grotta_lunare_area = grotta_lunare.tags.get(category="area")

    try:
        god_character = search_object("#1")[0]
    except ObjectDB.DoesNotExist:
        raise ObjectDB.DoesNotExist("God character non esiste")

    god_character.location = None
    # create the true admin
    god_character.desc = "Questo è ET."
    god_character.db.prelogout_location = grotta_lunare
    god_character.db.last_valid_area = grotta_lunare_area
    god_character.db.last_valid_coordinates = grotta_lunare.coordinates

    # creo due account di test con relativo pg
    t1_pg = create_test_character("hugo", grotta_lunare)
    t1_pg.desc = "Un vecchio lupo di mare con qualche dente in meno."
    t1_pg.db.prelogout_location = grotta_lunare
    t1_pg.db.last_valid_area = grotta_lunare_area
    t1_pg.db.last_valid_coordinates = grotta_lunare.coordinates

    t2_pg = create_test_character("sugo", grotta_lunare)
    t2_pg.desc = "Un uomo sfoggia un grembiule bianco smanicato."
    t2_pg.db.prelogout_location = grotta_lunare
    t2_pg.db.last_valid_area = grotta_lunare_area
    t2_pg.db.last_valid_coordinates = grotta_lunare.coordinates
