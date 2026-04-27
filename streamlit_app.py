import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import os

st.set_page_config(
    page_title="Registro de Horas - Centro Kinesiológico",
    page_icon="🩺",
    layout="wide"
)

ARCHIVO_DATOS = "registro_horas.csv"

st.title("🩺 Registro de Horas - Centro de Terapias Kinesiológicas")
st.write("Sistema para registrar atenciones, horas trabajadas y terapias realizadas.")

# Crear archivo si no existe
if not os.path.exists(ARCHIVO_DATOS):
    df_inicial = pd.DataFrame(columns=[
        "Fecha registro",
        "Nombre paciente",
        "RUT paciente",
        "Profesional",
        "Tipo de terapia",
        "Fecha atención",
        "Hora inicio",
        "Hora término",
        "Total horas",
        "Observaciones"
    ])
    df_inicial.to_csv(ARCHIVO_DATOS, index=False)

st.sidebar.title("Menú")
opcion = st.sidebar.radio(
    "Seleccione una opción",
    ["Registrar atención", "Ver registros", "Resumen de horas"]
)

if opcion == "Registrar atención":
    st.header("Registrar nueva atención")

    with st.form("formulario_registro"):
        col1, col2 = st.columns(2)

        with col1:
            nombre_paciente = st.text_input("Nombre del paciente")
            rut_paciente = st.text_input("RUT del paciente")
            profesional = st.text_input("Profesional / Kinesiólogo")

        with col2:
            tipo_terapia = st.selectbox(
                "Tipo de terapia",
                [
                    "Kinesiología motora",
                    "Kinesiología respiratoria",
                    "Rehabilitación",
                    "Masoterapia",
                    "Terapia deportiva",
                    "Otro"
                ]
            )
            fecha_atencion = st.date_input("Fecha de atención", value=date.today())
            hora_inicio = st.time_input("Hora de inicio", value=time(9, 0))
            hora_termino = st.time_input("Hora de término", value=time(10, 0))

        observaciones = st.text_area("Observaciones")

        enviar = st.form_submit_button("Guardar registro")

        if enviar:
            if not nombre_paciente or not rut_paciente or not profesional:
                st.error("Debe completar nombre del paciente, RUT y profesional.")
            else:
                inicio = datetime.combine(fecha_atencion, hora_inicio)
                termino = datetime.combine(fecha_atencion, hora_termino)

                if termino <= inicio:
                    st.error("La hora de término debe ser mayor que la hora de inicio.")
                else:
                    total_horas = round((termino - inicio).seconds / 3600, 2)

                    nuevo_registro = pd.DataFrame([{
                        "Fecha registro": datetime.now().strftime("%d-%m-%Y %H:%M"),
                        "Nombre paciente": nombre_paciente,
                        "RUT paciente": rut_paciente,
                        "Profesional": profesional,
                        "Tipo de terapia": tipo_terapia,
                        "Fecha atención": fecha_atencion.strftime("%d-%m-%Y"),
                        "Hora inicio": hora_inicio.strftime("%H:%M"),
                        "Hora término": hora_termino.strftime("%H:%M"),
                        "Total horas": total_horas,
                        "Observaciones": observaciones
                    }])

                    df = pd.read_csv(ARCHIVO_DATOS)
                    df = pd.concat([df, nuevo_registro], ignore_index=True)
                    df.to_csv(ARCHIVO_DATOS, index=False)

                    st.success("Registro guardado correctamente.")

elif opcion == "Ver registros":
    st.header("Registros guardados")

    df = pd.read_csv(ARCHIVO_DATOS)

    if df.empty:
        st.info("Aún no hay registros guardados.")
    else:
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar registros en CSV",
            data=csv,
            file_name="registro_horas_terapias.csv",
            mime="text/csv"
        )

elif opcion == "Resumen de horas":
    st.header("Resumen de horas")

    df = pd.read_csv(ARCHIVO_DATOS)

    if df.empty:
        st.info("Aún no hay datos para mostrar.")
    else:
        resumen = df.groupby("Profesional")["Total horas"].sum().reset_index()
        resumen = resumen.rename(columns={"Total horas": "Total horas trabajadas"})

        st.subheader("Horas por profesional")
        st.dataframe(resumen, use_container_width=True)

        st.bar_chart(resumen.set_index("Profesional"))
