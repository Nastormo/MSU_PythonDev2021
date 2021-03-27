import tkinter as tk
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
        self.T = tk.Text(self, undo=True, wrap=tk.WORD, font="fixed",
            inactiveselectbackground="MidnightBlue")
        self.T.grid(row=0, column=0, sticky="NEWS")
        self.T.bind('<<Modified>>', self.__analise)
        self.L = tk.Button(self, text="Load", command=self.load)
        self.L.grid(row=1, column=0, sticky="NEWS")
        self.S = tk.Button(self, text="Save", command=self.save)
        self.S.grid(row=1, column=1, sticky="NEWS")

    def event(self, name_figure, left_up_x, left_up_y, right_down_x, right_down_y, line, color_edge, color_fill):
        self.T.insert(tk.END, f"{name_figure} <{left_up_x} {left_up_y} {right_down_x} {right_down_y}> {line} {color_edge} {color_fill}\n")
    
    def clear(self):
        self.T.delete("1.0", tk.END)

    def save(self, file="File.txt"):
        fp = open(file, 'w')
        fp.write(self.T.get("1.0", tk.END))
        fp.close()

    def load(self, file="File.txt"):
        self.T.delete("1.0", tk.END)
        fp = open(file, "r")
        self.T.insert("1.0", fp.read())
        fp.close()

    def __analise(self, event):
        if (self.T.edit_modified() == 0):
            return
        data = self.T.get("1.0", tk.END).split("\n")
        self.eventModule.sendClear()
        self.T.delete("1.0", tk.END)
        for line in data:
            if len(line) == 0:
                break
            params = re.match(
                r"(?P<type>oval|rectangle)"
                r" \<"
                r"(?P<x0>[\d\.]+)"
                r" (?P<y0>[\d\.]+)"
                r" (?P<x1>[\d\.]+)"
                r" (?P<y1>[\d\.]+)"
                r"\>"
                r" (?P<line>[\d\.]+)"
                r" (?P<color_edge>[\#\w]+)"
                r" (?P<color_fill>[\#\w]+)",
                line
            )
            if not params is None:
                params = params.groupdict()
                print(params)
                self.eventModule.sendEvent(params["type"], float(params["x0"]), float(params["y0"]), 
                    float(params["x1"]), float(params["y1"]), float(params["line"]), 
                    params["color_edge"], params["color_fill"])
            else: 
                self.T.insert(tk.END, line)
        self.T.edit_modified(0)

class CanvasFrame(LabelFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, row=0, column=1, **kwargs)
        self.C = tk.Canvas(self)
        self.C.grid(row=0, column=0, sticky="NEWS")

    def event(self, name_figure, left_up_x, left_up_y, right_down_x, right_down_y, line, color_edge, color_fill):
        self.C.create_oval(left_up_x, left_up_y, right_down_x, right_down_y, fill=color_fill)
    
    def clear(self):
        for id in self.C.find_all():
            self.C.delete(id)


class EventModule():
    def __init__(self):
        self.recvs = []

    def sendEvent(self, name_figure, left_up_x, left_up_y, right_down_x, right_down_y, line, color_edge, color_fill):
        for recv in self.recvs:
            recv.event(name_figure, left_up_x, left_up_y, right_down_x, right_down_y, line, color_edge, color_fill)

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