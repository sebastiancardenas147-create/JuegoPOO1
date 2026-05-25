import math
import random
import sys

import pygame

from .constants import C, H, STAR, SKULL, TYPE_COLOR, W
from .data import POKEMONS_BASE, POKEMON_EMOJI
from .model import aplicar_stats_random
from .persistence import actualizar_top5, cargar_top5
from .utils import alpha_surface, draw_hp_bar, draw_rect_rounded, draw_text, lerp_color


class Button:
    def __init__(self, x, y, w, h, text, font,
                 color=None, hover_color=None, text_color=None,
                 radius=10, border_color=None, tag=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = color or C["btn"]
        self.hover_color = hover_color or C["btn_hover"]
        self.text_color = text_color or C["white"]
        self.radius = radius
        self.border_color = border_color
        self.tag = tag
        self._hovering = False
        self._pressing = False
        self.visible = True
        self.enabled = True

    def handle_event(self, event):
        if not self.visible or not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovering = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressing = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressing and self.rect.collidepoint(event.pos):
                self._pressing = False
                return True
            self._pressing = False
        return False

    def draw(self, surf):
        if not self.visible:
            return
        color = C["btn_press"] if self._pressing else (self.hover_color if self._hovering else self.color)
        draw_rect_rounded(surf, color, self.rect, self.radius,
                          border=2, border_color=self.border_color or C["border"])
        draw_text(surf, self.text, self.font, self.text_color,
                  self.rect.centerx, self.rect.centery - self.font.get_height() // 2,
                  align="center", shadow=True)


class Particle:
    def __init__(self, x, y, color, vel=None, life=40, size=4):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vel[0] if vel else random.uniform(-3, 3)
        self.vy = vel[1] if vel else random.uniform(-5, -1)
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        alpha = self.life / self.max_life
        r = max(1, int(self.size * alpha))
        color = lerp_color(self.color, (0, 0, 0), 1 - alpha)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), r)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def burst(self, x, y, color, n=20, life=50):
        for _ in range(n):
            self.particles.append(Particle(x, y, color, life=life,
                                           size=random.randint(3, 7)))

    def update_draw(self, surf):
        self.particles = [p for p in self.particles if p.update()]
        for p in self.particles:
            p.draw(surf)


class AppState:
    def __init__(self):
        self.screen_name = "menu"
        self.nombre_jugador = ""
        self.input_text = ""
        self.equipo_indices = []
        self.equipo_jugador = []
        self.equipo_maquina = []
        self.top5 = cargar_top5()
        self.gano_jugador = False
        self.derrotados_jugador = 0
        self.puntos_ganados = 0


class BackgroundStars:
    def __init__(self, n=80):
        self.stars = [self._new_star() for _ in range(n)]

    def _new_star(self):
        return {
            "x": random.uniform(0, W),
            "y": random.uniform(0, H),
            "r": random.uniform(0.5, 2.5),
            "spd": random.uniform(0.1, 0.4),
            "col": random.choice([C["accent"], C["blue"], C["purple"], C["white"]]),
            "alpha": random.randint(60, 200),
        }

    def update_draw(self, surf):
        for s in self.stars:
            s["y"] -= s["spd"]
            if s["y"] < -5:
                s["y"] = H + 5
                s["x"] = random.uniform(0, W)
            pygame.draw.circle(surf, s["col"], (int(s["x"]), int(s["y"])), int(s["r"]))


