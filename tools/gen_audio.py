"""Records every phrase in phrases.json as an MP3 using the Piper Greek voice.

Voice: rhasspy/piper-voices el_GR-rapunzelina-low (MIT licence, trained on a CC0 dataset).
Only phrases without a recording yet are generated, so re-runs are quick.
Usage: python tools/gen_audio.py <voice.onnx> <out_dir>
"""
import json, subprocess, sys, tempfile, wave
from pathlib import Path
from piper import PiperVoice
from piper.config import SynthesisConfig

model, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
phrases = json.loads((Path(__file__).parent.parent / "phrases.json").read_text(encoding="utf-8"))
voice = PiperVoice.load(model)
cfg = SynthesisConfig(length_scale=1.1)  # a little slower than normal, for learners


def speakable(t):
    """The voice drags out phrases that don't end like a sentence, so give every phrase an ending."""
    t = t.strip()
    return t if t[-1:] in ".!;?" else t + "."

made = 0
with tempfile.TemporaryDirectory() as tmp:
    for p in phrases:
        mp3 = out / f"{p['id']}.mp3"
        if mp3.exists():
            continue
        wav = Path(tmp) / "x.wav"
        with wave.open(str(wav), "wb") as w:
            voice.synthesize_wav(speakable(p["text"]), w, syn_config=cfg)
        # short silence at the start so phones don't clip the first sound
        n = wave.open(str(wav)).getnframes() / voice.config.sample_rate
        if n > 1.2 + 0.12 * len(p["text"]):
            print(f"LONG {n:.1f}s {p['text']!r}")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-af", "adelay=120|120,apad=pad_dur=0.15",
                        "-ac", "1", "-ar", "22050", "-b:a", "48k", str(mp3)], check=True)
        made += 1
# quick check of how a few phrases are pronounced and how long they are
def seconds(t):
    return sum(len(c.audio_int16_bytes) for c in voice.synthesize(speakable(t), syn_config=cfg)) / 2 / voice.config.sample_rate


for t in ["Γεια σου", "Καλημέρα", "ευχαριστώ", "Δουλεύω από Δευτέρα μέχρι Παρασκευή."]:
    secs = seconds(t)
    print(f"CHECK {t!r} phonemes={voice.phonemize(t)} seconds={secs:.2f} length_scale_default={voice.config.length_scale}")
print(f"{made} new recordings, {len(phrases)} phrases in total")
missing = [p["id"] for p in phrases if not (out / f"{p['id']}.mp3").exists()]
if missing:
    sys.exit(f"Missing recordings: {missing[:5]}")
