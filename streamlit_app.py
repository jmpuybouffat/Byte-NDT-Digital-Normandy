import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import hankel1
import pandas as pd
import io

# --- MOTEUR PHYSIQUE : RAYLEIGH-SOMMERFELD 2D ---
def rs_2Dv(b, f, c, x, z):
    kb = 2000 * np.pi * b * f / c
    N = max(1, int(np.round(2000 * f * b / c)))
    xb, zb = x/b, z/b
    xc = -1 + 2 * (np.arange(1, N + 1) - 0.5) / N
    p = 0
    for k in range(N):
        rb = np.sqrt((xb - xc[k])**2 + zb**2)
        p += hankel1(0, kb * rb)
    return p * (kb / N)

# --- MOTEUR KRAUTKRÄMER : DGS / AVG ---
def calculate_dgs(b, f, c, z_range, d_def):
    wavelength = c / (f * 1e3) # mm
    area = np.pi * b**2
    z_fresnel = area / wavelength
    # Écho de fond (Réflecteur infini)
    p_backwall = 1 - np.cos((2 * np.pi * z_fresnel) / z_range)
    # Echo défaut (Taille variable via slider)
    p_def = (area * np.pi * (d_def/2)**2) / (wavelength**2 * z_range**2)
    return p_backwall / np.max(p_backwall), p_def / np.max(p_backwall)

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Byte NDT - Digital Twin", layout="wide")
st.title("🌊 Byte NDT | Jumeau Numérique - Digital Twin")
st.markdown("### Inspection LSB 941 (Rayleigh-Sommerfeld & Krautkrämer)")

# Barre latérale (Sidebar)
st.sidebar.header("⚙️ Réglages / Parameters")
b_val = st.sidebar.slider("Demi-largeur b / Half-width (mm)", 0.5, 10.0, 3.15)
f_val = st.sidebar.slider("Fréquence f / Frequency (MHz)", 1.0, 10.0, 5.0)
c_val = st.sidebar.slider("Vitesse c / Velocity (m/s)", 2000, 6500, 5900)
d_def = st.sidebar.slider("Taille défaut / Defect Size (mm)", 0.1, 5.0, 2.0)

# Calculs
z_axis = np.linspace(1.0, 150, 300)
p_rs_vals = np.array([np.abs(rs_2Dv(b_val, f_val, c_val, 0, z)) for z in z_axis])
p_rs_norm = p_rs_vals / np.max(p_rs_vals)
p_bw, p_def_vals = calculate_dgs(b_val, f_val, c_val, z_axis, d_def)

# Affichage Graphique
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(z_axis, p_rs_norm, lw=3, color='#007acc', label='Byte NDT (RS_2Dv)')
ax.plot(z_axis, p_bw, 'r--', alpha=0.6, label='Krautkrämer (Fond/Backwall)')
ax.plot(z_axis, p_def_vals, 'g:', lw=2, label=f'Krautkrämer (Défaut {d_def}mm)')

ax.set_ylim(0, 1.2)
ax.set_xlabel("Distance Z (mm)")
ax.set_ylabel("Pression Normalisée / Normalized Pressure")
ax.legend()
ax.grid(True, alpha=0.2)
st.pyplot(fig)

# Aide à l'emploi
with st.expander("ℹ️ Aide à l'emploi / User Manual"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Français :**\n1. Ajustez les paramètres de la sonde (b, f, c).\n2. Utilisez le slider 'Taille défaut' pour simuler différents réflecteurs.\n3. Comparez la courbe bleue (notre calcul) aux standards Krautkrämer.")
    with col2:
        st.markdown("**English:**\n1. Adjust probe parameters (b, f, c).\n2. Use 'Defect Size' slider to simulate different reflectors.\n3. Compare blue curve (our model) with Krautkrämer standards.")

# Export
buf = io.BytesIO()
fig.savefig(buf, format="png")
st.download_button("📥 Download Report (PNG)", buf.getvalue(), "ByteNDT_Report.png")
