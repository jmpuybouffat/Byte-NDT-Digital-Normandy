import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

# --- FONCTION AUXILIAIRE : RECHERCHE DU POINT D'INTERSECTION (SNELL) ---
def snell_path(xi, e, xc_nn, angt, Dt0, c1, c2, x, z):
    # Calcule l'erreur sur la loi de Snell pour trouver le trajet du rayon
    Dtn = Dt0 + (e + xc_nn) * np.sin(angt * np.pi / 180)
    Dxn = x - (e + xc_nn) * np.cos(angt * np.pi / 180)
    
    sin_theta1 = xi / np.sqrt(xi**2 + Dtn**2)
    sin_theta2 = (Dxn - xi) / np.sqrt((Dxn - xi)**2 + z**2)
    
    return (1/c1) * sin_theta1 - (1/c2) * sin_theta2

# --- MOTEUR PHYSIQUE : RAYLEIGH-SOMMERFELD AVEC INTERFACE ---
def ls_2Dint(b, f, mat, e, angt, Dt0, x, z):
    d1, c1, d2, c2 = mat
    k1b = 2000 * np.pi * b * f / c1
    k2b = 2000 * np.pi * b * f / c2
    
    N = int(np.round(2000 * f * b / c1))
    if N < 1: N = 1
    
    xc = b * (-1 + 2 * (np.arange(1, N + 1) - 0.5) / N)
    p = 0
    eps = 1e-10
    
    for nn in range(N):
        # Recherche du point d'intersection xi par dichotomie
        Dtn = Dt0 + (e + xc[nn]) * np.sin(angt * np.pi / 180)
        Dxn = x - (e + xc[nn]) * np.cos(angt * np.pi / 180)
        
        try:
            # On cherche xi entre 0 et Dxn (point d'entrée dans le second milieu)
            xi = brentq(snell_path, -100, 100, args=(e, xc[nn], angt, Dt0, c1, c2, x, z))
        except:
            xi = Dxn * (c1 / (c1 + c2)) # Fallback si Snell échoue

        r1 = np.sqrt(xi**2 + Dtn**2) / b
        r2 = np.sqrt((Dxn - xi)**2 + z**2) / b
        
        ang1 = np.arcsin(xi / (b * r1 + eps))
        ang2 = np.arcsin((Dxn - xi) / (b * r2 + eps))
        ang = (angt * np.pi / 180) - ang1
        
        # Directivité du segment
        sinc_arg = k1b * np.sin(ang) / N
        dir_factor = np.sin(sinc_arg + eps) / (sinc_arg + eps)
        
        # Coefficient de transmission de pression Tp
        Tp = 2 * d2 * c2 * np.cos(ang1) / (d1 * c1 * np.cos(ang2) + d2 * c2 * np.cos(ang1) + eps)
        
        # Phase et divergence
        ph = np.exp(1j * k1b * r1 + 1j * k2b * r2)
        den = r1 + (c2 / c1) * r2 * (np.cos(ang1)**2) / (np.cos(ang2)**2 + eps)
        
        p += Tp * dir_factor * ph / np.sqrt(den + eps)
        
    return p * (np.sqrt(2 * k1b / (1j * np.pi))) / N

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Byte NDT - Interface Twin", layout="wide")
st.title("📐 Byte NDT | Twin Simplifié : Sonde + Wedge")

# Configuration Sidebar (Vos paramètres spécifiques)
st.sidebar.header("🛠️ Configuration du Test")
f = st.sidebar.slider("Fréquence (MHz)", 1.0, 10.0, 5.0)
b = st.sidebar.slider("Demi-largeur sonde b (mm)", 1.0, 10.0, 3.0) # Sonde 6mm
angt = st.sidebar.slider("Angle du Wedge (deg)", 0, 60, 30) # Wedge 30°

# Matériaux [d1, c1, d2, c2]
mat_rexolite = [1.05, 2350, 7.8, 3250] # Rexolite vers Acier (Shear Wave approx)

st.sidebar.info("Simulation : Wedge Rexolite (30°) -> Acier (45° Shear)")

# Grille de calcul
x_range = np.linspace(-10, 50, 80)
z_range = np.linspace(5, 60, 80)
X, Z = np.meshgrid(x_range, z_range)

# Calcul (Attention : temps de calcul plus long car recherche de racine Snell)
if st.button("Calculer le Twin"):
    v_int = np.vectorize(lambda x, z: np.abs(ls_2Dint(b, f, mat_rexolite, 0, angt, 15, x, z)))
    P = v_int(X, Z)

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.pcolormesh(X, Z, P, cmap='magma', shading='auto')
    plt.colorbar(im, label='Intensité')
    ax.set_xlabel("Distance X (mm)")
    ax.set_ylabel("Profondeur Z (mm)")
    ax.invert_yaxis()
    st.pyplot(fig)
