from moviepy.editor import ImageClip, CompositeVideoClip
from moviepy.video.fx.all import resize
import os
import random

PREDEFINED_BACKGROUNDS = ["calle.png", "galaxia.png", "habitacion.png", "oficina.png", "pesadilla.png"]
HOST_POSES = ["angry.png", "confused.png", "idle.png", "laughing.png", "sad.png", "shocked.png", "talking.png", "thinking.png"]


def get_host_pose(text):
    text = text.lower()
    if any(w in text for w in ["jajaja", "risa", "chiste"]):
        return "laughing.png"
    elif any(w in text for w in ["gritar", "furioso", "enojado"]):
        return "angry.png"
    elif any(w in text for w in ["¿", "?", "qué", "cómo", "sorprendido"]):
        return "shocked.png"
    elif any(w in text for w in ["hola", "bienvenidos", "presento"]):
        return "talking.png"
    elif any(w in text for w in ["pensando", "reflexionando", "dudando"]):
        return "thinking.png"
    elif any(w in text for w in ["triste", "deprimido", "lamentable"]):
        return "sad.png"
    elif any(w in text for w in ["confuso", "no entiendo"]):
        return "confused.png"
    else:
        return "idle.png"

def build_scene_clip(subtitle, images_folder, tone, index):
    dur = subtitle["end"] - subtitle["start"]

    # 1. Intenta usar imagen personalizada
    image_files = sorted([
        f for f in os.listdir(images_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.startswith("default")
    ])

    bg_path = None
    if index < len(image_files):
        bg_path = os.path.join(images_folder, image_files[index])
        print(f"[OK] Usando imagen personalizada: {bg_path}")
    else:
        # 2. Si no hay imagen suficiente, usar fondo predeterminado según tono
        fallback = get_background_for_scene(tone)
        bg_path = os.path.join("assets", "backgrounds", fallback)
        print(f"[INFO] Usando fondo por tono: {bg_path}")

    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"No se encontró la imagen de fondo: {bg_path}")

    bg_clip = ImageClip(bg_path).set_duration(dur)
    bg_clip = resize(bg_clip, height=1080)

    # 3. Decide si agregar el host solo si no es imagen personalizada
    if index >= len(image_files):  # Solo agregar host si no hay imagen personalizada
        pose_file = get_host_pose(subtitle["text"])
        pose_path = os.path.join("assets", "characters", "host", pose_file)
        if os.path.exists(pose_path):
            host = ImageClip(pose_path).set_duration(dur)
            host = resize(host, height=500)
            def host_pos(t):
                x = 100 + int(10 * random.uniform(-1, 1) * (t % 0.3))
                y = 500 + int(5 * random.uniform(-1, 1) * (t % 0.3))
                return (x, y)
            host = host.set_position(host_pos)
            return CompositeVideoClip([bg_clip, host])

    return bg_clip


# Función para elegir un fondo adecuado basado en el tono
def get_background_for_scene(tone):
    """
    Selecciona un fondo apropiado en base al tono o el contexto de la escena.
    Si no se necesita un fondo especial, se elige uno aleatoriamente de los fondos predefinidos.
    """
    if tone == "drama":
        return "pesadilla.png"
    elif tone == "comedia":
        return "calle.png"
    elif tone == "filosófico":
        return "galaxia.png"
    else:
        # Si no hay un tono específico, elegir un fondo aleatorio
        return random.choice(PREDEFINED_BACKGROUNDS)