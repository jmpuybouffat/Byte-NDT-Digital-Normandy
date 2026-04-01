import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. GÉOMÉTRIE (Équations Maple adaptées) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else: # EXTRADOS - Repère inversé
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
st.title("🛡️ Byte NDT | Jumeau Numérique : Détection Active")

# Notes de synthèse
with st.expander("📝 Note de Synthèse / Executive Summary"):
    col_fr, col_en = st.columns(2)
    with col_fr:
        st.markdown("**Motivation :** Simulation en temps réel du couplage acoustique à 45°. L'allumage du faisceau valide l'alignement géométrique sur la racine LSB 941.")
    with col_en:
        st.markdown("**Motivation:** Real-time 45° acoustic coupling simulation. Beam activation validates geometric alignment on the LSB 941 root.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Contrôle Scan")
    mode = st.radio("Côté d'inspection", ["Intrados", "Extrados"])
    t_scan = st.slider("Position Sonde (t)", -50, 150, 20)
    
    # Paramètres de la sonde
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    
    # Cible EDM fixe (ajustée selon le côté pour être dans le champ)
    target_y = 65.0 if mode == "Intrados" else 45.0
    target_z = get_target_curve(target_y, mode)
    
    # Calcul intersection faisceau à 45°
    projected_y = y_p + (target_z - z_p) * np.tan(np.radians(45))
    error = np.abs(projected_y - target_y)
    
    # Modèle d'amplitude (Tache de 10mm)
    amplitude = np.exp(-(error**2) / 80) 
    amp_db = 20 * np.log10(amplitude + 0.01)
    
    # --- LOGIQUE D'ALLUMAGE ---
    is_detected = amplitude > 0.75
    
    st.metric("Amplitude Signal", f"{amp_db:.1f} dB")
    
    if is_detected:
        st.error(f"🚨 EDM DÉTECTÉ (NC) - Position t={t_scan}")
        st.write(f"Largeur calculée : {4.1 * amplitude:.2f} mm")
    elif amplitude > 0.2:
        st.warning("⚠️ Écho détecté - Optimisation en cours...")
    else:
        st.info("⚪ Recherche d'indication...")

with col2:
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # 1. Tracé de la surface
    t_vals = np.linspace(-50, 150, 200)
    surf_pts = [get_lsb_geometry(tv, mode) for tv in t_vals]
    sy, sz = zip(*surf_pts)
    ax.plot(sy, sz, 'g-', lw=3, label=f"Surface {mode}")
    
    # 2. Tracé courbe cible
    ty_vals = np.linspace(min(sy), max(sy)+40, 100)
    tz_vals = [get_target_curve(ty, mode) for ty in ty_vals]
    ax.plot(ty_vals, tz_vals, 'k--', alpha=0.3, label="Plan Focal")

    # 3. L'EDM Fixe (Cible)
    ax.add_patch(plt.Rectangle((target_y-2, target_z-1), 4, 2, color='black', alpha=0.7, label="EDM 4x4"))

    # 4. LE FAISCEAU DYNAMIQUE ("L'ALLUMAGE")
    beam_color = "red" if is_detected else "orange"
    beam_alpha = 0.2 + (0.5 * amplitude) # S'intensifie au contact
    
    ax.fill([y_p, projected_y-6, projected_y+6], [z_p, target_z, target_z], 
            color=beam_color, alpha=beam_alpha, label="Faisceau PAUT")
    ax.plot([y_p, projected_y], [z_p, target_z], color=beam_color, lw=2, ls='--')

    # 5. LE SPOT DE RÉPONSE (Tache acoustique)
    if amplitude > 0.15:
        circle = plt.Circle((target_y, target_z), 6 * amplitude, color='red', alpha=amplitude*0.8)
        ax.add_artist(circle)
    
    # Sonde
    ax.scatter(y_p, z_p, color='blue', s=250, zorder=10)

    # Mise en forme
    ax.set_ylim(max(tz_vals)+20, min(sz)-20) # Auto-zoom
    ax.set_xlabel("Y (mm)")
    ax.set_ylabel("Profondeur Z (mm)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.1)
    st.pyplot(fig)
