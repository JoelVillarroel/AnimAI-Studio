from pydub import AudioSegment

def get_audio_duration(audio_path):
    audio = AudioSegment.from_file(audio_path)
    return len(audio) / 1000  # duración en segundos