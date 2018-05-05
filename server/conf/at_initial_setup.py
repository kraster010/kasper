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
from typeclasses.exits import TGStaticExit, TGDynamicExit
from typeclasses.map_engine import TGMapEngineFactory
from typeclasses.rooms import TGStaticRoom
from django.conf import settings


def set_playable_character(character, account):
    account.db.FIRST_LOGIN = True
    account.db._playable_characters.append(character)
    account.db._last_puppet = character


def create_second_admin(pg_name, home):
    new_account = create.create_account(key=pg_name, email="test%s@test.com" % pg_name, password="1234",
                                        typeclass=settings.BASE_ACCOUNT_TYPECLASS, is_superuser=True,
                                        permissions="Developer",
                                        locks="examine:perm(Developer);edit:false();delete:false();boot:false();msg:all()")

    new_character = create.create_object(typeclass=settings.BASE_CHARACTER_TYPECLASS, key=new_account.key, home=home,
                                         locks="examine:perm(Developer);edit:false();delete:false();boot:false();msg:all();puppet:false()")

    set_playable_character(new_character, new_account)

    new_character.db.desc = "This is %s." % pg_name

    return new_character


def create_test_character(pg_name, home):
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

    return new_character


def costruisci_interno_grotta(grotta_lunare):
    dentro1 = create.create_object(TGStaticRoom, key="Dentro una grotta", nohome=True)
    dentro1.desc = "Le pareti rocciose trasudano acqua, ci deve essere dell'acqua più in fondo."
    dentro1.titolo = "Dentro una grotta"

    dentro2 = create.create_object(TGStaticRoom, key="Una grande voragine", nohome=True)
    dentro2.desc = "Impensabile trovare una voragine di tali dimensioni."

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

    grotta_lunare.key = "Grotta Lunare"
    grotta_lunare.desc = "Un luogo quasi buio se non fosse per lievi raggi di luce che arrivano da più lontano."
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

    # create the true admin
    aldo = create_second_admin("aldo", grotta_lunare)

    aldo.desc = "This is ET."

    try:
        god_character = search_object("#1")[0]
    except ObjectDB.DoesNotExist:
        raise ObjectDB.DoesNotExist("God character non esiste")

    god_character.location = None

    # creo due account di test con relativo pg
    t1_pg = create_test_character("hugo", grotta_lunare)
    t1_pg.desc = "Un vecchio lupo di mare con qualche dente in meno."

    t2_pg = create_test_character("sugo", grotta_lunare)
    t2_pg.desc = "Un uomo sfoggia un grembiule bianco smanicato."
