import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import hankel1

# --- MOTEUR PHYSIQUE : RAYLEIGH-SOMMERFELD 2D ---
def rs_2Dv(b, f, c, e, x, z):
    kb = 2000 * np.pi * b * f / c
    N = int(np.round(20000 * f * b / c))
    if N <= 1: N = 1
    
    xb, zb, eb = x/b, z/b, e/b
    jj = np.arange(1, N + 1)
    xc = -1 + 2 * (jj - 0.5) / N
    
    p = 0
    for kk in range(N):
        rb = np.sqrt((xb - xc[kk] - eb)**2 + zb**2)
        p += hankel1(0, kb * rb)
    return p * (kb / N)

# --- INTERFACE ---
st.set_page_config(page_title="Byte NDT - Beam Engine", layout="wide")
st.title("🌊 Byte NDT | Acoustic Beam Engine")

# Sliders
st.sidebar.header("⚙️ Paramètres Physiques")
b_val = st.sidebar.slider("Demi-largeur b (mm)", 0.1, 10.0, 3.15)
f_val = st.sidebar.slider("Fréquence f (MHz)", 1.0, 10.0, 5.0)
c_val = st.sidebar.slider("Vitesse c (m/s)", 2000, 6500, 5900)
e_val = st.sidebar.slider("Offset e (mm) - [Simu Réseau]", -20.0, 20.0, 0.0)

# Zone de calcul pour l'image
st.subheader(f"Cartographie du faisceau (f={f_val}MHz, e={e_val}mm)")

x_vec = np.linspace(-30, 30, 100)
z_vec = np.linspace(1, 150, 150)
X, Z = np.meshgrid(x_vec, z_vec)

# Calcul de l'image (Module de la pression)
v_rs = np.vectorize(lambda x, z: np.abs(rs_2Dv(b_val, f_val, c_val, e_val, x, z)))
P = v_rs(X, Z)

# Affichage "Impression"
fig, ax = plt.subplots(figsize=(7, 9))
im = ax.pcolormesh(X, Z, P, cmap='magma', shading='auto') # 'magma' donne un aspect industriel
plt.colorbar(im, label='Intensité')
ax.set_xlabel("X (mm)")
ax.set_ylabel("Z (mm)")
ax.invert_yaxis()
st.pyplot(fig)
