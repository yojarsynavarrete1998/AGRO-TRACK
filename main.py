import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="AgroTrack Pro Honduras", layout="wide", page_icon="🚜")

# --- CONFIGURACIÓN DE ZONA HORARIA (HONDURAS) ---
hn_tz = pytz.timezone('America/Tegucigalpa')

def obtener_hora_hn():
    return datetime.now(hn_tz)

# --- BASE DE DATOS COMPARTIDA (Persiste para todos los usuarios) ---
@st.cache_resource
def inicializar_db_comun():
    return {
        "historial": [],
        "fertilizantes": [],
        "cosecha": [],
        "parcelas": {f"Parcela {i}": "Libre" for i in range(1, 11)}, # Ajustado a 10 parcelas
        "cronometros": {
            "Riego": {"activo": False, "inicio": None},
            "Foliar": {"activo": False, "inicio": None},
            "Fertirriego": {"activo": False, "inicio": None}
        }
    }

db = inicializar_db_comun()

st.title("🚜 AgroTrack Pro - Honduras 🇭🇳")
st.write(f"⏰ **Hora Local:** {obtener_hora_hn().strftime('%H:%M:%S')} | **Fecha:** {obtener_hora_hn().strftime('%d/%m/%Y')}")

# --- SECCIÓN 1: ESTADO DE PARCELAS (RECUPERADO) ---
st.header("📍 Mapa de Bloques / Parcelas")
st.info("Instrucciones: Haz clic en una parcela para marcarla como 'EN LABOR' (Rojo) o 'Libre' (Verde).")

# Crear una cuadrícula para las parcelas
cols_p = st.columns(5) 
for i, (nombre, estado) in enumerate(db["parcelas"].items()):
    with cols_p[i % 5]:
        if estado == "Libre":
            st.success(f"🟢 {nombre}")
            if st.button(f"Ocupar {nombre}", key=f"btn_{nombre}"):
                db["parcelas"][nombre] = "EN LABOR"
                st.rerun()
        else:
            st.error(f"🔴 {nombre}")
            if st.button(f"Liberar {nombre}", key=f"btn_{nombre}"):
                db["parcelas"][nombre] = "Libre"
                st.rerun()

st.divider()

# --- SECCIÓN 2: CONTROL DE LABORES ---
st.header("⚡ Labores en Tiempo Real")
c1, c2, c3 = st.columns(3)

def controlador(nombre_tarea, columna):
    with columna:
        estado = db["cronometros"][nombre_tarea]
        if not estado["activo"]:
            if st.button(f"▶️ Iniciar {nombre_tarea}", use_container_width=True):
                db["cronometros"][nombre_tarea]["activo"] = True
                db["cronometros"][nombre_tarea]["inicio"] = obtener_hora_hn()
                st.rerun()
        else:
            st.warning(f"⏳ {nombre_tarea} EN CURSO")
            if st.button(f"⏹️ Finalizar {nombre_tarea}", type="primary", use_container_width=True):
                fin = obtener_hora_hn()
                duracion = str(fin - estado["inicio"]).split(".")[0]
                db["historial"].append({
                    "Fecha": fin.strftime("%Y-%m-%d"),
                    "Labor": nombre_tarea,
                    "Inicio": estado["inicio"].strftime("%H:%M:%S"),
                    "Fin": fin.strftime("%H:%M:%S"),
                    "Duración": duracion
                })
                db["cronometros"][nombre_tarea]["activo"] = False
                st.rerun()

controlador("Riego", c1)
controlador("Foliar", c2)
controlador("Fertirriego", c3)

# --- SECCIÓN 3: DETALLES DE FERTIRRIEGO ---
if db["cronometros"]["Fertirriego"]["activo"]:
    st.markdown("### 🧪 Insumos para Fertirriego")
    with st.form("form_fertilizante"):
        insumo = st.text_input("Producto / Fertilizante")
        cant = st.number_input("Cantidad (kg o L)", min_value=0.0)
        enviar = st.form_submit_button("Registrar Insumo")
        if enviar:
            db["fertilizantes"].append({
                "Hora": obtener_hora_hn().strftime("%H:%M"),
                "Producto": insumo,
                "Cantidad": cant
            })
            st.toast("Insumo registrado correctamente")

# --- SECCIÓN 4: COSECHA ---
st.divider()
st.header("🧺 Registro de Cosecha")
with st.container():
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cant_cestas = st.number_input("Número de cestas", min_value=0, step=1)
    with col_c2:
        if st.button("📥 Guardar Cosecha", use_container_width=True):
            ahora = obtener_hora_hn()
            db["cosecha"].append({
                "Fecha": ahora.strftime("%Y-%m-%d"),
                "Semana": ahora.isocalendar()[1],
                "Cestas": cant_cestas
            })
            st.success(f"Registradas {cant_cestas} cestas")

# --- SECCIÓN 5: REPORTES ---
st.divider()
st.header("📊 Resumen de Datos")

tab1, tab2, tab3 = st.tabs(["Cosecha", "Fertilizantes", "Historial Tiempos"])

with tab1:
    if db["cosecha"]:
        df_c = pd.DataFrame(db["cosecha"])
        # Reporte Diario
        st.subheader("Diario")
        diario = df_c.groupby("Fecha")["Cestas"].sum().reset_index()
        st.dataframe(diario, use_container_width=True)
        # Reporte Semanal
        st.subheader("Semanal")
        semanal = df_c.groupby("Semana")["Cestas"].sum().reset_index()
        st.dataframe(semanal, use_container_width=True)
        
        csv = diario.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Excel Cosecha", csv, "cose



