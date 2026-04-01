import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. MOTEUR PHYSIQUE (Schmeer & Snell) ---
def get_scattering_amplitude(f, b_size, cp):
    kp = (2000 * np.pi * b_size * f) / cp
    return np.abs(np.sinc(kp / 10)) * (b_size**2)

# --- 2. GÉOMÉTRIE (Vos équations Maple) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else:
        y = -0.003609 * t**2 + 0.39014 * t + 19.703
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

def get_target_curve(y):
    # Équation de la courbe des indications (cible)
    return -0.001671 * y**2 + 0.00338 * y + 320.834

# --- 3. INTERFACE STREAMLIT ---
st.set_page_config(page_title="Byte NDT | Twin LSB 941", layout="wide")
st.title("🛡️ Byte NDT | Jumeau Numérique : Calibration EDM")

# Explication Bilingue
with st.expander("ℹ️ Note Technique / Technical Note"):
    st.write("**FR :** Simulation du couplage à 45°. L'EDM est placé sur la courbe des indications pour calibrer la détection.")
    st.write("**EN :** 45° coupling simulation. The EDM is placed on the indications curve to calibrate detection.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Paramètres")
    mode = st.radio("Côté d'inspection", ["Intrados", "Extrados"])
    t_scan = st.slider("Position de la sonde (t)", -30, 110, 15)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    
    # Calcul de détection (Simulation)
    dist_to_target = 25 # Distance estimée du parcours sonore
    target_y = y_p + 18 # Projection à 45°
    target_z_real = get_target_curve(target_y)
    
    amp = get_scattering_amplitude(5.0, 2.0, 5900)
    measured_width = 4.0 + (np.random.normal(0, 0.05))
    
    st.metric("Amplitude Écho", f"{20*np.log10(amp+0.1):.1f} dB")
    st.metric("Largeur à -6dB", f"{measured_width:.2f} mm")
    
    if measured_width > 4.0:
        st.error("❌ Verdict : NON CONFORME (NC)")
    else:
        st.success("✅ Verdict : CONFORME (C)")

with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 1. Profil de la racine
    t_range = np.linspace(-30, 110, 100)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', lw=2, label="Profil Racine LSB 941")
    
    # 2. Courbe des Indications (La cible)
    y_target_range = np.linspace(y_p, y_p + 40, 50)
    z_target_range = [get_target_curve(y) for y in y_target_range]
    ax.plot(y_target_range, z_target_range, 'k--', alpha=0.4, label="Courbe des Indications")

    # 3. La Sonde (Bleue)
    ax.scatter(y_p, z_p, color='blue', s=250, zorder=5, label="Sonde 6mm 5MHz")
    
    # 4. LE FAISCEAU (Orange) - "Le Shot"
    # On dessine un triangle pour simuler l'ouverture du faisceau à 45°
    beam_y = [y_p, target_y - 6, target_y + 6]
    beam_z = [z_p, target_z_real, target_z_real]
    ax.fill(beam_y, beam_z, color='orange', alpha=0.3, label="Faisceau 45° (Shear)")
    ax.plot([y_p, target_y], [z_p, target_z_real], color='orange', lw=2) # Axe central

    # 5. L'EDM (Rouge)
    ax.add_patch(plt.Rectangle((target_y-2, target_z_real-1), 4, 2, color='red', zorder=6, label="EDM (4x4mm)"))
    
    ax.set_ylim(350, 250)
    ax.set_xlim(y_p - 20, y_p + 60)
    ax.set_xlabel("Y (mm)")
    ax.set_ylabel("Profondeur Z (mm)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)
