"""Generate SVG figures + numbers for the VaR README (stdlib only)."""
import math, random, statistics, sys, os

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
N = statistics.NormalDist()

W, H = 760, 380
ML, MR, MT, MB = 60, 20, 40, 50
BG, AXIS, INK, MUTED = "#ffffff", "#9aa0a6", "#1f2328", "#57606a"
BLUE, RED, ORANGE = "#3b6fd6", "#d1453b", "#e08a1e"


def svg(body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="Helvetica,Arial,sans-serif">\n<rect width="100%" height="100%" fill="{BG}"/>\n'
            f'<text x="{W/2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="{INK}">{title}</text>\n'
            + body + "\n</svg>\n")


def scaler(x0, x1, y0, y1):
    sx = lambda x: ML + (x - x0) / (x1 - x0) * (W - ML - MR)
    sy = lambda y: H - MB - (y - y0) / (y1 - y0) * (H - MT - MB)
    return sx, sy


def axes(sx, sy, x0, x1, xticks, xlabel, fmt):
    b = [f'<line x1="{ML}" y1="{H-MB}" x2="{W-MR}" y2="{H-MB}" stroke="{AXIS}"/>']
    for t in xticks:
        b.append(f'<line x1="{sx(t):.1f}" y1="{H-MB}" x2="{sx(t):.1f}" y2="{H-MB+5}" stroke="{AXIS}"/>')
        b.append(f'<text x="{sx(t):.1f}" y="{H-MB+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{fmt(t)}</text>')
    b.append(f'<text x="{(ML+W-MR)/2}" y="{H-8}" text-anchor="middle" font-size="13" fill="{MUTED}">{xlabel}</text>')
    return b


def vline(sx, x, ytop, color, label, anchor="end", dy=0):
    X = sx(x)
    return [f'<line x1="{X:.1f}" y1="{ytop}" x2="{X:.1f}" y2="{H-MB}" stroke="{color}" stroke-width="2" stroke-dasharray="6 4"/>',
            f'<text x="{X + (-6 if anchor=="end" else 6):.1f}" y="{ytop+14+dy}" text-anchor="{anchor}" font-size="13" font-weight="bold" fill="{color}" stroke="#fff" stroke-width="4" paint-order="stroke">{label}</text>']


# 1. Parametric: normal curve, mean 1%, sd 1%
mu, sd = 1.0, 1.0
x0, x1 = -3.0, 5.0
sx, sy = scaler(x0, x1, 0, 0.42)
pdf = lambda x: math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))
xs = [x0 + i * (x1 - x0) / 400 for i in range(401)]
v95, v99 = mu - 1.645 * sd, mu - 2.326 * sd
b = axes(sx, sy, x0, x1, range(-3, 6), "1-year return (%)", lambda t: f"{t}%")
tail95 = [x for x in xs if x <= v95] + [v95]
tail99 = [x for x in xs if x <= v99] + [v99]
for tail, col, op in ((tail95, ORANGE, 0.45), (tail99, RED, 0.75)):
    pts = " ".join(f"{sx(x):.1f},{sy(pdf(x)):.1f}" for x in tail)
    b.append(f'<polygon points="{sx(x0):.1f},{sy(0):.1f} {pts} {sx(tail[-1]):.1f},{sy(0):.1f}" fill="{col}" fill-opacity="{op}"/>')
b.append('<polyline fill="none" stroke="%s" stroke-width="2.5" points="%s"/>' % (BLUE, " ".join(f"{sx(x):.1f},{sy(pdf(x)):.1f}" for x in xs)))
b += vline(sx, mu, MT + 10, BLUE, "mean = +1%", "start")
b += vline(sx, v99, MT + 20, RED, "99% VaR ≈ −1.33%", "end")
b += vline(sx, v95, MT + 70, ORANGE, "95% VaR ≈ −0.65%", "end")
b.append(f'<text x="{sx(2.9):.1f}" y="{MT+40}" font-size="12" fill="{RED}">■ worst 1% of outcomes</text>')
b.append(f'<text x="{sx(2.9):.1f}" y="{MT+58}" font-size="12" fill="{ORANGE}">■ + next 4% = worst 5%</text>')
open(f"{OUT}/parametric_var.svg", "w").write(svg("\n".join(b), "Parametric VaR: N(μ = 1%, σ = 1%)"))

# 2. Historical: 100 daily returns sorted worst → best
random.seed(7)
rets = sorted(round(random.gauss(0.05, 1.2) + (random.random() < 0.06) * random.gauss(-1.5, 1.0), 2) for _ in range(100))
lo, hi = math.floor(min(rets)), math.ceil(max(rets))
sx, sy = scaler(0, 100, lo, hi)
bw = (W - ML - MR) / 100
b = [f'<line x1="{ML}" y1="{sy(0):.1f}" x2="{W-MR}" y2="{sy(0):.1f}" stroke="{AXIS}"/>']
for y in range(lo, hi + 1):
    b.append(f'<text x="{ML-8}" y="{sy(y)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{y}%</text>')
