import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ARGEAL Control", layout="wide", page_icon="🌱")

hn_tz = pytz.timezone('America/Tegucigalpa')
def hora_hn():
    return datetime.now(hn_tz)

# --- INICIALIZACIÓN DE BASES DE DATOS SEPARADAS ---
if 'db_okra' not in st.session_state:
    st.session_state.db_okra = {"log": [], "parcelas": {f"O-{i}": "Libre" for i in range(1, 11)}, "sel": None}

if 'db_maiz' not in st.session_state:
    st.session_state.db_maiz = {"log": [], "parcelas": {f"M-{i}": "Libre" for i in range(1, 11)}, "sel": None}

if 'segmento' not in st.session_state:
    st.session_state.segmento = None

# --- PANTALLA DE SELECCIÓN INICIAL ---
if st.session_state.segmento is None:
    st.title("🏢 ARGEAL - Gestión Agrícola")
    st.subheader("Seleccione el segmento de producción:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Aquí puedes subir un archivo llamado logo_okra.png a tu GitHub
        if os.path.exists("logo_okra.png"):
            st.image("logo_okra.png", width=200)
        st.header("🟢 OKRA")
        if st.button("Entrar a Okra", use_container_width=True):
            st.session_state.segmento = "Okra"
            st.rerun()
            
    with col2:
        # Aquí puedes subir un archivo llamado logo_maiz.png a tu GitHub
        if os.path.exists("logo_maiz.png"):
            st.image("logo_maiz.png", width=200)
        st.header("🌽 MAÍZ")
        if st.button("Entrar a Maíz", use_container_width=True):
            st.session_state.segmento = "Maiz"
            st.rerun()

# --- INTERFAZ INTERNA DE SEGMENTO ---
else:
    seg = st.session_state.segmento
    db = st.session_state.db_okra if seg == "Okra" else st.session_state.db_maiz
    
    # Encabezado Personalizado
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        archivo_logo = "logo_okra.png" if seg == "Okra" else "logo_maiz.png"
        if os.path.exists(archivo_logo):
            st.image(archivo_logo, width=100)
    with col_titulo:
        st.title(f"ARGEAL - Proyecto {seg}")
        if st.button("⬅️ Cambiar Segmento"):
            st.session_state.segmento = None
            st.rerun()

    st.write(f"⏰ {hora_hn().strftime('%d/%m/%Y | %H:%M:%S')}")

    # --- MAPA DE PARCELAS ---
    st.subheader(f"📍 Bloques de {seg}")
    cols = st.columns(5)
    for i, (nombre, estado) in enumerate(db["parcelas"].items()):
        with cols[i % 5]:
            tipo = "primary" if db["sel"] == nombre else "secondary"
            if st.button(f"{nombre}\n({estado})", key=f"btn_{seg}_{nombre}", type=tipo, use_container_width=True):
                db["sel"] = nombre
                st.rerun()

    # --- EXPEDIENTE ---
    if db["sel"]:
        p_sel = db["sel"]
        st.divider()
        st.header(f"📋 Expediente: {p_sel}")
        
        c_inf, c_reg = st.columns([2, 1])

        with c_inf:
            if db["log"]:
                df = pd.DataFrame(db["log"])
                df_p = df[df["Parcela"] == p_sel]
                if not df_p.empty:
                    st.dataframe(df_p.drop(columns=["Parcela"]), use_container_width=True)
                else:
                    st.info("Sin registros.")
            else:
                st.info("Bitácora vacía.")

        with c_reg:
            with st.form(f"form_{seg}"):
                act = st.selectbox("Actividad", ["Cosecha", "Fertirriego", "Fitosanitario", "Mantenimiento", "Labor Cultural"])
                det = st.text_input("Detalle")
                resp = st.text_input("Responsable")
                if st.form_submit_button("Guardar"):
                    db["log"].append({
                        "Fecha": hora_hn().strftime("%Y-%m-%d %H:%M"),
                        "Parcela": p_sel,
                        "Actividad": act,
                        "Detalle": det,
                        "Responsable": resp
                    })
                    if act == "Cosecha": db["parcelas"][p_sel] = "EN COSECHA"
                    st.success("Guardado")
                    st.rerun()


