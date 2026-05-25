import pygame

from .constants import C


def draw_rect_rounded(surf, color, rect, radius=12, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def draw_text(surf, text, font, color, x, y, align="left", shadow=False):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        sr = s.get_rect()
        if align == "center":
            sr.centerx = x
        elif align == "right":
            sr.right = x
        else:
            sr.left = x
        sr.top = y + 2
        surf.blit(s, sr)

    img = font.render(text, True, color)
    rect = img.get_rect()
    if align == "center":
        rect.centerx = x
    elif align == "right":
        rect.right = x
    else:
        rect.left = x
    rect.top = y
    surf.blit(img, rect)
    return rect


def draw_hp_bar(surf, x, y, w, h, pct, label=""):
    pygame.draw.rect(surf, (30, 35, 55), (x, y, w, h), border_radius=4)
    if pct > 0:
        bar_w = max(4, int(w * pct))
        color = C["hp_full"] if pct > 0.5 else C["hp_mid"] if pct > 0.25 else C["hp_low"]
        pygame.draw.rect(surf, color, (x, y, bar_w, h), border_radius=4)
    pygame.draw.rect(surf, C["border"], (x, y, w, h), 1, border_radius=4)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def alpha_surface(w, h, color, alpha):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*color, alpha))
    return s