for i, r in enumerate(rets):
    col = RED if i == 4 else (ORANGE if i < 4 else BLUE)
    top, bot = sy(max(r, 0)), sy(min(r, 0))
    b.append(f'<rect x="{ML + i*bw + 0.5:.1f}" y="{top:.1f}" width="{bw-1:.1f}" height="{max(bot-top,0.5):.1f}" fill="{col}"/>')
X = ML + 4.5 * bw
b.append(f'<line x1="{X:.1f}" y1="{sy(rets[4])+8:.1f}" x2="{X+70:.1f}" y2="{sy(rets[4])+30:.1f}" stroke="{RED}"/>')
b.append(f'<text x="{X+74:.1f}" y="{sy(rets[4])+34:.1f}" font-size="13" font-weight="bold" fill="{RED}">5th-worst day = {rets[4]:.2f}% → 95% 1-day VaR</text>')
b.append(f'<text x="{(ML+W-MR)/2}" y="{H-8}" text-anchor="middle" font-size="13" fill="{MUTED}">100 daily returns, sorted from worst (left) to best (right)</text>')
open(f"{OUT}/historical_var.svg", "w").write(svg("\n".join(b), "Historical VaR: rank the observed returns"))

# 3. Monte Carlo: 10,000 simulated 1-year returns, N(1%, 1%)
random.seed(42)
sims = sorted(random.gauss(mu, sd) for _ in range(10_000))
mc95, mc99 = sims[int(0.05 * len(sims))], sims[int(0.01 * len(sims))]
bins = [x0 + i * 0.1 for i in range(81)]
counts = [0] * 80
for s in sims:
    k = int((s - x0) / 0.1)
    if 0 <= k < 80:
        counts[k] += 1
sx, sy = scaler(x0, x1, 0, max(counts) * 1.15)
b = axes(sx, sy, x0, x1, range(-3, 6), "simulated 1-year return (%)", lambda t: f"{t}%")
for k, c in enumerate(counts):
    left = bins[k]
    mid = left + 0.05
    col = RED if mid < mc99 else (ORANGE if mid < mc95 else BLUE)
    b.append(f'<rect x="{sx(left)+0.5:.1f}" y="{sy(c):.1f}" width="{sx(left+0.1)-sx(left)-1:.1f}" height="{sy(0)-sy(c):.1f}" fill="{col}"/>')
b += vline(sx, mc99, MT + 20, RED, f"1st pct = {mc99:.2f}%", "end")
b += vline(sx, mc95, MT + 70, ORANGE, f"5th pct = {mc95:.2f}%", "end")
open(f"{OUT}/monte_carlo_var.svg", "w").write(svg("\n".join(b), "Monte Carlo VaR: 10,000 simulated outcomes"))

# 4. VaR vs confidence level
cl = [0.80 + i * 0.0019 for i in range(101)]
vals = [-(mu - N.inv_cdf(c) * sd) for c in cl]  # loss as positive number
sx, sy = scaler(0.80, 0.995, -0.5, 2.0)
b = axes(sx, sy, 0.8, 0.995, [0.80, 0.85, 0.90, 0.95, 0.99], "confidence level", lambda t: f"{t*100:.0f}%")
for y in [-0.5, 0, 0.5, 1.0, 1.5, 2.0]:
    b.append(f'<line x1="{ML}" y1="{sy(y):.1f}" x2="{W-MR}" y2="{sy(y):.1f}" stroke="#eaeef2"/>')
    b.append(f'<text x="{ML-8}" y="{sy(y)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{y:.1f}%</text>')
b.append('<polyline fill="none" stroke="%s" stroke-width="2.5" points="%s"/>' % (BLUE, " ".join(f"{sx(c):.1f},{sy(v):.1f}" for c, v in zip(cl, vals))))
for c, col in ((0.95, ORANGE), (0.99, RED)):
    v = -(mu - N.inv_cdf(c) * sd)
    b.append(f'<circle cx="{sx(c):.1f}" cy="{sy(v):.1f}" r="5" fill="{col}"/>')
    b.append(f'<text x="{sx(c)-8:.1f}" y="{sy(v)-10:.1f}" text-anchor="end" font-size="13" font-weight="bold" fill="{col}">{c*100:.0f}% → loss {v:.2f}%</text>')
b.append(f'<text x="18" y="{(MT+H-MB)/2}" transform="rotate(-90 18 {(MT+H-MB)/2})" text-anchor="middle" font-size="13" fill="{MUTED}">potential loss (VaR)</text>')
open(f"{OUT}/var_vs_confidence.svg", "w").write(svg("\n".join(b), "Higher confidence → deeper into the tail → bigger VaR"))

# Numbers for the README
print("hist 5 worst:", rets[:5], "mean", round(statistics.mean(rets), 3), "sd", round(statistics.stdev(rets), 3))
print("hist ES95 (avg of 5 worst):", round(statistics.mean(rets[:5]), 3))
print("mc95", round(mc95, 3), "mc99", round(mc99, 3), "mc ES95", round(statistics.mean(sims[:500]), 3))
print("z95", N.inv_cdf(0.95), "z99", N.inv_cdf(0.99))
print("ES95 normal mu1 sd1:", mu - sd * N.pdf(N.inv_cdf(0.95)) / 0.05)
