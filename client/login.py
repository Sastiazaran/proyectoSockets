from __future__ import annotations

import pygame as pg

from theme import CREAM, CYAN, MUTED, PANEL_BORDER, PINK, load_font, rounded_rect


class InputBox:
    def __init__(self, x, y, width, height, placeholder="", password=False, max_length=24):
        self.rect = pg.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.password = password
        self.max_length = max_length
        self.text = ""
        self.font = load_font(18)
        self.body_font = pg.font.SysFont("verdana", 22)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0.0

    def value(self) -> str:
        return self.text

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_RETURN:
                self.active = False
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pg.K_TAB:
                return "tab"
            elif event.unicode and event.unicode.isprintable():
                if len(self.text) < self.max_length:
                    self.text += event.unicode
        return None

    def tick(self, dt: float):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0.0
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen):
        border = CYAN if self.active else PANEL_BORDER
        fill = (18, 16, 40)
        rounded_rect(screen, fill, self.rect, radius=12)
        rounded_rect(screen, border, self.rect, radius=12, width=2)

        if self.text:
            shown = ("•" * len(self.text)) if self.password else self.text
            color = CREAM
        else:
            shown = self.placeholder
            color = MUTED

        label = self.body_font.render(shown, True, color)
        text_pos = (self.rect.x + 16, self.rect.y + (self.rect.h - label.get_height()) // 2)
        screen.blit(label, text_pos)

        if self.active and self.cursor_visible:
            cursor_x = text_pos[0] + (label.get_width() if self.text else 0) + 2
            pg.draw.line(
                screen,
                PINK if self.password else CYAN,
                (cursor_x, self.rect.y + 10),
                (cursor_x, self.rect.y + self.rect.h - 10),
                2,
            )
