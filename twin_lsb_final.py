import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION DE LA PAGE (DOIT ÊTRE LA PREMIÈRE LIGNE STREAMLIT) ---
st.set_page_config(
    page_title="Byte NDT | Digital Twin LSB 941",
    layout="wide", # Utilise toute la largeur de l'écran
    initial_sidebar_state="expanded"
)

# --- 2. GÉOMÉTRIE LSB 941 (Équations Maple) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else: # EXTRADOS - Recalage géométrique
        y = -(-0.003609 * t**2 + 0.39014 * t + 19.703) + 70 
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y, mode="Intrados"):
    if mode == "Intrados":
        return -0.001671 * y**2 + 0.00338 * y + 320.834
    else: # EXTRADOS
        return -0.002120 * y**2 + 0.01039 * y + 338.591

# --- 3. INTERFACE UTILISATEUR ---
st.title("🛡️ Byte NDT | Système de Simulation PAUT")

# Organisation en deux colonnes égales pour les petits écrans
col1, col2 = st.columns([1, 1])

with col1:
    st.header("⚙️ Contrôle Hardware")
    mode = st.radio("Côté d'inspection", ["Intrados", "Extrados"])
    t_scan = st.slider("Position Barrette PAUT (t)", -50, 150, 10)
    angle_deg = st.slider("Angle de réfraction (Sectoriel)", 35, 75, 45)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    
    # Cible EDM fixe
    target_y = 65.0 if mode == "Intrados" else 25.0
    target_z = get_target_curve(target_y, mode)
    
    # Calcul d'impact
    projected_y = y_p + (target_z - z_p) * np.tan(np.radians(angle_deg))
    error = np.abs(projected_y - target_y)
    amplitude = np.exp(-(error**2) / 100)

    # Zone de résultat compacte
    st.subheader("📊 Analyse du Signal")
    st.metric("Amplitude", f"{20*np.log10(amplitude+0.01):.1f} dB")
    if amplitude > 0.6:
        st.error("🚨 ALERTE : INDICATION NC DÉTECTÉE")

with col2:
    # Taille réduite (8,6) pour éviter le scroll vertical
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Dessin des profils
    t_range = np.linspace(-50, 150, 200)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=3, label="Surface Aube")
    
    ty_range = np.linspace(min(sy)-10, max(sy)+40, 100)
    tz_range = [get_target_curve(ty, mode) for ty in ty_range]
    ax.plot(ty_range, tz_range, 'k--', alpha=0.4, label="Fond (EDM)")

    # Barrette PAUT et Sabot
    ax.add_patch(plt.Rectangle((y_p-12, z_p-6), 24, 6, color='gray', alpha=0.3))
    ax.add_patch(plt.Rectangle((y_p-10, z_p-8), 20, 2, color='blue', alpha=0.8, label="PAUT Probe"))

    # Faisceau
    b_color = "red" if amplitude > 0.5 else "orange"
    ax.fill([y_p, projected_y-8, projected_y+8], [z_p, target_z, target_z], color=b_color, alpha=0.2)
    ax.plot([y_p, projected_y], [z_p, target_z], color=b_color, lw=1.5, ls='--')

    # EDM
    ax.add_patch(plt.Rectangle((target_y-2, target_z-1), 4, 2, color='black'))

    # --- RÉGLAGES D'AFFICHAGE ---
    ax.set_aspect('equal', adjustable='box') # 1mm = 1mm
    ax.set_ylim(max(tz_range)+10, min(sz)-15) # Surface en haut
    ax.set_xlabel("Y (mm)")
    ax.set_ylabel("Z (mm)")
    ax.legend(loc='upper right', fontsize='x-small')
    ax.grid(True, linestyle=':', alpha=0.4)
    
    st.pyplot(fig)
