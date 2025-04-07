from moviepy.editor import (
    ImageClip, TextClip, AudioFileClip, CompositeVideoClip,
    CompositeAudioClip, concatenate_videoclips
)
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.all import resize
from PIL import Image, ImageDraw, ImageFont
import os
import json
from utils.style_engine import get_visual_preset
from utils.scene_director import get_animation_mode
from utils.scene_composer import build_scene_clip


def validate_image(img_path):
    try:
        with Image.open(img_path) as im:
            im.verify()
        return True
    except Exception as e:
        print(f"[ERROR] Imagen inválida o corrupta: {img_path} → {e}")
        return False

def get_dynamic_animation(base_clip, dur, mode="zoom_suave"):
    if mode == "zoom_rapido":
        return base_clip.resize(lambda t: 1 + 0.1 * (t / dur))
    elif mode == "zoom_lento":
        return base_clip.resize(lambda t: 1 + 0.03 * (t / dur))
    elif mode == "zoom_suave":
        return base_clip.resize(lambda t: 1 + 0.05 * (t / dur))
    elif mode == "paneo_diagonal":
        return base_clip.set_position(lambda t: (int(10 * t), int(5 * t)))
    elif mode == "paneo_lento":
        return base_clip.set_position(lambda t: (int(4 * t), int(2 * t)))
    elif mode == "zoom_etereo":
        return base_clip.resize(lambda t: 1 + 0.02 * (t / dur)).set_position(lambda t: (int(2 * t), int(2 * t)))
    elif mode == "rebotar":
        return base_clip.set_position(lambda t: (int(20 * abs((t % 0.5) - 0.25)), 0))
    else:
        return base_clip

