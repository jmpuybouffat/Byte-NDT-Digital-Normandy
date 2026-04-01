import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. GÉOMÉTRIE LSB 941 (Équations Maple) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else:
        y = -0.003609 * t**2 + 0.39014 * t + 19.703
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y):
    # Courbe des indications (Plan de détection)
    return -0.001671 * y**2 + 0.00338 * y + 320.834

# --- 2. CONFIGURATION DE L'INTERFACE ---
st.set_page_config(page_title="Byte NDT | Twin LSB 941", layout="wide")
st.title("🛡️ Byte NDT | Jumeau Numérique : Calibration EDM")

# Notes de synthèse bilingues
with st.expander("ℹ️ Note Technique / Technical Note"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**FR :** Simulation du couplage à 45°. L'EDM est fixe sur la courbe des indications. La détection n'est optimale que lorsque le faisceau est aligné géométriquement.")
    with col_b:
        st.write("**EN :** 45° coupling simulation. The EDM is fixed on the indications curve. Detection is optimal only when the beam is geometrically aligned.")

# --- 3. DÉFINITION DES EDMs FIXES (Positions synchronisées) ---
# J'ai ajusté 'y' pour qu'ils soient accessibles par le faisceau de la sonde
edms = {
    "EDM 1 (4x2x0.1)": {"y": 45.0, "h": 2.0, "color": "red"},
    "EDM 2 (4x4.1)": {"y": 80.0, "h": 4.1, "color": "orange"}
}

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Contrôle du Scan")
    mode = st.radio("Côté d'inspection", ["Intrados", "Extrados"])
    t_scan = st.slider("Position de la sonde (t)", -30, 110, 15)
    selected_target = st.selectbox("Cible EDM visée", list(edms.keys()))
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    target = edms[selected_target]
    z_target_fixed = get_target_curve(target['y'])
    
    # --- CALCUL DE L'INTERSECTION RÉELLE ---
    # On projette le faisceau à 45° jusqu'à la profondeur de l'EDM choisi
    projected_y = y_p + (z_target_fixed - z_p) * np.tan(np.radians(45))
    
    # Calcul de l'écart entre le faisceau et l'EDM fixe
    error = np.abs(projected_y - target["y"])
    
    # Modèle de réponse (Amplitude)
    beam_width = 10.0 # Largeur de tache acoustique (mm)
    amplitude = np.exp(-(error**2) / (beam_width**2))
    amp_db = 20 * np.log10(amplitude + 0.001)
    
    # Mesure de largeur simulée
    measured_w = target["h"] * (amplitude if amplitude > 0.4 else 0)
    
    st.metric("Amplitude Signal", f"{amp_db:.1f} dB")
    st.metric("Largeur à -6dB", f"{measured_w:.2f} mm")
    
    if measured_w >= 4.0:
        st.error(f"❌ {selected_target} : NON CONFORME (NC)")
    elif amplitude > 0.2:
        st.warning("⚠️ Signal détecté - Ajustez la position")
    else:
        st.info("⚪ Recherche de l'indication...")

with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 1. Profil de la racine
    t_range = np.linspace(-30, 110, 100)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=3, label="Profil Racine LSB 941")
    
    # 2. Courbe des Indications
    target_y_vals = np.linspace(0, 140, 100)
    target_z_vals = [get_target_curve(y) for y in target_y_vals]
    ax.plot(target_y_vals, target_z_vals, 'k--', alpha=0.3, label="Plan des EDM")

    # 3. Dessin des EDMs FIXES
    for name, data in edms.items():
        z_v = get_target_curve(data["y"])
        ax.add_patch(plt.Rectangle((data["y"]-2, z_v-1), 4, 2, color=data["color"], alpha=0.9, label=name))

    # 4. Dessin de la Sonde
    ax.scatter(y_p, z_p, color='blue', s=250, zorder=5, label="Sonde (5MHz)")
    
    # 5. Dessin du Faisceau (Dynamique)
    # Le triangle orange suit la sonde et montre le point d'impact calculé
    ax.fill([y_p, projected_y-5, projected_y+5], [z_p, z_target_fixed, z_target_fixed], color='orange', alpha=0.25, label="Faisceau 45°")
    ax.plot([y_p, projected_y], [z_p, z_target_fixed], color='orange', lw=2, ls='--')

    ax.set_ylim(350, 250) # Inversion pour profondeur
    ax.set_xlim(-10, 140)
    ax.set_xlabel("Position Y (mm)")
    ax.set_ylabel("Profondeur Z (mm)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.1)
    st.pyplot(fig)
