import math
import colorsys

def ker(a: int) -> int:
    a = abs(a)
    if a == 0:
        return 0
    r = a % 9
    return r if r != 0 else 9

def gould(n: int) -> int:
    return 2 ** bin(n).count('1')

def ker_cos(x: int, y: int, A: float = 10.0) -> int:
    val = A * math.cos(x * y)
    return ker(abs(round(val)))

def normalize(value, vmin, vmax):
    if vmax == vmin:
        return 0.0
    return max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))

def _rgb(r, g, b) -> str:
    return '#{:02x}{:02x}{:02x}'.format(
        max(0, min(255, int(r))),
        max(0, min(255, int(g))),
        max(0, min(255, int(b))),
    )

def hmm_mono(value, N=10, vmin=0, vmax=1, **_) -> str:
    t = (value % N) / max(N - 1, 1)
    v = int(t * 255)
    return _rgb(v, v, v)

def hmm_mono2(value, N=10, vmin=0, vmax=1, **_) -> str:
    t = (value % N) / max(N - 1, 1)
    r = int(t * 255)
    b = int((1 - t) * 255)
    g = int(min(r, b) * 0.6)
    return _rgb(r, g, b)

def hmm_bigradient(value, N=10, vmin=0, vmax=1, **_) -> str:
    t = normalize(value % N, 0, N - 1)
    r = int(t * 180)
    g = int((1 - t) * 100)
    b = int((1 - t) * 200 + t * 30)
    return _rgb(r, g, b)

def hmm_multigradient(value, N=10, vmin=0, vmax=1, **_) -> str:
    t = normalize(value % N, 0, N - 1)
    r, g, b = colorsys.hsv_to_rgb(t, 1.0, 1.0)
    return _rgb(r * 255, g * 255, b * 255)

def hmm_discrete(value, N=10, vmin=0, vmax=1, **_) -> str:
    palette = [
        (0, 0, 0), (220, 20, 60), (255, 140, 0), (255, 215, 0),
        (50, 205, 50), (0, 191, 255), (138, 43, 226), (255, 105, 180),
        (255, 255, 255), (64, 64, 64),
    ]
    idx = int(value % N) % len(palette)
    return _rgb(*palette[idx])

def hmm_thermal(value, N=10, vmin=0, vmax=1, **_) -> str:
    t = normalize(value % N, 0, N - 1)
    stops = [
        (0.00, (0, 0, 0)),
        (0.25, (0, 0, 200)),
        (0.50, (200, 0, 0)),
        (0.75, (255, 140, 0)),
        (1.00, (255, 255, 255)),
    ]
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0)
            return _rgb(
                c0[0] + k * (c1[0] - c0[0]),
                c0[1] + k * (c1[1] - c0[1]),
                c0[2] + k * (c1[2] - c0[2]),
            )
    return _rgb(255, 255, 255)

MODELS = {
    'HMM_N':  hmm_mono,
    'HMM_N2': hmm_mono2,
    'HMM_B':  hmm_bigradient,
    'HMM_R':  hmm_multigradient,
    'HMM_DN': hmm_discrete,
    'HMM_T':  hmm_thermal,
}

def get_color(model_name: str, value, N=10, vmin=0, vmax=1) -> str:
    fn = MODELS.get(model_name, hmm_multigradient)
    return fn(value, N=N, vmin=vmin, vmax=vmax)
