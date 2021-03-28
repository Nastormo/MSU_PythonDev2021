import tkinter as tk
from tkinter import colorchooser
import inspect
import re

class LabelFrame(tk.LabelFrame):
    def __init__(self, master=None, eventModule=None, row=0, column=0, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=row, column=column, sticky="NEWS")
        for column in range(self.grid_size()[0]):
            self.columnconfigure(column, weight=1)
        for row in range(self.grid_size()[1]):
            self.rowconfigure(row, weight=1)
        self.eventModule = eventModule

class TextFrame(LabelFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, text="File.txt", row=0, column=0, **kwargs)
        self._createWidgets()

    def _createWidgets(self):
        self._loadButton = tk.Button(self, text="Load", command=self._load)
        self._loadButton.grid(row=1, column=0, sticky="NEWS")
        self._saveButton = tk.Button(self, text="Save", command=self._save)
        self._saveButton.grid(row=1, column=1, sticky="NEWS")

        self.T = tk.Text(self, undo=True, wrap=tk.WORD, font="fixed",
            inactiveselectbackground="MidnightBlue")
        self.T.grid(row=0, columnspan=2, sticky="NEWS")
        self.T.bind('<<Modified>>', self._analise)
        self.T.tag_config('warning', background="red")

    def _save(self, file="File.txt"):
        fp = open(file, 'w')
        fp.write(self.T.get("1.0", tk.END))
        fp.close()

    def _load(self, file="File.txt"):
        self.T.delete("1.0", tk.END)
        fp = open(file, "r")
        self.T.insert("1.0", fp.read())
        fp.close()
    
    def _parseLine(self, line):
        params = re.match(
            r"(?P<type>oval|rectangle)"
            r" \<"
            r"(?P<x0>[\d\.]+) (?P<y0>[\d\.]+)"
            r" (?P<x1>[\d\.]+) (?P<y1>[\d\.]+)"
            r"\>"
            r" (?P<lineWidth>[\d\.]+)"
            r" (?P<lineColor>[\#\w]+)"
            r" (?P<fillColor>[\#\w]+)",
            line
        )
        if not params is None:
            params = params.groupdict()
        return params

    def _analise(self, event):
        if (self.T.edit_modified() == 0):
            return
        data = self.T.get("1.0", tk.END).split("\n")
        self.eventModule.sendClear()
        self.T.delete("1.0", tk.END)
        for line in data:
            if len(line) == 0:
                break
            params = self._parseLine(line)
            if params is None:
                self.T.insert(tk.END, line, 'warning')
            else:
                self.eventModule.sendCreate(
                    params["type"], 
                    float(params["x0"]), float(params["y0"]), 
                    float(params["x1"]), float(params["y1"]), 
                    float(params["lineWidth"]), 
                    params["lineColor"], 
                    params["fillColor"]
                )
        self.T.edit_modified(0)

    def create(self, nameFigure, x0, y0, x1, y1, lineWidth, lineColor, fillColor):
        self.T.insert(tk.END, f"{nameFigure} <{x0} {y0} {x1} {y1}> {lineWidth} {lineColor} {fillColor}\n")

    def update(self, id, x0, y0, x1, y1):
        self.T.edit_modified(1)
        data = self.T.get("1.0", tk.END).split("\n")
        self.eventModule.sendClear()
        self.T.delete("1.0", tk.END)
        curId = 0
        for line in data:
            if len(line) == 0:
                break
            params = self._parseLine(line)
            if params is None:
                self.T.insert(tk.END, line, 'warning')
            else:
                if (id == curId):
                    self.eventModule.sendCreate(
                        params["type"], 
                        float(x0), float(y0), 
                        float(x1), float(y1), 
                        float(params["lineWidth"]), 
                        params["lineColor"], 
                        params["fillColor"]
                    )
                else:
                    self.eventModule.sendCreate(
                        params["type"], 
                        float(params["x0"]), float(params["y0"]), 
                        float(params["x1"]), float(params["y1"]), 
                        float(params["lineWidth"]), 
                        params["lineColor"], 
                        params["fillColor"]
                    )
                curId += 1
        self.T.edit_modified(0)
        pass

    
    def clear(self):
        self.T.delete("1.0", tk.END)

