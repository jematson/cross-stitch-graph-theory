from tkinter import *
from tkinter import filedialog as fd

import xml.etree.ElementTree as ET
from main import *

file = None
crosses = None
colors = None
maxdim = None


def select_file():
    filetypes = (
        ('oxs files', '*.oxs'),
    )

    file = fd.askopenfilename(
        title='Choose a file',
        initialdir='/',
        filetypes = filetypes
    )

    if not file:
        return

    tree = ET.parse(file)
    crosses, colors, maxdim = parse_oxs_xml(tree)
    
    for widget in root.winfo_children():
        if widget != openb:
            widget.destroy()
    
    for p in crosses:
        newButton = Button(root, text=str(p), command=lambda p=p: print(p))
        newButton.pack(fill=X, padx=5, pady=2)

    
if __name__ == "__main__":
    root = Tk()
    root.resizable(False, False)
    root.geometry('300x150')


    openb = Button(
        root,
        text='Choose a File',
        command=select_file
    )
    openb.pack(expand=True)


    root.mainloop()