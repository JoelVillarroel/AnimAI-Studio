def get_visual_preset(tone):
    presets = {
        "drama": {
            "font": "Arial-Bold",
            "fontsize": 64,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 3,
            "text_position": "center",
            "anim_modes": ["zoom_lento", "paneo_diagonal"],
            "fade_duration": 0.5
        },
        "comedia": {
            "font": "Comic-Sans-MS",
            "fontsize": 60,
            "color": "yellow",
            "stroke_color": "red",
            "stroke_width": 2,
            "text_position": "bottom",
            "anim_modes": ["zoom_rapido", "rebotar"],
            "fade_duration": 0.2
        },
        "filosófico": {
            "font": "Georgia",
            "fontsize": 54,
            "color": "lightblue",
            "stroke_color": "black",
            "stroke_width": 1,
            "text_position": "top",
            "anim_modes": ["zoom_etereo", "paneo_lento"],
            "fade_duration": 0.4
        },
        "neutro": {
            "font": "Arial",
            "fontsize": 60,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 2,
            "text_position": "bottom",
            "anim_modes": ["zoom_suave"],
            "fade_duration": 0.3
        }
    }
    return presets.get(tone, presets["neutro"])
