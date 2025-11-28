import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os
from datetime import datetime, date

FILE_NAME = "tasks.json"
tasks = []
current_file_var = None  # will be set later

PRIORITY_LEVELS = ["High","Medium","Low"]
PRIORITY_ORDER = {"High":3,"Medium":2,"Low":1}
FUTURE_DATE,PAST_DATE = date(9999,12,31),date(1,1,1)
SORT_OPTIONS = [
    "Priority (High→Low)","Title A→Z","Title Z→A",
    "Due date (soonest)","Due date (latest)",
    "Status (Pending first)","Status (Completed first)",
    "Category (A→Z)",
]

def parse_date(s, default):
    s = s.strip() if s else ""
    if not s: return default
    for fmt in ("%Y-%m-%d","%Y/%m/%d"):
        try: return datetime.strptime(s,fmt).date()
        except: pass
    return default

def set_current_file(path):
    """Update the global FILE_NAME and the UI to show which file is active."""
    global FILE_NAME
    FILE_NAME = path
    basename = os.path.basename(FILE_NAME) if FILE_NAME else "(unsaved)"
    # update status bar text
    try:
        if current_file_var is not None:
            current_file_var.set(f"File: {basename}")
    except NameError:
        pass
    # update window title
    try:
        root.title(f"To-Do App (Final Project Version) - {basename}")
    except NameError:
        # root may not exist yet if called early
        pass

def load_tasks():
    global tasks
    if not os.path.exists(FILE_NAME):
        tasks = []
        return
    with open(FILE_NAME) as f:
        raw = json.load(f)
    tasks = [{
        "title":       t.get("title",""),
        "description": t.get("description",""),
        "due":         t.get("due",""),
        "priority":    t.get("priority","Medium"),
        "category":    t.get("category",""),
        "status":      t.get("status","Pending"),
        "created_at":  t.get("created_at", datetime.now().timestamp()),
    } for t in raw]

def save_tasks():
    with open(FILE_NAME,"w") as f:
        json.dump(tasks,f,indent=2)

def update_tree():
    tree.delete(*tree.get_children())
    cats = sorted({t.get("category","") for t in tasks if t.get("category","")})
    values = ["All"] + cats
    cat_filter_combo["values"] = values
    if cat_filter_var.get() not in values: cat_filter_var.set("All")

    status_f = status_filter_var.get()
    prio_f   = prio_filter_var.get()
    cat_f    = cat_filter_var.get()

    for t in tasks:
        title = t.get("title","")
        due   = t.get("due","")
        prio  = t.get("priority","Medium")
        cat   = t.get("category","")
        status= t.get("status","Pending")

        if status_f!="All" and status!=status_f: continue
        if prio_f  !="All" and prio  !=prio_f:  continue
        if cat_f   !="All" and cat   !=cat_f:   continue

        tree.insert("", "end", values=(title, cat, prio, due, status))

def clear_inputs():
    title_entry.delete(0,"end")
    desc_text.delete("1.0","end")
    due_entry.delete(0,"end")
    category_entry.delete(0,"end")
    priority_var.set("Medium")

def add_task():
    title = title_entry.get().strip()
    if not title:
        messagebox.showerror("Error","Title is required.")
        return
    tasks.append({
        "title":       title,
        "description": desc_text.get("1.0","end").strip(),
        "due":         due_entry.get().strip(),
        "priority":    priority_var.get(),
        "category":    category_entry.get().strip(),
        "status":      "Pending",
        "created_at":  datetime.now().timestamp(),
    })
    save_tasks()
    update_tree()
    clear_inputs()

def get_selected_task():
    sel = tree.selection()
    if not sel: return None
    title = tree.item(sel[0])["values"][0]
    for t in tasks:
        if t.get("title","") == title:
            return t
    return None

def toggle_status():
    t = get_selected_task()
    if not t: return
    t["status"] = "Completed" if t.get("status","Pending")=="Pending" else "Pending"
    save_tasks()
    update_tree()

def delete_task():
    t = get_selected_task()
    if not t: return
    tasks.remove(t)
    save_tasks()
    update_tree()

def clear_all_tasks():
    global tasks
    if not tasks:
        return
    if not messagebox.askyesno("Clear All", "Delete ALL tasks?"):
        return
    tasks.clear()
    save_tasks()
    update_tree()

def edit_task():
    t = get_selected_task()
    if t: open_edit_window(t)

