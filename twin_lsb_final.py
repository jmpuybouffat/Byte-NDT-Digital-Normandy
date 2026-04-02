import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. GÉOMÉTRIE LSB 941 (Équations Maple) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else: # EXTRADOS - Inversion et recalage
        y = -(-0.003609 * t**2 + 0.39014 * t + 19.703) + 70 
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y, mode="Intrados"):
    if mode == "Intrados":
        return -0.001671 * y**2 + 0.00338 * y + 320.834
    else: # EXTRADOS
        return -0.002120 * y**2 + 0.01039 * y + 338.591

# --- 2. CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Byte NDT | Digital Twin Precision", layout="wide")
st.title("🛡️ Byte NDT | Twin LSB 941 : Cohérence Géométrique")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Paramètres")
    mode = st.radio("Côté d'inspection", ["Intrados", "Extrados"])
    t_scan = st.slider("Position Barrette PAUT (t)", -50, 150, 10)
    
    # Angle de tir (Préparation Sectoriel)
    angle_deg = st.slider("Angle de réfraction (refracted)", 35, 75, 45)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    
    # Position de l'EDM (Cible fixe)
    target_y = 65.0 if mode == "Intrados" else 25.0
    target_z = get_target_curve(target_y, mode)
    
    # Calcul de projection avec l'angle dynamique
    projected_y = y_p + (target_z - z_p) * np.tan(np.radians(angle_deg))
    error = np.abs(projected_y - target_y)
    amplitude = np.exp(-(error**2) / 100) # Champ de pression

    st.metric("Amplitude", f"{20*np.log10(amplitude+0.01):.1f} dB")
    if amplitude > 0.6:
        st.error("🚨 DÉTECTION EDM")

with col2:
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 1. Tracé des surfaces
    t_range = np.linspace(-50, 150, 300)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=4, label="Surface d'entrée (Profil Aube)")
    
    ty_range = np.linspace(min(sy)-10, max(sy)+40, 100)
    tz_range = [get_target_curve(ty, mode) for ty in ty_range]
    ax.plot(ty_range, tz_range, 'k--', alpha=0.4, label="Ligne des EDM (Fond)")

    # 2. Dessin du Sabot (Wedge) & Sonde PAUT
    # On dessine un bloc pour le wedge (angle fixe pour l'instant)
    ax.add_patch(plt.Rectangle((y_p-12, z_p-8), 24, 8, color='gray', alpha=0.4, label="Wedge (Sabot)"))
    ax.add_patch(plt.Rectangle((y_p-10, z_p-10), 20, 3, color='blue', alpha=0.9, label="Barrette PAUT"))

    # 3. Faisceau (Champ de pression dynamique)
    b_color = "red" if amplitude > 0.5 else "orange"
    ax.fill([y_p, projected_y-10, projected_y+10], [z_p, target_z, target_z], color=b_color, alpha=0.25)
    ax.plot([y_p, projected_y], [z_p, target_z], color=b_color, lw=2, ls='--')

    # 4. EDM et Tache de réponse (Niveaux dB)
    ax.add_patch(plt.Rectangle((target_y-2, target_z-1.5), 4, 3, color='black', zorder=5))
    if amplitude > 0.15:
        # Zone -6dB
        ax.add_artist(plt.Circle((target_y, target_z), 8*amplitude, color='red', alpha=0.3))
        # Zone -3dB
        ax.add_artist(plt.Circle((target_y, target_z), 4*amplitude, color='red', alpha=0.6))

    # --- CONTRAINTES D'AFFICHAGE ---
    ax.set_aspect('equal', adjustable='box') # CRITIQUE : Échelle 1:1
    ax.set_ylim(max(tz_range)+15, min(sz)-20) 
    ax.set_xlabel("Y (mm)")
    ax.set_ylabel("Z (mm)")
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(loc='upper right')
    
    st.pyplot(fig)
