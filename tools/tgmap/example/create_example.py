import struct

byte_map = dict()

byte_map["oceano"] = 1
byte_map["pianura"] = 2
byte_map["collina"] = 3
byte_map["montagna"] = 4
byte_map["fiume"] = 5
byte_map["sorgente_fiume"] = 6

width = 10
height = 10


def save_mappa_terreni(map, width, height):
    with open("mappa_terreni.bin", "wb") as f:
        f.write(struct.pack("<II", width, height))
        f.write(bytearray(map))


def read_mappa_terreni():
    with open("mappa_terreni.bin", "rb") as f:
        w, h = struct.unpack('<II', f.read(8))
        return w, h, bytearray(f.read(w * h))


map = [1] * width * height

# faccio contorno
for row in range(0, height):
    if row == 0 or row == height - 1:
        for col in range(0, width):
            map[row * width + col] = 0
    else:
        for col in [0, width - 1]:
            map[row * width + col] = 0

# montagna in mezzo

for row in range(height // 2 - 2 // 2, height // 2 + 1):
    for col in range(width // 2 - 2 // 2, width // 2 + 1):
        map[row * width + col] = 4

# colline
for row in [3, 6]:
    for col in range(3, 7):
        map[row * width + col] = 3

for col in [3, 6]:
    for row in range(3, 7):
        map[row * width + col] = 3

# fiume
for col in range(6, width - 1):
    map[6 * width + col] = 5

# foce fiume
map[6 * width + 5] = 6

save_mappa_terreni(map, width, height)

width, height, map = read_mappa_terreni()

print width
print height

for x in range(0, height):
    for y in range(0, width):
        print map[x * width + y],
    print ""
