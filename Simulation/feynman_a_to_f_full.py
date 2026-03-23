import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np

def fermion(ax, x1, y1, x2, y2, label=None, arrow=True, lw=1.8, label_offset=(0, 0.05), fs=12):
    style = '-|>' if arrow else '-'
    p = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=12, lw=lw, color='black')
    ax.add_patch(p)
    if label:
        xm, ym = (x1+x2)/2 + label_offset[0], (y1+y2)/2 + label_offset[1]
        ax.text(xm, ym, label, ha='center', va='bottom', fontsize=fs)

def wavy(ax, x1, y1, x2, y2, label=None, amp=0.02, waves=7, lw=1.8, fs=12):
    t = np.linspace(0, 1, 300)
    dx, dy = x2 - x1, y2 - y1
    L = np.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    xs = x1 + dx * t + amp * np.sin(2 * np.pi * waves * t) * nx
    ys = y1 + dy * t + amp * np.sin(2 * np.pi * waves * t) * ny
    ax.plot(xs, ys, color='black', lw=lw)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.06, label, ha='center', va='bottom', fontsize=fs)

def gluon(ax, x1, y1, x2, y2, label=None, amp=0.025, turns=8, lw=1.6, fs=12):
    t = np.linspace(0, 1, 400)
    dx, dy = x2 - x1, y2 - y1
    L = np.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    xs = x1 + dx * t + amp * np.sin(2 * np.pi * turns * t) * nx
    ys = y1 + dy * t + amp * np.sin(2 * np.pi * turns * t) * ny
    ax.plot(xs, ys, color='black', lw=lw)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.06, label, ha='center', va='bottom', fontsize=fs)

def setup(ax, title, subtitle):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.02, 0.98, title, ha='left', va='top', fontsize=15, fontweight='bold')
    ax.text(0.02, 0.90, subtitle, ha='left', va='top', fontsize=10)

fig, axes = plt.subplots(2, 1, figsize=(11, 10))

# Tree
ax = axes[0]
setup(ax, r"Tree diagram: $B^+ \to K^+ \pi^0$", r"$B^+ = u\bar b$, spectator $u$ carried along")
fermion(ax, 0.08, 0.68, 0.30, 0.68, r"$\bar b$", arrow=False)
fermion(ax, 0.08, 0.32, 0.82, 0.32, r"$u$ (spectator)", arrow=True, label_offset=(0, -0.10), fs=11)
fermion(ax, 0.30, 0.68, 0.55, 0.82, r"$\bar u$", arrow=False)
wavy(ax, 0.30, 0.68, 0.52, 0.50, r"$W^+$")
fermion(ax, 0.52, 0.50, 0.80, 0.62, r"$u$")
fermion(ax, 0.84, 0.38, 0.52, 0.50, r"$\bar s$", arrow=False)
ax.text(0.80, 0.80, r"$u\bar u \;\to\; \pi^0$", fontsize=12)
ax.text(0.80, 0.12, r"$u\bar s \;\to\; K^+$", fontsize=12)
ax.text(0.02, 0.05, "Tree amplitude: color-allowed weak decay plus hadronization.", fontsize=10)

# Penguin
ax = axes[1]
setup(ax, r"Penguin diagram: $B^+ \to K^+ \pi^0$", r"Loop-induced $b \to s$ penguin with spectator $u$")
fermion(ax, 0.08, 0.28, 0.84, 0.28, r"$u$ (spectator)", arrow=True, label_offset=(0, -0.10), fs=11)
fermion(ax, 0.08, 0.68, 0.28, 0.68, r"$\bar b$", arrow=False)
loop = Circle((0.38, 0.68), 0.07, fill=False, lw=1.8, color='black')
ax.add_patch(loop)
ax.text(0.38, 0.68, "loop", ha='center', va='center', fontsize=10)
fermion(ax, 0.45, 0.68, 0.78, 0.68, r"$\bar s$", arrow=False)
gluon(ax, 0.38, 0.61, 0.60, 0.44, r"$g$")
fermion(ax, 0.60, 0.44, 0.84, 0.56, r"$u$")
fermion(ax, 0.88, 0.32, 0.60, 0.44, r"$\bar u$", arrow=False)
ax.text(0.80, 0.74, r"$u\bar s \;\to\; K^+$", fontsize=12)
ax.text(0.80, 0.12, r"$u\bar u \;\to\; \pi^0$", fontsize=12)
ax.text(0.02, 0.05, "Penguin amplitude: loop + gluon splitting; same final state as tree.", fontsize=10)

plt.tight_layout()
plt.show()