import time
import tkinter as tk
import tkinter.messagebox as msgbox
import numpy as np

class ExitButton(tk.Button):
    def __init__(self, window):
        tk.Button.__init__(self, window, text="Exit",  height=2, command=window.quit)
        self.grid(row=0, column=3, sticky=tk.N+tk.S+tk.E+tk.W)

class NewButton(tk.Button):
    def __init__(self, window):
        tk.Button.__init__(self, window, text="New",  height=2, command=window.NewPositions)
        self.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

class Number(tk.Button):
    def __init__(self, app, matrix, number):
        self.app_ = app
        self.matrix_ = matrix
        self.number_ = number
        self.shifts_ = [-1, 1, -4, 4]
        tk.Button.__init__(self, app, text=str(number), height=5, width=10, command=self.CheckPosition)
    
    def UpdatePosition(self):
        posNum = self.matrix_[self.number_]
        self.grid(row=posNum // 4 + 1, column=posNum % 4, sticky=tk.N+tk.S+tk.E+tk.W)
    
    def CheckPosition(self):
        numCurPos = self.matrix_[self.number_]
        zeroCurPos = self.matrix_[0]
        for shift in self.shifts_:
            if (zeroCurPos == numCurPos + shift):
                self.matrix_[self.number_] = zeroCurPos
                self.matrix_[0] = numCurPos
                self.UpdatePosition()
                self.app_.CheckWin()
                break

class Application(tk.Frame):
    def __init__(self, name='15 puzzle', master=None):
        tk.Frame.__init__(self, master)
        self.master.title(name)
        self.matrix_ = np.arange(16)
        self.winMatrix_ = np.arange(16) - 1
        self.winMatrix_[0] = 15
        self.numbers_ = [Number(self, self.matrix_, i+1) for i in range(15)]        
        self.InitUI()

    def InitUI(self):
        self.InitGrid()
        self.exitButton_ = ExitButton(self)
        self.newButton_ = NewButton(self)
        self.NewPositions()
    
    def InitGrid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        for i in [0, 1, 2, 3]:
            self.columnconfigure(i, weight=1)
        for i in [0, 1, 2, 3, 4]:
            self.rowconfigure(i, weight=1)

    def NewPositions(self):
        np.random.shuffle(self.matrix_)
        while(self.CheckSolvability()):
            np.random.shuffle(self.matrix_)
        for number in self.numbers_:
            number.UpdatePosition()
    
    def CheckSolvability(self):
        sum = 0
        for i in range(1, 16):
            sum += (self.matrix_[i+1:] < self.matrix_[i]).sum()
        sum += self.matrix_[0] // 4
        return sum % 2 == 0
    
    def CheckWin(self):
        if np.array_equal(self.matrix_, self.winMatrix_):
            msgbox.showinfo("", "You win!!!")
            self.NewPositions()

def main():
    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()