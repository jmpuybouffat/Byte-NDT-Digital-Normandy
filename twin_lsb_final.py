import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. CONFIGURATION (Stable & Large)
st.set_page_config(page_title="Byte NDT | Console", layout="wide")

# 2. GÉOMÉTRIE (Sûre)
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else: # EXTRADOS recalé
        y = -(-0.003609 * t**2 + 0.39014 * t + 19.703) + 110 
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y, mode="Intrados"):
    if mode == "Intrados": return -0.001671 * y**2 + 0.00338 * y + 320.834
    else: return -0.002120 * y**2 + 0.01039 * y + 342.0

# 3. INTERFACE
st.title("🛡️ Byte NDT | Console de Démonstration")

# SIDEBAR : LE PENSE-BÊTE URL
st.sidebar.header("🔗 PENSE-BÊTE / APP URL")
st.sidebar.code("https://byte-ndt-digital-normandy-upuqs4f8h7mxbjr3pc75qo.streamlit.app/")
st.sidebar.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    lang = st.radio("Langue", ["FR", "EN"], horizontal=True)
    mode = st.radio("Côté", ["Intrados", "Extrados"], horizontal=True)
    t_scan = st.slider("Position (t)", -40, 140, 50)
    angle_deg = st.slider("Angle (°)", 30, 70, 45)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    target_y = 65.0 if mode == "Intrados" else 40.0
    target_z = get_target_curve(target_y, mode)
    
    # Physique de détection
    dir_f = 1 if mode == "Intrados" else -1
    projected_y = y_p + dir_f * (target_z - z_p) * np.tan(np.radians(angle_deg))
    amplitude = np.exp(-(np.abs(projected_y - target_y)**2) / 100)
    
    st.metric("Signal (dB)", f"{20*np.log10(amplitude+0.001):.1f}")
    if amplitude > 0.6: st.error("🚨 EDM DÉTECTÉ / DETECTED")

with col2:
    fig, ax = plt.subplots(figsize=(8, 6)) 
    
    # Profils
    t_range = np.linspace(-40, 140, 150)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=4, label="Surface")
    
    ty_range = np.linspace(-10, 160, 100)
    tz_range = [get_target_curve(ty, mode) for ty in ty_range]
    ax.plot(ty_range, tz_range, 'k--', alpha=0.3, label="Fond")

    # Sonde & Faisceau
    color_b = "red" if amplitude > 0.6 else "orange"
    ax.add_patch(plt.Rectangle((y_p-10, z_p-8), 20, 3, color='blue', alpha=0.8))
    ax.fill([y_p, projected_y-8, projected_y+8], [z_p, target_z, target_z], color=color_b, alpha=0.2)
    ax.plot([y_p, projected_y], [z_p, target_z], color=color_b, ls='--')

    # EDM
    ax.add_patch(plt.Rectangle((target_y-2, target_z-1), 4, 2, color='black'))

    # --- CADRAGE DE SÉCURITÉ ---
    ax.set_aspect('equal')
    ax.set_xlim(-10, 160) # Fenêtre Y fixe
    ax.set_ylim(360, 250) # Fenêtre Z fixe (Fond en bas, Surface en haut)
    ax.grid(True, alpha=0.1)
    
    st.pyplot(fig)
