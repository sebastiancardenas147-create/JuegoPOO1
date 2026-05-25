import pygame

from pokemon_battle.constants import W, H, FPS
from pokemon_battle.ui import (
    AppState,
    BackgroundStars,
    ParticleSystem,
    ScreenMenu,
    ScreenNameInput,
    ScreenPokedex,
    ScreenBattle,
    ScreenResult,
    ScreenTop5,
)


def main():
    pygame.init()
    pygame.display.set_caption("Pokémon Battle")

    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    def F(size, bold=False):
        return pygame.font.SysFont("segoeui,dejavusans,arial", size, bold=bold)

    fonts = {
        "title_big": F(52, bold=True),
        "h2": F(28, bold=True),
        "bold": F(18, bold=True),
        "btn": F(17, bold=True),
        "normal": F(16),
        "small": F(14),
        "tiny": F(12),
        "emoji": F(32),
        "emoji_lg": F(52),
    }

    state = AppState()
    stars = BackgroundStars()
    particles = ParticleSystem()
    screens = {}
    current_screen = "menu"

    def rebuild_screen(name):
        if name == "menu":
            screens["menu"] = ScreenMenu(fonts, state, stars, particles)
        elif name == "name_input":
            screens["name_input"] = ScreenNameInput(fonts, state)
        elif name == "pokedex":
            screens["pokedex"] = ScreenPokedex(fonts, state)
        elif name == "battle":
            state.derrotados_jugador = 0
            state.puntos_ganados = 0
            screens["battle"] = ScreenBattle(fonts, state, particles)
        elif name == "result":
            screens["result"] = ScreenResult(fonts, state, particles)
        elif name == "top5":
            screens["top5"] = ScreenTop5(fonts, state)

    rebuild_screen("menu")

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        name = state.screen_name
        if name != current_screen:
            rebuild_screen(name)
            current_screen = name

        screen_obj = screens.get(name)
        if screen_obj:
            for event in events:
                screen_obj.handle_event(event)
            screen_obj.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
