import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import io
import csv

st.set_page_config(page_title="Beam Deflection Calculator", layout="wide")
st.title("Beam deflection calculator")
st.caption("Simply supported beam — point load and UDL")

# ── Section presets ──────────────────────────────────────────────────────────
SECTION_PRESETS = {
    "Custom": {"E": 200.0, "I": 100.0},
    "Wide flange — W200x100 (steel)": {"E": 200.0, "I": 11300.0},
    "Wide flange — W150x37 (steel)": {"E": 200.0, "I": 2660.0},
    "Circular tube — 100mm OD, 5mm wall (steel)": {"E": 200.0, "I": 168.0},
    "Rectangular bar — 50x100mm (steel)": {"E": 200.0, "I": 416.0},
    "Rectangular bar — 50x100mm (aluminium)": {"E": 69.0, "I": 416.0},
    "Timber — 90x190mm (structural pine)": {"E": 10.0, "I": 5140.0},
}

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Section & material")
    preset = st.selectbox("Section preset", list(SECTION_PRESETS.keys()))
    defaults = SECTION_PRESETS[preset]

    E = st.number_input(
        "Young's modulus E (GPa)",
        1.0, 300.0,
        value=float(defaults["E"]),
        step=1.0,
        disabled=(preset != "Custom"),
    ) * 1e9

    I = st.number_input(
        "Second moment of area I (cm⁴)",
        1.0, 50000.0,
        value=float(defaults["I"]),
        step=10.0,
        disabled=(preset != "Custom"),
    ) * 1e-8

    st.divider()
    st.header("Beam geometry")
    L = st.number_input("Beam length L (m)", 0.5, 30.0, 5.0, 0.5)

    st.divider()
    st.header("Loading")
    load_type = st.radio("Load type", ["Point load", "Uniformly distributed load (UDL)"])

    if load_type == "Point load":
        P = st.number_input("Point load P (kN)", 0.1, 2000.0, 10.0, 0.5) * 1e3
        a = st.slider("Load position a (m from left)", 0.01, float(L) - 0.01, float(L / 2), 0.01)
        w = None
    else:
        w = st.number_input("UDL intensity w (kN/m)", 0.1, 500.0, 5.0, 0.5) * 1e3
        P = None
        a = None

# ── Physics engine ────────────────────────────────────────────────────────────
n = 500
x = np.linspace(0, L, n)

if load_type == "Point load":
    b = L - a
    R_A = P * b / L
    R_B = P * a / L

    V = np.where(x < a, R_A, R_A - P)
    M = np.where(x <= a, R_A * x, R_A * x - P * (x - a))
    y = np.where(
        x <= a,
        (P * b * x) / (6 * L * E * I) * (L**2 - b**2 - x**2),
        (P * a * (L - x)) / (6 * L * E * I) * (2 * L * x - x**2 - a**2),
    )
else:
    R_A = w * L / 2
    R_B = w * L / 2

    V = R_A - w * x
    M = R_A * x - w * x**2 / 2
    y = (w * x) / (24 * E * I) * (L**3 - 2 * L * x**2 + x**3)

# Deflection is downward — flip sign for display (positive = down)
y_display = -y

# ── Key metrics ───────────────────────────────────────────────────────────────
max_defl_mm = abs(y_display).max() * 1000
max_moment_kNm = abs(M).max() / 1000
max_shear_kN = abs(V).max() / 1000
L_over_defl = L / abs(y_display).max() if abs(y_display).max() > 0 else float("inf")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Max deflection", f"{max_defl_mm:.2f} mm")
col2.metric("Max moment", f"{max_moment_kNm:.1f} kN·m")
col3.metric("Max shear", f"{max_shear_kN:.1f} kN")
col4.metric("L / δ ratio", f"{L_over_defl:.0f}" if L_over_defl < 1e6 else "—")

st.divider()

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(4, 1, figsize=(10, 11), gridspec_kw={"height_ratios": [1.4, 1, 1, 1]})
fig.patch.set_facecolor("white")
for ax in axes:
    ax.set_facecolor("white")

BLUE = "#378ADD"
RED = "#E24B4A"
GRAY = "#888780"
DARK = "#2C2C2A"

# ── Plot 0: Beam schematic ────────────────────────────────────────────────────
ax0 = axes[0]
ax0.set_xlim(-0.5, L + 0.5)
ax0.set_ylim(-1.2, 1.8)
ax0.axis("off")
ax0.set_title("Beam schematic", fontsize=11, fontweight="normal", color=DARK, loc="left", pad=6)

# Beam rectangle
beam_rect = mpatches.FancyBboxPatch(
    (0, -0.15), L, 0.3,
    boxstyle="square,pad=0",
    linewidth=1, edgecolor=DARK, facecolor="#D3D1C7"
)
ax0.add_patch(beam_rect)

# Left support — triangle
tri_L = mpatches.Polygon(
    [[0, -0.15], [-0.25, -0.75], [0.25, -0.75]],
    closed=True, facecolor=GRAY, edgecolor=DARK, linewidth=0.8
)
ax0.add_patch(tri_L)
ax0.plot([-0.35, 0.35], [-0.82, -0.82], color=DARK, linewidth=1.5)

# Right support — triangle
tri_R = mpatches.Polygon(
    [[L, -0.15], [L - 0.25, -0.75], [L + 0.25, -0.75]],
    closed=True, facecolor=GRAY, edgecolor=DARK, linewidth=0.8
)
ax0.add_patch(tri_R)
ax0.plot([L - 0.35, L + 0.35], [-0.82, -0.82], color=DARK, linewidth=1.5)

