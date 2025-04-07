from utils.audio_tools import get_audio_duration

def generate_subtitles(audio_path, script_path):
    duration = get_audio_duration(audio_path)
    if duration <= 0:
        print("[❌] Duración de audio inválida.")
        return []

    try:
        with open(script_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[❌] No se encontró el archivo de guion: {script_path}")
        return []

    num_lines = len(lines)
    if num_lines == 0:
        print("[❌] El guion está vacío.")
        return []

    segment_duration = duration / num_lines
    subtitles = []
    for i, line in enumerate(lines):
        start = i * segment_duration
        end = (i + 1) * segment_duration
        subtitles.append({
            "start": start,
            "end": end,
            "text": line
        })

    return subtitles
