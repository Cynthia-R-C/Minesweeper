from tkinter import *
from tkinter import messagebox
import random

class Box(Button):
    '''A box in minesweeper'''

    def __init__(self, master,callback,*args, **kwarg):
        # set up button object
        super().__init__(master,*args, **kwarg)
        self.bomb = False
        self.flagged = False
        self.revealed = False
        self.bombnum = 0
        self.isclicked = False
        self.callback = callback
        self.config(command=self.clicked)
        self.config(bg='white')
        self.config(relief=RAISED)
        # set up flagging
        self.bind("<Button-3>", self.toggle_flag)

    def is_clicked(self):
        '''Detects if a box is clicked'''
        return self.isclicked

    def clicked(self):
        '''Calls necessary functions when box is clicked'''
        self.isclicked = True
        self.callback()
        self.master.has_won()

    def __str__(self):
        '''Prints a Box as a string (for testing)'''
        row,column = self.get_coords()
        if self.is_bomb():
            return 'bomb at ' + str(row) + ',' + str(column)
        elif self.is_flagged():
            return 'flagged at ' + str(row) + ',' + str(column)
        else:
            return 'normal at ' + str(row) + ',' + str(column)

    def get_coords(self):
        '''Returns the row and column of a Box'''
        info = self.grid_info()
        row = info['row']
        column = info['column']
        return row,column

    def is_revealed(self):
        '''Detects if a box is revealed'''
        return self.revealed

    def reveal(self):
        '''Simulates revealing a box and detects what kind of box is revealed'''
        self.config(relief=RAISED)
        if not self.is_flagged():
            self.revealed = True
            if self.is_bomb():
                self.config(bg='red')
                self.config(text='*')
                self.master.lose()
            else:
                self.config(bg='light gray')
                if self.bombnum == 0:
                    self.config(text='')
                else:
                    self.config(text=str(self.bombnum),fg=self.get_bombnum_col(self.bombnum))   # sets the color of the text
            self.revealed = True

    def set_bombnum(self, n):
        '''Allows the Board class to change the bombnum variable'''
        self.bombnum = n

    def get_bombnum_col(self, n):
        '''Returns the correct color for a certain bombnum'''
        colormap = ['','blue','darkgreen','red','purple','maroon','cyan','black','dim gray']
        return colormap[n]
      
    def is_bomb(self):
        '''Detects if the box is a bomb'''
        return self.bomb

    def is_flagged(self):
        '''Detects if the box is flagged'''
        return self.flagged

    def is_blank(self):
        '''Detects if the box is blank (there are no bombs adjacent to it)'''
        return self.bombnum == 0

    def toggle_bomb(self):
        '''Makes the box a bomb'''
        self.bomb = True

    def toggle_flag(self, event):
        '''Toggles flag on and off'''
        if self.master.numflagged < self.master.numbombs or self.is_flagged():
            if not self.revealed:
                if self.is_flagged():
                    self.flagged = False
                    self.config(text='')
                else:
                    self.flagged = True
                    self.config(text='*')
            self.master.update_numflagged()

    def unflag(self):
        '''Strictly turns flag off, no matter if the box is flagged or not'''
        self.flagged = False

    def num_bombs_adj(self, row, column, boxes, width, height):
        '''Return the number of bombs adjacent of a certain box'''
        n = 0

        # for horizontally adjacent bombs
        if column != 0:
            if boxes[row][column - 1].is_bomb():
                n += 1
        if column != width - 1:
            if boxes[row][column + 1].is_bomb():
                n += 1

        # for vertically adjacent bombs
        if row != 0:
            if boxes[row - 1][column].is_bomb():
                n += 1
        if row != height - 1:
            if boxes[row + 1][column].is_bomb():
                n += 1

        # for diagonally adjacent bombs
        if row != 0 and column != 0:      # top left
            if boxes[row-1][column - 1].is_bomb():
                n += 1
        if row != height - 1 and column != 0:     # bottom left
            if boxes[row + 1][column - 1].is_bomb():
                n += 1
        if row != 0 and column != width - 1:     # top right
            if boxes[row - 1][column + 1].is_bomb():
                n += 1
        if row != height - 1 and column != width - 1:     # bottom right
            if boxes[row + 1][column + 1].is_bomb():
                n += 1

        return n
        

