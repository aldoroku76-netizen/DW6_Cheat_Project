import os
import sys
import tkinter as tk
from memory_mod import DW6Trainer


def resource_path(relative_path):
  try:
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")
  return os.path.join(base_path, relative_path)


class DW6CustomLauncher:

  def __init__(self, root):
    self.root = root
    self.root.title("Dynasty Warriors 6 Mod Launcher")
    self.root.geometry("380x480")
    self.root.configure(bg="#F5EBE0")
    self.root.resizable(False, False)

    logo_file = resource_path("logo-tr.png")
    if os.path.exists(logo_file):
      try:
        self.win_icon = tk.PhotoImage(file=logo_file)
        self.root.iconphoto(True, self.win_icon)
      except Exception:
        pass

    self.trainer = DW6Trainer()
    self.states = {}

    tk.Label(
        root,
        text="DYNASTY WARRIORS 6",
        font=("Impact", 16),
        fg="#7F5539",
        bg="#F5EBE0",
    ).pack(pady=(15, 2))

    tk.Label(
        root,
        text="AOB Code Injection Trainer Panel",
        font=("Arial", 9, "italic"),
        fg="#9C6644",
        bg="#F5EBE0",
    ).pack(pady=(0, 12))

    self.buttons = [
        ("Infinite Health (HP)", "hp", self.trainer.toggle_hp),
        ("Infinite Musou", "musou", self.trainer.toggle_musou),
        ("Full Renbu Gauge", "renbu", self.trainer.toggle_renbu),
        ("Instant Max Level / EXP", "level", self.trainer.toggle_level),
        ("Max Highlighted Weapon", "weapon", self.trainer.toggle_weapon),
        ("Max Highlighted Horse", "horse", self.trainer.toggle_horse),
    ]

    self.btn_widgets = {}

    for text, key, func in self.buttons:
      self.states[key] = False
      btn = tk.Button(
          root,
          text=f"{text} : OFF",
          bg="#E6CCB2",
          fg="#3D2B1F",
          activebackground="#DDB892",
          activeforeground="#3D2B1F",
          font=("Arial", 9, "bold"),
          width=34,
          height=1,
          bd=0,
          command=lambda k=key, f=func, t=text: self.on_toggle(k, f, t),
      )
      btn.pack(pady=4)
      self.btn_widgets[key] = btn

    footer_frame = tk.Frame(root, bg="#F5EBE0")
    footer_frame.pack(side="bottom", pady=(0, 12))

    created_frame = tk.Frame(footer_frame, bg="#F5EBE0")
    created_frame.pack(pady=(0, 4))

    if os.path.exists(logo_file):
      try:
        self.logo_raw = tk.PhotoImage(file=logo_file)
        self.logo_img = self.logo_raw.subsample(24, 24)
        logo_label = tk.Label(created_frame, image=self.logo_img, bg="#F5EBE0")
        logo_label.pack(side="left", padx=(0, 6))
      except Exception:
        pass

    created_label = tk.Label(
        created_frame,
        text="Create By : Timotius R.",
        font=("Arial", 9, "bold"),
        fg="#3D2B1F",
        bg="#F5EBE0",
    )
    created_label.pack(side="left")

    self.status_label = tk.Label(
        footer_frame,
        text="Status: Ready | Pastikan DW6_WIN.exe sudah jalan",
        fg="#588157",
        bg="#F5EBE0",
        font=("Arial", 8, "bold"),
    )
    self.status_label.pack()

  def on_toggle(self, key, func, name):
    res = func()
    if ": ON" in res:
      self.states[key] = True
      self.btn_widgets[key].config(
          text=f"{name} : ON", bg="#A3B18A", fg="#11111b"
      )
    elif ": OFF" in res:
      self.states[key] = False
      self.btn_widgets[key].config(
          text=f"{name} : OFF", bg="#E6CCB2", fg="#3D2B1F"
      )

    self.status_label.config(text=res)


if __name__ == "__main__":
  root = tk.Tk()
  app = DW6CustomLauncher(root)
  root.mainloop()