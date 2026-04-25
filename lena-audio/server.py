from flask import Flask, request, jsonify
import numpy as np
import tempfile
import os
from pydub import AudioSegment

app = Flask(__name__)

# -------- KEY DETECTION --------
def detectar_key(y, sr):
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    index = np.argmax(chroma_mean)

    return notas[index]

# -------- CAMELOT --------
camelot_map = {
    "C": "8B", "G": "9B", "D": "10B", "A": "11B", "E": "12B", "B": "1B",
    "F#": "2B", "C#": "3B", "G#": "4B", "D#": "5B", "A#": "6B", "F": "7B"
}

def converter_camelot(key):
    return camelot_map.get(key, "Desconhecida")

# -------- ENERGY --------
def calcular_energia(y):
    rms = np.mean(librosa.feature.rms(y=y))
    
    if rms < 0.02:
        return "Baixa"
    elif rms < 0.05:
        return "Média"
    else:
        return "Alta"

# -------- LOW MID ANALYSIS --------
def analisar_low_mid(y, sr):
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)

    idx = np.where((freqs >= 150) & (freqs <= 400))[0]
    energia_lowmid = np.mean(S[idx])

    if energia_lowmid < 0.01:
        return "Limpo"
    elif energia_lowmid < 0.03:
        return "Equilibrado"
    else:
        return "Carregado"

# -------- API --------
@app.route("/analisar", methods=["POST"])
def analisar():
    if "file" not in request.files:
        return jsonify({"error": "Arquivo não enviado"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nome do arquivo vazio"}), 400

    # Check file extension
    allowed_extensions = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        return jsonify({"error": f"Formato não suportado. Use: {', '.join(allowed_extensions)}"}), 400

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        file.save(temp.name)
        path = temp.name

    try:
        # Load audio with pydub
        audio = AudioSegment.from_file(path)
        # Convert to numpy array
        y = np.array(audio.get_array_of_samples(), dtype=np.float32)
        if audio.channels == 2:
            y = y.reshape((-1, 2)).mean(axis=1)  # Convert stereo to mono
        y = y / (2**15)  # Normalize to [-1, 1] range
        sr = audio.frame_rate

        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        key = detectar_key(y, sr)
        camelot = converter_camelot(key)
        energia = calcular_energia(y)
        lowmid = analisar_low_mid(y, sr)

        return jsonify({
            "bpm": int(round(tempo)),
            "key": key,
            "camelot": camelot,
            "energia": energia,
            "lowmid": lowmid
        })

    except Exception as e:
        app.logger.exception("Falha ao analisar arquivo")
        return jsonify({"error": f"Erro ao processar arquivo: {str(e) or 'Arquivo inválido ou corrompido'}"}), 500

    finally:
        try:
            os.remove(path)
        except OSError:
            pass

if __name__ == "__main__":
    app.run(port=5000)