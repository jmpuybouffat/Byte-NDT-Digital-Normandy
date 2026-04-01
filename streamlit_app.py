import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import hankel1
import pandas as pd
import io

# --- MOTEUR PHYSIQUE : RAYLEIGH-SOMMERFELD 2D ---
def rs_2Dv(b, f, c, x, z):
    kb = 2000 * np.pi * b * f / c
    N = int(np.round(2000 * f * b / c)) 
    if N < 1: N = 1
    xb, zb = x/b, z/b
    xc = -1 + 2 * (np.arange(1, N + 1) - 0.5) / N
    p = 0
    for k in range(N):
        rb = np.sqrt((xb - xc[k])**2 + zb**2)
        p += hankel1(0, kb * rb)
    return p * (kb / N)

# --- MOTEUR KRAUTKRÄMER : DGS / AVG ---
def calculate_dgs(b, f, c, z_range):
    wavelength = c / (f * 1e3) # mm
    area = np.pi * b**2
    z_fresnel = area / wavelength
    # Écho de fond (Réflecteur infini)
    p_backwall = 1 - np.cos((2 * np.pi * z_fresnel) / z_range)
    # Echo défaut type disque de 2mm
    d_def = 2.0
    p_def = (area * np.pi * (d_def/2)**2) / (wavelength**2 * z_range**2)
    return p_backwall / np.max(p_backwall), p_def / np.max(p_backwall)

# --- CONFIGURATION INTERFACE STREAMLIT ---
st.set_page_config(page_title="Byte NDT - Digital Twin", layout="wide")
st.title("Byte NDT - Simulation Intégrée Schmeer & Krautkrämer")

# Barre latérale pour les Sliders
st.sidebar.header("Réglages / Parameters")
b_val = st.sidebar.slider("Demi-largeur b (mm)", 0.5, 10.0, 3.15)
f_val = st.sidebar.slider("Fréquence f (MHz)", 1.0, 10.0, 5.0)
c_val = st.sidebar.slider("Vitesse c (m/s)", 2000, 6500, 5900)

# Calculs en temps réel
z_axis = np.linspace(1.0, 150, 300)
p_rs_vals = np.array([np.abs(rs_2Dv(b_val, f_val, c_val, 0, z)) for z in z_axis])
p_rs_norm = p_rs_vals / np.max(p_rs_vals)
p_bw, p_def = calculate_dgs(b_val, f_val, c_val, z_axis)

# --- AFFICHAGE DU GRAPHIQUE ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(z_axis, p_rs_norm, lw=2.5, color='#007acc', label='Byte NDT (RS_2Dv Profile)')
ax.plot(z_axis, p_bw, 'r--', alpha=0.7, label='Krautkrämer (Fond de pièce)')
ax.plot(z_axis, p_def, 'g:', lw=2, label='Krautkrämer (Défaut 2mm)')

ax.set_ylim(0, 1.2)
ax.set_title(f"Validation du Digital Twin - {f_val} MHz")
ax.set_xlabel("Distance Z (mm)")
ax.set_ylabel("Pression Normalisée")
ax.legend()
ax.grid(True, alpha=0.2)

# Affichage dans l'application web
st.pyplot(fig)

# --- BOUTONS D'EXPORTATION ---
st.write("### Exportation des résultats")
col1, col2 = st.columns(2)
with col1:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    st.download_button("Télécharger l'Image (PNG)", buf.getvalue(), "ByteNDT_Simulation.png", "image/png")
with col2:
    df = pd.DataFrame({'Z_mm': z_axis, 'Pression_RS': p_rs_norm, 'DGS_Fond': p_bw})
    st.download_button("Télécharger les Données (CSV)", df.to_csv(index=False).encode('utf-8'), "ByteNDT_Data.csv", "text/csv")
