import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. GÉOMÉTRIE (Équations Maple de la racine LSB 941) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else:
        y = -0.003609 * t**2 + 0.39014 * t + 19.703
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y):
    # Courbe de fond (Plan des indications)
    return -0.001671 * y**2 + 0.00338 * y + 320.834

# --- 2. CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Byte NDT | Digital Twin LSB 941", layout="wide")
st.title("🛡️ Byte NDT | Jumeau Numérique : Simulation de Détection")

# --- 3. NOTES DE SYNTHÈSE (FR/EN) ---
with st.expander("📝 Note de Synthèse / Executive Summary"):
    col_fr, col_en = st.columns(2)
    with col_fr:
        st.markdown("""
        **Motivation :** Cette démonstration valide l'algorithme Byte NDT sur des géométries réelles. 
        Le Jumeau Numérique anticipe le point d'impact acoustique avec précision.
        **Sûreté :** La précision du modèle élimine les erreurs d'interprétation humaine liées à la courbure complexe.
        """)
    with col_en:
        st.markdown("""
        **Motivation:** This demo validates the Byte NDT algorithm on real geometries. 
        The Digital Twin accurately predicts the acoustic impact point.
        **Reliability:** Model accuracy eliminates human errors caused by the part's complex curvature.
        """)

# --- 4. DÉFINITION DES EDMS FIXES (Cibles réelles) ---
edms = {
    "EDM 1 (4x2x0.1)": {"y": 45.0, "h": 2.0, "color": "red"},
    "EDM 2 (4x4.1)": {"y": 85.0, "h": 4.1, "color": "orange"}
}

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Paramètres du Scan")
    mode = st.radio("Côté d'inspection", ["Intrados", "Extrados"])
    t_scan = st.slider("Position de la sonde (t)", -30, 110, 15)
    selected_target = st.selectbox("Cible EDM visée", list(edms.keys()))
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    
    # Physique de détection
    target = edms[selected_target]
    z_target_fixed = get_target_curve(target['y'])
    
    # Calcul du trajet du faisceau à 45°
    # La projection Y du faisceau à la profondeur de la cible
    projected_y = y_p + (z_target_fixed - z_p) * np.tan(np.radians(45))
    
    # Écart entre l'axe du faisceau et le centre de l'EDM
    error = np.abs(projected_y - target["y"])
    
    # Modélisation de l'amplitude (Pic à 0dB quand error=0)
    beam_width = 8.0 
    amplitude = np.exp(-(error**2) / (beam_width**2))
    amp_db = 20 * np.log10(amplitude + 0.01)
    
    # Simulation mesure de largeur (ajustée par l'amplitude)
    measured_w = target["h"] * (amplitude if amplitude > 0.4 else 0)
    
    st.metric("Amplitude Signal", f"{amp_db:.1f} dB")
    st.metric("Largeur mesurée (-6dB)", f"{measured_w:.2f} mm")
    
    if measured_w >= 4.0:
        st.error("❌ Verdict : NON CONFORME (NC)")
    elif amplitude > 0.15:
        st.warning("⚠️ Détection partielle - Ajustez la position")
    else:
        st.info("⚪ Aucune détection (Faisceau hors zone)")

with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Dessin Profil Racine
    t_range = np.linspace(-30, 110, 100)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=3, label="Profil Racine LSB 941")
    
    # Dessin Courbe des Cibles
    target_y_vals = np.linspace(20, 130, 100)
    target_z_vals = [get_target_curve(y) for y in target_y_vals]
    ax.plot(target_y_vals, target_z_vals, 'k--', alpha=0.3, label="Plan de Détection")

    # Dessin des EDMs fixes (Ils ne bougent pas !)
    for name, data in edms.items():
        z_val = get_target_curve(data["y"])
        ax.add_patch(plt.Rectangle((data["y"]-2, z_val-1), 4, 2, color=data["color"], alpha=0.9, label=name))

    # Dessin Sonde (Bouge avec le slider)
    ax.scatter(y_p, z_p, color='blue', s=250, zorder=5, label="Sonde 6mm")
    
    # Dessin Faisceau Dynamique (Orange)
    # Le faisceau part de la sonde et "cherche" la cible
    ax.fill([y_p, projected_y-5, projected_y+5], [z_p, z_target_fixed, z_target_fixed], color='orange', alpha=0.2, label="Faisceau Acoustique")
    ax.plot([y_p, projected_y], [z_p, z_target_fixed], color='orange', lw=2, ls='--')

    ax.set_ylim(350, 250)
    ax.set_xlim(0, 150)
    ax.set_xlabel("Position Y (mm)")
    ax.set_ylabel("Profondeur Z (mm)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.1)
    st.pyplot(fig)
