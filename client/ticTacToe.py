#!/usr/bin/env python3
"""Neon arcade Tic-Tac-Toe client with local accounts and optional C auth server."""

from __future__ import annotations

import sys
from pathlib import Path

CLIENT_DIR = Path(__file__).resolve().parent
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

import pygame as pg

import auth_client
import users
from button import Button
from game_logic import EMPTY, PLAYER_O, PLAYER_X, Board
from login import InputBox
from theme import (
    BG_BOTTOM,
    BG_TOP,
    CELL,
    CELL_HOVER,
    CREAM,
    CYAN,
    DANGER,
    FPS,
    GOLD,
    HEIGHT,
    MUTED,
    OK,
    PINK,
    WIDTH,
    blit_text,
    draw_panel,
    draw_vertical_gradient,
    draw_vignette_orbs,
    load_font,
    rounded_rect,
    wrap_text,
)

BOARD_ORIGIN = (270, 150)
CELL_SIZE = 140
CELL_GAP = 12
BOARD_PIXELS = CELL_SIZE * 3 + CELL_GAP * 2


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Tic-Tac-Toe")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.time = 0.0

        self.title_font = load_font(26)
        self.heading_font = load_font(22)
        self.ui_font = load_font(16)
        self.small_font = load_font(11)
        self.body_font = pg.font.SysFont("verdana", 20)
        self.tiny_body = pg.font.SysFont("verdana", 16)

        self.state = "login"
        self.username = None
        self.status_message = ""
        self.status_ok = True
        self.server_online = False
        self.scores = {PLAYER_X: 0, PLAYER_O: 0}

        self.board = Board()
        self.hover_index = None
        self.ignore_clicks_until_up = False
        self.round_scored = False
        self.server_online = False
        self._server_check_at = -10.0

        self._build_login_widgets()
        self._build_menu_buttons()
        self._build_play_buttons()
        users.ensure_demo_user()

    def _build_login_widgets(self):
        box_w, box_h = 360, 48
        cx = WIDTH // 2 - box_w // 2
        self.user_box = InputBox(cx, 278, box_w, box_h, placeholder="username")
        self.pass_box = InputBox(cx, 360, box_w, box_h, placeholder="password", password=True)
        self.login_btn = Button((WIDTH // 2, 460), "LOG IN", self.ui_font, size=(360, 54))
        self.register_btn = Button(
            (WIDTH // 2, 528),
            "REGISTER",
            self.ui_font,
            size=(360, 54),
            fill=CYAN,
            fill_hover=(160, 240, 255),
            outline=True,
        )
        self.user_box.active = True

    def _build_menu_buttons(self):
        self.play_btn = Button((WIDTH // 2, 300), "PLAY", self.ui_font, size=(340, 60))
        self.help_btn = Button(
            (WIDTH // 2, 380),
            "HOW TO PLAY",
            self.ui_font,
            size=(340, 60),
            fill=CYAN,
            fill_hover=(160, 240, 255),
            outline=True,
        )
        self.quit_btn = Button(
            (WIDTH // 2, 460),
            "QUIT",
            self.ui_font,
            size=(340, 60),
            fill=PINK,
            fill_hover=(255, 150, 180),
        )
        self.logout_btn = Button(
            (WIDTH // 2, 540),
            "LOG OUT",
            self.small_font,
            size=(200, 44),
            fill=MUTED,
            fill_hover=CREAM,
            outline=True,
        )

    def _build_play_buttons(self):
        self.restart_btn = Button((WIDTH // 2 - 140, 640), "RESTART", self.small_font, size=(200, 48))
        self.menu_btn = Button(
            (WIDTH // 2 + 140, 640),
            "MENU",
            self.small_font,
            size=(200, 48),
            fill=CYAN,
            fill_hover=(160, 240, 255),
            outline=True,
        )
        self.help_back_btn = Button((WIDTH // 2, 600), "BACK", self.ui_font, size=(220, 52))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.time += dt
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self._quit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    if self.state == "play":
                        self.state = "menu"
                    elif self.state == "help":
                        self.state = "menu"

            self._refresh_server()
            self._draw_backdrop()

            if self.state == "login":
                self._login_screen(events, dt)
            elif self.state == "menu":
                self._menu_screen(events)
            elif self.state == "help":
                self._help_screen(events)
            elif self.state == "play":
                self._play_screen(events)

            pg.display.flip()

    def _refresh_server(self):
        if self.time - self._server_check_at < 2.0:
            return
        self._server_check_at = self.time
        self.server_online = auth_client.server_is_up(timeout=0.05)

    def _draw_backdrop(self):
        draw_vertical_gradient(self.screen, BG_TOP, BG_BOTTOM)
        draw_vignette_orbs(self.screen, self.time)

    def _login_screen(self, events, dt):
        mouse = pg.mouse.get_pos()
        for event in events:
            if self.user_box.handle_event(event) == "tab":
                self.user_box.active = False
                self.pass_box.active = True
            if self.pass_box.handle_event(event) == "tab":
                self.pass_box.active = False
                self.user_box.active = True
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self._try_login()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.login_btn.checkForInput(mouse):
                    self._try_login()
                elif self.register_btn.checkForInput(mouse):
                    self._try_register()

        self.user_box.tick(dt)
        self.pass_box.tick(dt)

        panel = pg.Rect(0, 0, 520, 560)
        panel.center = (WIDTH // 2, HEIGHT // 2 + 10)
        draw_panel(self.screen, panel)

        blit_text(self.screen, self.title_font, "TIC-TAC-TOE", GOLD, center=(WIDTH // 2, 130))
        blit_text(self.screen, self.tiny_body, "Distributed computing  ·  sockets lab", MUTED, center=(WIDTH // 2, 172))

        blit_text(self.screen, self.tiny_body, "Username", MUTED, topleft=(panel.x + 80, 252))
        blit_text(self.screen, self.tiny_body, "Password", MUTED, topleft=(panel.x + 80, 334))
        self.user_box.draw(self.screen)
        self.pass_box.draw(self.screen)
        self.login_btn.update(self.screen, mouse)
        self.register_btn.update(self.screen, mouse)

        badge = "SERVER ONLINE" if self.server_online else "SERVER OFFLINE"
        badge_color = OK if self.server_online else MUTED
        blit_text(self.screen, self.small_font, badge, badge_color, center=(WIDTH // 2, 575))
        blit_text(
            self.screen,
            self.tiny_body,
            "Demo login:  demo  /  demo123",
            MUTED,
            center=(WIDTH // 2, 602),
        )
        if self.status_message:
            color = OK if self.status_ok else DANGER
            blit_text(self.screen, self.tiny_body, self.status_message, color, center=(WIDTH // 2, 630))

    def _try_login(self):
        name = self.user_box.value().strip()
        password = self.pass_box.value()
        if name in {"", "username", "Name"} or not password:
            self.status_ok = False
            self.status_message = "Enter a username and password."
            return
        if not users.authenticate(name, password):
            self.status_ok = False
            self.status_message = "Unknown user or wrong password."
            return

        remote_note = ""
        if self.server_online:
            ok, reply = auth_client.authenticate_remote(name, password)
            remote_note = "  ·  " + (reply if ok else "playing locally")
        self.username = name
        self.status_ok = True
        self.status_message = ""
        self.state = "menu"
        pg.display.set_caption(f"Tic-Tac-Toe  —  {name}{remote_note}")

    def _try_register(self):
        name = self.user_box.value().strip()
        password = self.pass_box.value()
        err = users.register(name, password)
        if err:
            self.status_ok = False
            self.status_message = err
            return
        self.status_ok = True
        self.status_message = "Account created. You can log in now."

    def _menu_screen(self, events):
        mouse = pg.mouse.get_pos()
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_btn.checkForInput(mouse):
                    self._start_match()
                elif self.help_btn.checkForInput(mouse):
                    self.state = "help"
                elif self.quit_btn.checkForInput(mouse):
                    self._quit()
                elif self.logout_btn.checkForInput(mouse):
                    self.username = None
                    self.pass_box.text = ""
                    self.state = "login"
                    self.status_message = ""

        blit_text(self.screen, self.title_font, "MAIN MENU", GOLD, center=(WIDTH // 2, 120))
        who = self.username or "player"
        blit_text(self.screen, self.body_font, f"Welcome, {who}", CREAM, center=(WIDTH // 2, 175))
        blit_text(
            self.screen,
            self.body_font,
            f"Scoreboard   X {self.scores[PLAYER_X]}   —   O {self.scores[PLAYER_O]}",
            CREAM,
            center=(WIDTH // 2, 215),
        )
        self.play_btn.update(self.screen, mouse)
        self.help_btn.update(self.screen, mouse)
        self.quit_btn.update(self.screen, mouse)
        self.logout_btn.update(self.screen, mouse)

    def _help_screen(self, events):
        mouse = pg.mouse.get_pos()
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.help_back_btn.checkForInput(mouse):
                    self.state = "menu"

        panel = pg.Rect(0, 0, 720, 540)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        draw_panel(self.screen, panel)
        blit_text(self.screen, self.heading_font, "HOW TO PLAY", GOLD, center=(WIDTH // 2, 130))

        lines = [
            "Two players share one computer — X always starts.",
            "Click an empty cell to place your mark.",
            "Make three in a row to win: row, column, or diagonal.",
            "A full board with no winner is a tie.",
            "Restart begins a new round. Menu returns you home.",
            "Accounts live in data/users.txt. If the C server is up",
            "on port 8080, login is also checked over TCP sockets.",
        ]
        y = 190
        for line in lines:
            for wrapped in wrap_text(self.body_font, line, 600):
                blit_text(self.screen, self.body_font, wrapped, CREAM, center=(WIDTH // 2, y))
                y += 32
            y += 8
        self.help_back_btn.update(self.screen, mouse)

    def _start_match(self):
        self.board.reset()
        self.round_scored = False
        self.ignore_clicks_until_up = True
        self.state = "play"

    def _play_screen(self, events):
        mouse = pg.mouse.get_pos()
        if self.ignore_clicks_until_up and not pg.mouse.get_pressed()[0]:
            self.ignore_clicks_until_up = False

        self.hover_index = self._cell_at(*mouse)
        if self.board.is_over:
            self._finish_round_if_needed()

        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self._finish_round_if_needed()
                    self.board.reset()
                    self.round_scored = False
                elif event.key == pg.K_RETURN:
                    self._finish_round_if_needed()
                    self.state = "menu"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.restart_btn.checkForInput(mouse):
                    self._finish_round_if_needed()
                    self.board.reset()
                    self.round_scored = False
                elif self.menu_btn.checkForInput(mouse):
                    self._finish_round_if_needed()
                    self.state = "menu"
                elif not self.ignore_clicks_until_up:
                    index = self._cell_at(*event.pos)
                    if index is not None:
                        self.board.move(index)

        self._draw_hud()
        self._draw_board()
        self.restart_btn.update(self.screen, mouse)
        self.menu_btn.update(self.screen, mouse)

        if self.board.winner:
            pg.display.set_caption(f'Player "{self.board.winner}" wins!')
        elif self.board.is_tie:
            pg.display.set_caption("Game tied")
        else:
            pg.display.set_caption(f'Player "{self.board.turn}" to move')

    def _finish_round_if_needed(self):
        if self.round_scored:
            return
        if self.board.winner:
            self.scores[self.board.winner] += 1
            self.round_scored = True

    def _draw_hud(self):
        blit_text(self.screen, self.heading_font, "TIC-TAC-TOE", GOLD, center=(WIDTH // 2, 48))
        if self.board.winner:
            msg = f'Player {self.board.winner} wins'
            color = CYAN if self.board.winner == PLAYER_X else PINK
        elif self.board.is_tie:
            msg = "It's a tie"
            color = GOLD
        else:
            msg = f"Player {self.board.turn} to move"
            color = CYAN if self.board.turn == PLAYER_X else PINK
        blit_text(self.screen, self.ui_font, msg, color, center=(WIDTH // 2, 96))
        blit_text(
            self.screen,
            self.body_font,
            f"X  {self.scores[PLAYER_X]}     O  {self.scores[PLAYER_O]}",
            CREAM,
            center=(WIDTH // 2, 128),
        )

    def _cell_rect(self, index):
        row, col = divmod(index, 3)
        x = BOARD_ORIGIN[0] + col * (CELL_SIZE + CELL_GAP)
        y = BOARD_ORIGIN[1] + row * (CELL_SIZE + CELL_GAP)
        return pg.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def _cell_at(self, x, y):
        for index in range(9):
            if self._cell_rect(index).collidepoint(x, y):
                return index
        return None

    def _draw_board(self):
        board_rect = pg.Rect(
            BOARD_ORIGIN[0] - 18,
            BOARD_ORIGIN[1] - 18,
            BOARD_PIXELS + 36,
            BOARD_PIXELS + 36,
        )
        draw_panel(self.screen, board_rect, radius=28)

        for index, mark in enumerate(self.board.cells):
            rect = self._cell_rect(index)
            color = CELL_HOVER if index == self.hover_index and mark is EMPTY and not self.board.is_over else CELL
            if self.board.winning_line and index in self.board.winning_line:
                color = (26, 72, 88) if self.board.winner == PLAYER_X else (82, 28, 52)
            rounded_rect(self.screen, color, rect, radius=18)
            rounded_rect(self.screen, (70, 60, 120), rect, radius=18, width=1)
            if mark == PLAYER_X:
                self._draw_x(rect)
            elif mark == PLAYER_O:
                self._draw_o(rect)

        if self.board.winning_line:
            start = self._cell_rect(self.board.winning_line[0]).center
            end = self._cell_rect(self.board.winning_line[2]).center
            color = CYAN if self.board.winner == PLAYER_X else PINK
            pg.draw.line(self.screen, color, start, end, 12)
            pg.draw.line(self.screen, (255, 255, 230), start, end, 3)

    def _draw_x(self, rect):
        pad = 32
        a = (rect.left + pad, rect.top + pad)
        b = (rect.right - pad, rect.bottom - pad)
        c = (rect.right - pad, rect.top + pad)
        d = (rect.left + pad, rect.bottom - pad)
        pg.draw.line(self.screen, CYAN, a, b, 10)
        pg.draw.line(self.screen, CYAN, c, d, 10)
        pg.draw.circle(self.screen, CYAN, a, 5)
        pg.draw.circle(self.screen, CYAN, b, 5)
        pg.draw.circle(self.screen, CYAN, c, 5)
        pg.draw.circle(self.screen, CYAN, d, 5)

    def _draw_o(self, rect):
        pg.draw.circle(self.screen, PINK, rect.center, rect.w // 2 - 28, 10)
        pg.draw.circle(self.screen, (255, 180, 200), rect.center, rect.w // 2 - 28, 2)

    def render_preview(self, state: str, path: Path, extra=None):
        """Draw one screen to disk without opening a window manager."""
        self.state = state
        extra = extra or {}
        if "username" in extra:
            self.username = extra["username"]
        if extra.get("board"):
            self.board = extra["board"]
        self._draw_backdrop()
        if state == "login":
            self._login_screen([], 0)
        elif state == "menu":
            self._menu_screen([])
        elif state == "help":
            self._help_screen([])
        elif state == "play":
            self._play_screen([])
        pg.image.save(self.screen, str(path))

    def _quit(self):
        pg.quit()
        sys.exit()


def save_previews(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    game = Game()
    game.render_preview("login", out_dir / "login.png")
    game.username = "demo"
    game.render_preview("menu", out_dir / "menu.png")
    game.render_preview("help", out_dir / "help.png")

    mid = Board()
    for index in (0, 2, 4, 6):
        mid.move(index)
    game.board = mid
    game.render_preview("play", out_dir / "board.png")

    won = Board()
    for index in (0, 3, 1, 4, 2):
        won.move(index)
    game.board = won
    game.render_preview("play", out_dir / "win.png")
    print(f"Wrote previews to {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        target = Path(sys.argv[2]) if len(sys.argv) > 2 else CLIENT_DIR.parent / "docs"
        save_previews(target)
    else:
        Game().run()