def open_edit_window(task):
    win = tk.Toplevel(root)
    win.title("Edit Task")
    win.geometry("380x420")
    main = tk.Frame(win)
    main.pack(fill="both",expand=True,padx=10,pady=10)

    tk.Label(main,text="Title").grid(row=0,column=0,sticky="w")
    t_entry = tk.Entry(main,width=40)
    t_entry.grid(row=0,column=1,sticky="w")
    t_entry.insert(0,task["title"])

    tk.Label(main,text="Description").grid(row=1,column=0,sticky="nw",pady=(5,0))
    d_text = tk.Text(main,height=5,width=40)
    d_text.grid(row=1,column=1,sticky="w",pady=(5,0))
    d_text.insert("1.0",task["description"])

    tk.Label(main,text="Due Date").grid(row=2,column=0,sticky="w",pady=(5,0))
    du_entry = tk.Entry(main,width=20)
    du_entry.grid(row=2,column=1,sticky="w",pady=(5,0))
    du_entry.insert(0,task["due"])

    tk.Label(main,text="Priority").grid(row=3,column=0,sticky="w",pady=(5,0))
    p_var = tk.StringVar(value=task["priority"])
    ttk.Combobox(main,textvariable=p_var,values=PRIORITY_LEVELS,width=12)\
        .grid(row=3,column=1,sticky="w",pady=(5,0))

    tk.Label(main,text="Category").grid(row=4,column=0,sticky="w",pady=(5,0))
    c_entry = tk.Entry(main,width=20)
    c_entry.grid(row=4,column=1,sticky="w",pady=(5,0))
    c_entry.insert(0,task["category"])

    def save_edit():
        new_title = t_entry.get().strip()
        if not new_title:
            messagebox.showerror("Error","Title cannot be empty.")
            return
        task["title"]       = new_title
        task["description"] = d_text.get("1.0","end").strip()
        task["due"]         = du_entry.get().strip()
        task["priority"]    = p_var.get()
        task["category"]    = c_entry.get().strip()
        save_tasks()
        update_tree()
        win.destroy()

    tk.Button(main,text="Save Changes",command=save_edit)\
        .grid(row=5,column=0,columnspan=2,pady=15)

def sort_tasks():
    m = sort_var.get()
    if   m =="Priority (High→Low)":
        tasks.sort(key=lambda t:PRIORITY_ORDER.get(t.get("priority","Medium"),0),reverse=True)
    elif m =="Title A→Z":
        tasks.sort(key=lambda t:t.get("title","").lower())
    elif m =="Title Z→A":
        tasks.sort(key=lambda t:t.get("title","").lower(),reverse=True)
    elif m =="Due date (soonest)":
        tasks.sort(key=lambda t:parse_date(t.get("due",""),FUTURE_DATE))
    elif m =="Due date (latest)":
        tasks.sort(key=lambda t:parse_date(t.get("due",""),PAST_DATE),reverse=True)
    elif m =="Status (Pending first)":
        tasks.sort(key=lambda t:(0 if t.get("status","Pending")=="Pending" else 1,
                                 t.get("title","").lower()))
    elif m =="Status (Completed first)":
        tasks.sort(key=lambda t:(0 if t.get("status","Pending")=="Completed" else 1,
                                 t.get("title","").lower()))
    elif m =="Category (A→Z)":
        tasks.sort(key=lambda t:(t.get("category","").lower(),t.get("title","").lower()))
    save_tasks()
    update_tree()

def show_stats():
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("status","Pending")=="Completed")
    messagebox.showinfo("Task Statistics",
                        f"Total tasks: {total}\nCompleted: {completed}\nPending: {total-completed}")

def choose_file():
    path = filedialog.askopenfilename(
        title="Open task file",
        filetypes=[("JSON files","*.json"),("All files","*.*")]
    )
    if not path:
        return
    set_current_file(path)
    load_tasks()
    update_tree()

def new_file():
    global tasks
    path = filedialog.asksaveasfilename(
        title="Create new task file",
        defaultextension=".json",
        filetypes=[("JSON files","*.json"),("All files","*.*")]
    )
    if not path:
        return
    set_current_file(path)
    tasks = []
    save_tasks()
    update_tree()

def save_current_file():
    """Save tasks to the current FILE_NAME."""
    if not FILE_NAME:
        save_as_file()
        return
    save_tasks()
    messagebox.showinfo("Saved", f"Tasks saved to:\n{FILE_NAME}")

def save_as_file():
    """Choose a new file name and save (Save As...)."""
    path = filedialog.asksaveasfilename(
        title="Save tasks as...",
        defaultextension=".json",
        filetypes=[("JSON files","*.json"),("All files","*.*")]
    )
    if not path:
        return
    set_current_file(path)
    save_tasks()
    messagebox.showinfo("Saved", f"Tasks saved to:\n{FILE_NAME}")

def on_tree_click(event):
    # Only happens when clicking on the Status column
    if tree.identify("region", event.x, event.y) != "cell":
        return
    if tree.identify_column(event.x) != "#5":  # 5th column = "status"
        return
    row = tree.identify_row(event.y)
    if not row:
        return
    tree.selection_set(row)
    toggle_status()

def on_tree_double_click(event):
    row = tree.identify_row(event.y)
    if not row:
        return
    tree.selection_set(row)
    edit_task()

# ---------- UI ----------
root = tk.Tk()
root.title("To-Do App (Final Project Version)")
root.geometry("840x560")

# Status bar showing current file
current_file_var = tk.StringVar()
status_bar = tk.Label(root, textvariable=current_file_var, anchor="w")
status_bar.pack(fill="x", side="bottom")

