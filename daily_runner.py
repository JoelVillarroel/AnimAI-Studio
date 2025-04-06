import os
import datetime
from utils.audio_tools import get_audio_duration
from utils.subtitle_gen import generate_subtitles
from utils.whisper_subtitle_gen import generate_whisper_subtitles, whisper_transcribe_text
from utils.metadata_generator import generate_video_metadata
from utils.animator import create_video_with_animation
from utils.style_engine import analyze_script
from utils.visual_presets import get_visual_preset

def process_day_folder(day_folder):
    audio_path = os.path.join(day_folder, "audio.wav")
    script_path = os.path.join(day_folder, "script.txt")
    images_folder = os.path.join(day_folder, "images")
    output_folder = os.path.join("output", os.path.basename(day_folder))
    output_path = os.path.join(output_folder, "video.mp4")

    if not (os.path.exists(audio_path) and os.path.isdir(images_folder)):
        print(f"[SKIP] Carpeta incompleta: {day_folder}")
        return
    # Verificaciones
    missing = []
    if not os.path.exists(audio_path):
        missing.append("audio.wav")
    if not os.path.isdir(images_folder):
        missing.append("carpeta de imágenes")
    if missing:
        print(f"[❌] Faltan elementos en {day_folder}: {', '.join(missing)}")
        return
    if os.path.exists(output_path):
        print(f"[SKIP] Video ya existe: {output_path}")
        return

    # Transcripción automática si no existe el script
    if not os.path.exists(script_path):
        print("[INFO] No se encontró script. Transcribiendo desde audio...")
        transcribed_text = whisper_transcribe_text(audio_path)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(transcribed_text)
        print("[OK] Script generado desde audio.")

    os.makedirs(output_folder, exist_ok=True)

    print(f"[INFO] Procesando carpeta: {day_folder}")
    duration = get_audio_duration(audio_path)
    print(f"[OK] Duración del audio: {duration:.2f} segundos")

    tone = analyze_script(script_path)
    print(f"[INFO] Tono detectado: {tone}")

    print("[INFO] Generando subtítulos con Whisper...")
    subtitles = generate_whisper_subtitles(audio_path)

    print("[INFO] Generando metadata...")
    generate_video_metadata(script_path, tone=tone)

    print("[INFO] Generando video...")
    create_video_with_animation(images_folder, subtitles, audio_path, duration, output_path, tone=tone)

    print(f"[✅] Video final guardado en: {output_path}\n")

def run_daily_production(base_dir="scripts", mode="today"):
    if mode == "today":
        today = datetime.date.today().isoformat()
        day_folder = os.path.join(base_dir, today)
        process_day_folder(day_folder)
    elif mode == "all":
        for entry in sorted(os.listdir(base_dir)):
            day_folder = os.path.join(base_dir, entry)
            if os.path.isdir(day_folder):
                process_day_folder(day_folder)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "today"
    run_daily_production(mode=mode)
