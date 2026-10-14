"""Procedural cinematic score for Ushvika product films (royalty-free, generated from scratch).
usage: python3 score.py out.wav config.json
Hits are synced to the visual timeline in index.html."""
import numpy as np, wave, sys, json
CFG = json.load(open(sys.argv[2]))

SR = 44100
DUR = CFG['dur']
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(CFG.get('seed', 1))
L = np.zeros(N); R = np.zeros(N)

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)

def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s
    A, D, Rr = int(a*SR), int(d*SR), int(r*SR)
    e[:A] = np.linspace(0, 1, A, endpoint=False)
    e[A:A+D] = np.linspace(1, s, D, endpoint=False)[:max(0, min(D, n-A))]
    e[-Rr:] *= np.linspace(1, 0, Rr)
    return e

def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR); j = min(N, i + len(sig)); sig = sig[:j-i] * gain
    L[i:j] += sig * np.sqrt((1 - pan) / 2) * 1.414
    R[i:j] += sig * np.sqrt((1 + pan) / 2) * 1.414

def lowpass(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))

def bandpass(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    X *= (f > lo) & (f < hi)
    return np.fft.irfft(X, len(x))

# ---- warm pad: D minor  i – VI – III – VII  (Dm, Bb, F, C) ----
chords = CFG['chords']
seg = 3.6
for k in range(int(DUR / seg) + 1):
    st = k * seg; n = int((seg + 1.5) * SR); tt = np.arange(n) / SR
    sig = np.zeros(n)
    for m in chords[k % 4]:
        for det in (-0.12, 0, 0.12):
            f0 = midi(m + det)
            for h in range(1, 7):
                sig += np.sin(2*np.pi*f0*h*tt + rng.random()*6.28) / h**1.8
    sig = lowpass(sig, 1400) * env_adsr(n, 1.2, 0.5, 0.85, 1.6)
    g = 0.010 if st < 3.5 else 0.016
    add(sig, st, pan=(-0.3 if k % 2 else 0.3), gain=g)

# ---- music-box / pluck arpeggio from the reveal ----
beat = 0.6
arp = {i: a for i, a in enumerate(CFG['arp'])}
tt0 = CFG['start']
i = 0
while tt0 < CFG['pulse_end']:
    k = int(tt0 // seg) % 4
    m = arp[k][i % 6] + 12
    n = int(1.4 * SR); tt = np.arange(n)/SR
    f0 = midi(m)
    s = (np.sin(2*np.pi*f0*tt) + 0.35*np.sin(2*np.pi*f0*2*tt) + 0.12*np.sin(2*np.pi*f0*3.01*tt)) * np.exp(-tt*4.5)
    s[:200] *= np.linspace(0, 1, 200)
    add(s, tt0, pan=np.sin(i*0.9)*0.6, gain=0.065)
    tt0 += beat/2; i += 1

# ---- low strings / bass line from 8.2 ----
for k in range(int(CFG['start'] // seg), int(CFG['pulse_end'] // seg) + 1):
    st = max(CFG['start'], k*seg); n = int((seg+0.4)*SR); tt = np.arange(n)/SR
    f0 = midi(chords[k % 4][0] - 12)
    s = sum(np.sin(2*np.pi*f0*h*tt)/h**1.3 for h in range(1, 6))
    add(lowpass(s, 500)*env_adsr(n, .25, .3, .8, .5), st, gain=0.05)

# ---- percussion pulse 8.2 – 27.5 ----
def kick():
    n = int(.5*SR); tt = np.arange(n)/SR
    f = 45 + 90*np.exp(-tt*28)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt*7)
def tick():
    n = int(.08*SR); return bandpass(rng.standard_normal(n), 6000, 14000) * np.exp(-np.arange(n)/SR*60)
K = kick(); TK = tick()
b = CFG['start']
while b < CFG['pulse_end']:
    add(K, b, gain=0.35)
    add(TK, b + beat/2, pan=0.4, gain=0.06)
    if (b - CFG['start']) % (beat*4) > beat*3 - 0.01: add(TK, b + beat*0.75, pan=-0.4, gain=0.04)
    b += beat

# ---- cinematic impacts (synced to visual hits) ----
def impact(length=4.0, big=True):
    n = int(length*SR); tt = np.arange(n)/SR
    sub = np.sin(2*np.pi*np.cumsum(38 + 60*np.exp(-tt*6))/SR) * np.exp(-tt*1.3)
    nz = lowpass(rng.standard_normal(n), 900) * np.exp(-tt*3.5) * 0.6
    metal = sum(np.sin(2*np.pi*f*tt + rng.random()*6) for f in (311, 466, 622, 932)) * np.exp(-tt*1.8) * 0.06
    return (sub + nz + (metal if big else 0))
for h, g in CFG['hits']:
    add(impact(), h, gain=g)

# ---- risers & swooshes ----
def riser(length):
    n = int(length*SR); tt = np.arange(n)/SR
    nz = rng.standard_normal(n)
    out = np.zeros(n); chunk = SR//20
    for c in range(0, n, chunk):
        p = c/n; out[c:c+chunk] = bandpass(nz[c:c+chunk], 400+5000*p, 1200+9000*p)
    tone = np.sin(2*np.pi*np.cumsum(200 + 600*(tt/length)**2)/SR) * 0.15
    return (out + tone) * (tt/length)**2.2
for end, ln in CFG['risers']:
    add(riser(ln), end-ln, gain=0.35)
def swoosh():
    n = int(.7*SR); tt = np.arange(n)/SR
    return bandpass(rng.standard_normal(n), 800, 7000) * np.sin(np.pi*tt/.7)**2
for s in CFG['swooshes']:
    add(swoosh(), s - .2, pan=0.5, gain=0.12)

# ---- simple stereo reverb ----
def reverb(x, seed):
    ir_n = int(2.6*SR); it = np.arange(ir_n)/SR
    ir = np.random.default_rng(seed).standard_normal(ir_n) * np.exp(-it*2.4); ir[0] = 0
    nfft = 1 << int(np.ceil(np.log2(len(x)+ir_n)))
    y = np.fft.irfft(np.fft.rfft(x, nfft)*np.fft.rfft(ir, nfft), nfft)[:len(x)]
    return y / np.max(np.abs(y)) * np.max(np.abs(x))
Lw, Rw = reverb(L, 1), reverb(R, 2)
L = L*0.8 + Lw*0.35; R = R*0.8 + Rw*0.35

# master: fade in/out, soft clip, normalise
fade = np.ones(N); fi = int(0.4*SR); fo = int(1.6*SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
st = np.stack([L, R], 1) * fade[:, None]
st = np.tanh(st / np.max(np.abs(st)) * 1.6) / np.tanh(1.6) * 0.89
out = sys.argv[1]
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype('<i2').tobytes())
print('wrote', out)