def save_thumbnail_from_video(video_clip, output_path="output/thumbnail.png", title="<joexe>"):
    thumbnail_time = min(3, video_clip.duration / 2)
    frame = video_clip.get_frame(thumbnail_time)
    img = Image.fromarray(frame)

    draw = ImageDraw.Draw(img)
    font_path = "assets/Roboto-Bold.ttf"
    if os.path.exists(font_path):
        font = ImageFont.truetype(font_path, 72)
        text_w, text_h = draw.textsize(title, font=font)
        draw.text(((img.width - text_w) // 2, 30), title, font=font, fill="white", stroke_fill="black", stroke_width=3)

    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((100, 100))
        img.paste(logo, (img.width - 120, 20), logo)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"[OK] Miniatura guardada en: {output_path}")

def get_music_volume():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            return float(config.get("music_volume", 0.2))
    except:
        return 0.2

from moviepy.editor import (
    ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
)
from moviepy.video.fx.all import resize, fadein, fadeout
import os
import random

def create_video_with_animation(images_folder, subtitles, audio_path, duration, output_path, tone):
    clips = []
    print(f"Este es el tone que recibe la función create_video_with_animation: {tone}")

    preset = get_visual_preset(tone)

    for i, subtitle in enumerate(subtitles):
        dur = subtitle["end"] - subtitle["start"]
        print(f"[DEBUG] Generando escena {i+1} con duración {dur:.2f}s")

        base_clip = build_scene_clip(subtitle, images_folder, tone, i)
        anim_mode = get_animation_mode(subtitle["text"], tone)
        animated_clip = get_dynamic_animation(base_clip, dur, anim_mode)

        txt_clip = TextClip(
            subtitle["text"],
            fontsize=preset["fontsize"],
            font=preset["font"],
            color=preset["color"],
            stroke_color=preset["stroke_color"],
            stroke_width=preset["stroke_width"],
            size=animated_clip.size,
            method="caption"
        ).set_duration(dur).set_position(preset["text_position"])

        scene = CompositeVideoClip([animated_clip, txt_clip]).set_duration(dur)
        scene = fadein(scene, preset["fade_duration"])
        scene = fadeout(scene, preset["fade_duration"])
        clips.append(scene)

    from utils.config_loader import load_config
    config = load_config("config.json")

    use_random_music = config.get("random_music", False)

    full_clips = []

    if config.get("include_intro", False):
        intro = get_intro_clip()
        full_clips.append(intro)

    full_clips.extend(clips)

    if config.get("include_outro", False):
        outro = get_outro_clip()
        full_clips.append(outro)

    main_video = concatenate_videoclips(full_clips, method="compose", padding=-0.5)
    logo_overlay = get_logo_clip(duration=main_video.duration)
    composed_video = CompositeVideoClip([main_video, logo_overlay.set_start(0)])
    composed_video = composed_video.set_duration(main_video.duration)

    final = composed_video

    # 🎧 Audio principal
    audio = AudioFileClip(audio_path)
    final_audio = audio.subclip(0, min(audio.duration, final.duration - 0.05))

    # 🎼 Música de fondo segura
    music_path = None
    music_folder = f"assets/music/{tone}"

    if use_random_music and os.path.isdir(music_folder):
        music_files = [os.path.join(music_folder, f) for f in os.listdir(music_folder)
                    if f.lower().endswith((".mp3", ".wav"))]
        if music_files:
            music_path = random.choice(music_files)
            print(f"[🎵] Música aleatoria seleccionada: {os.path.basename(music_path)}")
    else:
        default_path = f"{music_folder}.mp3"
        if os.path.exists(default_path):
            music_path = default_path
            print(f"[🎵] Música fija seleccionada: {os.path.basename(music_path)}")
    
    if os.path.isdir(music_folder):
        music_files = [os.path.join(music_folder, f) for f in os.listdir(music_folder)
                    if f.lower().endswith((".mp3", ".wav"))]
        if music_files:
            music_path = random.choice(music_files)
    if os.path.exists(music_path):
        music_volume = get_music_volume()
        music_clip = AudioFileClip(music_path)

        # Asegurar duración segura para mezcla
        safe_duration = min(final_audio.duration, music_clip.duration - 0.05)
        music = music_clip.subclip(0, safe_duration).volumex(music_volume)
        final_audio = final_audio.subclip(0, safe_duration)

        combined_audio = CompositeAudioClip([music, final_audio])
        final = final.set_audio(combined_audio)
        print(f"[INFO] Música de fondo aplicada: {tone} ({music_volume})")
    else:
        final = final.set_audio(final_audio)
        print("[INFO] No se encontró música de fondo para este tono.")

    # 🖼️ Miniatura
    save_thumbnail_from_video(final)

    # 💾 Exportación
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
        ffmpeg_params=["-movflags", "+faststart"],
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )

def get_logo_clip(duration=3, pos=("right", "top")):
    logo = ImageClip("assets/logo.png").set_duration(duration)
    logo = resize(logo, height=80)
    logo = logo.set_position(pos).margin(right=20, top=20, opacity=0)
    logo = fadein(logo, 1)
    logo = fadeout(logo, 1)
    return logo

def get_intro_clip():
    logo = ImageClip("assets/logo.png").set_duration(2)
    logo = resize(logo, height=150)
    logo = logo.set_position("center")
    logo = fadein(logo, 1)
    logo = fadeout(logo, 1)

    if os.path.exists("assets/bip.wav"):
        bip = AudioFileClip("assets/bip.wav").set_duration(2)
        return logo.set_audio(bip)
    return logo

def get_outro_clip():
    from moviepy.editor import TextClip

    outro_text = TextClip(
        "Gracias por ver\nSuscribite para más",
        fontsize=60,
        font="Arial-Bold",
        color="white",
        stroke_color="black",
        stroke_width=2,
        size=(1920, 1080),
        method="caption"
    ).set_duration(3).set_position("center")

    logo = ImageClip("assets/logo.png").set_duration(3)
    logo = resize(logo, height=100).set_position(("center", 800))

    return CompositeVideoClip([outro_text, logo])