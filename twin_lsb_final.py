import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION (Stable & Large) ---
st.set_page_config(page_title="Byte NDT | Twin LSB 941", layout="wide")

# --- 2. GÉOMÉTRIE (Inchangée, validée par vos tests) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else: # EXTRADOS
        y = -(-0.003609 * t**2 + 0.39014 * t + 19.703) + 110 
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y, mode="Intrados"):
    if mode == "Intrados": return -0.001671 * y**2 + 0.00338 * y + 320.834
    else: return -0.002120 * y**2 + 0.01039 * y + 342.0

# --- 3. INTERFACE ---
st.title("🛡️ Byte NDT | Console de Simulation")

col1, col2 = st.columns([1, 2]) # On donne plus de place au graphique

with col1:
    lang = st.radio("Language", ["Français", "English"], horizontal=True)
    mode = st.radio("Mode", ["Intrados", "Extrados"], horizontal=True)
    t_scan = st.slider("Position (t)", -40, 140, 52)
    angle_deg = st.slider("Angle (°)", 30, 70, 45)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    target_y = 65.0 if mode == "Intrados" else 40.0
    target_z = get_target_curve(target_y, mode)
    
    # Calcul détection
    dir_f = 1 if mode == "Intrados" else -1
    projected_y = y_p + dir_f * (target_z - z_p) * np.tan(np.radians(angle_deg))
    amplitude = np.exp(-(np.abs(projected_y - target_y)**2) / 100)
    
    st.metric("Signal", f"{20*np.log10(amplitude+0.001):.1f} dB")
    if amplitude > 0.6: st.error("🚨 EDM DETECTED / DÉTECTÉ")

with col2:
    # On fixe une taille de figure standard
    fig, ax = plt.subplots(figsize=(10, 7)) 
    
    # Profils
    t_range = np.linspace(-40, 140, 200)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=4, label="Surface")
    
    ty_range = np.linspace(0, 150, 100)
    tz_range = [get_target_curve(ty, mode) for ty in ty_range]
    ax.plot(ty_range, tz_range, 'k--', alpha=0.3, label="Fond")

    # Sonde & Sabot
    ax.add_patch(plt.Rectangle((y_p-12, z_p-8), 24, 8, color='gray', alpha=0.3))
    ax.add_patch(plt.Rectangle((y_p-10, z_p-10), 20, 2, color='blue', alpha=0.9))

    # Faisceau
    color_b = "red" if amplitude > 0.6 else "orange"
    ax.fill([y_p, projected_y-8, projected_y+8], [z_p, target_z, target_z], color=color_b, alpha=0.2)
    ax.plot([y_p, projected_y], [z_p, target_z], color=color_b, ls='--', lw=2)

    # EDM
    ax.add_patch(plt.Rectangle((target_y-2, target_z-1), 4, 2, color='black', zorder=5))

    # --- CADRAGE FIXE (LA SOLUTION) ---
    ax.set_aspect('equal')
    # On définit des limites fixes qui marchent pour les deux modes
    ax.set_xlim(-10, 160)
    ax.set_ylim(360, 250) # De 360 (fond) à 250 (air)
    
    ax.set_xlabel("Y (mm)")
    ax.set_ylabel("Z (mm)")
    ax.grid(True, alpha=0.2)
    ax.legend(loc="upper right")
    
    st.pyplot(fig)
