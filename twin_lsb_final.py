import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Byte NDT | Digital Twin LSB 941", layout="wide")

# --- 2. GÉOMÉTRIE (Équations Maple Recalées) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else: # EXTRADOS - Correction de l'inversion et décalage
        y = -(-0.003609 * t**2 + 0.39014 * t + 19.703) + 120 
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y, mode="Intrados"):
    if mode == "Intrados":
        return -0.001671 * y**2 + 0.00338 * y + 320.834
    else: # EXTRADOS
        return -0.002120 * y**2 + 0.01039 * y + 345.591

# --- 3. INTERFACE BILINGUE ---
st.title("🛡️ Byte NDT | Digital Twin LSB 941")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Settings / Paramètres")
    
    # Sélection de la langue / Language Toggle
    lang = st.radio("Language / Langue", ["Français", "English"], horizontal=True)
    
    labels = {
        "Français": {
            "mode": "Côté d'inspection", "pos": "Position Barrette PAUT (t)",
            "angle": "Angle de réfraction (Sectoriel)", "amp": "Amplitude Signal",
            "verdict": "Verdict de détection", "found": "EDM DÉTECTÉ", "search": "Recherche...",
            "surface": "Surface Aube", "fond": "Fond (EDM)", "probe": "Sonde PAUT"
        },
        "English": {
            "mode": "Inspection Side", "pos": "PAUT Probe Position (t)",
            "angle": "Refraction Angle (Sectorial)", "amp": "Signal Amplitude",
            "verdict": "Detection Verdict", "found": "EDM DETECTED", "search": "Scanning...",
            "surface": "Blade Surface", "fond": "Bottom (EDM)", "probe": "PAUT Probe"
        }
    }[lang]

    mode = st.radio(labels["mode"], ["Intrados", "Extrados"])
    t_scan = st.slider(labels["pos"], -50, 150, 35)
    angle_deg = st.slider(labels["angle"], 35, 75, 45 if mode == "Intrados" else 55)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    
    # Cible EDM fixe (recalée pour l'extrados)
    target_y = 65.0 if mode == "Intrados" else 45.0
    target_z = get_target_curve(target_y, mode)
    
    # Calcul d'impact physique
    # Inversion de la direction du faisceau pour l'Extrados
    direction = 1 if mode == "Intrados" else -1
    projected_y = y_p + direction * (target_z - z_p) * np.tan(np.radians(angle_deg))
    
    error = np.abs(projected_y - target_y)
    amplitude = np.exp(-(error**2) / 100)
    amp_db = 20 * np.log10(amplitude + 0.001)

    st.subheader(f"📊 {labels['amp']}")
    st.metric("Amplitude", f"{amp_db:.1f} dB")
    
    if amplitude > 0.6:
        st.error(f"🚨 {labels['found']} (NC)")
    else:
        st.info(f"⚪ {labels['search']}")

with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 1. Tracé de la géométrie de l'aube
    t_range = np.linspace(-50, 150, 300)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=4, label=labels["surface"])
    
    # 2. Tracé de la ligne des EDM
    ty_range = np.linspace(min(sy)-10, max(sy)+10, 100)
    tz_range = [get_target_curve(ty, mode) for ty in ty_range]
    ax.plot(ty_range, tz_range, 'k--', alpha=0.4, label=labels["fond"])

    # 3. Dessin Sonde & Sabot (Wedge)
    ax.add_patch(plt.Rectangle((y_p-12, z_p-8), 24, 8, color='gray', alpha=0.3))
    ax.add_patch(plt.Rectangle((y_p-10, z_p-10), 20, 3, color='blue', alpha=0.9, label=labels["probe"]))

    # 4. Faisceau Sectoriel (Dynamique)
    b_color = "red" if amplitude > 0.6 else "orange"
    ax.fill([y_p, projected_y-8, projected_y+8], [z_p, target_z, target_z], color=b_color, alpha=0.2)
    ax.plot([y_p, projected_y], [z_p, target_z], color=b_color, lw=2, ls='--')

    # 5. Cible EDM (Rectangle noir)
    ax.add_patch(plt.Rectangle((target_y-2, target_z-1.5), 4, 3, color='black', zorder=5))

    # --- RÉGLAGES D'AFFICHAGE ---
    ax.set_aspect('equal', adjustable='box')
    # Inversion Z pour avoir la surface en haut
    ax.set_ylim(max(tz_range)+20, min(sz)-20)
    ax.set_xlabel("Y (mm)")
    ax.set_ylabel("Z (mm)")
    ax.legend(loc='upper right', fontsize='small')
    ax.grid(True, linestyle=':', alpha=0.3)
    
    st.pyplot(fig)

# Pied de page bilingue
st.sidebar.markdown("---")
st.sidebar.info("💡 **Byte NDT** - Digital Twin & Machine Learning for NDT Inspection")
