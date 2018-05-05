"""
Evennia settings file.

The available options are found in the default settings file found
here:

c:\users\colom\documents\projects\evennia\evennia\settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "kasper"

# Server ports. If enabled and marked as "visible", the port
# should be visible to the outside world on a production server.
# Note that there are many more options available beyond these.

# Telnet ports. Visible.
TELNET_ENABLED = False
TELNET_PORTS = [4000]
# (proxy, internal). Only proxy should be visible.
WEBSERVER_ENABLED = True
WEBSERVER_PORTS = [(4001, 4002)]
# Telnet+SSL ports, for supporting clients. Visible.
SSL_ENABLED = False
SSL_PORTS = [4003]
# SSH client ports. Requires crypto lib. Visible.
SSH_ENABLED = False
SSH_PORTS = [4004]
# Websocket-client port. Visible.
WEBSOCKET_CLIENT_ENABLED = True
WEBSOCKET_CLIENT_PORT = 4005
# Internal Server-Portal port. Not visible.
AMP_PORT = 4006

# terrain path relative to the script world.engine
MAP_FOLDER = os.path.join("world", "mapengine", "resources")
TERRAIN_MAP = "mappa_terreni.bin"
TEMPERATURE_MAP = "mappa_temperature.bin"

# Typeclass for account objects (linked to a character) (fallback)
BASE_ACCOUNT_TYPECLASS = "typeclasses.defaults.default_accounts.Account"
# Typeclass and base for all objects (fallback)
BASE_OBJECT_TYPECLASS = "typeclasses.objects.Object"
# Typeclass for character objects linked to an account (fallback)
BASE_CHARACTER_TYPECLASS = "typeclasses.characters.TGCharacter"
# Typeclass for rooms (fallback)
BASE_ROOM_TYPECLASS = "typeclasses.rooms.TGStaticRoom"
# Typeclass for Exit objects (fallback).
BASE_EXIT_TYPECLASS = "typeclasses.exits.TGStaticExit"
# Typeclass for Channel (fallback).
BASE_CHANNEL_TYPECLASS = "typeclasses.defaults.default_channels.Channel"
# Typeclass for Scripts (fallback). You usually don't need to change this
# but create custom variations of scripts on a per-case basis instead.
BASE_SCRIPT_TYPECLASS = "typeclasses.defaults.default_scripts.Script"

# Default location for all objects
DEFAULT_HOME = "#2"
# The start position for new characters. Default is Limbo (#2).
#  MULTISESSION_MODE = 0, 1 - used by default unloggedin create command
#  MULTISESSION_MODE = 2,3 - used by default character_create command
START_LOCATION = "#2"

INSTALLED_APPS = INSTALLED_APPS + ("world.mapengine",)

print "http://localhost:4001/webclient/"
######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print "secret_settings.py file not found or failed to import."
