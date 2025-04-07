import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import json
import os

STYLE_PATH = "config/style_presets.json"

class StyleEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Estilo Visual")
        self.geometry("600x600")

        self.presets = {}
        self.selected_tone = tk.StringVar()
        self.entries = {}

        self.load_styles()
        self.create_widgets()

    def load_styles(self):
        if os.path.exists(STYLE_PATH):
            with open(STYLE_PATH, "r", encoding="utf-8") as f:
                self.presets = json.load(f)

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(pady=10)

        ttk.Label(top, text="Seleccioná el tono: ").pack(side=tk.LEFT)
        tones = list(self.presets.keys())
        self.tone_menu = ttk.Combobox(top, values=tones, textvariable=self.selected_tone, state="readonly")
        self.tone_menu.pack(side=tk.LEFT)
        self.tone_menu.bind("<<ComboboxSelected>>", lambda e: self.load_fields())

        form = ttk.Frame(self)
        form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.entries = {}
        for i, field in enumerate(["font", "fontsize", "color", "stroke_color", "stroke_width", "text_position"]):
            ttk.Label(form, text=field.capitalize()).grid(row=i, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form)
            entry.grid(row=i, column=1, sticky="ew", pady=5)
            self.entries[field] = entry

            if "color" in field:
                btn = ttk.Button(form, text="🎨", command=lambda e=entry: self.choose_color(e))
                btn.grid(row=i, column=2, padx=5)

        form.columnconfigure(1, weight=1)

        ttk.Button(self, text="Guardar Cambios", command=self.save_changes).pack(pady=10)

    def load_fields(self):
        tone = self.selected_tone.get()
        if tone in self.presets:
            for key, entry in self.entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(self.presets[tone].get(key, "")))

    def choose_color(self, entry):
        color_code = colorchooser.askcolor(title="Elegí un color")[1]
        if color_code:
            entry.delete(0, tk.END)
            entry.insert(0, color_code)

    def save_changes(self):
        tone = self.selected_tone.get()
        if not tone:
            messagebox.showwarning("Atención", "Seleccioná un tono para editar.")
            return

        for key, entry in self.entries.items():
            value = entry.get().strip()
            if key in ["fontsize", "stroke_width"]:
                try:
                    value = int(value)
                except ValueError:
                    messagebox.showerror("Error", f"{key} debe ser un número.")
                    return
            self.presets[tone][key] = value

        with open(STYLE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.presets, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Guardado", "Cambios guardados correctamente.")

if __name__ == "__main__":
    app = StyleEditor()
    app.mainloop()
