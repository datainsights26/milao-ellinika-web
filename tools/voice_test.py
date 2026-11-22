import sys, wave, io
from piper import PiperVoice
from piper.config import SynthesisConfig
v = PiperVoice.load(sys.argv[1])
print("CFG", v.config.noise_scale, v.config.noise_w_scale, v.config.length_scale, v.config.sample_rate)
words = ["Αθήνα", "γάλα", "Γεια σου", "Καλημέρα", "νερό", "Δουλεύω από Δευτέρα μέχρι Παρασκευή."]
configs = {"default": SynthesisConfig(), "nw0.3": SynthesisConfig(noise_w_scale=0.3), "nw0": SynthesisConfig(noise_w_scale=0.0, noise_scale=0.333),
           "comma": SynthesisConfig(noise_w_scale=0.3)}
for name, c in configs.items():
    out = []
    for w in words:
        t = w if name != "comma" else "Λοιπόν, " + w
        secs = sum(len(ch.audio_int16_bytes) for ch in v.synthesize(t, syn_config=c)) / 2 / v.config.sample_rate
        out.append(f"{w}={secs:.2f}")
    print("RES", name, " ".join(out))
# save samples for inspection
import os; os.makedirs("samples", exist_ok=True)
for name in ["default", "nw0.3", "nw0"]:
    for i, w in enumerate(words[:3]):
        with wave.open(f"samples/{name}-{i}.wav", "wb") as f:
            v.synthesize_wav(w, f, syn_config=configs[name])
