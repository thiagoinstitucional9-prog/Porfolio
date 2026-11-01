from youtube_transcript_api import YouTubeTranscriptApi

api = YouTubeTranscriptApi()
partes = api.fetch("cWBaLICTnJo", languages=["es", "es-419", "en"])

texto = " ".join(p.text.replace("\n", " ") for p in partes)

with open("transcripcion.txt", "w", encoding="utf-8") as f:
    f.write(texto)

print(len(texto.split()), "palabras")

palabras = open("transcripcion.txt", encoding="utf-8").read().split()
n = 10                      # cantidad de capítulos
tam = -(-len(palabras) // n)

with open("libro.txt", "w", encoding="utf-8") as f:
    for i in range(n):
        f.write(f"\n\nCapítulo {i+1}\n\n")
        f.write(" ".join(palabras[i*tam:(i+1)*tam]))

print("Listo:", len(palabras), "palabras en", n, "capítulos")