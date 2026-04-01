import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io

# --- MOTEUR PHYSIQUE : ASYMPTOTIC RAYLEIGH-SOMMERFELD 2D (ls_2Dv) ---
def ls_2Dv(b, f, c, e, x, z, n_opt=None):
    kb = 2000 * np.pi * b * f / c
    if n_opt is not None:
        N = n_opt
    else:
        N = int(np.round(2000 * f * b / c))
        if N < 1: N = 1
            
    xb, zb, eb = x/b, z/b, e/b
    jj = np.arange(1, N + 1)
    xc = -1 + 2 * (jj - 0.5) / N
    
    p = 0
    eps = 1e-10 
    for kk in range(N):
        diff_x = xb - xc[kk] - eb
        ang = np.arctan(diff_x / zb)
        ang = ang + eps * (ang == 0)
        
        # Facteur de directivité (Sinc)
        sinc_arg = kb * np.sin(ang) / N
        dir_factor = np.sin(sinc_arg) / (sinc_arg + eps)
        
        rb = np.sqrt(diff_x**2 + zb**2)
        # Onde cylindrique asymptotique
        p += dir_factor * np.exp(1j * kb * rb) / np.sqrt(rb)
    
    # Facteur externe (Normalisation)
    external_factor = np.sqrt(2 * kb / (1j * np.pi)) / N
    return p * external_factor

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Byte NDT - Fast Beam Engine", layout="wide")
st.title("🌊 Byte NDT | Fast Beam Engine (Asymptotic Model)")
st.markdown("### Modèle à haute vitesse pour Machine Learning & Champ Lointain")

# Sidebar
st.sidebar.header("⚙️ Paramètres de Simulation")
b_val = st.sidebar.slider("Demi-largeur b (mm)", 0.5, 10.0, 3.15)
f_val = st.sidebar.slider("Fréquence f (MHz)", 0.5, 10.0, 5.0)
c_val = st.sidebar.slider("Vitesse c (m/s)", 2000, 6500, 5900)
e_val = st.sidebar.slider("Offset / Position e (mm)", -25.0, 25.0, 0.0)

# Zone de calcul
x_vec = np.linspace(-40, 40, 100)
z_vec = np.linspace(5, 150, 150) # On évite z=0 pour l'asymptotique
X, Z = np.meshgrid(x_vec, z_vec)

with st.spinner('Calcul du champ asymptotique...'):
    v_ls = np.vectorize(lambda x, z: np.abs(ls_2Dv(b_val, f_val, c_val, e_val, x, z)))
    P = v_ls(X, Z)

# Affichage "Look CIVA"
fig, ax = plt.subplots(figsize=(8, 11))
im = ax.pcolormesh(X, Z, P, cmap='inferno', shading='auto')
plt.colorbar(im, label='Intensité Relative')
ax.set_xlabel("X (mm)")
ax.set_ylabel("Z (mm)")
ax.invert_yaxis()
ax.set_title(f"Faisceau Asymptotique : b={b_val}mm, f={f_val}MHz, e={e_val}mm")
st.pyplot(fig)

# Note pour Digital Normandy
with st.expander("📝 Note Technique"):
    st.write("Ce modèle utilise l'approximation de l'onde cylindrique pour de grands nombres d'onde. "
             "Il est idéal pour simuler rapidement des bases de données massives pour l'IA.")
