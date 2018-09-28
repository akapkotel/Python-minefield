# -*- coding: utf-8 -*-

import time
import random as r
from Tkinter import *
from PIL import Image, ImageTk
from functools import partial

class Minefield(object):
    """
    This class creates and works with in-game logic.
    """

    class Tile(object):
        """
        This class produces virtual tile-objects with info about mines, flags etc.
        """
        def __init__(self, number, row, column):
            """
            Constructor for one minefield-tile.
            :param number: int, number of current tile
            :param row: int, row of current tile on the minefield
            :param column: int, column of current tile on the minefield
            """
            self.number = number
            self.row = row
            self.column = column
            self.revealed = False
            self.mine = False
            self.flag = False
            self.questionmark = False
            self.surroundingMines = 0
            self.tilesToReveal = []

        def __repr__(self):
            return 'Tile_'+str(self.number)+'(row:'+str(self.row)+', column:'+str(self.column)+')'

    # important variable! You need to store tile's amount to give new tile correct number!
    tilesCount = 0

    def __init__(self, size, mineProbability):
        """
        Constructor of the whole minefield.
        :param size: int, amount of rows and columns for the minefield
        :param mineProbability: int, percentage probability that tile contains mine
        """
        self.size = size
        self.tiles = {}
        for i in range(self.size):
            for y in range(self.size):
                self.tiles[Minefield.tilesCount] = self.Tile(Minefield.tilesCount, i, y)
                Minefield.tilesCount+=1

        # temporary list, only required by checkNeighbours method:
        self.tilesList = zip(self.tiles.keys(), self.tiles.values())

        # here are the mines planted into the previously created tiles
        for tile in self.tiles:
            if r.randint(0, 100) <= mineProbability:
                self.tiles[tile].mine = True
                mineProbability -= 2
            else:
                mineProbability += 1
        # we check if there are mines in surrounding tiles to display correct number when non-mine tile is revealed
        for tile in self.tiles:
            self.tiles[tile].surroundingMines = self.checkNeighbours(tile)
        # we no longer need this temporary list:
        del self.tilesList

    def checkNeighbours(self, id):
        """
        This method checks surrounding tiles on-by-one if they are mined.
        :param id: int, current tile number
        :return: int, number of surrounding tiles containing mines
        """

        surroundingMines = 0
        tilesToCheck = []
        row = self.tiles[id].row
        column = self.tiles[id].column

        if row == 0:
            tilesToCheck.append((row + 1, column))
            if column == 0:
                tilesToCheck.append((row + 1, column + 1))
                tilesToCheck.append((row, column + 1))
            elif column < self.size-1:
                tilesToCheck.append((row, column - 1))
                tilesToCheck.append((row + 1, column - 1))
                tilesToCheck.append((row + 1, column + 1))
                tilesToCheck.append((row, column + 1))
            else:
                tilesToCheck.append((row, column - 1))
                tilesToCheck.append((row + 1, column - 1))
        elif row < self.size-1:
            tilesToCheck.append((row + 1, column))
            tilesToCheck.append((row - 1, column))
            if column == 0:
                tilesToCheck.append((row + 1, column + 1))
                tilesToCheck.append((row, column + 1))
                tilesToCheck.append((row - 1, column + 1))
            elif column < self.size-1:
                tilesToCheck.append((row + 1, column + 1))
                tilesToCheck.append((row, column + 1))
                tilesToCheck.append((row - 1, column + 1))
                tilesToCheck.append((row - 1, column - 1))
                tilesToCheck.append((row, column - 1))
                tilesToCheck.append((row + 1, column - 1))
            else:
                tilesToCheck.append((row - 1, column - 1))
                tilesToCheck.append((row, column - 1))
                tilesToCheck.append((row + 1, column - 1))
        else:
            tilesToCheck.append((row - 1, column))
            if column == 0:
                tilesToCheck.append((row - 1, column + 1))
                tilesToCheck.append((row, column + 1))
            elif column < self.size-1:
                tilesToCheck.append((row - 1, column + 1))
                tilesToCheck.append((row, column + 1))
                tilesToCheck.append((row - 1, column - 1))
                tilesToCheck.append((row, column - 1))
            else:
                tilesToCheck.append((row - 1, column - 1))
                tilesToCheck.append((row, column - 1))

        for pair in tilesToCheck:
            for tile in self.tilesList[pair[0]*self.size:(pair[0]*self.size)+pair[1]+1]:
                if tile[1].row == pair[0]:
                    if  tile[1].column == pair[1]:
                        if tile[1].mine:
                            surroundingMines += 1
                        else:
                            # if tile does not contain mine, we add it to the list of tiles revealed after click on the tile
                            self.tiles[id].tilesToReveal.append(tile[1].number)
                else:
                    continue
        return surroundingMines

    def putFlag(self, id, arg):
        """
        This method is called when player right-clicks on a tile. It changes a .flag or .questionmark property of a tile.
        :param id: int, tile's number
        :param arg: required by partial(), ignore it.
        """
        if not self.tiles[id].revealed:
            if self.tiles[id].flag:
                self.tiles[id].flag = False
                self.tiles[id].questionmark = True
                game.redrawButton(id, questionmark=self.tiles[id].questionmark)
            else:
                if self.tiles[id].questionmark:
                    self.tiles[id].questionmark = False
                    game.redrawButton(id, questionmark=self.tiles[id].questionmark)
                else:
                    self.tiles[id].flag = True
                    game.redrawButton(id, flag=self.tiles[id].flag)

    def revealTile(self, id):
        """
        This method is called when polayer left-clicks on a tile. It checks if the tile contains mine or not and then it
        reveals tile to the player calling game.redrawButton().
        :param id: int, clicked tile's number
        """
        if self.tiles[id].revealed:
            if not self.tiles[id].mine:
                return
            pass
        else:
            self.tiles[id].revealed = True
        game.redrawButton(id, mine=self.tiles[id].mine)


