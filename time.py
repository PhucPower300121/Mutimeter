import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import pytz
import json
import os
import webbrowser

# File lưu danh sách timezones
CONFIG_FILE = "timezones.json"

# Nếu chưa có file, tạo mặc định
DEFAULT_ZONES = [
    ("Việt Nam", "Asia/Ho_Chi_Minh"),
    ("Tokyo", "Asia/Tokyo"),
    ("New York", "America/New_York"),
    ("London", "Europe/London"),
    ("Los Angeles", "America/Los_Angeles")
]

def load_zones():
    if not os.path.exists(CONFIG_FILE):
        save_zones(DEFAULT_ZONES)
        return DEFAULT_ZONES
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_ZONES

def save_zones(zones):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(zones, f, ensure_ascii=False, indent=2)

zones = load_zones()

root = tk.Tk()
root.title("Multimeter")
root.configure(bg="#0f0f0f")
root.resizable(False, False)

# GRID CONTAINER
container = tk.Frame(root, bg="#0f0f0f")
container.pack(padx=10, pady=10)

labels = []

def rebuild_grid():
    """Xây lại grid mỗi khi thêm/xóa timezone."""
    for widget in container.winfo_children():
        widget.destroy()
    labels.clear()

    cols = 3
    for i, (name, zone) in enumerate(zones):
        frame = tk.Frame(container, bg="#101010", padx=10, pady=10)
        frame.grid(row=i // cols, column=i % cols, padx=10, pady=10)

        tk.Label(frame, text=name, fg="#ffaa00", bg="#101010",
                 font=("Consolas", 14, "bold")).pack()

        time_label = tk.Label(frame, text="--:--:--", fg="white", bg="#101010",
                              font=("Consolas", 22))
        time_label.pack()

        labels.append((time_label, zone))

def update_time():
    for label, zone in labels:
        try:
            tz = pytz.timezone(zone)
            now = datetime.now(tz).strftime("%H:%M:%S")
        except:
            now = "ERR"
        label.config(text=now)
    root.after(1000, update_time)

def custom_input_dialog(title, fields):
    dlg = tk.Toplevel(root)
    dlg.title(title)
    dlg.configure(bg="#0f0f0f")
    dlg.resizable(False, False)
    dlg.grab_set()

    entries = {}

    for field in fields:
        frame = tk.Frame(dlg, bg="#0f0f0f")
        frame.pack(pady=5, padx=10, anchor="w")

        tk.Label(frame, text=field, fg="white", bg="#0f0f0f",
                 font=("Consolas", 12)).pack(anchor="w")

        e = tk.Entry(frame, fg="white", bg="#1a1a1a",
                     insertbackground="white",
                     font=("Consolas", 12), relief="flat")
        e.pack(fill="x")
        entries[field] = e

    link_btn = tk.Button(
        dlg,
        text="List of Time Zones",
        font=("Consolas", 11),
        fg="#ffaa00",
        bg="#0f0f0f",
        activebackground="#1a1a1a",
        relief="flat",
        cursor="hand2",
        command=lambda: webbrowser.open("https://timezonedb.com/time-zones")
    )
    link_btn.pack(pady=(5, 5))

    result = {}

    def ok():
        for f in fields:
            result[f] = entries[f].get()
        dlg.destroy()

    def cancel():
        result.clear()      # báo hiệu "cancel"
        dlg.destroy()

    # Button row
    btn_frame = tk.Frame(dlg, bg="#0f0f0f")
    btn_frame.pack(pady=10, padx=10, fill="x")

    btn_ok = tk.Button(btn_frame, text="OK",
                       bg="#ffaa00", fg="black",
                       activebackground="#ffcc44",
                       font=("Consolas", 12), relief="flat",
                       command=ok)
    btn_ok.pack(side="left", expand=True, fill="x", padx=(0,5))

    btn_cancel = tk.Button(btn_frame, text="Cancel",
                           bg="#333333", fg="white",
                           activebackground="#555555",
                           font=("Consolas", 12), relief="flat",
                           command=cancel)
    btn_cancel.pack(side="right", expand=True, fill="x", padx=(5,0))

    dlg.wait_window()
    return result

def dark_confirm(message):
    dlg = tk.Toplevel(root)
    dlg.title("Confirm")
    dlg.configure(bg="#0f0f0f")
    dlg.resizable(False, False)
    dlg.grab_set()

    tk.Label(dlg, text=message,
             fg="white", bg="#0f0f0f",
             font=("Consolas", 12), wraplength=250).pack(padx=15, pady=15)

    result = {"ok": False}

    def yes():
        result["ok"] = True
        dlg.destroy()

    def no():
        dlg.destroy()

    btn_frame = tk.Frame(dlg, bg="#0f0f0f")
    btn_frame.pack(pady=10, padx=10, fill="x")

    tk.Button(btn_frame, text="Xóa",
              bg="#ff4444", fg="white",
              activebackground="#ff6666",
              font=("Consolas", 12), relief="flat",
              command=yes).pack(side="left", expand=True, fill="x", padx=(0,5))

    tk.Button(btn_frame, text="Cancel",
              bg="#333333", fg="white",
              activebackground="#555555",
              font=("Consolas", 12), relief="flat",
              command=no).pack(side="right", expand=True, fill="x", padx=(5,0))

    dlg.wait_window()
    return result["ok"]


def open_settings():
    win = tk.Toplevel(root)
    win.title("Settings")
    win.configure(bg="#0f0f0f")
    win.geometry("350x400")

    # Listbox dark mode
    listbox = tk.Listbox(
        win,
        font=("Consolas", 12),
        height=12,
        bg="#1a1a1a",
        fg="white",
        selectbackground="#ffaa00",
        selectforeground="black",
        borderwidth=0,
        highlightthickness=0
    )
    listbox.pack(pady=10, fill="both", expand=True)

    for name, zone in zones:
        listbox.insert("end", f"{name}  —  {zone}")

    def add_zone():
        data = custom_input_dialog("Add a region", ["Area Name", "Timezone"])

        name = data.get("Area Name")
        zone = data.get("Timezone")

        if not name or not zone:
            return

        try:
            pytz.timezone(zone)
        except:
            messagebox.showerror("Error", "Invalid timezone!")
            return

        zones.append((name, zone))
        save_zones(zones)
        rebuild_grid()
        listbox.insert("end", f"{name}  —  {zone}")

    def remove_zone():
        idx = listbox.curselection()
        if not idx:
            return

        index = idx[0]
        name = zones[index][0]

        if not dark_confirm(f"Do you really want to delete '{name}'?"):
            return

        del zones[index]
        save_zones(zones)
        rebuild_grid()
        listbox.delete(index)
    
    # Buttons dark style
    btn_add = tk.Button(
        win, text="Add",
        font=("Consolas", 12),
        command=add_zone,
        bg="#ffaa00",
        fg="black",
        activebackground="#ffcc44",
        relief="flat"
    )
    btn_add.pack(pady=5, fill="x")

    btn_del = tk.Button(
        win, text="Remove",
        font=("Consolas", 12),
        command=remove_zone,
        bg="#ff4444",
        fg="white",
        activebackground="#ff6666",
        relief="flat"
    )
    btn_del.pack(pady=5, fill="x")

# Nút settings
btn = tk.Button(root, text="⚙ Settings", font=("Consolas", 12),
                command=open_settings, bg="#ffaa00")
btn.pack(pady=5)

rebuild_grid()
update_time()
root.mainloop()

