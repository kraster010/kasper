def load_map_from_file():
    import os
    from django.conf import settings
    map_path = os.path.join(settings.MAP_FOLDER, settings.TERRAIN_MAP)
    print "loaded map at: %s" % map_path

    if not map_path:
        raise RuntimeError("mappa mancante!! {}".format(map_path))

    with open(map_path) as f:
        import struct
        w, h = struct.unpack('<II', f.read(8))
        return w, h, bytearray(f.read(w * h))


def get_new_coordinates(coordinates, exit_key):
    x, y = coordinates
    if exit_key in ["nord", "n"]:
        return x, y + 1
    if exit_key in ["est", "e"]:
        return x + 1, y
    if exit_key in ["sud", "s"]:
        return x, y - 1
    if exit_key in ["ovest", "o"]:
        return x - 1, y
    raise RuntimeError()
