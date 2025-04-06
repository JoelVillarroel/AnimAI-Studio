import os

os.environ["IMAGEMAGICK_BINARY"] = "C:/Program Files/ImageMagick-7.1.1-Q16/magick.exe"

from utils.config_loader import load_config
from utils.audio_tools import get_audio_duration
from utils.subtitle_gen import generate_subtitles
from utils.whisper_subtitle_gen import generate_whisper_subtitles, whisper_transcribe_text
from utils.metadata_generator import generate_video_metadata
from utils.animator import create_video_with_animation
from utils.style_engine import analyze_script

def main():
    print("[🧠] AnimAI Studio inicializado...")

    config = load_config("config.json")
    audio_path = config["audio_path"]
    script_path = config["script_path"]
    images_folder = config["images_folder"]
    output_path = config["output_path"]
    subtitle_engine = config.get("subtitle_engine", "basic")

    for path in [audio_path, images_folder]:
            # Verificar existencia de archivos importantes
        missing = []

        if not os.path.exists(audio_path):
            missing.append(f"Audio: {audio_path}")
        if not os.path.exists(images_folder):
            missing.append(f"Carpeta de imágenes: {images_folder}")

        if missing:
            print("[❌] Faltan archivos necesarios:")
            for m in missing:
                print(f"    - {m}")
            return

    # Transcripción automática si no existe el script
    if not os.path.exists(script_path):
        print("[INFO] No se encontró script. Transcribiendo desde audio...")
        transcribed_text = whisper_transcribe_text(audio_path)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(transcribed_text)
        print("[OK] Script generado desde audio.")

    print("[INFO] Calculando duración del audio...")
    duration = get_audio_duration(audio_path)
    print(f"[✅] Duración del audio: {duration:.2f} segundos")

    print("[INFO] Analizando tono del guion...")
    tone = analyze_script(script_path)
    print(f"[🎭] Tono detectado: {tone}")

    print("[INFO] Generando subtítulos...")
    if subtitle_engine == "whisper":
        subtitles = generate_whisper_subtitles(audio_path)
    else:
        subtitles = generate_subtitles(audio_path, script_path)

    for sub in subtitles:
        print(f"{sub['start']:.2f}s - {sub['end']:.2f}s: {sub['text']}")

    print("[INFO] Generando metadata para YouTube...")
    generate_video_metadata(script_path, tone=tone)

    print("[🎬] Produciendo video final...")
    print(f"[DEBUG] Tone en main.py: {tone}")  # Verifica que 'tone' está bien antes de pasar a la siguiente función
    create_video_with_animation(images_folder, subtitles, audio_path, duration, output_path, tone=tone)

    print(f"[✅] Video generado correctamente en: {output_path}")

if __name__ == "__main__":
    main()
