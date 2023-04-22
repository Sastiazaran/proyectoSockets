import pygame as pg
import sys
from random import randint
from button import Button
import socket

"""
Proyecto sockets
Computo distribuido

Autores:
@Pablo Uscanga
@Sebastian Astiazaran
@Rolo boliche

"""

WINDOW_SIZE = 500
CELL_SIZE = WINDOW_SIZE // 3
BG = pg.image.load('./client/resources/Background.png')
INF = float('inf')
vec2 = pg.math.Vector2

CELL_CENTER = vec2(CELL_SIZE / 2)

#################################################################################################
#################################################################################################
#################################################################################################
#################################################################################################

class TicTacToe:
    def __init__(self, game):
        self.game = game
        self.fieldImage = self.getScaledImage(path = './client/resources/table.jpg', res = [WINDOW_SIZE] * 2)
        self.oImage = self.getScaledImage(path = './client/resources/o.png', res = [CELL_SIZE] * 2)
        self.xImage = self.getScaledImage(path = './client/resources/x.png', res = [CELL_SIZE] * 2)

        self.gameArray = [[INF, INF, INF],[INF, INF, INF],[INF, INF, INF]]
        self.player = randint(0, 1)

        self.lineIndicesArray = [[(0,0), (0,1), (0,2)],
                                    [(1,0), (1,1), (1,2)], 
                                    [(2,0), (2,1), (2,2)],
                                    [(0,0), (1,0), (2,0)], 
                                    [(0,1), (1,1), (2,1)], 
                                    [(0,2), (1,2), (2,2)],
                                    [(0,0), (1,1), (2,2)],
                                    [(0,2), (1,1), (2,0)]]
        
        self.winner = None
        self.gameSteps = 0
        self.font = pg.font.SysFont('Verdana', CELL_SIZE // 4, True)

    def checkWinner(self):
        for line_indices in self.lineIndicesArray:
            sumLine = sum([self.gameArray[i][j] for i, j in line_indices])
            if sumLine in {0, 3}:
                self.winner = 'XO'[sumLine == 0]
                self.winnerLine = [vec2(line_indices[0][::-1]) * CELL_SIZE + CELL_CENTER,
                                   vec2(line_indices[2][::-1]) * CELL_SIZE + CELL_CENTER]

    def runGameProcesss(self):
        currentCell = vec2(pg.mouse.get_pos()) // CELL_SIZE
        col, row = map(int, currentCell)
        leftClick = pg.mouse.get_pressed()[0]

        if leftClick and self.gameArray[row][col] == INF and not self.winner:
            self.gameArray[row][col] = self.player
            self.player = not self.player
            self.gameSteps += 1
            self.checkWinner()

    def drawObjects(self):
        for y, row in enumerate(self.gameArray):
            for x, obj in enumerate(row):
                if obj != INF:
                    self.game.screen.blit(self.xImage if obj else self.oImage, vec2(x, y) * CELL_SIZE)

    def drawWinner(self):
        if self.winner:
            pg.draw.line(self.game.screen, 'red', *self.winnerLine, CELL_SIZE // 8)
            label0 = self.font.render(f'Player "{self.winner}" wins!', True, 'white', 'black')
            self.game.screen.blit(label0, (WINDOW_SIZE // 2 - label0.get_width() // 2, WINDOW_SIZE // 4))
            

    def draw(self):
        self.game.screen.blit(self.fieldImage, (0,0))
        self.drawObjects()
        self.drawWinner()

    @staticmethod
    def getScaledImage(path, res):
        img = pg.image.load(path)
        return pg.transform.scale(img, res)
    
    def printCaption(self):
        pg.display.set_caption(f'Player "{"OX" [self.player]}" turn')
        if self.winner:
            pg.display.set_caption(f'Player " {self.winner}" wins! Press space to restart')
        elif self.gameSteps == 9:
            pg.display.set_caption(f'Game Tied! Press space to restart')
    
    def run(self):
        game.screen.fill("white")
        self.printCaption()
        self.draw()
        self.runGameProcesss()

#################################################################################################
#################################################################################################
#################################################################################################
#################################################################################################

class Game:

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode([WINDOW_SIZE] * 2)
        self.clock = pg.time.Clock()
        self.tictactoe = TicTacToe(self)

    def newGame(self):
        self.tictactoe = TicTacToe(self)

    def checkEvents(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.newGame()

    def get_font(size): # Returns Press-Start-2P in the desired size
        return pg.font.Font("./client/resources/font.ttf", size)
    
    def options(self):
        while True:
            OPTIONS_MOUSE_POS = pg.mouse.get_pos()

            game.screen.fill("white")

            OPTIONS_TEXT = Game.get_font(20).render("This is the OPTIONS WINDOW_SIZE.", True, "Black")
            OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(250, 100))
            game.screen.blit(OPTIONS_TEXT, OPTIONS_RECT)

            OPTIONS_BACK = Button(image=None, pos=(250, 170), 
                                text_input="BACK", font=Game.get_font(30), base_color="Black", hovering_color="Green")

            OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
            OPTIONS_BACK.update(game.screen)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                        Game.run(self)

            pg.display.update()

    def run(self):
        while True:
            game.screen.blit(BG, (0, 0))

            MENU_MOUSE_POS = pg.mouse.get_pos()

            MENU_TEXT = Game.get_font(50).render("MAIN MENU", True, "#b68f40")
            MENU_RECT = MENU_TEXT.get_rect(center=(250, 100))

            PLAY_BUTTON = Button(image=pg.image.load("./client/resources/PlayRect.png"), pos=(250, 170), 
                                text_input="PLAY", font=Game.get_font(40), base_color="#d7fcd4", hovering_color="White")
            OPTIONS_BUTTON = Button(image=pg.image.load("./client/resources/OptionsRect.png"), pos=(250, 240), 
                                text_input="HOW TO PLAY", font=Game.get_font(40), base_color="#d7fcd4", hovering_color="White")
            QUIT_BUTTON = Button(image=pg.image.load("./client/resources/QuitRect.png"), pos=(250, 310), 
                                text_input="QUIT", font=Game.get_font(40), base_color="#d7fcd4", hovering_color="White")

            game.screen.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(game.screen)
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.tictactoe.run()
                        self.checkEvents()
                        pg.display.update()
                        self.clock.tick(60)
                    if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        Game.options(self)
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pg.quit()
                        sys.exit()

            pg.display.update()

#################################################################################################
#################################################################################################
#################################################################################################
#################################################################################################

if __name__ == '__main__':
    game = Game()
    game.run()