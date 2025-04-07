import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess

CONFIG_PATH = "config/host_reactions.json"

class ReactionEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Reacciones del Host")
        self.geometry("600x600")

        self.reactions = {}
        self.selected_effect = tk.StringVar()

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_row = ttk.Frame(frame)
        top_row.pack(fill=tk.X)

        ttk.Label(top_row, text="Efecto:").pack(side=tk.LEFT)
        self.effect_combo = ttk.Combobox(top_row, textvariable=self.selected_effect, state="readonly")
        self.effect_combo.pack(side=tk.LEFT, padx=5)
        self.effect_combo.bind("<<ComboboxSelected>>", lambda e: self.load_triggers())

        self.trigger_listbox = tk.Listbox(frame, height=15)
        self.trigger_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        entry_row = ttk.Frame(frame)
        entry_row.pack(fill=tk.X, pady=5)

        self.new_trigger = tk.Entry(entry_row)
        self.new_trigger.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(entry_row, text="Agregar", command=self.add_trigger).pack(side=tk.LEFT, padx=5)
        ttk.Button(entry_row, text="Eliminar", command=self.remove_trigger).pack(side=tk.LEFT)

        ttk.Button(self, text="Guardar Cambios", command=self.save_config).pack(pady=10)
        ttk.Button(self, text="Abrir desde Panel Principal", command=ReactionEditor).pack(pady=5)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self.reactions = json.load(f)
                self.effect_combo["values"] = list(self.reactions.keys())
                if self.reactions:
                    self.selected_effect.set(list(self.reactions.keys())[0])
                    self.load_triggers()

    def load_triggers(self):
        effect = self.selected_effect.get()
        self.trigger_listbox.delete(0, tk.END)
        if effect in self.reactions:
            for word in self.reactions[effect]:
                self.trigger_listbox.insert(tk.END, word)

    def add_trigger(self):
        effect = self.selected_effect.get()
        word = self.new_trigger.get().strip().lower()
        if effect and word:
            if word not in self.reactions[effect]:
                self.reactions[effect].append(word)
                self.trigger_listbox.insert(tk.END, word)
                self.new_trigger.delete(0, tk.END)

    def remove_trigger(self):
        effect = self.selected_effect.get()
        selection = self.trigger_listbox.curselection()
        if effect and selection:
            idx = selection[0]
            word = self.trigger_listbox.get(idx)
            self.reactions[effect].remove(word)
            self.trigger_listbox.delete(idx)

    def save_config(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.reactions, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Guardado", "Cambios guardados correctamente.")

if __name__ == "__main__":
    app = ReactionEditor()
    app.mainloop()