class CanvasFrame(LabelFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, row=0, column=1, **kwargs)
        self._fillColor = "#000000"
        self._lineColor = "#FF0000"
        self._lineWidth = 1
        self._pressedLBM = False
        self._activeFigure = None
        self._action = None
        self._createWidgets()

    def _createWidgets(self):
        self._fillColorButton = tk.Button(self, text='Fill Color', command=self._newFillColor)
        self._fillColorButton.grid(row = 0, column=0, sticky="WE")
        self._lineColorButton = tk.Button(self, text='Line Color', command=self._newLineColor)
        self._lineColorButton.grid(row=0, column=1, sticky="WE")
        self._lineWidthBox = tk.Spinbox(self, width=5, from_=1, to=100, command=self._newLineWidth)
        self._lineWidthBox.grid(row = 0, column=2, sticky="WE")

        self.C = tk.Canvas(self)
        self.C.grid(row = 1, columnspan=3, sticky="NWSE")
        self.C.bind("<Button-1>",        self._pressLBM)
        self.C.bind("<ButtonRelease-1>", self._releaseLBM)
        self.C.bind("<Motion>",          self._mouseMove)

    def _newLineWidth(self):
        self._lineWidth = self._lineWidthBox.get()

    def _newFillColor(self):
        color_code = colorchooser.askcolor()
        self._fillColor = color_code[-1]
        #self._fillColorButton.configure(background=self._fillColor)

    def _newLineColor(self):
        color_code = colorchooser.askcolor()
        self._lineColor = color_code[-1]
        #self._lineColorButton.configure(background=self._lineColor)

    def _pressLBM(self, event):
        self._pressedLBM = True
        x, y = event.x, event.y

        idFigures = self.C.find_overlapping(x-1, y-1, x+1, y+1)
        if (len(idFigures) != 0):
            self._activeFigure = idFigures[-1], x, y
            self._action = "Update"
        else:
            id = self.C.create_oval(
                x, y, x, y,
                fill=self._fillColor,
                outline=self._lineColor,
                width=self._lineWidth)
            self._activeFigure = id, x, y
            self._action = "Create"

    def _releaseLBM(self, event):
        id, _, _ = self._activeFigure
        x0, y0, x1, y1 = self.C.coords(id)
        if (self._action == "Create"):
            self.eventModule.sendCreate("oval", x0, y0, x1, y1, self._lineWidth, self._lineColor, self._fillColor)
        elif (self._action == "Update"):
            start_id = self.C.find_all()[0]
            self.eventModule.sendUpdate(id - start_id, x0, y0, x1, y1)
        self._pressedLBM = False
        self._activeFigure = None
        self._action = None

    def _mouseMove(self, event):
        if not self._pressedLBM or self._action is None:
            return
        if self._action == "Update":
            self._move(event.x, event.y)
        elif self._action == "Create":
            self._resize(event.x, event.y)

    def _resize(self, x, y):
        id, x_start, y_start = self._activeFigure
        self.C.coords(id, min(x, x_start), min(y, y_start), max(x, x_start), max(y, y_start))

    def _move(self, x, y):
        id, x_start, y_start = self._activeFigure
        shift_x = x - x_start
        shift_y = y - y_start
        x0, y0, x1, y1 = self.C.coords(id)
        self.C.coords(id, x0+shift_x, y0+shift_y, x1+shift_x, y1+shift_y)
        self._activeFigure = id, x, y

    def create(self, nameFigure, x0, y0, x1, y1, lineWidth, lineColor, fillColor):
        self.C.create_oval(x0, y0, x1, y1, fill=fillColor, outline=lineColor, width=lineWidth)

    def update(self, id, x0, y0, x1, y1):
        pass

    def clear(self):
        for id in self.C.find_all():
            self.C.delete(id)


class EventModule():
    def __init__(self):
        self.recvs = []

    def sendCreate(self, nameFigure, x0, y0, x1, y1, lineWidth, lineColor, fillColor):
        for recv in self.recvs:
            recv.create(nameFigure, x0, y0, x1, y1, lineWidth, lineColor, fillColor)

    def sendUpdate(self, id, x0, y0, x1, y1):
        for recv in self.recvs:
            recv.update(id, x0, y0, x1, y1)

    def sendClear(self):
        for recv in self.recvs:
            recv.clear()

    def regRecv(self, recv):
        self.recvs.append(recv)


class Window(tk.Tk):
    def __init__(self, title="<application>", **kwargs):
        super().__init__(**kwargs)
        self.title(title)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        eventModule = EventModule()
        self.FT = TextFrame(self, eventModule=eventModule)
        self.FC = CanvasFrame(self, eventModule=eventModule)
        eventModule.regRecv(self.FT)
        eventModule.regRecv(self.FC)

def main():
    app = Window(title="Sample application")
    app.mainloop()

if __name__ == '__main__':
    main()