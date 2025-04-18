import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json
import subprocess
from datetime import datetime
from utils.edit_host_reactions import ReactionEditor

SCRIPTS_DIR = "scripts"
OUTPUT_DIR = "output"
CONFIG_PATH = "config.json"
STYLE_PATH = "config/style_presets.json"

class ControlPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AnimAI Studio - Panel de Control")
        self.geometry("800x800")

        self.selected_date = tk.StringVar()
        self.music_volume = tk.DoubleVar()

        self.load_config()
        self.create_widgets()
        self.load_dates()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.music_volume.set(config.get("music_volume", 0.2))


    def save_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}

        config["music_volume"] = self.music_volume.get()

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def create_widgets(self):
        

        # Dentro de create_widgets()
        frame_top = ttk.Frame(self)
        frame_top.pack(pady=10)

        self.thumbnail_combo = ttk.Combobox(frame_top, state="readonly")
        self.thumbnail_combo.pack(side=tk.LEFT, padx=5)

        self.load_previous_thumbnails()

        frame_top = ttk.Frame(self)
        frame_top.pack(pady=10)

        frame_presets = ttk.LabelFrame(self, text="Presets de Producción")
        frame_presets.pack(fill=tk.X, padx=10, pady=10)

        self.preset_combo = ttk.Combobox(frame_presets, state="readonly")
        self.preset_combo.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(frame_presets, text="Aplicar", command=self.apply_selected_preset).pack(side=tk.LEFT, padx=5)

        self.load_presets()

        ttk.Label(frame_top, text="Fechas disponibles:").pack(side=tk.LEFT, padx=5)
        self.date_combo = ttk.Combobox(frame_top, textvariable=self.selected_date, state="readonly")
        self.date_combo.pack(side=tk.LEFT)

        ttk.Button(frame_top, text="📝 Editar guion", command=self.open_script_editor).pack(side=tk.LEFT, padx=5)
        

        ttk.Label(frame_top, text="Escena:").pack(side=tk.LEFT, padx=5)
        self.scene_spinbox = ttk.Spinbox(frame_top, from_=0, to=20, width=5)
        self.scene_spinbox.pack(side=tk.LEFT)
        self.scene_spinbox.bind("<Button-3>", lambda e: self.preview_selected())

        self.scene_count_label = ttk.Label(frame_top, text="")
        self.scene_count_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(frame_top, text="Procesar", command=self.process_selected).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_top, text="Vista previa escena", command=self.preview_selected).pack(side=tk.LEFT)
        ttk.Button(frame_top, text="Estimar duración", command=self.estimate_video_duration).pack(side=tk.LEFT, padx=5)
        self.preview_thumb_label = ttk.Label(self)
        self.preview_thumb_label.pack(pady=5)

        frame_config = ttk.LabelFrame(self, text="Configuración de música")
        frame_config.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_config, text="Volumen de música de fondo (0.0 a 1.0):").pack(anchor="w", padx=10, pady=5)
        scale = ttk.Scale(frame_config, from_=0.0, to=1.0, variable=self.music_volume, orient=tk.HORIZONTAL)
        scale.pack(fill=tk.X, padx=10)
        ttk.Button(frame_config, text="Guardar configuración", command=self.save_config).pack(pady=5)

        frame_style = ttk.LabelFrame(self, text="Estilo visual del texto")
        frame_style.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(frame_style, text="Editar estilo visual", command=self.open_style_editor).pack(pady=5)

        self.thumbnail_label = ttk.Label(self)
        self.thumbnail_label.pack(pady=10)

        self.meta_text = tk.Text(self, height=10, wrap=tk.WORD)
        self.meta_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(self, text="Copiar título y descripción", command=self.copy_metadata).pack(pady=5)
        ttk.Button(self, text="Editar Reacciones del Host", command=ReactionEditor).pack(pady=5)

        self.selected_date.trace_add("write", self.update_scene_limit)

    def open_style_editor(self):
        subprocess.Popen(["python", "utils/edit_style_presets.py"])

    def load_preview_thumbnail(self, date, scene_index):
        thumbnail_path = f"preview_thumbnail_{date}_s{scene_index}.png"
        
        # Mostrar miniatura si existe
        if os.path.exists(thumbnail_path):
            img = Image.open(thumbnail_path).resize((300, 170))
            self.thumbnail_image = ImageTk.PhotoImage(img)
            self.thumbnail_label.configure(image=self.thumbnail_image)
        else:
            self.thumbnail_label.configure(image=None)

    def load_previous_thumbnails(self):
                history_path = "preview_history.json"
                if os.path.exists(history_path):
                    with open(history_path, "r", encoding="utf-8") as f:
                        preview_history = json.load(f)

                    thumbnails = [f"{entry['date']} - Escena {entry['scene_index']}" for entry in preview_history]
                    self.thumbnail_combo["values"] = thumbnails
                    if thumbnails:
                        self.thumbnail_combo.set(thumbnails[0])  # Set the first one as selected

    def preview_selected(self):
        self.title(f"AnimAI Studio - Escena {scene_index + 1}")
        date = self.selected_date.get()
        if not date:
            messagebox.showwarning("Vista previa", "Seleccioná una fecha válida.")
            return

        try:
            from utils.config_loader import load_config
            from utils.subtitle_gen import generate_subtitles
            from utils.whisper_subtitle_gen import generate_whisper_subtitles

            config = load_config("config.json")
            audio_path = os.path.join("audio", date, "narration.wav")
            script_path = os.path.join("scripts", date, "script.txt")

            if config.get("subtitle_engine", "basic") == "whisper":
                subtitles = generate_whisper_subtitles(audio_path)
            else:
                subtitles = generate_subtitles(audio_path, script_path)

            max_scene = max(len(subtitles) - 1, 0)
            self.scene_spinbox.config(to=max_scene)
            self.scene_count_label.config(text=f"/ {max_scene + 1} escenas")

        except Exception as e:
            self.scene_spinbox.config(to=20)
            self.scene_count_label.config(text="/ ? escenas")

        try:
            scene_index = int(self.scene_spinbox.get())
            if scene_index < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El número de escena debe ser un entero positivo.")
            return

        try:
            scene_index = int(self.scene_spinbox.get())
            if scene_index < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El número de escena debe ser un entero positivo.")
            return

        if scene_index >= len(subtitles):
            messagebox.showerror("Error", f"El índice de escena {scene_index} excede el número total ({len(subtitles)}).")
            return

        # Mostrar datos de la escena
        selected_sub = subtitles[scene_index]
        text = selected_sub["text"]
        start = selected_sub["start"]
        end = selected_sub["end"]
        duration = end - start
        total_scenes = len(subtitles)

        info = (
            f"🎬 Escena {scene_index + 1} / {total_scenes}\n"
            f"🕓 Duración: {duration:.2f} segundos\n"
            f"📝 Texto:\n{text}"
        )
        messagebox.showinfo("Información de la escena", info)
        
        subprocess.run(["python", "preview_scene.py", date, str(scene_index)])
        
        # Cargar miniatura desde historial
        self.load_preview_thumbnail(date, scene_index)

    def load_presets(self):
        preset_folder = "presets"
        if not os.path.exists(preset_folder):
            os.makedirs(preset_folder)
        files = [f for f in os.listdir(preset_folder) if f.endswith(".json")]
        self.preset_combo["values"] = files
        if files:
            self.preset_combo.set(files[0])

    def apply_selected_preset(self):
        selected = self.preset_combo.get()
        if not selected:
            messagebox.showwarning("Presets", "Seleccioná un preset.")
            return

        preset_path = os.path.join("presets", selected)
        try:
            with open(preset_path, "r", encoding="utf-8") as f:
                preset = json.load(f)

            config_path = "config.json"
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            config.update(preset)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.load_config()
            messagebox.showinfo("Presets", f"Preset '{selected}' aplicado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar el preset: {e}")


    def update_scene_limit(self, *args):
        date = self.selected_date.get()
        if not date:
            return

        try:
            from utils.config_loader import load_config
            from utils.subtitle_gen import generate_subtitles
            from utils.whisper_subtitle_gen import generate_whisper_subtitles

            config = load_config("config.json")
            audio_path = os.path.join("audio", date, "narration.wav")
            script_path = os.path.join("scripts", date, "script.txt")

            if config.get("subtitle_engine", "basic") == "whisper":
                subtitles = generate_whisper_subtitles(audio_path)
            else:
                subtitles = generate_subtitles(audio_path, script_path)

            max_scene = max(len(subtitles) - 1, 0)
            self.scene_spinbox.config(to=max_scene)
            self.scene_count_label.config(text=f"/ {max_scene + 1} escenas")
        except:
            self.scene_spinbox.config(to=20)
            self.scene_count_label.config(text="/ ? escenas")

    def load_dates(self):
        dates = [d for d in os.listdir(SCRIPTS_DIR) if os.path.isdir(os.path.join(SCRIPTS_DIR, d))]
        dates.sort(reverse=True)
        self.date_combo["values"] = dates
        if dates:
            self.selected_date.set(dates[0])
    
    def open_script_editor(self):
        import tkinter as tk
        from tkinter import Toplevel, messagebox, scrolledtext
        import os

        date = self.selected_date.get()
        if not date:
            messagebox.showwarning("Atención", "Seleccioná una fecha primero.")
            return

        script_path = os.path.join("scripts", date, "script.txt")
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"No se encontró el guion: {script_path}")
            return

        editor = Toplevel(self)
        editor.title(f"Editar Guion - {date}")
        editor.geometry("700x600")

        text_area = scrolledtext.ScrolledText(editor, wrap=tk.WORD, font=("Arial", 12))
        text_area.pack(fill=tk.BOTH, expand=True)

        with open(script_path, "r", encoding="utf-8") as f:
            text_area.insert(tk.END, f.read())

        def guardar():
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(text_area.get("1.0", tk.END).strip())
            messagebox.showinfo("Listo", "Guion guardado correctamente.")
            editor.destroy()

        btn_guardar = ttk.Button(editor, text="Guardar", command=guardar)
        btn_guardar.pack(pady=5)

    def estimate_video_duration(self):
        import os
        from utils.config_loader import load_config
        from utils.audio_tools import get_audio_duration
        from utils.subtitle_gen import generate_subtitles
        from utils.whisper_subtitle_gen import generate_whisper_subtitles

        date = self.selected_date.get()
        if not date:
            messagebox.showwarning("Atención", "Seleccioná una fecha válida.")
            return

        config = load_config("config/config.json")
        audio_path = os.path.join("audio", date, "narration.wav")
        script_path = os.path.join("scripts", date, "script.txt")

        try:
            audio_duration = get_audio_duration(audio_path)
        except:
            messagebox.showerror("Error", "No se pudo leer el archivo de audio.")
            return

        if config.get("subtitle_engine", "basic") == "whisper":
            subtitles = generate_whisper_subtitles(audio_path)
        else:
            subtitles = generate_subtitles(audio_path, script_path)

        total_subs = len(subtitles)
        duration_est = sum([s["end"] - s["start"] for s in subtitles])
        info = f"🎵 Duración del audio: {audio_duration:.2f}s\n📝 Escenas: {total_subs}\n🎬 Duración estimada del video: {duration_est:.2f}s"

        messagebox.showinfo("Estimación del video", info)

    
    def run_validator(self):
        import subprocess
        result = subprocess.run(["python", "utils/validate_system.py"], capture_output=True, text=True)

        if result.returncode == 0:
            messagebox.showinfo("Validación completada", result.stdout)
        else:
            messagebox.showwarning("Problemas encontrados", result.stdout + "\n" + result.stderr)

    def process_selected(self):
        date = self.selected_date.get()
        if not date:
            messagebox.showwarning("Atención", "Seleccioná una fecha.")
            return
        
        if not os.path.exists(os.path.join("scripts", date)):
            messagebox.showerror("Error", f"No se encontró la carpeta de guion para {date}")
            return

        if not os.path.exists(os.path.join("audio", date, "narration.wav")):
            messagebox.showerror("Error", f"No se encontró el audio para {date}")
            return
        
        output_path = os.path.join(OUTPUT_DIR, date, "video.mp4")
        if os.path.exists(output_path):
            if not messagebox.askyesno("Ya existe", "Ese día ya fue procesado. ¿Reprocesar?"):
                return
            
        if not self.validate_before_render():
            return

        result = subprocess.run(["python", "daily_runner.py", date], capture_output=True, text=True)
        if result.returncode == 0:
            messagebox.showinfo("Éxito", f"Video generado para {date}.")
            self.load_metadata_and_thumbnail(date)
        else:
            messagebox.showerror("Error", f"Hubo un error al procesar {date}:{result.stderr}")

    def load_metadata_and_thumbnail(self, date):
        meta_path = os.path.join(OUTPUT_DIR, date, "video_metadata.json")
        thumb_path = os.path.join(OUTPUT_DIR, date, "thumbnail.png")

        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.meta_text.delete("1.0", tk.END)
                self.meta_text.insert(tk.END, f"TÍTULO:\n{data.get('title')}\n\nDESCRIPCIÓN:\n{data.get('description')}")

        if os.path.exists(thumb_path):
            img = Image.open(thumb_path).resize((300, 170))
            self.thumbnail_image = ImageTk.PhotoImage(img)
            self.thumbnail_label.configure(image=self.thumbnail_image)
        else:
            self.thumbnail_label.configure(image="")

    def copy_metadata(self):
        metadata = self.meta_text.get("1.0", tk.END).strip()
        if metadata:
            self.clipboard_clear()
            self.clipboard_append(metadata)
            messagebox.showinfo("Copiado", "Título y descripción copiados al portapapeles.")

    def validate_before_render(self):
        import os
        from utils.config_loader import load_config
        from utils.audio_tools import get_audio_duration
        from utils.subtitle_gen import generate_subtitles
        from utils.whisper_subtitle_gen import generate_whisper_subtitles

        date = self.selected_date.get()
        if not date:
            messagebox.showwarning("Atención", "Seleccioná una fecha válida.")
            return False

        try:
            config = load_config("config/config.json")
        except:
            messagebox.showerror("Error", "No se pudo cargar el archivo de configuración.")
            return False

        audio_path = os.path.join("audio", date, "narration.wav")
        script_path = os.path.join("scripts", date, "script.txt")
        images_folder = os.path.join("scripts", date, "images")

        if not os.path.exists(audio_path):
            messagebox.showerror("Error", f"No se encontró el archivo de audio: {audio_path}")
            return False

        if not os.path.exists(script_path):
            messagebox.showwarning("Advertencia", f"No se encontró el guion: {script_path}. Se intentará transcribir automáticamente.")
        
        if not os.path.isdir(images_folder):
            messagebox.showwarning("Advertencia", f"No se encontraron imágenes en: {images_folder}. Se usarán fondos por defecto.")

        try:
            audio_duration = get_audio_duration(audio_path)
        except:
            messagebox.showerror("Error", "No se pudo leer el archivo de audio.")
            return False

        if config.get("subtitle_engine", "basic") == "whisper":
            subtitles = generate_whisper_subtitles(audio_path)
        else:
            if not os.path.exists(script_path):
                messagebox.showerror("Error", "No hay script para generar subtítulos básicos.")
                return False
            subtitles = generate_subtitles(audio_path, script_path)

        if not subtitles:
            messagebox.showerror("Error", "No se pudieron generar subtítulos.")
            return False

        return True

if __name__ == "__main__":
    app = ControlPanel()
    app.mainloop()
