import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. MOTEUR PHYSIQUE (Schmeer C7/G.7) ---
def get_scattering_amplitude(f, b_size, cp, cs):
    kp = (2000 * np.pi * b_size * f) / cp
    A_base = np.abs(np.sinc(kp / 10)) * (b_size**2)
    return A_base

# --- 2. GÉOMÉTRIE DE L'AUBE (Équations Maple) ---
def get_lsb_geometry(t, mode="Intrados"):
    if mode == "Intrados":
        y = 0.001808 * t**2 - 0.13147 * t + 17.336
        z = -0.003862 * t**2 + 0.13915 * t + 276.437
    else:
        y = -0.003609 * t**2 + 0.39014 * t + 19.703
        z = -0.005488 * t**2 + 0.40635 * t + 322.563
    return y, z

# --- 3. INTERFACE STREAMLIT ---
st.set_page_config(page_title="Byte NDT | LSB 941 Digital Twin", layout="wide")
st.title("🛡️ Byte NDT | Jumeau Numérique de Calibration")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Paramètres")
    mode = st.radio("Côté d'inspection", ["Intrados", "Extrados"])
    t_scan = st.slider("Position de la sonde (t)", -30, 110, 0)
    
    y_p, z_p = get_lsb_geometry(t_scan, mode)
    amp = get_scattering_amplitude(5.0, 2.0, 5900, 3230)
    measured_width = 4.0 + (np.random.normal(0, 0.05))
    
    st.metric("Amplitude Écho", f"{20*np.log10(amp+0.1):.1f} dB")
    st.metric("Largeur à -6dB", f"{measured_width:.2f} mm")
    
    if measured_width > 4.0:
        st.error("❌ Verdict : NON CONFORME (NC)")
    else:
        st.success("✅ Verdict : CONFORME (C)")

with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    t_range = np.linspace(-30, 110, 100)
    pts = [get_lsb_geometry(tr, mode) for tr in t_range]
    sy, sz = zip(*pts)
    ax.plot(sy, sz, 'g-', label="Profil Racine LSB 941")
    ax.scatter(y_p, z_p, color='blue', s=200, label="Sonde")
    ax.arrow(y_p, z_p, 15, 15, head_width=3, color='orange', alpha=0.6)
    
    ax.set_ylim(350, 250)
    ax.set_xlabel("Y (mm)")
    ax.set_ylabel("Z (mm)")
    ax.legend()
    st.pyplot(fig)
