from .model import Ataque, Pokemon, PokemonFantasma, PokemonLegendario

POKEMONS_BASE = [
    Pokemon("Pikachu", 35, 55, 40, [
        Ataque("Impactrueno", 30, 0.15),
        Ataque("Rayo", 40, 0.10),
        Ataque("Trueno", 55, 0.05),
    ]),
    Pokemon("Charizard", 78, 84, 78, [
        Ataque("Lanzallamas", 50, 0.12),
        Ataque("Vuelo", 45, 0.12),
        Ataque("Llamarada", 65, 0.07),
    ]),
    Pokemon("Blastoise", 79, 83, 100, [
        Ataque("Hidrobomba", 55, 0.10),
        Ataque("Surf", 40, 0.12),
        Ataque("Pistola Agua", 30, 0.18),
    ]),
    PokemonLegendario("Mewtwo", 106, 110, 90, [
        Ataque("Psiquico", 65, 0.15),
        Ataque("Sombra Vil", 50, 0.10),
        Ataque("Rayo", 45, 0.12),
    ]),
    PokemonFantasma("Gengar", 60, 65, 60, [
        Ataque("Bola Sombra", 40, 0.15),
        Ataque("Hipnosis", 15, 0.30),
        Ataque("Puño Sombra", 30, 0.12),
    ]),
    PokemonLegendario("Rayquaza", 105, 150, 90, [
        Ataque("Cometa Draco", 70, 0.12),
        Ataque("Hiperrayo", 65, 0.08),
        Ataque("Ascenso Draco", 75, 0.07),
    ]),
]

POKEMON_EMOJI = {
    "Pikachu": "⚡",
    "Charizard": "🔥",
    "Blastoise": "💧",
    "Mewtwo": "🌀",
    "Gengar": "👻",
    "Rayquaza": "🐉",
}
