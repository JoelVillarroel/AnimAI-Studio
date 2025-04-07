import json
import os

def generate_video_metadata(script_path, tone="neutro", branding="<joexe>"):
    with open(script_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        full_text = " ".join(lines).lower()

    if any(word in full_text for word in ["call center", "encierro", "gritar", "horrible"]):
        theme = "Una historia real desde adentro de un trabajo terrible."
        title = "Lo que viví en ese trabajo fue inhumano"
        hashtags = "#callcenter #joexe #humornegro #trabajo #argentina"
    elif any(word in full_text for word in ["existencia", "universo", "vida"]):
        theme = "Una reflexión existencial con imágenes que te hacen pensar."
        title = "¿Qué sentido tiene todo esto?"
        hashtags = "#filosofía #reflexión #joexe #pensar #universo"
    elif any(word in full_text for word in ["jajaja", "broma", "risa", "absurdo"]):
        theme = "Una historia absurda contada con humor sarcástico."
        title = "Esto no tiene sentido... pero te va a hacer reír"
        hashtags = "#humor #absurdo #joexe #animación #historias"
    else:
        theme = "Un relato con imágenes animadas y mucho estilo."
        title = "Esta historia no la vas a olvidar"
        hashtags = "#joexe #historias #animación #argentina"

    description = f"{theme}\n\nProducido por {branding}. Suscribite para más historias como esta.\n\n{hashtags}"

    metadata = {
        "title": title,
        "description": description
    }

    os.makedirs("output", exist_ok=True)
    with open("output/video_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("[OK] Metadata generada en output/video_metadata.json")
    print("\n--- TÍTULO ---")
    print(title)
    print("\n--- DESCRIPCIÓN ---")
    print(description)
    print("\n---------------------")

    return metadata


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python metadata_generator.py scripts/2025-04-06.txt")
        exit(1)

    generate_video_metadata(sys.argv[1])
