import whisper
import json
import os
from utils.config_loader import load_config

MODEL = None

def load_model():
    global MODEL
    if MODEL is None:
        print("[INFO] Cargando modelo Whisper...")

        config = load_config("config.json")
        model_name = config.get("whisper_model", "base")

        print(f"[INFO] Modelo configurado: {model_name}")
        MODEL = whisper.load_model(model_name)
    return MODEL

def generate_whisper_subtitles(audio_path, language="es"):
    model = load_model()

    if not os.path.exists(audio_path):
        print(f"[❌] Audio no encontrado: {audio_path}")
        return []

    print(f"[INFO] Transcribiendo audio con Whisper: {audio_path}")
    result = model.transcribe(audio_path, language=language)

    subtitles = []
    for segment in result["segments"]:
        subtitles.append({
            "start": float(segment["start"]),
            "end": float(segment["end"]),
            "text": segment["text"].strip()
        })

    return subtitles

def whisper_transcribe_text(audio_path):
    model = load_model()
    print(f"[INFO] Transcribiendo texto completo desde audio: {audio_path}")
    result = model.transcribe(audio_path, fp16=False)
    return result["text"]

def save_subtitles_to_json(subtitles, output_path="output/subtitles.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(subtitles, f, indent=2, ensure_ascii=False)
    print(f"[OK] Subtítulos guardados en {output_path}")
