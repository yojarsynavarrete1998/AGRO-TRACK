import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AgroTrack Compartido", layout="wide")

# --- LA CAJA COMÚN (Para que todos vean lo mismo) ---
@st.cache_resource
def obtener_base_datos_comun():
    # Esto solo se ejecuta una vez cuando la app nace en internet
    return {
        "historial": [],
        "parcelas": {f"Parcela {i}": "Libre" for i in range(1, 7)},
        "cronometros": {
            "Riego": {"activo": False, "inicio": None},
            "Foliar": {"activo": False, "inicio": None},
            "Fertirriego": {"activo": False, "inicio": None}
        }
    }

db = obtener_base_datos_comun()

st.title("🚜 AgroTrack: Panel Compartido")
st.info("💡 Lo que registres aquí será visible para todos los demás usuarios en tiempo real.")

# --- SECCIÓN 1: MAPA DE PARCELAS ---
st.subheader("📍 Estado Actual de los Bloques")
cols_p = st.columns(3)
for i, (nombre, estado) in enumerate(db["parcelas"].items()):
    with cols_p[i % 3]:
        color = "🟢" if estado == "Libre" else "🔴"
        st.write(f"{color} **{nombre}**")
        if st.button(f"Cambiar {nombre}", key=f"btn_{nombre}"):
            db["parcelas"][nombre] = "EN LABOR" if estado == "Libre" else "Libre"
            st.rerun()

st.divider()

# --- SECCIÓN 2: CONTROL DE LABORES ---
st.subheader("⚡ Labores en Ejecución")
c1, c2, c3 = st.columns(3)

def controlador_compartido(nombre_tarea, columna):
    with columna:
        estado = db["cronometros"][nombre_tarea]
        if not estado["activo"]:
            if st.button(f"▶️ Iniciar {nombre_tarea}", use_container_width=True):
                db["cronometros"][nombre_tarea]["activo"] = True
                db["cronometros"][nombre_tarea]["inicio"] = datetime.now()
                st.rerun()
        else:
            st.error(f"⏳ {nombre_tarea} ACTIVO")
            # Mostrar cuánto tiempo lleva (opcional)
            if st.button(f"⏹️ Finalizar {nombre_tarea}", type="primary", use_container_width=True):
                fin = datetime.now()
                duracion = str(fin - estado["inicio"]).split(".")[0]
                db["historial"].append({
                    "Labor": nombre_tarea,
                    "Inicio": estado["inicio"].strftime("%H:%M:%S"),
                    "Fin": fin.strftime("%H:%M:%S"),
                    "Duración": duracion
                })
                db["cronometros"][nombre_tarea]["activo"] = False
                st.rerun()

controlador_compartido("Riego", c1)
controlador_compartido("Foliar", c2)
controlador_compartido("Fertirriego", c3)

# --- SECCIÓN 3: HISTORIAL ---
st.divider()
if db["historial"]:
    st.subheader("📋 Resumen de hoy (Todos los usuarios)")
    st.table(pd.DataFrame(db["historial"]))
    

