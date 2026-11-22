"""Compare Greek voices: generate test phrases, then check them with Whisper speech recognition."""
import subprocess, wave, os, json, unicodedata, difflib
import numpy as np, torch, scipy.io.wavfile as wavfile
from transformers import VitsModel, AutoTokenizer
from faster_whisper import WhisperModel

words = ["Αθήνα", "γάλα", "νερό", "Γεια σου", "Καλημέρα", "ευχαριστώ", "Χαίρω πολύ.", "Πόσο κάνει;", "τα πορτοκάλια",
         "Δουλεύω από Δευτέρα μέχρι Παρασκευή.", "Θα ήθελα έναν καφέ.", "ψωμί", "άλφα. Αθήνα"]
os.makedirs("samples", exist_ok=True)

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalpha())

tok = AutoTokenizer.from_pretrained("facebook/mms-tts-ell")
mms = VitsModel.from_pretrained("facebook/mms-tts-ell")
print("MMS uroman needed:", getattr(tok, "is_uroman", None))
for i, w in enumerate(words):
    inp = tok(w, return_tensors="pt")
    torch.manual_seed(0)
    with torch.no_grad():
        audio = mms(**inp).waveform[0].numpy()
    wavfile.write(f"samples/mms-{i}.wav", mms.config.sampling_rate, (audio * 32767).astype(np.int16))
    subprocess.run(["espeak-ng", "-v", "el", "-s", "140", "-w", f"samples/espeak-{i}.wav", w], check=True)

asr = WhisperModel("small", device="cpu", compute_type="int8")
for eng in ["mms", "espeak"]:
    scores = []
    for i, w in enumerate(words):
        f = f"samples/{eng}-{i}.wav"
        segs, info = asr.transcribe(f, language="el", beam_size=5)
        text = " ".join(s.text for s in segs).strip()
        with wave.open(f) as x:
            dur = x.getnframes() / x.getframerate()
        sc = difflib.SequenceMatcher(None, norm(w), norm(text)).ratio()
        scores.append(sc)
        print(f"RES {eng:7s} {dur:5.2f}s score={sc:.2f} want={w!r} heard={text!r}")
    print(f"AVG {eng} {sum(scores)/len(scores):.2f}")