# Reactions
ax0.annotate("", xy=(0, -0.15), xytext=(0, -0.85),
             arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))
ax0.text(0.08, -0.55, f"R_A={R_A/1000:.1f} kN", fontsize=8, color=BLUE)

ax0.annotate("", xy=(L, -0.15), xytext=(L, -0.85),
             arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))
ax0.text(L - 0.08, -0.55, f"R_B={R_B/1000:.1f} kN", fontsize=8, color=BLUE, ha="right")

if load_type == "Point load":
    # Single downward arrow at load position
    ax0.annotate("", xy=(a, 0.15), xytext=(a, 1.2),
                 arrowprops=dict(arrowstyle="->", color=RED, lw=2))
    ax0.text(a, 1.35, f"P = {P/1000:.1f} kN", fontsize=9, color=RED, ha="center")
    ax0.plot([a, a], [-0.15, -0.15], color=RED, linewidth=0)

    # Dimension lines
    ax0.annotate("", xy=(a, 1.05), xytext=(0, 1.05),
                 arrowprops=dict(arrowstyle="<->", color=GRAY, lw=0.8))
    ax0.text(a / 2, 1.12, f"a={a:.1f} m", fontsize=7.5, color=GRAY, ha="center")
else:
    # UDL arrows
    n_arrows = max(5, int(L * 2))
    xs_udl = np.linspace(0.1, L - 0.1, n_arrows)
    for xi in xs_udl:
        ax0.annotate("", xy=(xi, 0.15), xytext=(xi, 0.75),
                     arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax0.plot([0, L], [0.75, 0.75], color=RED, linewidth=1.2)
    ax0.text(L / 2, 1.0, f"w = {w/1000:.1f} kN/m", fontsize=9, color=RED, ha="center")

# Span label
ax0.text(L / 2, -1.1, f"L = {L:.1f} m", fontsize=8.5, color=DARK, ha="center")

# ── Plot 1: Shear force diagram ───────────────────────────────────────────────
ax1 = axes[1]
ax1.axhline(0, color=DARK, linewidth=0.6, linestyle="--", alpha=0.5)
ax1.fill_between(x, V / 1000, 0, where=(V >= 0), color=BLUE, alpha=0.25)
ax1.fill_between(x, V / 1000, 0, where=(V < 0), color=RED, alpha=0.25)
ax1.plot(x, V / 1000, color=DARK, linewidth=1.5)
ax1.set_ylabel("Shear (kN)", fontsize=10)
ax1.set_title("Shear force diagram", fontsize=11, fontweight="normal", color=DARK, loc="left", pad=4)
ax1.tick_params(labelsize=8)
ax1.spines[["top", "right"]].set_visible(False)
ax1.spines[["left", "bottom"]].set_color("#D3D1C7")

# ── Plot 2: Bending moment diagram ───────────────────────────────────────────
ax2 = axes[2]
ax2.axhline(0, color=DARK, linewidth=0.6, linestyle="--", alpha=0.5)
ax2.fill_between(x, M / 1000, 0, where=(M >= 0), color=BLUE, alpha=0.2)
ax2.fill_between(x, M / 1000, 0, where=(M < 0), color=RED, alpha=0.2)
ax2.plot(x, M / 1000, color=DARK, linewidth=1.5)
ax2.set_ylabel("Moment (kN·m)", fontsize=10)
ax2.set_title("Bending moment diagram", fontsize=11, fontweight="normal", color=DARK, loc="left", pad=4)
ax2.tick_params(labelsize=8)
ax2.spines[["top", "right"]].set_visible(False)
ax2.spines[["left", "bottom"]].set_color("#D3D1C7")

# ── Plot 3: Deflection diagram ────────────────────────────────────────────────
ax3 = axes[3]
ax3.axhline(0, color=DARK, linewidth=0.6, linestyle="--", alpha=0.5)
ax3.fill_between(x, y_display * 1000, 0, color=BLUE, alpha=0.15)
ax3.plot(x, y_display * 1000, color=BLUE, linewidth=2)
ax3.set_ylabel("Deflection (mm)", fontsize=10)
ax3.set_xlabel("Position along beam (m)", fontsize=10)
ax3.set_title("Deflection diagram", fontsize=11, fontweight="normal", color=DARK, loc="left", pad=4)
ax3.tick_params(labelsize=8)
ax3.spines[["top", "right"]].set_visible(False)
ax3.spines[["left", "bottom"]].set_color("#D3D1C7")

# Mark max deflection
idx_max = np.argmax(np.abs(y_display))
ax3.annotate(
    f"  δ_max = {max_defl_mm:.2f} mm",
    xy=(x[idx_max], y_display[idx_max] * 1000),
    xytext=(x[idx_max] + L * 0.05, y_display[idx_max] * 1000 * 0.6),
    fontsize=8, color=BLUE,
    arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.8),
)

fig.tight_layout(pad=2.0)
st.pyplot(fig)

# ── Download CSV ──────────────────────────────────────────────────────────────
st.divider()

buf = io.StringIO()
writer = csv.writer(buf)
writer.writerow(["x (m)", "Shear V (kN)", "Moment M (kN·m)", "Deflection δ (mm)"])
for xi, Vi, Mi, yi in zip(x, V / 1000, M / 1000, y_display * 1000):
    writer.writerow([f"{xi:.4f}", f"{Vi:.4f}", f"{Mi:.4f}", f"{yi:.4f}"])

st.download_button(
    label="Download results as CSV",
    data=buf.getvalue(),
    file_name="beam_results.csv",
    mime="text/csv",
)

st.caption("Built with Python · NumPy · Matplotlib · Streamlit")