class Board(Frame):
    '''A frame for the board of minesweeper'''

    def __init__(self, master, width, height, numbombs):
        # set up Frame object
        Frame.__init__(self,master)
        self.grid()
        # set up variables and boxes
        self.lost = False
        self.width = width
        self.height = height
        self.numbombs = numbombs
        self.numflagged = 0
        self.boxes = []
        self.currentrow = None
        self.currentcol = None
        for i in range(height):
            row = []
            for j in range(width):
                box = Box(self, self.when_clicked, text=' ', width=4, height=2)
                box.grid(row=i, column=j)
                row.append(box)
            self.boxes.append(row)
        # set up bombs
        self.bombLabel = Label(self,text=str(numbombs),font=('Arial',18))
        self.bombLabel.grid(row=self.height+1,column=round(self.width/2))
        bombs = []
        tot = self.width * self.height
        for n in range(numbombs):
            while True:
                loc = random.randint(0,tot-1)
                pos = self.get_row_column(loc)
                if pos not in bombs:
                    bombs.append(pos)
                    break
        for posn in bombs:
            row, column = posn
            self.boxes[row][column].toggle_bomb()
        # set up adjacent bomb numbers
        for n in range(tot):
            row, column = self.get_row_column(n)
            box = self.boxes[row][column]
            if not box.is_bomb():
                numbombsadj = box.num_bombs_adj(row, column, self.boxes, self.width, self.height)
                box.set_bombnum(numbombsadj)
            else:
                box.set_bombnum(100)

    # setting up number of flags
    def update_numflagged(self):
        '''Updates number of boxes flagged (for the label at the bottom of the screen)'''
        self.numflagged = sum(1 for row in self.boxes for box in row if box.is_flagged())
        self.bombLabel.config(text=str(self.numbombs-self.numflagged))

    # setting up auto reveal
    def when_clicked(self):
        '''finds the box that was clicked and runs auto_reveal() on it'''
        for n in range(self.width * self.height):
                row,column = self.get_row_column(n)
                box = self.boxes[row][column]
                if box.is_clicked():
                    self.currentrow = row
                    self.currentcol = column
                    self.auto_reveal()
                  
    # setting up losing the game
    def lose(self):
        '''Simulates losing the game'''
        if not self.lost:
            self.lost = True
            messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)
            for n in range(self.width * self.height):
                row,column = self.get_row_column(n)
                box = self.boxes[row][column]
                if box.is_bomb():
                    box.unflag()
                    box.reveal()

    # setting up winning the game
    def has_won(self):
        '''Detects whether the user has won the game or not'''
        notbombs = sum(1 for row in self.boxes for box in row if not box.is_bomb())
        notbombrevealed = sum(1 for row in self.boxes for box in row if not box.is_bomb() and box.is_revealed())
        if notbombs == notbombrevealed:
            self.win()

    def win(self):
        '''Simulates winning'''
        messagebox.showinfo('Minesweeper','Congratulations -- you won!',parent=self)
  

# NEW PROBLEM: All the boxes are revealing themselves ;-;. Why is auto-reveal being triggered and revealing the bombs when I didn't even click anything? Also sometimes flagging works and sometimes it doesn't. Attempting solution: use auto_reveal all the time, but if not blank then don't run the autoreveal parts, just run the reveal part in the auto reveal. Problem: the self.currentrow and self.currentcol isn't settint to the correct row and column. Has function get_coords() in Box class now that can return row and column of Box, but don't know how to incorporate it into auto_reveal()

# New problem: WHERE DO I PUT THE LOOP SO THAT THE PROGRAM CAN RUN??!!

# New problem: HOW DO I MAKE THE WINDOW DETECT WHEN I CLICK WHEN I CLICK A BUTTON? Idea: get rid of clicking the window and try to use a function in Box to trigger a function in Board


    def get_row_column(self, n):
        '''Returns row and column of a box when the box number is entered'''
        row = n//self.width
        column = n%self.width
        return row,column

    def auto_reveal(self):
        '''Simulates a general reveal function for any box, automatically reveals adjacent boxes if target box is blank'''
        row = self.currentrow
        column = self.currentcol
        box = self.boxes[row][column]
        box.reveal()
        if box.is_blank():
            adj = self.get_adj(row, column, self.width, self.height)
            for posn in adj:
                r = posn[0]
                c = posn[1]
                if not self.boxes[r][c].is_bomb():
                    if self.boxes[r][c].is_blank() and not self.boxes[r][c].is_revealed():
                        self.currentrow = r
                        self.currentcol = c
                        self.auto_reveal()
                    else:
                        self.boxes[r][c].reveal()

    def get_adj(self, row, column, width, height):
        '''Returns a list of tuples of row, column specifying adjacent boxes'''
        adj = []

        # for horizontally adjacent boxes
        if column != 0:
            adj.append((row,column-1))
        if column != width - 1:
            adj.append((row,column + 1))

        # for vertically adjacent boxes
        if row != 0:
            adj.append((row - 1,column))
        if row != height - 1:
            adj.append((row + 1,column))

        # for diagonally adjacent boxes
        if row != 0 and column != 0:      # top left
            adj.append((row-1,column - 1))
        if row != height - 1 and column != 0:     # bottom left
            adj.append((row + 1,column - 1))
        if row != 0 and column != width - 1:     # top right
            adj.append((row - 1,column + 1))
        if row != height - 1 and column != width - 1:     # bottom right
            adj.append((row + 1,column + 1))

        return adj

# play the game
width = int(input("Enter grid width: "))
height = int(input("Enter grid height: "))
numbombs = int(input("Enter number of bombs: "))
root = Tk()
root.title('Minesweeper')
game = Board(root, width, height, numbombs)
game.mainloop()
