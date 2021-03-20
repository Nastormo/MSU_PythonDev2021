import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter.messagebox import showinfo
from functools import partial
import re

def newItem(self, name, widget_type, geometry, **kwargs):
    class newWidget(widget_type):
        def __init__(self, geometry, **kwargs):
            super().__init__(**kwargs)

            params = re.match(
                r"(?P<row>\d+)"
                r"(\.(?P<row_weight>\d+))?"
                r"(\+(?P<height>\d+))?"
                r":"
                r"(?P<column>\d+)"
                r"(\.(?P<column_weight>\d+))?"
                r"(\+(?P<width>\d+))?"
                r"(/(?P<gravity>[NEWSnews]+))?",
                geometry
            ).groupdict()

            print(params)
            row = int(params["row"])
            column = int(params["column"])
            self.grid(row=row, rowspan = 1 + (0 if params["height"] is None else int(params["height"])),
                column=column, columnspan = 1 + (0 if params["width"] is None else int(params["width"])),
                sticky= "NEWS" if params["gravity"] is None else params["gravity"]
            )
            self.master.rowconfigure(row, weight = 1 if params["row_weight"] is None else int(params["row_weight"]))
            self.master.columnconfigure(column, weight = 1 if params["column_weight"] is None else int(params["column_weight"]))
            print(kwargs)

        def __getattr__(self, item):
            return partial(newItem, self, item)

    widget = newWidget(geometry, master=self, **kwargs)
    setattr(self, name, widget)
    return widget

class Application(tk.Frame):
    def __init__(self, title):
        super().__init__()
        self.master.title(title)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.grid(sticky="NWSE")
        self.createWidgets()

    def __getattr__(self, item):
        return partial(newItem, self, item)
    
    def createWidgets(self):
        pass


class App(Application):
    def createWidgets(self):
        self.message = "Congratulations!\nYou've found a sercet level!"
        self.F1(tk.LabelFrame, "1:0", text="Frame 1")
        self.F1.B1(tk.Button, "0:0/NW", text="1")
        self.F1.B2(tk.Button, "0:1/NE", text="2")
        self.F1.B3(tk.Button, "1:0+1/SEW", text="3")
        self.F2(tk.LabelFrame, "1:1", text="Frame 2")
        self.F2.B1(tk.Button, "0:0/N", text="4")
        self.F2.B2(tk.Button, "0+1:1/SEN", text="5")
        self.F2.B3(tk.Button, "1:0/S", text="6")
        self.Q(tk.Button, "2.0:1.2/SE", text="Quit", command=self.quit)
        self.F1.B3.bind("<Any-Key>", lambda event: showinfo(self.message.split()[0], self.message))

def main():
    app = App(title="Sample application")
    app.mainloop()

if __name__ == '__main__':
    main()