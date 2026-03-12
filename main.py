import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="AgroTrack Pro Honduras", layout="wide")

# --- CONFIGURACIÓN DE ZONA HORARIA (HONDURAS) ---
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
        "parcelas": {f"Parcela {i}": "Libre" for i in range(1, 7)},
        "cronometros": {
            "Riego": {"activo": False, "inicio": None},
            "Foliar": {"activo": False, "inicio": None},
            "Fertirriego": {"activo": False, "inicio": None}
        }
    }

db = inicializar_db_comun()

st.title("🚜 AgroTrack Pro - Honduras 🇭🇳")
st.write(f"⏰ Hora Local: {obtener_hora_hn().strftime('%H:%M:%S')}")

# --- SECCIÓN 1: CONTROL DE LABORES ---
st.header("⚡ Control de Labores")
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
            st.error(f"⏳ {nombre_tarea} EN CURSO")
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

# --- SECCIÓN 2: DETALLES DE FERTIRRIEGO (AÑADIDO) ---
if db["cronometros"]["Fertirriego"]["activo"]:
    st.info("🧪 Registro de Insumos para Fertirriego")
    with st.expander("Añadir Fertilizantes Aplicados", expanded=True):
        insumo = st.text_input("Nombre del Fertilizante (ej. Urea, Potasio)")
        cant = st.number_input("Cantidad (kg/L)", min_value=0.0)
        if st.button("Registrar Insumo"):
            db["fertilizantes"].append({
                "Fecha": obtener_hora_hn().strftime("%Y-%m-%d %H:%M"),
                "Producto": insumo,
                "Cantidad": cant
            })
            st.success("Insumo guardado")

# --- SECCIÓN 3: REGISTRO DE COSECHA (AÑADIDO) ---
st.divider()
st.header("🧺 Registro de Cosecha")
col_c1, col_c2 = st.columns(2)
with col_c1:
    cant_cestas = st.number_input("Número de cestas cosechadas", min_value=0, step=1)
with col_c2:
    if st.button("Guardar Cosecha del Día", use_container_width=True):
        ahora = obtener_hora_hn()
        db["cosecha"].append({
            "Fecha": ahora.strftime("%Y-%m-%d"),
            "Semana": ahora.isocalendar()[1],
            "Cestas": cant_cestas
        })
        st.success(f"Registradas {cant_cestas} cestas")

# --- SECCIÓN 4: REPORTES Y EXTRACCIÓN (AÑADIDO) ---
st.divider()
st.header("📊 Reportes de Producción")

if db["cosecha"]:
    df_cosecha = pd.DataFrame(db["cosecha"])
    
    # Reporte Diario
    st.subheader("📅 Reporte Diario")
    diario = df_cosecha.groupby("Fecha")["Cestas"].sum().reset_index()
    st.dataframe(diario, use_container_width=True)
    
    # Reporte Semanal
    st.subheader("📅 Reporte Semanal")
    semanal = df_cosecha.groupby("Semana")["Cestas"].sum().reset_index()
    st.dataframe(semanal, use_container_width=True)

    # Descarga de Archivos
    csv_diario = diario.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte Diario", csv_diario, "cosecha_diaria.csv", "text/csv")
else:
    st.write("No hay datos de cosecha aún.")

# Mostrar Fertilizantes aplicados por otros
if db["fertilizantes"]:
    with st.expander("Ver Historial de Fertilizantes Aplicados"):
        st.table(pd.DataFrame(db["fertilizantes"]))
    


