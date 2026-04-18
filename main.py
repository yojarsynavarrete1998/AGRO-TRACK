import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AgroTrack Pro", layout="wide", page_icon="🚜")

# Zona Horaria Honduras
hn_tz = pytz.timezone('America/Tegucigalpa')
def hora_hn():
    return datetime.now(hn_tz)

# --- BASE DE DATOS (ESTADO DE SESIÓN) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "log_actividades": [],
        "parcelas": {f"Parcela {i}": "Libre" for i in range(1, 11)},
        "seleccionada": None
    }

db = st.session_state.db

st.title("🚜 AgroTrack Pro - Alnagro 🇭🇳")
st.write(f"📅 **Fecha:** {hora_hn().strftime('%d/%m/%Y')} | ⏰ **Hora:** {hora_hn().strftime('%H:%M:%S')}")

# --- SECCIÓN 1: MAPA DE PARCELAS ---
st.subheader("📍 Mapa de Bloques (Toca uno para ver detalles)")
cols = st.columns(5)
for i, (nombre, estado) in enumerate(db["parcelas"].items()):
    with cols[i % 5]:
        # El botón cambia de estilo si la parcela está seleccionada
        tipo_boton = "primary" if db["seleccionada"] == nombre else "secondary"
        if st.button(f"{nombre}\n({estado})", key=f"btn_{nombre}", type=tipo_boton, use_container_width=True):
            db["seleccionada"] = nombre
            st.rerun()

st.divider()

# --- SECCIÓN 2: EXPEDIENTE DE LA PARCELA SELECCIONADA ---
if db["seleccionada"]:
    p_sel = db["seleccionada"]
    st.header(f"📋 Expediente: {p_sel}")
    
    col_info, col_registro = st.columns([2, 1])

    with col_info:
        st.subheader("📜 Historial de Labores")
        if db["log_actividades"]:
            df = pd.DataFrame(db["log_actividades"])
            # Filtramos para mostrar solo lo de esta parcela
            df_parcela = df[df["Parcela"] == p_sel]
            if not df_parcela.empty:
                st.dataframe(df_parcela.drop(columns=["Parcela"]), use_container_width=True)
            else:
                st.info("No hay registros previos para esta parcela.")
        else:
            st.info("La bitácora está vacía.")

    with col_registro:
        st.subheader("➕ Registrar Labor")
        with st.form("nueva_labor"):
            tipo_labor = st.selectbox("Tipo de Actividad", [
                "Cosecha", "Fertirriego", "Control Fitosanitario", 
                "Mantenimiento Riego", "Labor Cultural", "Monitoreo"
            ])
            detalle = st.text_input("Detalle (Ej: 50 cestas / Urea / Gusano)")
            responsable = st.text_input("Responsable")
            
            if st.form_submit_button("Guardar en Bitácora"):
                nueva_entrada = {
                    "Fecha": hora_hn().strftime("%Y-%m-%d %H:%M"),
                    "Parcela": p_sel,
                    "Actividad": tipo_labor,
                    "Detalle": detalle,
                    "Responsable": responsable
                }
                db["log_actividades"].append(nueva_entrada)
                # Si es cosecha, podríamos cambiar el estado a "En Cosecha"
                if tipo_labor == "Cosecha":
                    db["parcelas"][p_sel] = "COSECHANDO"
                
                st.success(f"Registrado en {p_sel}")
                st.rerun()
    
    if st.button("⬅️ Deseleccionar Parcela"):
        db["seleccionada"] = None
        st.rerun()
else:
    st.info("👆 Toca una parcela arriba para ver su historial o registrar una nueva actividad.")

# --- SECCIÓN 3: EXPORTACIÓN ---
st.divider()
if st.sidebar.button("🗑️ Reiniciar Todo (Cuidado)"):
    st.session_state.db = {
        "log_actividades": [],
        "parcelas": {f"Parcela {i}": "Libre" for i in range(1, 11)},
        "seleccionada": None
    }
    st.rerun()

if db["log_actividades"]:
    st.sidebar.subheader("📥 Descargas")
    df_full = pd.DataFrame(db["log_actividades"])
    csv = df_full.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Descargar Bitácora Completa", csv, "bitacora_alnagro.csv", "text/csv")





