import pygame as pg
import sys
from random import randint

WINDOW_SIZE = 500
CELL_SIZE = WINDOW_SIZE // 3

INF = float('inf')
vec2 = pg.math.Vector2

CELL_CENTER = vec2(CELL_SIZE / 2)

class TicTacToe:
    def __init__(self, game):
        self.game = game
        self.fieldImage = self.getScaledImage(path = './resources/table.jpg', res = [WINDOW_SIZE] * 2)
        self.oImage = self.getScaledImage(path = './resources/o.png', res = [CELL_SIZE] * 2)
        self.xImage = self.getScaledImage(path = './resources/x.png', res = [CELL_SIZE] * 2)

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
        self.printCaption()
        self.draw()
        self.runGameProcesss()

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


    def run(self):
        while True:
            self.tictactoe.run()
            self.checkEvents()
            pg.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()