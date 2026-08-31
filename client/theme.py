"""Visual theme and drawing helpers for the Pygame client."""

from __future__ import annotations

import math
from pathlib import Path

import pygame as pg

CLIENT_DIR = Path(__file__).resolve().parent
FONT_PATH = CLIENT_DIR / "resources" / "font.ttf"

WIDTH, HEIGHT = 960, 720
FPS = 60

# Palette — midnight arcade
BG_TOP = (16, 14, 36)
BG_BOTTOM = (8, 7, 20)
PANEL = (24, 21, 48)
PANEL_BORDER = (72, 62, 120)
VIOLET = (124, 92, 255)
VIOLET_HOVER = (158, 132, 255)
CYAN = (94, 225, 255)
PINK = (255, 107, 157)
GOLD = (240, 193, 75)
CREAM = (244, 241, 255)
MUTED = (154, 146, 186)
CELL = (32, 28, 62)
CELL_HOVER = (48, 42, 88)
WIN_GLOW = (255, 214, 90)
OK = (86, 220, 150)
DANGER = (255, 96, 118)
SHADOW = (4, 3, 12)


def load_font(size: int, fallback: str = "verdana") -> pg.font.Font:
    try:
        if FONT_PATH.exists():
            return pg.font.Font(str(FONT_PATH), size)
    except (pg.error, OSError):
        pass
    return pg.font.SysFont(fallback, size, bold=True)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def draw_vertical_gradient(surface: pg.Surface, top, bottom) -> None:
    height = surface.get_height()
    width = surface.get_width()
    for y in range(height):
        t = y / max(height - 1, 1)
        color = (
            int(lerp(top[0], bottom[0], t)),
            int(lerp(top[1], bottom[1], t)),
            int(lerp(top[2], bottom[2], t)),
        )
        pg.draw.line(surface, color, (0, y), (width, y))


def draw_vignette_orbs(surface: pg.Surface, t: float) -> None:
    cx, cy = WIDTH // 2, HEIGHT // 2
    orbs = (
        (cx - 220, cy - 80, 260, (50, 30, 110), 0.6),
        (cx + 260, cy + 140, 220, (20, 70, 110), 0.9),
        (cx + 40, cy - 220, 180, (90, 30, 80), 1.3),
    )
    overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    for x, y, r, color, speed in orbs:
        pulse = 1 + 0.08 * math.sin(t * speed)
        rr = int(r * pulse)
        pg.draw.circle(overlay, (*color, 55), (int(x), int(y)), rr)
    surface.blit(overlay, (0, 0))


def rounded_rect(surface, color, rect, radius=16, width=0):
    pg.draw.rect(surface, color, rect, width=width, border_radius=radius)


def draw_panel(surface, rect, radius=22):
    shadow = rect.move(0, 8)
    rounded_rect(surface, (0, 0, 0), shadow, radius)
    rounded_rect(surface, PANEL, rect, radius)
    rounded_rect(surface, PANEL_BORDER, rect, radius, width=2)


def blit_text(surface, font, text, color, center=None, topleft=None, alpha=None):
    image = font.render(text, True, color)
    if alpha is not None:
        image.set_alpha(alpha)
    rect = image.get_rect()
    if center:
        rect.center = center
    if topleft:
        rect.topleft = topleft
    surface.blit(image, rect)
    return rect


def wrap_text(font, text, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
