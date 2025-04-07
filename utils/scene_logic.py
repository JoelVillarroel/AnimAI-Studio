from moviepy.editor import (
    ImageClip, CompositeVideoClip
)
from moviepy.video.fx.all import resize, zoom_in, fadein, fadeout
import os
import random
import json

# Cargar configuración de reacciones del host
with open("config/host_reactions.json", "r", encoding="utf-8") as f:
    HOST_REACTIONS = json.load(f)

def apply_reactions(host_clip, phrase):
    lower_phrase = phrase.lower()
    for effect_name, triggers in HOST_REACTIONS.items():
        if any(trigger in lower_phrase for trigger in triggers):
            if effect_name == "zoom_and_fade":
                host_clip = zoom_in(host_clip, 1.1)
                host_clip = fadein(host_clip, 0.3).fx(fadeout, 0.3)
            elif effect_name == "fade_only":
                host_clip = fadein(host_clip, 0.5).fx(fadeout, 0.5)
            elif effect_name == "zoom_in":
                host_clip = zoom_in(host_clip, 1.2)
            elif effect_name == "shake":
                # Movimiento leve horizontal
                host_clip = host_clip.set_position(lambda t: (100 + int(10 * random.uniform(-1, 1)), 500))
            elif effect_name == "blur":
                from moviepy.video.fx.all import blur
                host_clip = host_clip.fx(blur, 2)
            # Se pueden agregar más efectos aquí
    return host_clip

def validate_reactions():
    known_effects = {"zoom_and_fade", "fade_only", "zoom_in"}  # Agregá acá los que vayas creando
    with open("config/host_reactions.json", "r", encoding="utf-8") as f:
        reactions = json.load(f)

    for effect, triggers in reactions.items():
        if effect not in known_effects:
            print(f"[WARN] El efecto '{effect}' no está implementado en apply_reactions()")
        if not triggers:
            print(f"[WARN] El efecto '{effect}' no tiene palabras clave asignadas")

def build_scene_clip(subtitle, tone):
    dur = subtitle["end"] - subtitle["start"]
    text = subtitle["text"]

    scene_info = analyze_scene_components(text)
    pose = scene_info["pose"]
    bg_name = scene_info["scene"]

    # Cargar fondo
    bg_path = os.path.join("assets", "scenes", bg_name)

    if not os.path.exists(bg_path):
        print(f"[WARN] Fondo no encontrado: {bg_path} → usando fondo neutro.")
        bg_path = os.path.join("assets", "backgrounds", "oficina.png")  # fallback

    bg_clip = ImageClip(bg_path).set_duration(dur)
    bg_clip = resize(bg_clip, height=1080)

    # Si la oración tiene múltiples frases separadas por puntos o comas
    phrases = [p.strip() for p in text.split(".") if p.strip()] + [p.strip() for p in text.split(",") if p.strip()]
    phrases = list(dict.fromkeys(phrases))[:2]  # máximo 2 cambios de emoción

    host_clips = []
    for i, phrase in enumerate(phrases):
        sub_dur = dur / len(phrases)
        comp = analyze_scene_components(phrase)
        sub_pose_path = os.path.join("assets", "characters", "host", f"{comp['pose']}.png")

        if not os.path.exists(sub_pose_path):
            print(f"[WARN] Pose no encontrada: {sub_pose_path} → usando idle.png.")
            sub_pose_path = os.path.join("assets", "characters", "host", "idle.png")

        if os.path.exists(sub_pose_path):
            host = ImageClip(sub_pose_path).set_duration(sub_dur)
            host = resize(host, height=500)

            def host_pos(t):
                x = 100 + int(10 * random.uniform(-1, 1) * (t % 0.3))
                y = 500 + int(5 * random.uniform(-1, 1) * (t % 0.3))
                return (x, y)

            host = host.set_position(host_pos).set_start(i * sub_dur)
            host = apply_reactions(host, phrase)
            host_clips.append(host)

    if host_clips:
        scene = CompositeVideoClip([bg_clip] + host_clips).set_duration(dur)
    else:
        scene = bg_clip

    return scene

def detect_emotion(text):
    text = text.lower()
    if any(word in text for word in ["jajaja", "risa", "chiste", "divertido"]):
        return "humor"
    elif any(word in text for word in ["gritar", "odio", "nooo", "maldito", "furioso"]):
        return "ira"
    elif any(word in text for word in ["triste", "llanto", "soledad", "dolor"]):
        return "tristeza"
    elif any(word in text for word in ["¿", "cómo", "por qué", "dónde"]):
        return "confusion"
    elif any(word in text for word in ["sueño", "galaxia", "universo", "pensar"]):
        return "reflexion"
    elif any(word in text for word in ["asco", "asqueroso", "repugnante"]):
        return "disgusto"
    elif any(word in text for word in ["ups", "torpe", "vergüenza"]):
        return "verguenza"
    elif any(word in text for word in ["meh", "ok", "ajá"]):
        return "neutral"
    elif any(word in text for word in ["cool", "tranqui", "todo bien"]):
        return "cool"
    elif any(word in text for word in ["maldito", "explotó", "rompí", "ira total"]):
        return "ira"
    elif any(word in text for word in ["asco", "vomito", "puaj", "repugnante"]):
        return "disgusto"
    elif any(word in text for word in ["jodido", "vergüenza", "torpe"]):
        return "verguenza"
    elif any(word in text for word in ["nerd", "sistema", "analicé", "curioso"]):
        return "curioso"
    elif any(word in text for word in ["qué carajo", "¡no!", "temblando", "me muero"]):
        return "terror"
    elif any(word in text for word in ["ah claro", "sí sí", "jajaja... claro"]):
        return "sarcasmo"
    return "neutro"

def get_scene_for_emotion(emotion):
    scenes = {
        "humor": ["calle.png", "oficina.png"],
        "ira": ["pesadilla.png", "oficina.png"],
        "tristeza": ["habitacion.png"],
        "confusion": ["habitacion.png", "galaxia.png"],
        "reflexion": ["galaxia.png"],
        "disgusto": ["oficina.png"],
        "verguenza": ["habitacion.png"],
        "neutral": ["oficina.png"],
        "cool": ["calle.png"],
        "neutro": ["oficina.png"]
    }
    return scenes.get(emotion, ["oficina.png"])[0]

def get_pose_for_emotion(emotion):
    poses = {
        "humor": "laughing",
        "ira": "angry_extreme",
        "tristeza": "sad",
        "confusion": "confused",
        "reflexion": "thinking",
        "disgusto": "sick",
        "verguenza": "awkward",
        "neutral": "idle",
        "cool": "cool",
        "sarcasmo": "smirk",
        "terror": "screaming",
        "curioso": "nerdy",
        "neutro": "idle"
    }
    return poses.get(emotion, "idle")

def get_recommended_animation(emotion):
    anims = {
        "humor": "rebotar",
        "ira": "zoom_rapido",
        "tristeza": "zoom_lento",
        "confusion": "paneo_diagonal",
        "reflexion": "zoom_etereo",
        "disgusto": "paneo_lento",
        "verguenza": "zoom_lento",
        "neutral": "zoom_suave",
        "cool": "paneo_lento",
        "neutro": "zoom_suave"
    }
    return anims.get(emotion, "zoom_suave")

def analyze_scene_components(text):
    emotion = detect_emotion(text)
    scene = get_scene_for_emotion(emotion)
    pose = get_pose_for_emotion(emotion)
    anim = get_recommended_animation(emotion)
    return {
        "emotion": emotion,
        "scene": scene,
        "pose": pose,
        "animation": anim
    }