class ScreenMenu:
    def __init__(self, fonts, state, stars, particles):
        self.fonts = fonts
        self.state = state
        self.stars = stars
        self.particles = particles
        self.t = 0

        cx = W // 2
        self.btn_jugar = Button(cx - 120, 340, 240, 52, "⚔  JUGAR",
                                fonts["btn"], C["accent2"], border_color=C["accent"])
        self.btn_top5 = Button(cx - 120, 410, 240, 52, "🏆  TOP 5",
                               fonts["btn"], C["btn"], border_color=C["border"])
        self.btn_salir = Button(cx - 120, 480, 240, 52, "✖  SALIR",
                                fonts["btn"], (80, 30, 30), border_color=C["red"])
        self.buttons = [self.btn_jugar, self.btn_top5, self.btn_salir]

    def handle_event(self, event):
        if self.btn_jugar.handle_event(event):
            self.state.screen_name = "name_input"
        if self.btn_top5.handle_event(event):
            self.state.screen_name = "top5"
        if self.btn_salir.handle_event(event):
            pygame.quit()
            sys.exit()

    def draw(self, surf):
        self.t += 1
        surf.fill(C["bg"])
        self.stars.update_draw(surf)

        cx = W // 2
        draw_rect_rounded(surf, C["panel"], pygame.Rect(cx - 200, 160, 400, 400), 20,
                          border=2, border_color=C["border"])

        pulse = math.sin(self.t * 0.04) * 3
        title_col = lerp_color(C["accent"], C["accent2"], (math.sin(self.t * 0.03) + 1) / 2)
        draw_text(surf, "POKÉMON", self.fonts["title_big"], title_col,
                  cx, int(195 + pulse), align="center", shadow=True)
        draw_text(surf, "BATTLE", self.fonts["title_big"], C["white"],
                  cx, int(253 + pulse), align="center", shadow=True)
        draw_text(surf, "— Desktop Edition —", self.fonts["small"], C["gray"],
                  cx, 310, align="center")

        self.particles.update_draw(surf)
        for b in self.buttons:
            b.draw(surf)

        if random.random() < 0.03:
            self.particles.burst(random.randint(cx - 200, cx + 200),
                                 random.randint(160, 560),
                                 random.choice([C["accent"], C["blue"]]), n=5, life=40)


class ScreenNameInput:
    def __init__(self, fonts, state):
        self.fonts = fonts
        self.state = state
        cx = W // 2
        self.btn_ok = Button(cx - 100, 420, 200, 48, "CONFIRMAR",
                             fonts["btn"], C["accent2"], border_color=C["accent"])
        self.btn_back = Button(cx - 100, 480, 200, 48, "← VOLVER",
                               fonts["btn"], C["btn"], border_color=C["border"])
        self.input_rect = pygame.Rect(cx - 180, 340, 360, 52)
        self.cursor_t = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.state.input_text = self.state.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                self._confirmar()
            elif len(self.state.input_text) < 20:
                if event.unicode.isprintable():
                    self.state.input_text += event.unicode
        if self.btn_ok.handle_event(event):
            self._confirmar()
        if self.btn_back.handle_event(event):
            self.state.screen_name = "menu"

    def _confirmar(self):
        nombre = self.state.input_text.strip() or "Entrenador"
        self.state.nombre_jugador = nombre
        self.state.screen_name = "pokedex"

    def draw(self, surf):
        self.cursor_t += 1
        surf.fill(C["bg"])
        cx = W // 2
        draw_rect_rounded(surf, C["panel"], pygame.Rect(cx - 220, 220, 440, 360), 20,
                          border=2, border_color=C["border"])
        draw_text(surf, "¿Cómo te llamas,", self.fonts["h2"], C["white"],
                  cx, 250, align="center")
        draw_text(surf, "entrenador?", self.fonts["h2"], C["accent"],
                  cx, 285, align="center")

        draw_rect_rounded(surf, (30, 35, 55), self.input_rect, 8,
                          border=2, border_color=C["accent"])
        display = self.state.input_text
        if self.cursor_t % 60 < 30:
            display += "|"
        draw_text(surf, display, self.fonts["h2"], C["white"],
                  self.input_rect.centerx,
                  self.input_rect.y + 12, align="center")

        self.btn_ok.draw(surf)
        self.btn_back.draw(surf)


