import random, os
import sys

# thanks chatGPT
def getch():
    """Wait for a single keypress and return it as a string."""
    try:
        # Windows
        import msvcrt
        ch = msvcrt.getch()

        try:
            return ch.decode("utf-8") # convert bytes to str
        except UnicodeDecodeError:
            return ""
    except ImportError:
        # Unix/Linux/Mac
        import tty, termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch

# almost everything below this is the original though lol
# wonder if I'd do anything differently now
class Game_2048:
    # inner Tile class so everything is contained
    class Tile:
        def __init__(self, number):
            self.number = number
            self.bMerged = False

    def __init__(self):
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
    
    # evaluating whether we can still move or merge the number in our position
    # used for moving the tiles
    def evalPos(self, row, col, rowMod, colMod):
        return ((rowMod > 0 and row < self.tableWidth - 1) or (rowMod < 0 and row > 0) \
            or (colMod > 0 and col < self.tableWidth - 1) or (colMod < 0 and col > 0))
    
    # moving the tiles
    # rowMod and colMod can be 1, 0, -1
    # 1 means that we're moving in the positive direction of that axis (down, right)
    # -1 means that we're moving in the negative direction of that axis (up, left)
    # 0 means that we aren't moving on that axis
    # we add these modifiers to our positions when we move them
    # we can only move in the four cardinal directions, so one of them is always 0
    # our position on that axis doesn't get modified so we can merge the for loop
    # where we move our tiles 

    # rows and cols depend on the direction, e.g we don't have to check the first row
    # when we move tiles up, since those can't move anyway, and
    # we check for mergers with the tiles below them
    # their order also matters e.g when going down it's the last row we don't have to check
    # not the first one
    def moveTiles(self, rowMod, colMod, rows, cols):
        bTilesMoved = False
        
        for i in rows:
            for j in cols:
                # we only move real numbers, zero, you sucker
                if self.gameTable[self.crd(i, j)].number > 0:
                    row = i
                    col = j
                    
                    # only one of these cases is ever relevant, and COINCIDENTALLY
                    # that's the one we need
                    eval = self.evalPos(row, col, rowMod, colMod)
                    
                    # we move in the direction while there's free space
                    while eval and self.gameTable[self.crd(row + rowMod, col + colMod)].number == 0:
                        self.gameTable[self.crd(row + rowMod, col + colMod)].number = self.gameTable[self.crd(row, col)].number
                        self.gameTable[self.crd(row, col)].number = 0
                        row += rowMod
                        col += colMod
                        bTilesMoved = True
                        eval = self.evalPos(row, col, rowMod, colMod)
                    
                    eval = self.evalPos(row, col, rowMod, colMod)
                    
                    # if the tile next to us in the direction we're moving has the same value, they merge
                    if eval and self.gameTable[self.crd(row, col)].number == self.gameTable[self.crd(row + rowMod, col + colMod)].number \
                        and not self.gameTable[self.crd(row + rowMod, col + colMod)].bMerged:
                        
                        self.gameTable[self.crd(row + rowMod, col + colMod)].number *= 2
                        self.gameTable[self.crd(row + rowMod, col + colMod)].bMerged = True
                        self.gameTable[self.crd(row, col)].number = 0
                        bTilesMoved = True
        
        return bTilesMoved

    # main gameloop
    def gameLoop(self):
        self.gameTable[self.spaceToSpawn()].number = self.numero()
        # this is the list for rows, cols in reverse order for when we need it
        axis = [i for i in range(self.tableWidth - 1)]
        axis.reverse()
        
        os.system("cls" if os.name == "nt" else "clear")
        self.printTable()

        while(not self.gameOver()):
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

            cDir = getch()

            if cDir == "a":
                bLeft = True
            elif cDir == "w":
                bUp = True
            elif cDir == "d":
                bRight = True
            elif cDir == "s":
                bDown = True
            elif cDir == "q":
                sys.exit()
            
            # moving the tiles
            if bLeft:
                bTilesMoved = self.moveTiles(0, -1, [i for i in range(self.tableWidth)], [i for i in range(1, self.tableWidth)])
                
            if bUp:
                bTilesMoved = self.moveTiles(-1, 0, [i for i in range(1, self.tableWidth)], [i for i in range(self.tableWidth)])
            
            if bRight:
                bTilesMoved = self.moveTiles(0, 1, [i for i in range(self.tableWidth)], axis)
                
            if bDown:
                bTilesMoved = self.moveTiles(1, 0, axis, [i for i in range(self.tableWidth)])

            if bTilesMoved:
                # we can only spawn a new number if at least one tile was moved
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

        print("game over")
        
    def newGame(self):
        self.gameTable = [self.Tile(0) for i in range(self.tableWidth ** 2)]
        self.columnWidth = 1

        print("use wasd to move, q to quit. Press any key to start :)")
        getch()

        self.gameLoop()

newgame = Game_2048()

start = 1

while start == 1:
    newgame.newGame()
    print("play again? 1 for yes 0 for no")

    ch = getch()

    try:
        start = int(ch)
    except Exception:
        start = 0
