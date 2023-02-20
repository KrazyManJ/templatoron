from tkinter import *
from tkinter.filedialog import *
from tkinter.ttk import Treeview

from templatoron import TemplatoronObject

FILE_TYPES = [("Templatoron File", ".json")]

Opened_Templatoron: TemplatoronObject | None = None
i = -1


def update_view():
    for i in tree.get_children():
        tree.delete(i)
    i = -1

    def add_tree(data: dict, parent: str):
        global i
        for k, v in data.items():
            i += 1
            tree.insert(parent=parent, index="end", iid=str(i), text=k)
            if isinstance(v, dict):
                add_tree(v, str(i))

    add_tree(Opened_Templatoron.structure, "")


def open_templ_file():
    global Opened_Templatoron
    pth = askopenfilename(filetypes=FILE_TYPES, initialdir="/")
    if pth != "":
        Opened_Templatoron = TemplatoronObject.from_file(pth)
        update_view()


def scan_folder():
    global Opened_Templatoron
    pth = askdirectory(initialdir="/")
    if pth != "":
        Opened_Templatoron = TemplatoronObject.from_scaning_folder(pth)
        update_view()


def save_templ_file():
    pth = asksaveasfilename(confirmoverwrite=True, filetypes=FILE_TYPES, initialfile="temp_project.json")
    if pth != "":
        Opened_Templatoron.save(pth)


def create_project():
    global Opened_Templatoron
    if Opened_Templatoron is not None:
        cwin = Toplevel()
        cwin.grab_set()

        def create():
            varvalues = {}
            for v in Opened_Templatoron.variables:
                if cwin.getvar(v) == "":
                    return
                varvalues[v] = cwin.getvar(v)
            output = askdirectory()
            Opened_Templatoron.create_project(output, **varvalues)
            cwin.destroy()

        for i, var in enumerate(Opened_Templatoron.variables):
            Label(cwin, text=var).grid(row=i, column=0)
            Entry(cwin, textvariable=var).grid(row=i, column=1)
        Button(cwin, text="Finish", command=create).grid(columnspan=2, column=0, row=len(Opened_Templatoron.variables))


if __name__ == '__main__':
    win = Tk()
    win.geometry("600x600")
    win.title("Templatoron")

    menu = Menu(tearoff=0)
    cascade = Menu(tearoff=0)
    cascade.add_command(label="Open templatoron file...", command=open_templ_file)
    cascade.add_command(label="Scan folder...", command=scan_folder)
    cascade.add_command(label="Save templatoron file as...", command=save_templ_file)
    menu.add_cascade(menu=cascade, label="File")
    win.configure(menu=menu)

    tree = Treeview(win, show="tree", selectmode="extended", height=20)
    tree.pack(fill="both", padx=10, pady=10)

    create_project = Button(text="Create Project", command=create_project)
    create_project.pack(pady=20)

    win.mainloop()