input_frame = tk.LabelFrame(root,text="Add Task")
input_frame.pack(fill="x",padx=10,pady=5)
input_frame.columnconfigure(1,weight=1)

tk.Label(input_frame,text="Title").grid(row=0,column=0,sticky="w",padx=5,pady=2)
title_entry = tk.Entry(input_frame,width=40)
title_entry.grid(row=0,column=1,sticky="we",padx=5,pady=2)

tk.Label(input_frame,text="Description").grid(row=1,column=0,sticky="nw",padx=5,pady=2)
desc_text = tk.Text(input_frame,height=3,width=40)
desc_text.grid(row=1,column=1,sticky="we",padx=5,pady=2)

tk.Label(input_frame,text="Due (YYYY-MM-DD)").grid(row=2,column=0,sticky="w",padx=5,pady=2)
due_entry = tk.Entry(input_frame,width=20)
due_entry.grid(row=2,column=1,sticky="w",padx=5,pady=2)

tk.Label(input_frame,text="Priority").grid(row=3,column=0,sticky="w",padx=5,pady=2)
priority_var = tk.StringVar(value="Medium")
ttk.Combobox(input_frame,textvariable=priority_var,
             values=PRIORITY_LEVELS,width=12).grid(row=3,column=1,sticky="w",padx=5,pady=2)

tk.Label(input_frame,text="Category").grid(row=4,column=0,sticky="w",padx=5,pady=2)
category_entry = tk.Entry(input_frame,width=20)
category_entry.grid(row=4,column=1,sticky="w",padx=5,pady=2)

tk.Button(input_frame,text="Add Task",command=add_task)\
    .grid(row=5,column=0,columnspan=2,pady=5)

filter_frame = tk.LabelFrame(root,text="Filters & Sorting")
filter_frame.pack(fill="x",padx=10,pady=5)

status_filter_var = tk.StringVar(value="All")
prio_filter_var   = tk.StringVar(value="All")
cat_filter_var    = tk.StringVar(value="All")
sort_var          = tk.StringVar(value=SORT_OPTIONS[0])

tk.Label(filter_frame,text="Status:").pack(side="left",padx=(5,2))
ttk.Combobox(filter_frame,textvariable=status_filter_var,
             values=["All","Pending","Completed"],width=12).pack(side="left",padx=3)

tk.Label(filter_frame,text="Priority:").pack(side="left",padx=(10,2))
ttk.Combobox(filter_frame,textvariable=prio_filter_var,
             values=["All"]+PRIORITY_LEVELS,width=10).pack(side="left",padx=3)

tk.Label(filter_frame,text="Category:").pack(side="left",padx=(10,2))
cat_filter_combo = ttk.Combobox(filter_frame,textvariable=cat_filter_var,
                                values=["All"],width=14)
cat_filter_combo.pack(side="left",padx=3)

tk.Label(filter_frame,text="Sort by:").pack(side="left",padx=(10,2))
ttk.Combobox(filter_frame,textvariable=sort_var,
             values=SORT_OPTIONS,width=18).pack(side="left",padx=3)

tk.Button(filter_frame,text="Apply Filters",command=update_tree).pack(side="left",padx=5)
tk.Button(filter_frame,text="Sort",command=sort_tasks).pack(side="left",padx=3)

columns = ("title","category","priority","due","status")
tree_frame = tk.Frame(root)
tree_frame.pack(fill="both",expand=True,padx=10,pady=5)
tree = ttk.Treeview(tree_frame,columns=columns,show="headings")
for col in columns:
    tree.heading(col,text=col.title())
    tree.column(col,width=120,anchor="w")
tree.column("title",width=220)
tree.grid(row=0,column=0,sticky="nsew")

scrollbar = ttk.Scrollbar(tree_frame,orient="vertical",command=tree.yview)
scrollbar.grid(row=0,column=1,sticky="ns")
tree.configure(yscrollcommand=scrollbar.set)
tree_frame.rowconfigure(0,weight=1)
tree_frame.columnconfigure(0,weight=1)

action_frame = tk.Frame(root)
action_frame.pack(fill="x",padx=10,pady=5)
for text,cmd in [
    ("Toggle Status", toggle_status),
    ("Edit",          edit_task),
    ("Delete",        delete_task),
    ("Stats",         show_stats),
    ("Save",          save_current_file),
    ("Save As",       save_as_file),
    ("Open File",     choose_file),
    ("New File",      new_file),
]:
    tk.Button(action_frame,text=text,command=cmd).pack(side="left",padx=5)

# ---- Bindings ----
root.bind('<Return>',         lambda e: add_task())
root.bind('<Delete>',         lambda e: delete_task())
root.bind('<Control-Delete>', lambda e: clear_all_tasks())
root.bind('<Escape>',         lambda e: root.destroy())
root.bind('<Control-d>',      lambda e: toggle_status())

tree.bind("<Button-1>",  on_tree_click)        # click Status column to toggle
tree.bind("<Double-1>", on_tree_double_click)  # double-click row to edit

# initialize with default file
set_current_file(FILE_NAME)
load_tasks()
update_tree()
root.mainloop()
'''Setup complete'''