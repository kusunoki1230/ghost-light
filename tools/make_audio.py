"""Record every study-scene line that has no audio yet (Kokoro TTS, runs offline on CPU).

Setup once:
  pip install kokoro-onnx soundfile
  download kokoro-v1.0.onnx and voices-v1.0.bin from
  https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
  and pass their folder:  python tools/make_audio.py /path/to/models
Each study scene lists a voice per character in "voices" (e.g. am_michael, af_heart).
"""
import json, os, subprocess, sys, tempfile
import soundfile as sf
from kokoro_onnx import Kokoro

models = sys.argv[1]
k = Kokoro(os.path.join(models, "kokoro-v1.0.onnx"), os.path.join(models, "voices-v1.0.bin"))
content = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "content")
cat = json.load(open(os.path.join(content, "catalog.json")))
made = 0
for e in cat["packs"]:
    p = json.load(open(os.path.join(content, e["file"])))
    for sc in p["study"]:
        for line in sc["lines"]:
            out = os.path.join(content, line["audio"])
            if os.path.exists(out):
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            text = line["en"].replace("—", ", ").replace("'tis", "it's").replace("'Tis", "It's")
            audio, sr = k.create(text, voice=sc["voices"][line["who"]], speed=0.92, lang="en-us")
            wav = os.path.join(tempfile.gettempdir(), "gl.wav")
            sf.write(wav, audio, sr)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-b:a", "48k", out], check=True)
            made += 1
print("recorded", made, "new lines")