class Game(object):
    """
    This class contains whole GUI - visual side of game using Tkinter module.
    """

    def __init__(self, master):
        self.mainframe = master
        self.mainframe.title("Minefield")
        self.images = {}
        self.tileButtons = []
        self.inGame = False
        self.killTime = False
        self.gameTime = 0
        self.gameSize = 10
        self.gameDifficulty = 10

        # Menu:
        self.menubar = Menu(root)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New game", command=lambda: self.newGame(self.inGame))
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Options", command=self.options)
        self.menubar.add_cascade(label="Menu", menu=self.filemenu)
        # display the menu
        root.config(menu=self.menubar)

        self.topframe = Frame(self.mainframe)
        self.topframe.pack(side=TOP, expand=YES, fill=BOTH)

        self.pointsframe = LabelFrame(self.topframe, text="Points:")
        self.pointsframe.pack(side=LEFT)
        self.pointsvalue = Label(self.pointsframe, text="-", relief=SUNKEN, bg="white", width=3)
        self.pointsvalue.pack(side=RIGHT)
        self.faceframe = Frame(self.topframe)
        self.faceframe.pack(side=LEFT, fill=BOTH, expand=YES)
        self.facebutton = Button(self.faceframe, image=self.show_image('face'), command=lambda: self.newGame(self.inGame))
        self.facebutton.pack()
        self.timeframe = LabelFrame(self.topframe, text="Time:")
        self.timeframe.pack(side=RIGHT)
        self.timelabel = Label(self.timeframe, text="", relief=SUNKEN, bg="white", width=4)
        self.timelabel.pack()

        self.boardframe = Frame(self.mainframe)
        self.boardframe.pack(side=TOP, fill=BOTH, expand=YES)
        self.newGame()

    def newGame(self, inGame=None):
        """
        This method starts a new game: creates a minefield and draws a board.
        :param inGame: boolean, if there is a game already started
        """
        global minefield
        if inGame:
            del minefield
            Minefield.tilesCount = 0
            self.tileButtons = []
            self.pointsvalue.configure(text='-')
            self.facebutton.configure(image=self.show_image('face'))
        self.inGame = True
        self.killTime = False
        self.without = []
        minefield = Minefield(self.gameSize, self.gameDifficulty)
        self.drawButtons()
        self.gameTime = 0
        self.update_time()

    def options(self):
        """
        This method creates and displays game-options window.
        """
        self.optionswindow = Toplevel(self.mainframe)
        self.optionswindow.title('Game options')
        self.sizelabel = LabelFrame(self.optionswindow, text='Minefield size:')
        self.sizelabel.pack(side=TOP, fill=BOTH, expand=YES)
        self.sizescale = Scale(self.sizelabel, from_=8, to=30, orient=HORIZONTAL, sliderlength=20, showvalue=0,
                               length=200, command=self.changeGameSize)
        self.sizescale.set(self.gameSize)
        self.sizescale.pack(side=LEFT)
        self.sizevalue = Label(self.sizelabel, text=self.sizescale.get(), relief=SUNKEN, bg="white", width=3)
        self.sizevalue.pack(side=LEFT)

        self.probabilitylabel = LabelFrame(self.optionswindow, text='Probability for mine:')
        self.probabilitylabel.pack(side=TOP, fill=BOTH, expand=YES)
        self.probabilityscale = Scale(self.probabilitylabel, from_=1, to=100, orient=HORIZONTAL, sliderlength=20,
                                      showvalue=0, length=200, command=self.changeGameDifficulty)
        self.probabilityscale.set(self.gameDifficulty)
        self.probabilityscale.pack(side=LEFT)
        self.probabilityvalue = Label(self.probabilitylabel, text=self.probabilityscale.get(), relief=SUNKEN, bg="white", width=3)
        self.probabilityvalue.pack(side=LEFT)

    def changeGameSize(self, event):
        self.gameSize = self.sizescale.get()
        self.sizevalue.configure(text= self.sizescale.get())

    def changeGameDifficulty(self, event):
        self.gameDifficulty = self.probabilityscale.get()
        self.probabilityvalue.configure(text=self.probabilityscale.get())

    def drawButtons(self):
        """
        This method draws all the tiles at the start of game.
        """
        for tile in minefield.tiles:
            self.tileButtons.append(Button(self.boardframe, name=str(tile), width=33, height=33, borderwidth=1,
            relief=RAISED, image=self.show_image('tile'), command=partial(minefield.revealTile, tile)))
            self.tileButtons[-1].bind("<Button-3>", partial(minefield.putFlag, tile))
            self.tileButtons[-1].grid(row= minefield.tiles[tile].row+1, column = minefield.tiles[tile].column+1)

    def redrawButton(self, id, mine=None, flag=None, questionmark=None):
        """
        This method redraws a tile, when it is clicked by player. It displays proper image: a mine, flag, question mark
        or number of mines in neighbourhood.
        :param id: int, number of clicked tile
        :param mine: boolean, if there is a mine in the tile
        :param flag: boolean, if there is a flag on the tile
        :param questionmark: boolean, if there is a question mark on the tile
        """
        if mine != None:
            self.tileButtons[id].configure(relief=SUNKEN)
            if mine:
                self.facebutton.configure(image=self.show_image('dead'))
                self.tileButtons[id].configure(image=self.show_image('kaboom'))
                self.kaboom()
                return
            else:
                self.tileButtons[id].configure(image=self.show_image(str(minefield.tiles[id].surroundingMines)))
                self.redrawNeighbours(id)
        if flag != None:
            if flag:
                self.tileButtons[id].configure(image=self.show_image('flag'))
            else:
                self.tileButtons[id].configure(image=self.show_image('tile'))
        if questionmark != None:
            if questionmark:
                self.tileButtons[id].configure(image=self.show_image('questionmark'))
            else:
                self.tileButtons[id].configure(image=self.show_image('tile'))
        # each time we check if player cleared whole minefield
        self.checkIfWon()

    def redrawNeighbours(self, id):
        """
        When player clicks on the tile, we reveal all tiles without mines around.
        :param id: int, clicked tile number
        """
        revealMore = []
        self.without.append(id)
        for tile in minefield.tiles[id].tilesToReveal:
            this = minefield.tiles[tile]
            if not (this.revealed or this.number in self.without):
                self.tileButtons[tile].configure(image=self.show_image(str(this.surroundingMines)))
                self.tileButtons[tile].configure(relief=SUNKEN)
                this.revealed = True
                if this.surroundingMines == 0:
                    revealMore.append(tile)
            else:
                continue
        for tile in revealMore:
            self.redrawNeighbours(tile)

    def kaboom(self):
        """
        This method is called when player clicks on a mine, or when game ended - it reveals whole minefield.
        """
        self.killTime = True
        points = 0
        for tile in minefield.tiles:
            if not minefield.tiles[tile].revealed:
                if minefield.tiles[tile].flag:
                    if minefield.tiles[tile].mine:
                        points += 1
                    else:
                        self.tileButtons[tile].configure(image=self.show_image('no_mine'))
                        points -= 1
                else:
                    if minefield.tiles[tile].mine:
                        self.tileButtons[tile].configure(image=self.show_image('mine'))
                        points -= 2
                    else:
                        self.tileButtons[tile].configure(image=self.show_image(str(minefield.tiles[tile].surroundingMines)))
            self.tileButtons[tile].configure(relief=SUNKEN)
        self.pointsvalue.configure(text=points)

    def checkIfWon(self):
        """
        This method checks if player revealed all tiles. If so, game ends.
        """
        for tile in minefield.tiles:
            if minefield.tiles[tile].revealed or minefield.tiles[tile].flag or minefield.tiles[tile].questionmark:
                continue
            else:
                return
        self.facebutton.configure(image=self.show_image('happy'))
        self.kaboom()

    def show_image(self, image):
        """
        Displays proper image. Image must exist in the same directory and it's format must be .jpg. It populates dict
        'images' with ImageTk objects generated here. They are ready to use.
        :param image: string name of image to show
        :return: ImageTk object to display
        """
        if image not in self.images:
            self.images[image] = ImageTk.PhotoImage(Image.open(image+".jpg"))
        return self.images[image]

    def update_time(self):
        if self.inGame and not self.killTime:
            if self.gameTime < 60:
                if self.gameTime%60 < 10:
                    time = '0:0'+str(self.gameTime)
                else:
                    time = '0:'+str(self.gameTime)
            else:
                if self.gameTime%60 < 10:
                    time = str(self.gameTime/60)+':0'+str(self.gameTime%60)
                else:
                    time = str(self.gameTime/60)+':'+str(self.gameTime%60)
            self.timelabel.configure(text=time)
            self.gameTime += 1
            root.after(1000, self.update_time)

if __name__ == "__main__":
    root = Tk()
    game = Game(root)
    root.mainloop()
