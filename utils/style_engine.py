import json
import os

STYLE_PRESETS_PATH = "config/style_presets.json"

def _load_presets():
    if not os.path.exists(STYLE_PRESETS_PATH):
        raise FileNotFoundError(f"No se encontró el archivo: {STYLE_PRESETS_PATH}")
    
    with open(STYLE_PRESETS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_style_for(tone):
    presets = _load_presets()
    return presets.get(tone, presets.get("neutro"))

def get_visual_preset(tone):
    # Alias para get_style_for(), usado por animator.py
    return get_style_for(tone)
