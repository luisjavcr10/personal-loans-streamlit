import streamlit as st
import numpy as np

# Configuración de la página principal de la aplicación
st.set_page_config(page_title="Sistema Experto para Préstamos", layout="wide")

# Título de la aplicación
st.title("🏦 Sistema Experto para Evaluación de Préstamos Personales")
st.markdown("""
<style>
    .main .block-container {background-color: #f7f9fa; border-radius: 12px; padding: 24px;}
    .stButton>button {background-color: #4CAF50; color: white; font-weight: bold; border-radius: 8px;}
    .stSlider>div>div {color: #1976d2;}
</style>
""", unsafe_allow_html=True)

# Descripción general del sistema
st.write("""
Este sistema experto evalúa la elegibilidad para préstamos personales basado en:
- Historial crediticio
- Ingresos
- Deudas existentes
- Garantías
- Tiempo de empleo
""")

# Función principal para evaluar la solicitud de préstamo
# Recibe los parámetros del solicitante y retorna un puntaje de elegibilidad
# Cada factor suma una cantidad específica de puntos según reglas de negocio

def evaluar_prestamo(puntaje_credito, ingresos_mensuales, deudas, garantia, tiempo_empleo):
    puntaje = 0

    # Evaluación del puntaje crediticio
    if puntaje_credito > 750:
        puntaje += 40
    elif puntaje_credito > 650:
        puntaje += 30
    elif puntaje_credito > 550:
        puntaje += 20
    else:
        puntaje += 10

    # Evaluación de ingresos mensuales
    if ingresos_mensuales > 5000:
        puntaje += 20
    elif ingresos_mensuales > 3000:
        puntaje += 15
    elif ingresos_mensuales > 1500:
        puntaje += 10
    else:
        puntaje += 5

    # Evaluación del ratio de deudas respecto a ingresos
    ratio_deuda = deudas / ingresos_mensuales if ingresos_mensuales > 0 else 1
    if ratio_deuda < 0.3:
        puntaje += 20
    elif ratio_deuda < 0.5:
        puntaje += 15
    elif ratio_deuda < 0.7:
        puntaje += 10
    else:
        puntaje += 5

    # Evaluación del tipo de garantía ofrecida
    if garantia == "Propiedad":
        puntaje += 15
    elif garantia == "Vehículo":
        puntaje += 10
    elif garantia == "Depósito":
        puntaje += 5
    else:
        puntaje += 0

    # Evaluación del tiempo en el empleo actual
    if tiempo_empleo > 5:
        puntaje += 15
    elif tiempo_empleo > 3:
        puntaje += 10
    elif tiempo_empleo > 1:
        puntaje += 5
    else:
        puntaje += 0

    return puntaje

# Interfaz de usuario con Streamlit para ingresar los datos del solicitante
with st.form("form_prestamo"):
    st.header("Información del Solicitante")
    st.markdown("Por favor, completa los siguientes campos para evaluar tu solicitud de préstamo. Los campos marcados con * son obligatorios.")

    col1, col2 = st.columns(2)

    with col1:
        # Entrada del puntaje crediticio
        puntaje_credito = st.slider("Puntaje crediticio (300-850)*", 300, 850, 650, help="Un puntaje más alto mejora tus posibilidades de aprobación.")
        # Entrada de ingresos mensuales
        ingresos_mensuales = st.number_input("Ingresos mensuales netos ($)*", min_value=0, value=3000, help="Incluye tu ingreso neto mensual.")
        # Entrada de deudas mensuales
        deudas = st.number_input("Deudas mensuales ($)*", min_value=0, value=1000, help="Suma total de tus pagos mensuales de deuda.")

    with col2:
        # Selección del tipo de garantía ofrecida
        garantia = st.selectbox("Garantía ofrecida",
                                ["Ninguna", "Depósito", "Vehículo", "Propiedad"], help="Selecciona si puedes ofrecer algún tipo de garantía.")
        # Entrada del tiempo en el empleo actual
        tiempo_empleo = st.number_input("Tiempo en empleo actual (años)*", min_value=0, max_value=50, value=3, help="Años en tu empleo actual.")
        # Entrada del monto solicitado
        monto_prestamo = st.number_input("Monto solicitado ($)*", min_value=100, value=5000, help="Cantidad que deseas solicitar.")

    # Botón para enviar el formulario y evaluar la solicitud
    submitted = st.form_submit_button("Evaluar Solicitud")

    if submitted:
        errores = []
        if ingresos_mensuales <= 0:
            errores.append("Los ingresos mensuales deben ser mayores que cero.")
        if deudas < 0:
            errores.append("Las deudas mensuales no pueden ser negativas.")
        if deudas > ingresos_mensuales:
            errores.append("Las deudas mensuales no pueden superar los ingresos mensuales.")
        if puntaje_credito < 300 or puntaje_credito > 850:
            errores.append("El puntaje crediticio debe estar entre 300 y 850.")
        if tiempo_empleo < 0 or tiempo_empleo > 50:
            errores.append("El tiempo en empleo debe estar entre 0 y 50 años.")
        if monto_prestamo < 100:
            errores.append("El monto solicitado debe ser al menos $100.")

        if errores:
            st.error("\n".join(errores))
        else:
            # Llamada a la función de evaluación
            puntaje = evaluar_prestamo(puntaje_credito, ingresos_mensuales, deudas, garantia, tiempo_empleo)

            st.subheader("Resultado de la Evaluación")

            # Determinación del resultado según el puntaje obtenido
            if puntaje >= 80:
                st.success("✅ Préstamo APROBADO")
                # Cálculo de tasa de interés aleatoria dentro de un rango
                tasa_interes = 8.5 + np.random.uniform(0, 3)
                # Cálculo del plazo máximo aprobado
                plazo_max = min(60, int(monto_prestamo / (ingresos_mensuales * 0.4)))
                st.write(f"Tasa de interés ofrecida: {tasa_interes:.2f}%")
                st.write(f"Plazo máximo aprobado: {plazo_max} meses")
            elif puntaje >= 60:
                st.warning("⚠️ Préstamo CONDICIONAL")
                st.write("Se requiere revisión adicional o garantía adicional")
                st.write("Un asesor se comunicará contigo")
            else:
                st.error("❌ Préstamo RECHAZADO")
                st.write("No cumples con los requisitos mínimos")

            # Mostrar el puntaje obtenido
            st.write(f"Puntaje de evaluación: <span style='color:#1976d2;font-size:22px'><b>{puntaje}/100</b></span>", unsafe_allow_html=True)

            # Recomendaciones para mejorar la elegibilidad si el puntaje es bajo
            if puntaje < 60:
                st.info("""
                <span style='color:#e65100'><b>Recomendaciones para mejorar tu elegibilidad:</b></span>
                <ul>
                <li>Mejora tu puntaje crediticio pagando deudas a tiempo</li>
                <li>Reduce tu ratio de deuda/ingresos</li>
                <li>Considera ofrecer una garantía</li>
                <li>Mantén tu empleo actual por más tiempo</li>
                </ul>
                """, unsafe_allow_html=True)

# Sección lateral con explicación del sistema experto
st.sidebar.header("Acerca del Sistema Experto")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
st.sidebar.write("""
Este sistema utiliza reglas basadas en conocimiento de expertos en crédito para evaluar solicitudes de préstamos.

**Factores considerados:**
- Puntaje crediticio (40%)
- Ingresos vs deudas (40%)
- Garantías (10%)
- Estabilidad laboral (10%)
""")
