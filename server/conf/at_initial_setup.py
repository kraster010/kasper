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
from evennia import search_object, ObjectDB, AccountDB
from evennia.server.initial_setup import get_god_account
from evennia.utils import create
from typeclasses.characters import TGCharacter
from typeclasses.exits import TGStaticExit, TGDynamicExit
from typeclasses.map_engine import TGMapEngineFactory
from typeclasses.rooms import TGStaticRoom
from django.conf import settings


def create_test_character(id, pg_name):
    test = create.create_account("test%i" % id, email="test%i@test.com" % id, password="%i" % id,
                                 typeclass=settings.BASE_ACCOUNT_TYPECLASS)

    test_pg = create.create_object(TGCharacter, key=pg_name)

    test.attributes.add("_first_login", True)
    test.attributes.add("_last_puppet", test_pg)

    try:
        test.db._playable_characters.append(test_pg)
    except AttributeError:
        test.db_playable_characters = [test_pg]

    return test_pg


def costruisci_interno_grotta(grotta_lunare):
    dentro1 = create.create_object(TGStaticRoom, key="GrottaLunare_1", nohome=True)
    dentro1.desc = "Le pareti rocciose trasudano acqua, ci deve essere dell'acqua più in fondo."
    dentro1.titolo = "Dentro una grotta"

    dentro2 = create.create_object(TGStaticRoom, key="GrottaLunareTrono", nohome=True)
    dentro2.desc = "Un trono avvolto da un groviglio di spade posa al centro della stanza su un piedistallo di " \
                   "pietra bianca squadrata."

    dentro2.titolo = "Dentro una grotta"

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


def at_initial_setup():

    # prendo Limbo e la trasformo (è una stanza di tipo TGStaticRoom se non cambiano le configurazioni di default nuove)
    try:
        grotta_lunare = search_object("#2")[0]
    except ObjectDB.DoesNotExist:
        raise ObjectDB.DoesNotExist("Limbo non esiste")

    grotta_lunare.key = "GrottaLunare"
    grotta_lunare.desc = "Un luogo quasi buio se non fosse per lievi raggi di luce che arrivano da più lontano."
    grotta_lunare.titolo = "Grotta Lunare"
    grotta_lunare.coordinates = (5, 5)

    costruisci_interno_grotta(grotta_lunare)

    # forzo la creazione del map_engine
    map_engine = TGMapEngineFactory().get()

    # ci aggiungo le uscite ovest nord est
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

    # aggiungo  la grotta_lunare_nella lista delle rooms essendo diciamo un "portale
    map_engine._rooms.add(grotta_lunare.coordinates, grotta_lunare)

    #
    # pre_fuori = create.create_object(TGStaticRoom, key="wilderness_key", nohome=True)
    #
    # wild_exit_n = create.create_object(typeclass=TGStaticExit,
    #                                    key="nord",
    #                                    aliases=["n"],
    #                                    location=grotta_lunare,
    #                                    destination=grotta_lunare,
    #                                    report_to=None)
    #
    # wild_exit_s = create.create_object(typeclass=TGStaticExit,
    #                                    key="sud",
    #                                    aliases=["s"],
    #                                    location=grotta_lunare,
    #                                    destination=grotta_lunare,
    #                                    report_to=None)

    try:
        god_character = search_object("#1")[0]
    except ObjectDB.DoesNotExist:
        raise ObjectDB.DoesNotExist("God character non esiste")

    god_character.location = grotta_lunare
    god_character.home = grotta_lunare

    # creo due account di test con relativo pg
    t1_pg = create_test_character(1, "hugo")
    t1_pg.attributes.add("prelogout_location", grotta_lunare)

    t2_pg = create_test_character(2, "sugo")
    t2_pg.attributes.add("prelogout_location", grotta_lunare)
