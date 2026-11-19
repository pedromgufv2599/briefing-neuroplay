"""Trilha original de 40s para o vídeo do Jeca (síntese própria, sem samples de terceiros).
Estilo: dedilhado de viola + groove pop, 120 BPM, Sol maior (G D Em C).
Impactos e whooshes nas trocas de cena: 5 / 11.5 / 19.5 / 28 / 34.5 s.
Uso: python3 trilha.py saida.wav
"""
import sys, wave
import numpy as np

SR = 44100
DUR = 40.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)

L = np.zeros(N); R = np.zeros(N)

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * l
    R[i:i + len(sig)] += sig * r

def lowpass(x, k=8):
    ker = np.ones(k) / k
    return np.convolve(x, ker, mode="same")

def pluck(freq, dur=1.6, bright=0.5, decay=0.996):
    """Corda dedilhada por síntese aditiva (afinada), com par de oitava levemente desafinado (viola)."""
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    base = 2.2 + (1 - decay) * 400          # decaimento geral
    pos = 0.18                               # ponto do dedilhado
    for h in range(1, 13):
        f = freq * h
        if f > 9000: break
        amp = abs(np.sin(np.pi * h * pos)) / h ** (1.6 - bright)
        out += amp * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t * base * (1 + 0.35 * (h - 1)))
    # par de oitava da viola caipira (cordas duplas)
    out += 0.35 * np.sin(2 * np.pi * freq * 2.004 * t) * np.exp(-t * base * 1.6)
    att = np.minimum(1, t / 0.002)
    env = np.ones(n); fade = int(0.04 * SR); env[-fade:] = np.linspace(1, 0, fade)
    return out * att * env * 0.6

def kick():
    n = int(0.32 * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 1.0

def clap():
    n = int(0.22 * SR); t = np.arange(n) / SR
    nz = rng.uniform(-1, 1, n)
    nz = lowpass(nz - lowpass(nz, 10), 4)   # palma: sem grave e sem chiado
    env = np.exp(-t * 22)
    for d in (0.0, 0.011, 0.022):       # três batidas curtas = palma
        j = int(d * SR); env[j:j + 60] += 0.6
    return nz * env * 0.55

def shaker(acc=1.0):
    n = int(0.05 * SR); t = np.arange(n) / SR
    nz = rng.uniform(-1, 1, n); nz = lowpass(np.diff(nz, prepend=0), 5)
    return nz * np.exp(-t * 70) * 0.08 * acc

def bass(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)
    env = np.minimum(1, t / 0.005) * np.exp(-t * 3.2)
    return np.tanh(1.6 * s) * env * 0.42

def impact():
    n = int(1.1 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 + 40 * np.exp(-t * 10)) * t) * np.exp(-t * 3.5)
    nz = rng.uniform(-1, 1, n); nz = lowpass(nz, 3) * np.exp(-t * 7) * 0.35
    return (boom * 0.9 + nz)

def whoosh(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = rng.uniform(-1, 1, n)
    hp = lowpass(nz - lowpass(nz, 24), 5)
    env = (t / dur) ** 2.2
    return hp * env * 0.45

def crash(dur=2.4):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = rng.uniform(-1, 1, n); nz = lowpass(np.diff(nz, prepend=0), 6)
    return nz * np.exp(-t * 2.6) * 0.2

# acordes: (baixo, [notas do dedilhado])
CH = [
    (43, [55, 59, 62, 67]),   # G
    (38, [57, 62, 66, 69]),   # D
    (40, [52, 55, 59, 64]),   # Em
    (36, [48, 52, 55, 60]),   # C
]
PAT = [0, 2, 1, 3, 2, 1, 3, 2]
CHANGES = [5.0, 11.5, 19.5, 28.0, 34.5]
END = 39.0
BREAK = (27.0, 28.0)          # respiro antes do preço

nbars = int(np.ceil(END / BAR))
for b in range(nbars):
    t0 = b * BAR
    root, notes = CH[b % 4]
    # dedilhado de viola em colcheias
    for i, idx in enumerate(PAT):
        t = t0 + i * BEAT / 2
        if t >= END: break
        f = midi(notes[idx])
        add(pluck(f, 1.4, bright=0.65, decay=0.995), t, 0.42, pan=(-0.35 if i % 2 else 0.35))
        add(pluck(f * 2, 0.6, bright=0.8, decay=0.99), t + 0.004, 0.06, pan=(0.35 if i % 2 else -0.35))
    # rasqueado no 1º tempo dos compassos pares
    if b % 2 == 0:
        for k, m in enumerate(notes):
            add(pluck(midi(m), 1.8, 0.7, 0.996), t0 + k * 0.014, 0.16, pan=-0.1 + 0.07 * k)
    for beat in range(4):
        t = t0 + beat * BEAT
        if t >= END: break
        inbreak = BREAK[0] <= t < BREAK[1]
        if not inbreak:
            add(kick(), t, 0.55)
            if beat in (1, 3):
                add(clap(), t, 0.9 if t < 34.5 else 1.05)
            fb = midi(root) if beat in (0, 1) else midi(root + 7)
            if beat in (0, 2):
                add(bass(fb, BEAT * 1.6), t, 0.6)
            if beat == 3:
                add(bass(midi(root + 12), BEAT * 0.45), t + BEAT / 2, 0.45)
        for s in range(4):
            ts = t + s * BEAT / 4
            if ts < END and not inbreak:
                add(shaker(1.6 if s == 2 else 1.0), ts, 1.0, pan=0.5)
        # palmas em colcheia na reta final (CTA)
        if t >= 34.5 and not inbreak:
            add(clap(), t + BEAT / 2, 0.45, pan=-0.3)

for c in CHANGES:
    add(whoosh(), c - 0.45, 0.8)
    add(impact(), c, 0.5)
    add(crash(1.8), c, 0.6, pan=0.2)
add(impact(), 0.0, 0.6)
add(crash(2.0), 0.0, 0.5)
# subida antes do preço
add(whoosh(1.0), BREAK[1] - 1.0, 0.9)
# final: rasqueado de G aberto + crash
for k, m in enumerate([43, 50, 55, 59, 62, 67]):
    add(pluck(midi(m), 2.4, 0.7, 0.997), END + k * 0.018, 0.28)
add(impact(), END, 0.9); add(crash(2.6), END, 0.8)

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
fade = int(0.6 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= np.max(np.abs(mix)) / 0.89
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok", sys.argv[1])
