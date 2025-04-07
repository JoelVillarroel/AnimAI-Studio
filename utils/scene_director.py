def get_animation_mode(text, tone="neutro"):
    text = text.lower()

    if any(word in text for word in ["gritar", "explosión", "escape", "horrible", "nooo", "¡"]):
        return "zoom_rapido"
    elif any(word in text for word in ["jajaja", "risa", "broma", "absurdo"]):
        return "rebotar"
    elif any(word in text for word in ["sueño", "universo", "eterno", "galaxia"]):
        return "zoom_etereo"
    elif any(word in text for word in ["así fue", "finalmente", "y entonces"]):
        return "paneo_lento"
    elif any(word in text for word in ["mirá", "te muestro", "observá"]):
        return "paneo_diagonal"

    # fallback según tono general
    tone_defaults = {
        "drama": "zoom_lento",
        "comedia": "zoom_rapido",
        "filosófico": "zoom_etereo",
        "neutro": "zoom_suave"
    }
    return tone_defaults.get(tone, "zoom_suave")
