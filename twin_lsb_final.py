import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION ÉCRAN LARGE ---
st.set_page_config(page_title="Byte NDT | Twin LSB 941", layout="wide")

# --- 2. GÉOMÉTRIE ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else: # EXTRADOS
        y = -(-0.003609 * t**2 + 0.39014 * t + 19.703) + 100 
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y, mode="Intrados"):
    if mode == "Intrados": return -0.001671 * y**2 + 0.00338 * y + 320.834
    else: return -0.002120 * y**2 + 0.01039 * y + 342.0

# --- 3. INTERFACE ---
st.title("🛡️ Byte NDT | Console de Simulation")

# Colonnes équilibrées pour petit écran
col1, col2 = st.columns([1, 1.2])

with col1:
    lang = st.radio("Language", ["Français", "English"], horizontal=True)
    mode = st.radio("Mode", ["Intrados", "Extrados"], horizontal=True)
    t_scan = st.slider("Position (t)", -40, 140, 45)
    angle_deg = st.slider("Angle (°)", 30, 70, 45 if mode=="Intrados" else 55)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    target_y = 65.0 if mode == "Intrados" else 35.0
    target_z = get_target_curve(target_y, mode)
    
    # Physique
    dir_f = 1 if mode == "Intrados" else -1
    projected_y = y_p + dir_f * (target_z - z_p) * np.tan(np.radians(angle_deg))
    amplitude = np.exp(-(np.abs(projected_y - target_y)**2) / 120)
    
    st.metric("Signal", f"{20*np.log10(amplitude+0.001):.1f} dB")
    if amplitude > 0.6: st.error("🚨 EDM DETECTED / DETECTÉ")

with col2:
    # TAILLE DU GRAPHIQUE RÉDUITE pour éviter de scroller
    fig, ax = plt.subplots(figsize=(6, 5)) 
    
    # Dessin des profils
    t_range = np.linspace(-40, 140, 200)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=3)
    
    ty_range = np.linspace(min(sy)-10, max(sy)+10, 100)
    tz_range = [get_target_curve(ty, mode) for ty in ty_range]
    ax.plot(ty_range, tz_range, 'k--', alpha=0.3)

    # Sonde et Sabot
    ax.add_patch(plt.Rectangle((y_p-10, z_p-6), 20, 6, color='gray', alpha=0.3))
    ax.add_patch(plt.Rectangle((y_p-8, z_p-8), 16, 2, color='blue', alpha=0.9))

    # Faisceau
    color_b = "red" if amplitude > 0.6 else "orange"
    ax.fill([y_p, projected_y-7, projected_y+7], [z_p, target_z, target_z], color=color_b, alpha=0.2)
    ax.plot([y_p, projected_y], [z_p, target_z], color=color_b, ls='--')

    # EDM
    ax.add_patch(plt.Rectangle((target_y-2, target_z-1), 4, 2, color='black', zorder=5))

    # --- REGLAGE ECHELLE ET VISIBILITÉ ---
    ax.set_aspect('equal')
    # On resserre la vue sur la zone utile pour que ce soit plus gros à l'écran
    ax.set_xlim(min(sy)-5, max(sy)+5)
    ax.set_ylim(max(tz_range)+10, min(sz)-10)
    
    # On agrandit les labels pour votre écran
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.grid(True, alpha=0.2)
    
    st.pyplot(fig)

# Lien direct bilingue
st.sidebar.markdown("---")
st.sidebar.write("🔗 **App Link / Lien App :**")
st.sidebar.code("https://byte-ndt-digital-normandy-upuqs4f8h7mxbjr3pc75qo.streamlit.app/")
