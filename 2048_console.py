import random, os
import pygame, sys

class Game_2048:
    # inner Tile class so everything is contained
    class Tile:
        def __init__(self, number):
            self.number = number
            self.bMerged = False

    def __init__(self):
        pygame.init()

        # vars for pygame
        self.size = width, height = (1, 1)
        self.COLOR_BLACK = (0, 0, 0)
        self.clock = pygame.time.Clock()
        
        self.screen = pygame.display.set_mode(self.size) # initalising pygame window

        # 2048 table variables
        self.tableWidth = 4
        self.gameTable = [self.Tile(0) for i in range(self.tableWidth ** 2)]
        
        # variables to format the console output and make it pretty
        self.columnWidth = 1 # so we can format the output
        self.numberColours = {
            0 : "\033[0m",
            2 : "\033[90m",
            4 : "\033[31m",
            8 : "\033[32m",
            16 : "\033[33m",
            32 : "\033[34m",
            64 : "\033[35m",
            128 : "\033[91m",
            256 : "\033[092m",
            512 : "\033[093m",
            1024 : "\033[94m",
            2048 : "\033[95m",
        }

    # since the table is a one-dim array, this returns the index 
    # based on a row and column
    def crd(self, row, col):
        return row * self.tableWidth + col

    # the game is over when there are no two values that are the same
    # next to each other horizontally or vertically
    # and no free spaces remain
    def gameOver(self):
        for i in range(self.tableWidth):
            for j in range(self.tableWidth):
                # as long as there are zeroes, we can play
                if self.gameTable[self.crd(i, j)].number == 0:
                    return False
                # we check to the right
                if j < self.tableWidth - 1:
                    if(self.gameTable[self.crd(i, j)].number == self.gameTable[self.crd(i, j + 1)].number):
                        return False
                # we check below
                if i < self.tableWidth - 1:
                    if(self.gameTable[self.crd(i, j)].number == self.gameTable[self.crd(i + 1, j)].number):
                        return False

        return True

    # printing it as a square on console
    def printTable(self):
        for i in range(self.tableWidth):
            line = ""
            
            for j in range(self.tableWidth):
                # formatting it with colour and as many spaces after the number as the largest
                # existing number in the table would need
                line += self.numberColours[self.gameTable[self.crd(i, j)].number % 2048] + \
                    str(self.gameTable[self.crd(i, j)].number) + \
                    (self.columnWidth - len(str(self.gameTable[self.crd(i, j)].number)) + 1) * " " + \
                    self.numberColours[0]

            print(line)

        print("")

    # getting the index of a free square where we can spawn a number
    def spaceToSpawn(self):
        freePlaces = []

        for i in range(self.tableWidth ** 2):
            if self.gameTable[i].number == 0:
                freePlaces.append(i);

        return freePlaces[random.randrange(len(freePlaces))]

    # getting a value/number to spawn
    def numero(self):
        return 2 if (random.randrange(1000) % 9) else 4

    # main gameloop
    def gameLoop(self):
        self.gameTable[self.spaceToSpawn()].number = self.numero()

        os.system("cls" if os.name == "nt" else "clear")
        self.printTable()

        while(not self.gameOver()):
            self.clock.tick(60) # 60 fps

            # every cell is mergeable at the beginning of the turn
            for i in range(self.tableWidth):
                for j in range(self.tableWidth):
                    self.gameTable[self.crd(i, j)].bMerged = False

            # important: just because we want to move in a direction, 
            # it doesn't mean that we CAN - this is set when we did move
            bTilesMoved = False

            bLeft = False
            bUp = False
            bRight = False
            bDown = False

            # keyboard movement
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit();
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        bLeft = True
                    elif event.key == pygame.K_UP:
                        bUp = True
                    elif event.key == pygame.K_RIGHT:
                        bRight = True
                    elif event.key == pygame.K_DOWN:
                        bDown = True

            if bLeft:
                for i in range(self.tableWidth):
                    for j in range(1, self.tableWidth):
                        # we only move real numbers, zero, you sucker
                        if self.gameTable[self.crd(i, j)].number > 0:
                            col = j
                            # while there's free space to the left of the tile, we move it to the left
                            while col > 0 and self.gameTable[self.crd(i, col - 1)].number == 0:
                                self.gameTable[self.crd(i, col - 1)].number = self.gameTable[self.crd(i, col)].number
                                self.gameTable[self.crd(i, col)].number = 0
                                col -= 1
                                bTilesMoved = True

                            # if the tile to the left of it has the same number and hasn't yet merged with another tile, we FUSE THEM
                            if col > 0 and self.gameTable[self.crd(i, col)].number == self.gameTable[self.crd(i, col - 1)].number \
                                and not self.gameTable[self.crd(i, col - 1)].bMerged:
                                
                                self.gameTable[self.crd(i, col - 1)].number *= 2
                                self.gameTable[self.crd(i, col - 1)].bMerged = True
                                self.gameTable[self.crd(i, col)].number = 0
                                bTilesMoved = True
                
            if bUp:
                for i in range(1, self.tableWidth):
                    for j in range(self.tableWidth):
                        # we only move real numbers, zero, you sucker
                        if self.gameTable[self.crd(i, j)].number > 0:
                            row = i
                            # while there's free space above the tile, we move it up
                            while row > 0 and self.gameTable[self.crd(row - 1, j)].number == 0:
                                self.gameTable[self.crd(row - 1, j)].number = self.gameTable[self.crd(row, j)].number
                                self.gameTable[self.crd(row, j)].number = 0
                                row -= 1
                                bTilesMoved = True

                            # if the tile above it has the same number and hasn't yet merged with another tile, we FUSE THEM
                            if row > 0 and self.gameTable[self.crd(row, j)].number == self.gameTable[self.crd(row - 1, j)].number \
                                and not self.gameTable[self.crd(row - 1, j)].bMerged:
                                
                                self.gameTable[self.crd(row - 1, j)].number *= 2
                                self.gameTable[self.crd(row - 1, j)].bMerged = True
                                self.gameTable[self.crd(row, j)].number = 0
                                bTilesMoved = True
            
            if bRight:
                reverseCols = [i for i in range(self.tableWidth - 1)]
                reverseCols.reverse()
                # we have to look from the last column left (i.e in reverse order) for correct tile movement
                for i in range(self.tableWidth):
                    for j in reverseCols:
                        # we only move real numbers, zero, you sucker
                        if self.gameTable[self.crd(i, j)].number > 0:
                            col = j
                            # while there's free space to the right of the tile, we move it to the right
                            while col < self.tableWidth - 1 and self.gameTable[self.crd(i, col + 1)].number == 0:
                                self.gameTable[self.crd(i, col + 1)].number = self.gameTable[self.crd(i, col)].number
                                self.gameTable[self.crd(i, col)].number = 0
                                col += 1
                                bTilesMoved = True

                            # if the tile to the right of it has the same number and hasn't yet merged with another tile, we FUSE THEM
                            if col < self.tableWidth - 1 and self.gameTable[self.crd(i, col)].number == self.gameTable[self.crd(i, col + 1)].number \
                                and not self.gameTable[self.crd(i, col + 1)].bMerged:
                                
                                self.gameTable[self.crd(i, col + 1)].number *= 2
                                self.gameTable[self.crd(i, col + 1)].bMerged = True
                                self.gameTable[self.crd(i, col)].number = 0
                                bTilesMoved = True
                
            if bDown:
                reverseRows = [i for i in range(self.tableWidth - 1)]
                reverseRows.reverse()
                # we have to look from the last row up (i.e in reverse order) for correct tile movement
                for i in reverseRows:
                    for j in range(self.tableWidth):
                        # we only move real numbers, zero, you sucker
                        if self.gameTable[self.crd(i, j)].number > 0:
                            row = i
                            # while there's free space below the tile, we move it down
                            while row < self.tableWidth - 1 and self.gameTable[self.crd(row + 1, j)].number == 0:
                                self.gameTable[self.crd(row + 1, j)].number = self.gameTable[self.crd(row, j)].number
                                self.gameTable[self.crd(row, j)].number = 0
                                row += 1
                                bTilesMoved = True

                            # if the tile below it has the same number and hasn't yet merged with another tile, we FUSE THEM
                            if row < self.tableWidth - 1 and self.gameTable[self.crd(row, j)].number == self.gameTable[self.crd(row + 1, j)].number \
                                and not self.gameTable[self.crd(row + 1, j)].bMerged:
                                
                                self.gameTable[self.crd(row + 1, j)].number *= 2
                                self.gameTable[self.crd(row + 1, j)].bMerged = True
                                self.gameTable[self.crd(row, j)].number = 0
                                bTilesMoved = True

            if bTilesMoved:
                # we can only spawn a new number if at least a tile was moved
                freeSpace = self.spaceToSpawn()
                numberToSpawn = self.numero()
                self.gameTable[freeSpace].number = numberToSpawn

                # we set the number of spaces necessary after each column for
                # them to be equidistant from each other
                for i in range(self.tableWidth):
                    for j in range(self.tableWidth):
                        if self.columnWidth < len(str(self.gameTable[self.crd(i, j)].number)):
                            self.columnWidth = len(str(self.gameTable[self.crd(i, j)].number))

                os.system("cls" if os.name == "nt" else "clear")
                self.printTable()
                print("{0} was spawned at {1} {2}".format(numberToSpawn, int(freeSpace / self.tableWidth) + 1, (freeSpace % self.tableWidth) + 1))

            self.screen.fill(self.COLOR_BLACK)
            pygame.display.flip();

        print("game over")

newgame = Game_2048()
newgame.gameLoop()
