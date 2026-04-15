import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroTrack Pro Honduras", layout="wide", page_icon="🚜")

# --- SECCIÓN DEL LOGO ---
logo_path = "logo.png" 
if os.path.exists(logo_path):
    col_logo, _ = st.columns([1, 4])
    with col_logo:
        st.image(logo_path, width=150)

# --- ZONA HORARIA HONDURAS ---
hn_tz = pytz.timezone('America/Tegucigalpa')
def obtener_hora_hn():
    return datetime.now(hn_tz)

# --- BASE DE DATOS COMPARTIDA ---
@st.cache_resource
def inicializar_db_comun():
    return {
        "historial": [],
        "fertilizantes": [],
        "cosecha": [],
        "parcelas": {f"Parcela {i}": "Libre" for i in range(1, 11)},
        "cronometros": {
            "Riego": {"activo": False, "inicio": None},
            "Foliar": {"activo": False, "inicio": None},
            "Fertirriego": {"activo": False, "inicio": None}
        }
    }

db = inicializar_db_comun()

st.title("🚜 AgroTrack Pro - Honduras 🇭🇳")
st.write(f"⏰ **Hora Local:** {obtener_hora_hn().strftime('%H:%M:%S')}")

# --- PARCELAS ---
st.header("📍 Mapa de Bloques")
cols_p = st.columns(5) 
for i, (nombre, estado) in enumerate(db["parcelas"].items()):
    with cols_p[i % 5]:
        color = "🟢" if estado == "Libre" else "🔴"
        st.write(f"{color} **{nombre}**")
        if st.button(f"Cambiar {nombre}", key=f"btn_{nombre}"):
            db["parcelas"][nombre] = "EN LABOR" if estado == "Libre" else "Libre"
            st.rerun()

st.divider()

# --- LABORES ---
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

# --- FERTIRRIEGO ---
if db["cronometros"]["Fertirriego"]["activo"]:
    st.info("🧪 Registro de Insumos")
    with st.form("form_fert"):
        insumo = st.text_input("Producto")
        cant = st.number_input("Cantidad (kg/L)", min_value=0.0)
        if st.form_submit_button("Registrar"):
            db["fertilizantes"].append({"Hora": obtener_hora_hn().strftime("%H:%M"), "Producto": insumo, "Cantidad": cant})
            st.success("Guardado")

# --- COSECHA ---
st.divider()
st.header("🧺 Cosecha")
col_c1, col_c2 = st.columns(2)
with col_c1:
    cant_cestas = st.number_input("Cestas", min_value=0, step=1)
with col_c2:
    if st.button("📥 Guardar Cosecha", use_container_width=True):
        ahora = obtener_hora_hn()
        db["cosecha"].append({"Fecha": ahora.strftime("%Y-%m-%d"), "Semana": ahora.isocalendar()[1], "Cestas": cant_cestas})
        st.success("Registrado")

# --- REPORTES ---
st.divider()
st.header("📊 Reportes")
tab1, tab2, tab3 = st.tabs(["Cosecha", "Fertilizantes", "Tiempos"])

with tab1:
    if db["cosecha"]:
        df_c = pd.DataFrame(db["cosecha"])
        diario = df_c.groupby("Fecha")["Cestas"].sum().reset_index()
        st.dataframe(diario, use_container_width=True)
        csv = diario.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Excel", csv, "cosecha.csv")
    else:
        st.write("Sin datos")

with tab2:
    if db["fertilizantes"]:
        st.table(pd.DataFrame(db["fertilizantes"]))

with tab3:
    if db["historial"]:
        st.dataframe(pd.DataFrame(db["historial"]), use_container_width=True)





