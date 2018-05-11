# coding=utf-8
import re

# Settings
# Fa parte dell'emote parser ma siccome lo usiamo in altri punti è piu comodo lasciarlo qui
# The prefix is the (single-character) symbol used to find the start
# of a object reference, such as /tall (note that
# the system will understand multi-word references like '/a tall man' too).
from django.conf import settings

from evennia.utils import variable_from_module

PREFIX = "/"

# The num_sep is the (single-character) symbol used to separate the
# sdesc from the number when  trying to separate identical sdescs from
# one another. This is the same syntax used in the rest of Evennia, so
# by default, multiple "tall" can be separated by entering 1-tall,
# 2-tall etc.
NUM_SEP = "."

# Texts

EMOTE_NOMATCH_ERROR = \
    """|RNo match for |r{ref}|R.|n"""

EMOTE_MULTIMATCH_ERROR = \
    """|RMultiple possibilities for {ref}:
    |r{reflist}|n"""

RE_FLAGS = re.MULTILINE + re.IGNORECASE + re.UNICODE

RE_PREFIX = re.compile(r"^%s" % PREFIX, re.UNICODE)

# This regex will return groups (num, word), where num is an optional counter to
# separate multimatches from one another and word is the first word in the
# marker. So entering "/tall man" will return groups ("", "tall")
# and "/2-tall man" will return groups ("2", "tall").
RE_OBJ_REF_START = re.compile(r"%s(?:([0-9]+)%s)*(\w+)" % (PREFIX, NUM_SEP), RE_FLAGS)

RE_LEFT_BRACKETS = re.compile(r"\{+", RE_FLAGS)
RE_RIGHT_BRACKETS = re.compile(r"\}+", RE_FLAGS)

# Reference markers are used internally when distributing the emote to
# all that can see it. They are never seen by players and are on the form {#dbref}.
RE_REF = re.compile(r"\{+\#([0-9]+)\}+")

# This regex is used to quickly reference one self in an emote.
RE_SELF_REF = re.compile(r"/me|@", RE_FLAGS)

# regex for non-alphanumberic end of a string
RE_CHAREND = re.compile(r"\W+$", RE_FLAGS)

# reference markers for language
RE_REF_LANG = re.compile(r"\{+\##([0-9]+)\}+")

# language says in the emote are on the form "..." or langname"..." (no spaces).
# this regex returns in groups (langname, say), where langname can be empty.
RE_LANGUAGE = re.compile(r"(?:\((\w+)\))*(\".+?\")")

AT_SEARCH_RESULT = variable_from_module(*settings.SEARCH_AT_RESULT.rsplit('.', 1))
