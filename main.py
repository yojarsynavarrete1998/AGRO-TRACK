import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(page_title="ARGEAL Smart Control", layout="wide")

# Estilo personalizado: Fondo oscuro y tarjetas llamativas
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { border-radius: 10px; height: 3em; font-weight: bold; }
    .urgente { background-color: #ff4b4b; color: white; border-radius: 5px; padding: 10px; }
    .preventivo { background-color: #ffa500; color: white; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

hn_tz = pytz.timezone('America/Tegucigalpa')
def hora_hn(): return datetime.now(hn_tz)

# --- BASES DE DATOS ---
if 'db' not in st.session_state:
    # Estructura con fecha de siembra y alertas
    st.session_state.db = {
        "Okra": {"log": [], "parcelas": {f"O-{i}": {"estado": "Libre", "siembra": None, "bloqueo": None} for i in range(1, 11)}},
        "Maiz": {"log": [], "parcelas": {f"M-{i}": {"estado": "Libre", "siembra": None, "bloqueo": None} for i in range(1, 11)}},
        "segmento": None,
        "sel": None
    }

db = st.session_state.db

# --- SELECTOR DE SEGMENTO ---
if db["segmento"] is None:
    st.title("🏢 ARGEAL - Centro de Mando")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚜 ENTRAR A OKRA (Exportación)", use_container_width=True):
            db["segmento"] = "Okra"; st.rerun()
    with col2:
        if st.button("🌽 ENTRAR A MAÍZ (Grano)", use_container_width=True):
            db["segmento"] = "Maiz"; st.rerun()
else:
    seg = db["segmento"]
    p_data = db[seg]["parcelas"]
    
    st.title(f"PROYECTO {seg.upper()} - ARGEAL")
    if st.button("⬅️ Volver al Menú Principal"):
        db["segmento"] = None; st.rerun()

    # --- MAPA VISUAL CON ALERTAS ---
    st.subheader("📍 Estado de Bloques")
    cols = st.columns(5)
    for i, (id_p, info) in enumerate(p_data.items()):
        with cols[i % 5]:
            # Lógica de colores según estado
            color = "secondary"
            label = f"{id_p}\n{info['estado']}"
            
            # Alerta de bloqueo por carencia
            if info['bloqueo'] and hora_hn().date() < info['bloqueo']:
                color = "primary" # Azul/Rojo en Streamlit para resaltar
                label = f"🚫 {id_p}\nBLOQUEADO"
            elif info['estado'] == "URGENTE":
                label = f"⚠️ {id_p}\nREVISAR"

            if st.button(label, key=id_p, type=color, use_container_width=True):
                db["sel"] = id_p
                st.rerun()

    # --- EXPEDIENTE Y FORMULARIO ---
    if db["sel"]:
        p_sel = db["sel"]
        st.divider()
        col_exp, col_form = st.columns([2, 1])

        with col_exp:
            st.header(f"📋 Detalles {p_sel}")
            # Mostrar días desde la siembra
            if p_data[p_sel]['siembra']:
                dias = (hora_hn().date() - p_data[p_sel]['siembra']).days
                st.metric("Edad del Cultivo", f"{dias} días")
            
            if p_data[p_sel]['bloqueo']:
                restante = (p_data[p_sel]['bloqueo'] - hora_hn().date()).days
                if restante > 0:
                    st.error(f"⚠️ Días de Carencia restantes: {restante} días. ¡No Cosechar!")

        with col_form:
            st.subheader("⚙️ Registrar Labor")
            with st.form("registro"):
                tipo = st.selectbox("Prioridad/Labor", [
                    "Normal: Cosecha", 
                    "Normal: Fertirriego",
                    "MANEJABLE: Labor Cultural",
                    "EXIGENTE: Control Plagas",
                    "BLOQUEO: Aplicación Química"
                ])
                fecha_s = st.date_input("¿Fecha de Siembra?", value=None)
                dias_c = st.number_input("Días de Carencia (si aplica)", min_value=0)
                det = st.text_area("Notas")
                
                if st.form_submit_button("Actualizar Parcela"):
                    # Guardar log
                    db[seg]["log"].append({"Fecha": hora_hn(), "P": p_sel, "Tarea": tipo, "Nota": det})
                    
                    # Actualizar estado de la parcela
                    if "EXIGENTE" in tipo: p_data[p_sel]["estado"] = "URGENTE"
                    else: p_data[p_sel]["estado"] = "Activo"
                    
                    if fecha_s: p_data[p_sel]["siembra"] = fecha_s
                    if dias_c > 0:
                        p_data[p_sel]["bloqueo"] = hora_hn().date() + timedelta(days=dias_c)
                    
                    st.success("Información actualizada")
                    st.rerun()



