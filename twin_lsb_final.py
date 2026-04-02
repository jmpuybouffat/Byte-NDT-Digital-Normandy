import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. GÉOMÉTRIE LSB 941 (Équations Maple) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else: # EXTRADOS
        y = -0.003609 * t**2 + 0.39014 * t + 19.703
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y, mode="Intrados"):
    if mode == "Intrados":
        return -0.001671 * y**2 + 0.00338 * y + 320.834
    else: # EXTRADOS
        return -0.002120 * y**2 + 0.01039 * y + 275.591

# --- 2. CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Byte NDT | Digital Twin LSB 941", layout="wide")
st.title("🛡️ Byte NDT | Jumeau Numérique : Géométrie & Champ de Pression")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Contrôle Scan")
    mode = st.radio("Côté d'inspection", ["Intrados", "Extrados"])
    t_scan = st.slider("Position Sonde (t)", -50, 150, 20)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    
    # Cibles EDM fixes ajustées pour être dans la course du scan
    target_y = 65.0 if mode == "Intrados" else 50.0
    target_z = get_target_curve(target_y, mode)
    
    # Calcul intersection à 45°
    projected_y = y_p + (target_z - z_p) * np.tan(np.radians(45))
    error = np.abs(projected_y - target_y)
    
    # Modèle d'amplitude (Champ de pression Gaussien)
    amplitude = np.exp(-(error**2) / 120) 
    amp_db = 20 * np.log10(amplitude + 0.01)
    
    st.metric("Amplitude Signal", f"{amp_db:.1f} dB")
    
    if amplitude > 0.70: # Seuil -3dB approx
        st.error(f"🚨 NC : DÉTECTION CRITIQUE (-3dB zone)")
    elif amplitude > 0.50: # Seuil -6dB
        st.warning("⚠️ SIGNAL ALERTE (-6dB zone)")
    elif amplitude > 0.25: # Seuil -12dB
        st.info("⚪ Écho de structure détecté (-12dB)")

with col2:
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # 1. Surface (EN HAUT)
    t_range = np.linspace(-50, 150, 200)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=4, label=f"Surface PA ({mode})")
    
    # 2. Courbe des Indications (EN BAS)
    ty_range = np.linspace(min(sy), max(sy)+50, 100)
    tz_range = [get_target_curve(ty, mode) for ty in ty_range]
    ax.plot(ty_range, tz_range, 'k--', alpha=0.5, label="Courbe de fond (Indications)")

    # 3. L'EDM Fixe
    ax.add_patch(plt.Rectangle((target_y-2, target_z-1.5), 4, 3, color='black', alpha=0.8, zorder=5, label="EDM 4x4"))

    # 4. Faisceau et Champ de Pression
    b_color = "red" if amplitude > 0.5 else "orange"
    # Faisceau principal
    ax.fill([y_p, projected_y-8, projected_y+8], [z_p, target_z, target_z], color=b_color, alpha=0.2)
    ax.plot([y_p, projected_y], [z_p, target_z], color=b_color, lw=2, ls='--')

    # Simulation de la tache de pression (Gradient -3, -6, -12 dB)
    if amplitude > 0.1:
        # Zone -12dB (Large et claire)
        ax.add_artist(plt.Circle((target_y, target_z), 12 * amplitude, color='red', alpha=0.15))
        # Zone -6dB (Moyenne)
        ax.add_artist(plt.Circle((target_y, target_z), 7 * amplitude, color='red', alpha=0.3))
        # Zone -3dB (Cœur du faisceau)
        ax.add_artist(plt.Circle((target_y, target_z), 3 * amplitude, color='red', alpha=0.6))
    
    # Sonde
    ax.scatter(y_p, z_p, color='blue', s=300, zorder=10, label="Sonde")

    # --- REGLAGE DU FORMAT GÉOMÉTRIQUE ---
    # On force l'axe Z à montrer la surface en haut et le fond en bas
    ax.set_ylim(max(tz_range)+15, min(sz)-15) 
    ax.set_xlabel("Axe Y - Longueur (mm)")
    ax.set_ylabel("Axe Z - Profondeur (mm)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)
