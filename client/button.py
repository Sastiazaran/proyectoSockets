from __future__ import annotations

import pygame as pg

from theme import CREAM, SHADOW, VIOLET, VIOLET_HOVER, rounded_rect


class Button:
    def __init__(
        self,
        pos,
        text,
        font,
        size=(300, 58),
        fill=VIOLET,
        fill_hover=VIOLET_HOVER,
        text_color=CREAM,
        outline=False,
    ):
        self.text_input = text
        self.font = font
        self.fill = fill
        self.fill_hover = fill_hover
        self.text_color = text_color
        self.outline = outline
        self.rect = pg.Rect(0, 0, size[0], size[1])
        self.rect.center = pos
        self.hovered = False

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def _label(self, color):
        return self.font.render(self.text_input, True, color)

    def update(self, screen, mouse_pos=None):
        if mouse_pos is None:
            mouse_pos = pg.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        fill = self.fill_hover if self.hovered else self.fill

        shadow = self.rect.move(0, 5)
        rounded_rect(screen, SHADOW, shadow, radius=16)

        if self.outline:
            rounded_rect(screen, (20, 18, 40), self.rect, radius=16)
            rounded_rect(screen, fill, self.rect, radius=16, width=2)
            label_color = CREAM if self.hovered else fill
        else:
            rounded_rect(screen, fill, self.rect, radius=16)
            label_color = self.text_color

        label = self._label(label_color)
        screen.blit(label, label.get_rect(center=self.rect.center))

    # Keep the old name used around the project.
    def changeColor(self, position):
        self.hovered = self.rect.collidepoint(position)
