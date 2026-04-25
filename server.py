from flask import Flask, request, jsonify
import librosa
import numpy as np
import tempfile
import os

app = Flask(__name__)

def detectar_key(y, sr):
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    index = np.argmax(chroma_mean)

    return notas[index]

def calcular_energia(y):
    rms = np.mean(librosa.feature.rms(y=y))
    
    if rms < 0.02:
        return "Baixa"
    elif rms < 0.05:
        return "Média"
    else:
        return "Alta"

@app.route("/analisar", methods=["POST"])
def analisar():
    file = request.files["file"]

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        file.save(temp.name)
        path = temp.name

    try:
        y, sr = librosa.load(path)

        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        key = detectar_key(y, sr)
        energia = calcular_energia(y)

        return jsonify({
    "bpm": int(round(float(tempo))),
    "key": key,
    "energia": energia
})

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        os.remove(path)

if __name__ == "__main__":
    app.run(port=5000)