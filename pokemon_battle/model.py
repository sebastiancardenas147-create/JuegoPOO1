import copy
import random


class Ataque:
    """Representa un movimiento de combate."""
    def __init__(self, nombre, dano, crit):
        self.nombre = nombre
        self.__dano = dano
        self.crit = crit
        self.tipo = "normal"

    @property
    def dano(self):
        return self.__dano

    @dano.setter
    def dano(self, valor):
        if valor > 0:
            self.__dano = valor

    def es_critico(self):
        return random.random() < self.crit

    def calcular_dano(self, ataque_stat, defensa_stat):
        mult = 1.5 if self.es_critico() else 1.0
        raw = ataque_stat * self.__dano / max(1, defensa_stat) * mult
        return max(1, int(raw)), mult > 1.0

    def info(self):
        return f"{self.nombre}  DMG:{self.__dano}  CRIT:{int(self.crit*100)}%"


class Pokemon:
    """Clase base Pokémon."""
    kind = "normal"

    def __init__(self, nombre, hp, ataque, defensa, ataques):
        self.nombre = nombre
        self.hp_max = hp
        self.hp = hp
        self.ataque = ataque
        self.defensa = defensa
        self.ataques = ataques

    def esta_vivo(self):
        return self.hp > 0

    def recibir_dano(self, dano):
        self.hp = max(0, self.hp - dano)

    def hp_pct(self):
        return self.hp / self.hp_max

    def usar_ataque(self, objetivo, ataque):
        dano, crit = ataque.calcular_dano(self.ataque, objetivo.defensa)
        objetivo.recibir_dano(dano)
        return dano, crit, False


class PokemonLegendario(Pokemon):
    """Pokémon legendario: bonus de daño fijo."""
    kind = "legendary"
    bonus = 10

    def usar_ataque(self, objetivo, ataque):
        dano, crit = ataque.calcular_dano(self.ataque, objetivo.defensa)
        dano += self.bonus
        objetivo.recibir_dano(dano)
        return dano, crit, False


class PokemonFantasma(Pokemon):
    """Pokémon fantasma: el OBJETIVO puede esquivar."""
    kind = "ghost"
    evasion = 0.20

    def recibir_dano(self, dano):
        super().recibir_dano(dano)

    def usar_ataque(self, objetivo, ataque):
        if isinstance(objetivo, PokemonFantasma) and random.random() < objetivo.evasion:
            return 0, False, True
        dano, crit = ataque.calcular_dano(self.ataque, objetivo.defensa)
        objetivo.recibir_dano(dano)
        return dano, crit, False


def aplicar_stats_random(pokemon):
    p = copy.deepcopy(pokemon)
    p.hp = max(1, p.hp + random.randint(-10, 10))
    p.hp_max = p.hp
    p.ataque = max(1, p.ataque + random.randint(-10, 10))
    p.defensa = max(1, p.defensa + random.randint(-10, 10))
    return p
