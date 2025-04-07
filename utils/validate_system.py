import os
import json

def check_file(path, description):
    if not os.path.exists(path):
        print(f"[❌] Falta {description}: {path}")
        return False
    print(f"[✅] {description}: OK")
    return True

def validate_style_presets():
    path = "config/style_presets.json"
    print("\n🔎 Validando style_presets.json")
    if not os.path.exists(path):
        print("[❌] No se encontró style_presets.json")
        return False

    with open(path, "r", encoding="utf-8") as f:
        presets = json.load(f)

    required_keys = ["font", "fontsize", "color", "stroke_color", "stroke_width", "text_position", "anim_modes", "fade_duration"]
    all_ok = True

    for tone, preset in presets.items():
        for key in required_keys:
            if key not in preset:
                print(f"[⚠️] Falta '{key}' en tono '{tone}'")
                all_ok = False
    if all_ok:
        print("[✅] Todos los estilos están completos.")
    return all_ok

def validate_host_reactions():
    path = "config/host_reactions.json"
    print("\n🔎 Validando host_reactions.json")
    if not os.path.exists(path):
        print("[❌] No se encontró host_reactions.json")
        return False

    with open(path, "r", encoding="utf-8") as f:
        reactions = json.load(f)

    implemented_effects = {"zoom_and_fade", "fade_only", "zoom_in", "shake", "blur"}
    all_ok = True

    for effect, triggers in reactions.items():
        if effect not in implemented_effects:
            print(f"[⚠️] El efecto '{effect}' no está implementado.")
            all_ok = False
        if not triggers:
            print(f"[⚠️] El efecto '{effect}' no tiene palabras clave.")
            all_ok = False
    if all_ok:
        print("[✅] Reacciones del host válidas.")
    return all_ok

def validate_assets():
    print("\n🔎 Validando assets")
    folders = [
        "assets/logo.png",
        "assets/music",
        "assets/backgrounds",
        "assets/characters/host"
    ]
    all_ok = True
    for f in folders:
        if not os.path.exists(f):
            print(f"[❌] Falta: {f}")
            all_ok = False
        else:
            print(f"[✅] {f}: OK")
    return all_ok

def validate_config():
    print("\n🔎 Validando config.json")
    path = "config.json"
    if not os.path.exists(path):
        print("[❌] No se encontró config.json")
        return False
    with open(path, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
            print("[✅] config.json cargado correctamente.")
            if "whisper_model" in config:
                print(f"[INFO] whisper_model: {config['whisper_model']}")
            return True
        except:
            print("[❌] config.json tiene un error de sintaxis.")
            return False

def run_all_validations():
    print("\n==== VALIDACIÓN DE SISTEMA AnimAI Studio ====\n")

    status = {
        "config": validate_config(),
        "styles": validate_style_presets(),
        "reactions": validate_host_reactions(),
        "assets": validate_assets(),
    }

    if all(status.values()):
        print("\n🎉 Todo está OK. El sistema está listo para producir.")
    else:
        print("\n⚠️ Hay problemas. Revisá los mensajes anteriores.")

if __name__ == "__main__":
    run_all_validations()
