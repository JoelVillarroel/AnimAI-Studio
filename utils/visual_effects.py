from moviepy.video.fx.all import blur, colorx
from moviepy.editor import VideoClip
import random
import numpy as np
from moviepy.video.fx.all import blur, colorx, invert_colors

def apply_emotion_effect(clip: VideoClip, text: str, tone: str) -> VideoClip:
    text = text.lower()

    if any(word in text for word in ["gritar", "temblor", "explosión", "caos"]):
        return add_glitch_effect(clip)
    elif any(word in text for word in ["temblando", "miedo", "shock"]):
        return apply_shake(clip)
    elif any(word in text for word in ["sueño", "pensar", "duda", "silencio"]):
        return clip.fx(blur, 2)
    elif any(word in text for word in ["delirio", "locura"]):
        return clip.fx(invert_colors)
    elif tone == "filosófico":
        return clip.fx(colorx, 0.9)
    elif tone == "drama":
        return clip.fx(colorx, 0.8)
    elif tone == "comedia":
        return clip.fx(colorx, 1.2)
    return clip

def apply_shake(clip: VideoClip) -> VideoClip:
    def shake(t):
        x = int(10 * random.uniform(-1, 1))
        y = int(5 * random.uniform(-1, 1))
        return (x, y)
    return clip.set_position(shake)

def add_glitch_effect(clip: VideoClip) -> VideoClip:
    def jitter(get_frame, t):
        frame = get_frame(t)
        dx = random.randint(-5, 5)
        dy = random.randint(-5, 5)
        new_frame = np.zeros_like(frame)
        h, w = frame.shape[:2]
        src_x1 = max(-dx, 0)
        src_y1 = max(-dy, 0)
        dst_x1 = max(dx, 0)
        dst_y1 = max(dy, 0)
        src_x2 = w - abs(dx)
        src_y2 = h - abs(dy)
        new_frame[dst_y1:dst_y1 + src_y2, dst_x1:dst_x1 + src_x2] = frame[src_y1:src_y1 + src_y2, src_x1:src_x1 + src_x2]
        return new_frame

    return clip.fl(jitter, apply_to=["mask", "video"])
