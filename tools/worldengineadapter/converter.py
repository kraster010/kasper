import struct
from worldengine import world, biome

filename = "dataset/tg_dev.world"

world = world.World.open_protobuf(filename=filename)

print world.width
print world.height

pos = (30, 30)
bioma = world.biome_at(pos)

print bioma.name().rsplit(" ", 1)[1]

distinct_terr_type = biome.Biome.all_names()

print distinct_terr_type

temp = list(distinct_terr_type)

trans = dict(
    scrub="prateria",
    woodland="bosco",
    ice="ghiacchiaio",
    ocean="oceano",
    tundra="tundra",
    steppe="steppa",
    sea="mare",
    desert="deserto",
    forest="foresta"
)

scores = dict()
scores["main river"] = 0
scores["creek"] = 0
scores["alta montagna"] = 0
scores["bassa montagna"] = 0
scores["oceano"] = 0
scores["collina"] = 0
scores["giungla"] = 0
scores["chapparal"] = 0
scores["savanna"] = 0
scores["iceland"] = 0
scores["steppa"] = 0
scores["tundra"] = 0
scores["foresta"] = 0
scores["pianura"] = 0
scores["deserto"] = 0

byte_map = dict()

byte_map["main river"] = 1
byte_map["creek"] = 2
byte_map["alta montagna"] = 3
byte_map["bassa montagna"] = 4
byte_map["oceano"] = 5
byte_map["collina"] = 6
byte_map["giungla"] = 7
byte_map["chapparal"] = 8
byte_map["savanna"] = 9
byte_map["iceland"] = 10
byte_map["steppa"] = 11
byte_map["tundra"] = 12
byte_map["foresta"] = 13
byte_map["pianura"] = 14
byte_map["deserto"] = 15

terrain_map = []

map_classifiers = dict()
map_classifiers["oceano"] = [world.is_ocean]
map_classifiers["main river"] = [world.contains_main_river]
map_classifiers["creek"] = [world.contains_creek]
map_classifiers["alta montagna"] = [world.is_high_mountain]
map_classifiers["bassa montagna"] = [world.is_low_mountain]
map_classifiers["collina"] = [world.is_hill]
map_classifiers["giungla"] = [world.is_jungle]
map_classifiers["chapparal"] = [world.is_chaparral]
map_classifiers["savanna"] = [world.is_savanna]
map_classifiers["iceland"] = [world.is_iceland]
map_classifiers["steppa"] = [world.is_steppe]
map_classifiers["tundra"] = [world.is_tundra]
map_classifiers[
    "foresta"] = world.is_tropical_dry_forest, world.is_warm_temperate_forest, world.is_boreal_forest, world.is_temperate_forest
map_classifiers["pianura"] = [world.is_cold_parklands]
map_classifiers["deserto"] = [world.is_cool_desert, world.is_hot_desert]

classifiers_order_temp = ["oceano", "pianura", "main river", "creek", "alta montagna", "bassa montagna", "collina",
                          "chapparal", "savanna", "steppa", "tundra", "giungla", "deserto", "foresta", "iceland"]

classifiers_order = [map_classifiers[x] for x in classifiers_order_temp]


def check_classifier(ordered_classifier_list, position):
    for func in ordered_classifier_list:
        if func(position):
            return True
    return False


for x in range(world.height):
    for y in range(world.width):
        pos = x, y
        found = False
        for pr in classifiers_order_temp:
            if check_classifier(map_classifiers[pr], pos):
                terrain_map.append(pr)
                scores[pr] += 1
                found = True
                break

        if found:
            continue

        terrain_map.append("shit")

byte_map_temp = bytearray([byte_map[x] for x in terrain_map])

import os
import shutil
import datetime

backup_folder = "backup"
nome_mappa = "mappa_terreni"
ext = ".bin"
nome_mappa_with_ext = nome_mappa + ext


def update_mappa_terreni(map, make_backup=False):
    if make_backup:
        backup_path = nome_mappa + str(datetime.datetime.now()) + ext
        backup_path = os.path.join(backup_folder, backup_path)
        shutil.copy(nome_mappa_with_ext, backup_path)

    with open("mappa_terreni.bin", "wb") as f:
        f.seek(8)
        f.write(bytearray(map))


def save_mappa_terreni(map, width, height):
    with open("mappa_terreni.bin", "wb") as f:
        f.write(struct.pack("<II", width, height))
        f.write(bytearray(map))


def read_mappa_terreni():
    with open("mappa_terreni.bin", "rb") as f:
        w, h = struct.unpack('<II', f.read(8))
        return w, h, bytearray(f.read(w * h))


width, height, map = read_mappa_terreni()


for x, y in sorted([(x, y) for x, y in scores.iteritems()], key=lambda lb: lb[1], reverse=True):
    print "{} : {}".format(x, y)

# print "fuck" if "shit" in terrain_map else "OK!"