def draw_pokemon_card(surf, fonts, pokemon, x, y, w, h, selected, hover, idx):
    kind = pokemon.kind
    base_color = TYPE_COLOR.get(kind, TYPE_COLOR["normal"])
    bg_color = tuple(min(255, c + 15) for c in base_color) if hover else base_color
    border_col = C["accent"] if selected else (C["border"] if not hover else C["blue"])

    draw_rect_rounded(surf, bg_color, (x, y, w, h), 14)
    draw_rect_rounded(surf, (0, 0, 0, 0), (x, y, w, h), 14,
                      border=3 if selected else 1, border_color=border_col)

    draw_text(surf, f"#{idx+1}", fonts["small"], C["gray"], x + 10, y + 8)
    emoji = POKEMON_EMOJI.get(pokemon.nombre, "?")
    draw_text(surf, emoji, fonts["emoji"], C["white"], x + w // 2, y + 18, align="center")

    name_col = C["accent"] if selected else C["white"]
    draw_text(surf, pokemon.nombre, fonts["bold"], name_col,
              x + w // 2, y + 80, align="center", shadow=True)

    if kind == "legendary":
        draw_text(surf, STAR + " LEGENDARIO", fonts["tiny"], C["legendary"],
                  x + w // 2, y + 100, align="center")
    elif kind == "ghost":
        draw_text(surf, "👻 FANTASMA", fonts["tiny"], C["ghost"],
                  x + w // 2, y + 100, align="center")

    stats = [("HP", pokemon.hp_max), ("ATQ", pokemon.ataque), ("DEF", pokemon.defensa)]
    for si, (lbl, val) in enumerate(stats):
        sy = y + 118 + si * 22
        draw_text(surf, lbl, fonts["tiny"], C["gray"], x + 10, sy)
        bar_w = int((val / 160) * (w - 60))
        pygame.draw.rect(surf, (30, 35, 55), (x + 40, sy + 3, w - 50, 12), border_radius=4)
        pygame.draw.rect(surf, C["blue"], (x + 40, sy + 3, bar_w, 12), border_radius=4)
        draw_text(surf, str(val), fonts["tiny"], C["white"], x + w - 8, sy, align="right")

    draw_text(surf, "Ataques:", fonts["tiny"], C["gray"], x + 8, y + 188)
    for ai, atk in enumerate(pokemon.ataques):
        draw_text(surf, f"• {atk.nombre}", fonts["tiny"], C["white"],
                  x + 8, y + 202 + ai * 13)

    if selected:
        s = alpha_surface(w, h, C["accent"], 25)
        surf.blit(s, (x, y))


class ScreenPokedex:
    def __init__(self, fonts, state):
        self.fonts = fonts
        self.state = state
        self.hover_i = -1

        CX = W // 2
        self.btn_confirmar = Button(CX - 120, H - 65, 240, 48,
                                    "INICIAR BATALLA ⚔",
                                    fonts["btn"], C["accent2"],
                                    border_color=C["accent"])
        self.btn_back = Button(40, H - 65, 120, 48, "← VOLVER",
                               fonts["btn"], C["btn"], border_color=C["border"])

        self.card_w = 170
        self.card_h = 245
        self.cols = 3
        self.pad = 18
        total_w = self.cols * self.card_w + (self.cols - 1) * self.pad
        start_x = (W - total_w) // 2
        start_y = 105
        self.cards_rects = []
        for i in range(len(POKEMONS_BASE)):
            col = i % self.cols
            row = i // self.cols
            cx = start_x + col * (self.card_w + self.pad)
            cy = start_y + row * (self.card_h + self.pad)
            self.cards_rects.append(pygame.Rect(cx, cy, self.card_w, self.card_h))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover_i = -1
            for i, r in enumerate(self.cards_rects):
                if r.collidepoint(event.pos):
                    self.hover_i = i
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.cards_rects):
                if r.collidepoint(event.pos):
                    if i in self.state.equipo_indices:
                        self.state.equipo_indices.remove(i)
                    elif len(self.state.equipo_indices) < 2:
                        self.state.equipo_indices.append(i)
        if self.btn_confirmar.handle_event(event):
            if len(self.state.equipo_indices) == 2:
                self._iniciar_batalla()
        if self.btn_back.handle_event(event):
            self.state.screen_name = "menu"

    def _iniciar_batalla(self):
        self.state.equipo_jugador = [
            aplicar_stats_random(POKEMONS_BASE[i]) for i in self.state.equipo_indices
        ]
        disponibles = [i for i in range(len(POKEMONS_BASE)) if i not in self.state.equipo_indices]
        elegidos = random.sample(disponibles, 2)
        self.state.equipo_maquina = [
            aplicar_stats_random(POKEMONS_BASE[i]) for i in elegidos
        ]
        self.state.screen_name = "battle"

    def draw(self, surf):
        surf.fill(C["bg"])
        draw_text(surf, "POKÉDEX — Selecciona tu equipo (2 Pokémon)",
                  self.fonts["h2"], C["accent"], W // 2, 18, align="center", shadow=True)
        n_sel = len(self.state.equipo_indices)
        col = C["green"] if n_sel == 2 else C["gray"]
        draw_text(surf, f"Seleccionados: {n_sel}/2",
                  self.fonts["normal"], col, W // 2, 60, align="center")

        for i, (p, rect) in enumerate(zip(POKEMONS_BASE, self.cards_rects)):
            draw_pokemon_card(surf, self.fonts, p,
                              rect.x, rect.y, rect.w, rect.h,
                              i in self.state.equipo_indices,
                              i == self.hover_i, i)

        self.btn_confirmar.enabled = (n_sel == 2)
        self.btn_confirmar.color = C["accent2"] if n_sel == 2 else (60, 60, 80)
        self.btn_confirmar.draw(surf)
        self.btn_back.draw(surf)


class BattleLog:
    MAX = 8

    def __init__(self):
        self.lines = []

    def add(self, text, color=None):
        self.lines.append({"text": text, "color": color or C["white"]})
        if len(self.lines) > self.MAX:
            self.lines.pop(0)

    def draw(self, surf, fonts, x, y, w, h):
        draw_rect_rounded(surf, C["panel"], (x, y, w, h), 10,
                          border=1, border_color=C["border"])
        for i, line in enumerate(self.lines):
            draw_text(surf, line["text"], fonts["small"], line["color"],
                      x + 10, y + 8 + i * 22)


class ScreenBattle:
    def __init__(self, fonts, state, particles):
        self.fonts = fonts
        self.state = state
        self.particles = particles
        self.log = BattleLog()
        self.t = 0
        self.shake = {"j": 0, "m": 0}
        self.shake_off = {"j": (0, 0), "m": (0, 0)}
        self.idx_j = 0
        self.idx_m = 0
        self.turno = "jugador"
        self.atk_anim = 0
        self.atk_color = C["red"]
        self.atk_buttons = []
        self._build_atk_buttons()
        self.btn_continue = Button(W // 2 - 100, H - 65, 200, 45,
                                   "▶ CONTINUAR", fonts["btn"],
                                   C["accent2"], border_color=C["accent"])
        self.show_continue = False
        self._intro_log()

    def _intro_log(self):
        eq_j = self.state.equipo_jugador
        eq_m = self.state.equipo_maquina
        self.log.add("¡Que empiece el combate!", C["accent"])
        self.log.add(f"Tu equipo: {eq_j[0].nombre} y {eq_j[1].nombre}", C["blue"])
        self.log.add(f"Rival:     {eq_m[0].nombre} y {eq_m[1].nombre}", C["red"])

    def _build_atk_buttons(self):
        pj = self.state.equipo_jugador[self.idx_j]
        self.atk_buttons = []
        base_y = 490
        for i, atk in enumerate(pj.ataques):
            b = Button(W // 2 - 220 + i * 155, base_y, 145, 48,
                       atk.nombre, self.fonts["small"],
                       C["btn"], border_color=C["border"], tag=i)
            self.atk_buttons.append(b)

    def handle_event(self, event):
        if self.turno == "fin":
            return
        if self.turno == "jugador":
            for b in self.atk_buttons:
                if b.handle_event(event):
                    self._jugador_ataca(b.tag)
        elif self.turno == "maquina_espera":
            if self.btn_continue.handle_event(event):
                self._maquina_ataca()
                self.show_continue = False

    def _jugador_ataca(self, atk_idx):
        pj = self.state.equipo_jugador[self.idx_j]
        pm = self.state.equipo_maquina[self.idx_m]
        atk = pj.ataques[atk_idx]

        dano, crit, esquivo = pj.usar_ataque(pm, atk)

        if esquivo:
            self.log.add(f"{pm.nombre} esquivó el ataque!", C["purple"])
        else:
            msg = f"{pj.nombre} usa {atk.nombre} → {dano} DMG"
            if crit:
                msg += " ¡CRÍTICO!"
            self.log.add(msg, C["accent"])
            self.shake["m"] = 12
            self.particles.burst(650, 280, C["accent2"] if not crit else C["accent"],
                                 n=25 if crit else 15)

        if not pm.esta_vivo():
            self.log.add(f"¡{pm.nombre} fue derrotado!", C["red"])
            self.idx_m += 1
            if self.idx_m >= len(self.state.equipo_maquina):
                self._fin(True)
                return
            else:
                self.log.add(f"¡Máquina envía a {self.state.equipo_maquina[self.idx_m].nombre}!", C["red"])

        self.turno = "maquina_espera"
        self.show_continue = True

    def _maquina_ataca(self):
        pj = self.state.equipo_jugador[self.idx_j]
        pm = self.state.equipo_maquina[self.idx_m]
        atk = random.choice(pm.ataques)

        dano, crit, esquivo = pm.usar_ataque(pj, atk)

        if esquivo:
            self.log.add(f"{pj.nombre} esquivó el ataque!", C["purple"])
        else:
            msg = f"Máquina usa {atk.nombre} → {dano} DMG"
            if crit:
                msg += " ¡CRÍTICO!"
            self.log.add(msg, C["red"])
            self.shake["j"] = 12
            self.particles.burst(220, 280, C["red"], n=25 if crit else 15)

        if not pj.esta_vivo():
            self.log.add(f"¡{pj.nombre} fue derrotado!", C["red"])
            self.state.derrotados_jugador += 1
            self.idx_j += 1
            if self.idx_j >= len(self.state.equipo_jugador):
                self._fin(False)
                return
            else:
                self.log.add(f"Envías a {self.state.equipo_jugador[self.idx_j].nombre}!", C["blue"])
                self._build_atk_buttons()

        self.turno = "jugador"

    def _fin(self, gano):
        self.state.gano_jugador = gano
        self.turno = "fin"
        if gano:
            supervivientes = sum(1 for p in self.state.equipo_jugador if p.esta_vivo())
            puntos = 15 if supervivientes == 1 else 10
        else:
            puntos = -(self.state.derrotados_jugador * 5)

        self.state.puntos_ganados = puntos
        self.state.top5 = actualizar_top5(self.state.nombre_jugador, puntos)
        self._to_result_timer = 90

    def _draw_pokemon_sprite(self, surf, pokemon, cx, cy, shake_key, active):
        ox, oy = self.shake_off[shake_key]
        if self.shake[shake_key] > 0:
            ox = random.randint(-6, 6)
            oy = random.randint(-3, 3)
            self.shake[shake_key] -= 1
            self.shake_off[shake_key] = (ox, oy)
        else:
            self.shake_off[shake_key] = (0, 0)

        x = cx + ox
        y = cy + oy
        r = 65
        alive = pokemon.esta_vivo()
        alpha_c = (200, 200, 200) if not alive else (255, 255, 255)
        kind = pokemon.kind
        ring_c = TYPE_COLOR.get(kind, TYPE_COLOR["normal"])
        pygame.draw.circle(surf, ring_c, (x, y), r)
        pygame.draw.circle(surf, C["border"], (x, y), r, 2)

        emoji = POKEMON_EMOJI.get(pokemon.nombre, "?")
        img = self.fonts["emoji_lg"].render(emoji, True, alpha_c)
        ir = img.get_rect(center=(x, y))
        surf.blit(img, ir)

        draw_text(surf, pokemon.nombre, self.fonts["bold"],
                  C["white"] if alive else C["gray"],
                  x, y + r + 6, align="center")
        draw_hp_bar(surf, x - 60, y + r + 26, 120, 12, pokemon.hp_pct())
        draw_text(surf, f"{pokemon.hp}/{pokemon.hp_max}",
                  self.fonts["tiny"], C["gray"], x, y + r + 42, align="center")
        if not alive:
            draw_text(surf, "DERROTADO", self.fonts["tiny"], C["red"],
                      x, y + r + 56, align="center")

    def draw(self, surf):
        self.t += 1
        if self.turno == "fin":
            self._to_result_timer -= 1
            if self._to_result_timer <= 0:
                self.state.screen_name = "result"
                return

        surf.fill(C["bg"])
        draw_rect_rounded(surf, C["panel"], pygame.Rect(0, 0, W, 75), 0)
        draw_text(surf, f"⚔  COMBATE: {self.state.nombre_jugador} VS MÁQUINA",
                  self.fonts["h2"], C["accent"], W // 2, 22, align="center", shadow=True)
        turno_txt = {
            "jugador": f"Turno de {self.state.nombre_jugador} — elige ataque",
            "maquina_espera": "Máquina lista para atacar — presiona CONTINUAR",
            "fin": "¡Combate terminado!"
        }.get(self.turno, "")
        draw_text(surf, turno_txt, self.fonts["small"], C["gray"], W // 2, 52, align="center")

        draw_rect_rounded(surf, C["panel2"], pygame.Rect(50, 90, W - 100, 330), 16,
                          border=1, border_color=C["border"])

        eq_j = self.state.equipo_jugador
        eq_m = self.state.equipo_maquina
        self._draw_pokemon_sprite(surf, eq_j[self.idx_j], 220, 260, "j", True)
        if self.idx_j == 1 and eq_j[0].hp == 0:
            self._draw_pokemon_sprite(surf, eq_j[0], 100, 320, "j", False)
        if self.idx_j == 0 and len(eq_j) > 1:
            p2 = eq_j[1]
            pygame.draw.circle(surf, (30, 35, 55), (110, 370), 35)
            lbl = self.fonts["tiny"].render(p2.nombre, True, C["gray"])
            surf.blit(lbl, lbl.get_rect(center=(110, 370)))

        if self.idx_m < len(eq_m):
            self._draw_pokemon_sprite(surf, eq_m[self.idx_m], 660, 260, "m", True)
        if self.idx_m == 1 and len(eq_m) > 1 and eq_m[0].hp <= 0:
            self._draw_pokemon_sprite(surf, eq_m[0], 780, 320, "m", False)
        if self.idx_m == 0 and len(eq_m) > 1:
            p2 = eq_m[1]
            pygame.draw.circle(surf, (30, 35, 55), (780, 370), 35)
            lbl = self.fonts["tiny"].render(p2.nombre, True, C["gray"])
            surf.blit(lbl, lbl.get_rect(center=(780, 370)))

        pulse = abs(math.sin(self.t * 0.06))
        vc = lerp_color(C["accent"], C["accent2"], pulse)
        draw_text(surf, "VS", self.fonts["title_big"], vc, W // 2, 230, align="center", shadow=True)

        self.log.draw(surf, self.fonts, 50, 435, W - 100, 195)
        if self.turno == "jugador":
            draw_text(surf, "Elige ataque:", self.fonts["small"], C["gray"],
                      W // 2 - 220, 468)
            for b in self.atk_buttons:
                b.draw(surf)

        if self.show_continue and self.turno == "maquina_espera":
            self.btn_continue.draw(surf)

        self.particles.update_draw(surf)


class ScreenResult:
    def __init__(self, fonts, state, particles):
        self.fonts = fonts
        self.state = state
        self.particles = particles
        self.t = 0

        cx = W // 2
        self.btn_menu = Button(cx - 130, H - 90, 260, 52,
                               "← VOLVER AL MENÚ", fonts["btn"],
                               C["btn"], border_color=C["border"])
        self.btn_retry = Button(cx - 130, H - 150, 260, 52,
                                "⚔  REVANCHA", fonts["btn"],
                                C["accent2"], border_color=C["accent"])

        if state.gano_jugador:
            for _ in range(5):
                particles.burst(random.randint(200, W - 200),
                                random.randint(100, 300),
                                random.choice([C["accent"], C["green"], C["blue"]]),
                                n=30, life=80)

    def handle_event(self, event):
        if self.btn_menu.handle_event(event):
            self.state.screen_name = "menu"
            self.state.equipo_indices = []
            self.state.input_text = ""
        if self.btn_retry.handle_event(event):
            self.state.screen_name = "pokedex"
            self.state.equipo_indices = []

    def draw(self, surf):
        self.t += 1
        surf.fill(C["bg"])

        gano = self.state.gano_jugador
        puntos = self.state.puntos_ganados
        top5 = self.state.top5

        draw_rect_rounded(surf, C["panel"], pygame.Rect(W // 2 - 320, 50, 640, 540), 20,
                          border=2, border_color=C["border"])

        if gano:
            pulse = abs(math.sin(self.t * 0.05))
            rc = lerp_color(C["green"], C["accent"], pulse)
            draw_text(surf, "🏆 ¡VICTORIA!", self.fonts["title_big"], rc,
                      W // 2, 75, align="center", shadow=True)
        else:
            draw_text(surf, SKULL + " DERROTA", self.fonts["title_big"], C["red"],
                      W // 2, 75, align="center", shadow=True)

        draw_text(surf, self.state.nombre_jugador,
                  self.fonts["h2"], C["accent"], W // 2, 140, align="center")

        if puntos >= 0:
            pt_txt = f"+{puntos} puntos"
            pt_col = C["green"]
            if gano:
                surviv = sum(1 for p in self.state.equipo_jugador if p.esta_vivo())
                if surviv == 1:
                    draw_text(surf, "⭐ ¡Ganaste con 1 Pokémon! +5 bonus",
                              self.fonts["normal"], C["accent"], W // 2, 178, align="center")
        else:
            pt_txt = f"{puntos} puntos"
            pt_col = C["red"]

        draw_text(surf, pt_txt, self.fonts["h2"], pt_col,
                  W // 2, 205, align="center", shadow=True)

        pygame.draw.line(surf, C["border"], (W // 2 - 270, 245), (W // 2 + 270, 245), 1)

        draw_text(surf, "🏆  TOP 5 JUGADORES", self.fonts["bold"], C["accent"],
                  W // 2, 258, align="center", shadow=True)
        medallas = ["🥇", "🥈", "🥉", "4", "5"]
        for i, e in enumerate(top5):
            y = 290 + i * 38
            color = C["accent"] if i == 0 else C["blue"] if i == 1 else C["green"] if i == 2 else C["gray"]
            isme = e["nombre"].lower() == self.state.nombre_jugador.lower()
            bg = (40, 50, 80) if isme else C["panel2"]
            draw_rect_rounded(surf, bg, (W // 2 - 260, y - 4, 520, 32), 8)
            medal = medallas[i] if i < len(medallas) else str(i + 1)
            draw_text(surf, f"{medal}  {e['nombre']}", self.fonts["normal"], color,
                      W // 2 - 240, y)
            draw_text(surf, f"{e['puntos']} pts", self.fonts["bold"], color,
                      W // 2 + 240, y, align="right")
            if isme:
                draw_text(surf, "◄ tú", self.fonts["tiny"], C["accent"],
                          W // 2 + 270, y + 2)

        self.particles.update_draw(surf)
        self.btn_retry.draw(surf)
        self.btn_menu.draw(surf)


class ScreenTop5:
    def __init__(self, fonts, state):
        self.fonts = fonts
        self.state = state
        cx = W // 2
        self.btn_back = Button(cx - 100, H - 70, 200, 48, "← VOLVER",
                               fonts["btn"], C["btn"], border_color=C["border"])

    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            self.state.screen_name = "menu"

    def draw(self, surf):
        surf.fill(C["bg"])
        cx = W // 2
        draw_rect_rounded(surf, C["panel"], pygame.Rect(cx - 300, 60, 600, 540), 20,
                          border=2, border_color=C["border"])
        draw_text(surf, "🏆  TOP 5 MEJORES ENTRENADORES",
                  self.fonts["h2"], C["accent"], cx, 90, align="center", shadow=True)

        top5 = cargar_top5()
        medallas = ["🥇", "🥈", "🥉", "4", "5"]
        if not top5:
            draw_text(surf, "¡Sin jugadores aún! Sé el primero.",
                      self.fonts["normal"], C["gray"], cx, 300, align="center")
        else:
            for i, e in enumerate(top5):
                y = 170 + i * 70
                color = C["accent"] if i == 0 else C["blue"] if i == 1 else C["green"] if i == 2 else C["gray"]
                draw_rect_rounded(surf, C["panel2"], (cx - 260, y - 8, 520, 58), 12,
                                  border=1, border_color=color)
                medal = medallas[i] if i < len(medallas) else str(i + 1)
                draw_text(surf, f"{medal}", self.fonts["h2"], color, cx - 230, y)
                draw_text(surf, e["nombre"], self.fonts["h2"], C["white"], cx - 180, y)
                draw_text(surf, f"{e['puntos']} pts", self.fonts["h2"], color,
                          cx + 240, y, align="right")

        self.btn_back.draw(surf)
