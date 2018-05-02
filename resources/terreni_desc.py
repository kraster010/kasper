# coding=utf-8
# L'assegnamento è posizionale, non cambiarlo se non si fa cosa  si fa
__all__ = ["get_room_data"]

__inverse_byte_map = ["TerrainOceano", "TerrainPianura", "TerrainCollina", "TerrainMontagna", "TerrainFiume",
                      "TerrainSorgenteFiume"]


def get_room_data(id_terreno):
    return globals()[__inverse_byte_map[id_terreno]]


class TerrainOceano(object):
    titolo = "Oceano"
    descrizioni = ["OceanoDesc1", "OceanoDesc2"]


class TerrainPianura(object):
    titolo = "Pianura"
    descrizioni = ["PianuraDesc1", "PianuraDesc2"]


class TerrainCollina(object):
    titolo = "Collina"
    descrizioni = ["CollinaDesc1", "CollinaDesc2"]


class TerrainMontagna(object):
    titolo = "Montagna"
    descrizioni = ["MontagnaDesc1", "MontagnaDesc2"]


class TerrainFiume(object):
    titolo = "Fiume"
    descrizioni = ["FiumeDesc1", "FiumeDesc2"]


class TerrainSorgenteFiume(object):
    titolo = "Sorgente Fiume"
    descrizioni = ["SorgenteFiumeDesc1", "SorgenteFiumeDesc2"]
