import sys
import os
import json
from moviepy.editor import CompositeVideoClip
from utils.config_loader import load_config
from utils.audio_tools import get_audio_duration
from utils.subtitle_gen import generate_subtitles
from utils.style_engine import get_style_for, analyze_script
from utils.scene_composer import build_scene_clip
from utils.whisper_subtitle_gen import generate_whisper_subtitles
from PIL import Image

if len(sys.argv) < 2:
    print("Uso: python preview_scene.py <fecha> [índice_escena]")
    sys.exit(1)
    

date = sys.argv[1]
scene_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0

config = load_config("config.json")
audio_path = os.path.join("audio", date, "narration.wav")
script_path = os.path.join("scripts", date, "script.txt")

if not os.path.exists(audio_path):
    print(f"[❌] No se encontró el audio: {audio_path}")
    sys.exit(1)

if not os.path.exists(script_path):
    print(f"[❌] No se encontró el guion: {script_path}")
    sys.exit(1)

print(f"[INFO] Mostrando vista previa para: {date}, escena {scene_index}")

duration = get_audio_duration(audio_path)
tone = analyze_script(script_path)
style = get_style_for(tone)


subtitle_engine = config.get("subtitle_engine", "basic")

if subtitle_engine == "whisper":
    subtitles = generate_whisper_subtitles(audio_path)
else:
    subtitles = generate_subtitles(audio_path, script_path)

if not subtitles:
    print("[ERROR] No se generaron subtítulos.")
    sys.exit(1)

if scene_index >= len(subtitles):
    print(f"[ERROR] El índice de escena {scene_index} excede el número total de escenas ({len(subtitles)}).")
    sys.exit(1)

scene_clip = build_scene_clip(subtitles[scene_index], tone)

# Guardar frame como miniatura con nombre único
thumbnail_path = f"preview_thumbnail_{date}_s{scene_index}.png"
scene_clip.save_frame(thumbnail_path, t=0.5)

# También guardar un alias como "preview_thumbnail.png" para mostrar en el panel
Image.open(thumbnail_path).save("preview_thumbnail.png")

# Mostrar preview
scene_clip.preview(fps=24)

# Guardar historial de miniaturas
history_path = "preview_history.json"
if os.path.exists(history_path):
    with open(history_path, "r", encoding="utf-8") as f:
        preview_history = json.load(f)
else:
    preview_history = []

# Añadir nueva miniatura al historial
thumbnail_data = {
    "date": date,
    "scene_index": scene_index,
    "thumbnail": thumbnail_path
}
preview_history.append(thumbnail_data)

with open(history_path, "w", encoding="utf-8") as f:
    json.dump(preview_history, f, indent=2)
