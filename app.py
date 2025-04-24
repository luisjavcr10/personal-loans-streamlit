import streamlit as st
import numpy as np

# --- Lógica de evaluación principal ---
def evaluar_solicitud(datos):
    '''
    Evalúa la solicitud de préstamo basado en múltiples factores.
    Devuelve:
    - Decisión: Aprobado/Denegado
    - Monto aprobado (si aplica)
    - Tasa de interés (si aplica)
    - Motivo de denegación (si aplica)
    - Recomendaciones
    '''
    resultado = {
        'decision': None,
        'monto_aprobado': 0,
        'tasa_interes': None,
        'motivo_denegacion': None,
        'recomendaciones': []
    }
    
    # 1. Validación de edad
    if datos['edad'] < 18 or datos['edad'] > 77:
        resultado['decision'] = 'DENEGADO'
        resultado['motivo_denegacion'] = 'Edad fuera del rango permitido (18-77 años)'
        resultado['recomendaciones'].append('Solicitar cuando esté dentro del rango de edad permitido')
        return resultado
        
    # 2. Capacidad de pago
    cuota_estimada = (datos['monto_solicitado'] / max(datos['plazo_deseado'], 1))
    capacidad_pago = datos['ingreso_mensual'] - datos['gasto_mensual'] - cuota_estimada
    
    if capacidad_pago < datos['ingreso_mensual'] * 0.3:
        resultado['decision'] = 'DENEGADO'
        resultado['motivo_denegacion'] = 'Capacidad de pago insuficiente'
        resultado['recomendaciones'].append('Aumentar ingresos o reducir gastos mensuales')
        resultado['recomendaciones'].append(f'Reducir monto solicitado a máximo ${datos["ingreso_mensual"] * 3.5:,.2f}')
        return resultado
        
    # 3. Historial crediticio
    if datos['puntaje_credito'] < 630:
        resultado['decision'] = 'DENEGADO'
        resultado['motivo_denegacion'] = 'Puntaje crediticio muy bajo (<630)'
        resultado['recomendaciones'].append('Mejorar puntaje de crédito pagando deudas a tiempo')
        return resultado
        
    # 4. Garantías para montos altos
    if datos['monto_solicitado'] > 4.6 * datos['ingreso_mensual'] and datos['garantia'] == 'Ninguna':
        resultado['decision'] = 'DENEGADO'
        resultado['motivo_denegacion'] = 'Monto alto sin garantía suficiente'
        resultado['recomendaciones'].append('Ofrecer garantía (propiedad o vehículo)')
        resultado['recomendaciones'].append(f'Reducir monto solicitado a máximo ${datos["ingreso_mensual"] * 4.6:,.2f}')
        return resultado

    # --- Cálculo de aprobación ---
    
    # 1. Monto aprobado basado en ingresos
    monto_max = min(datos['monto_solicitado'], datos['ingreso_mensual'] * 12)
    
    # 2. Ajuste por puntaje crediticio
    if datos['puntaje_credito'] >= 750:
        monto_aprobado = monto_max * 1.0
    elif datos['puntaje_credito'] >= 650:
        monto_aprobado = monto_max * 0.8
    elif datos['puntaje_credito'] >= 550:
        monto_aprobado = monto_max * 0.6
    else:
        monto_aprobado = monto_max * 0.4
    
    # 3. Ajuste por garantía
    if datos['garantia'] == 'Propiedad':
        monto_aprobado *= 1.2
    elif datos['garantia'] == 'Vehículo':
        monto_aprobado *= 1.1
    
    monto_aprobado = min(monto_aprobado, datos['monto_solicitado'])
    
    # --- Cálculo de tasa de interés ---
    tasa_base = 18.0  # Tasa base
    
    # Ajustes por puntaje
    if datos['puntaje_credito'] >= 800:
        tasa_base -= 6.0
    elif datos['puntaje_credito'] >= 700:
        tasa_base -= 3.0
    elif datos['puntaje_credito'] < 600:
        tasa_base += 5.0
    
    # Ajustes por garantía
    if datos['garantia'] == 'Propiedad':
        tasa_base -= 2.5
    elif datos['garantia'] == 'Vehículo':
        tasa_base -= 1.5
    
    # Ajustes por tipo de empleo
    if datos['tipo_empleo'] == 'Independiente':
        tasa_base += 3.0
    elif datos['tipo_empleo'] == 'Pensionado':
        tasa_base -= 1.0
    
    # Asegurar tasa mínima
    tasa_final = max(tasa_base, 12.0)
    
    # --- Resultado final ---
    resultado['decision'] = 'APROBADO'
    resultado['monto_aprobado'] = round(monto_aprobado, 2)
    resultado['tasa_interes'] = round(tasa_final, 2)
    
    # --- Recomendaciones adicionales ---
    if datos['puntaje_credito'] < 700:
        resultado['recomendaciones'].append('Mejorar puntaje crediticio para obtener mejores tasas')
    
    if datos['gasto_mensual'] > datos['ingreso_mensual'] * 0.5:
        resultado['recomendaciones'].append('Reducir gastos fijos para mejorar capacidad de pago')
    
    if datos['morosidad']:
        resultado['recomendaciones'].append('Evitar morosidades para mejorar historial crediticio')
    
    if datos['antiguedad_laboral'] < 12:
        resultado['recomendaciones'].append('Consolidar antigüedad laboral (mínimo 12 meses recomendado)')
    
    return resultado

# --- Configuración de la interfaz ---
st.set_page_config(
    page_title="Sistema Experto para Préstamos",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main .block-container {
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .success-box {
        
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #2e7d32;
        margin-bottom: 1.5rem;
    }
    .warning-box {
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #ff8f00;
        margin-bottom: 1.5rem;
    }
    .error-box {
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #c62828;
        margin-bottom: 1.5rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .result-value {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1e88e5;
    }
</style>
""", unsafe_allow_html=True)

# --- Interfaz de usuario ---
st.title("🏦 Sistema Experto para Préstamos Personales")
st.markdown("""
Complete el formulario para evaluar su elegibilidad para un préstamo personal.
Los campos marcados con * son obligatorios.
""")

with st.form("form_prestamo"):
    st.header("📋 Información Personal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        edad = st.number_input("Edad*", min_value=18, max_value=77, value=30)
        estado_civil = st.selectbox("Estado civil*", ["Soltero", "Casado", "Divorciado", "Viudo", "Unión libre"])
        dependientes = st.number_input("Personas que dependen económicamente de usted*", min_value=0, max_value=10, value=0)
        
    with col2:
        tipo_empleo = st.selectbox("Tipo de empleo*", ["Dependiente", "Independiente", "Pensionado", "Desempleado"])
        antiguedad_laboral = st.number_input("Antigüedad en su empleo actual (meses)*", min_value=0, max_value=600, value=12)
        morosidad = st.checkbox("¿Ha tenido morosidad en pagos en el último año?")
    
    st.header("💵 Información Financiera")
    
    col3, col4 = st.columns(2)
    
    with col3:
        ingreso_mensual = st.number_input("Ingreso mensual neto ($)*", min_value=0, value=3000, step=100)
        gasto_mensual = st.number_input("Gastos mensuales fijos ($)*", min_value=0, value=1000, step=100)
        
    with col4:
        puntaje_credito = st.slider("Puntaje crediticio (300-850)*", 300, 850, 650)
        garantia = st.selectbox("Garantía que puede ofrecer", ["Ninguna", "Depósito de ahorros", "Vehículo", "Propiedad"])
    
    st.header("📝 Detalles del Préstamo")
    
    monto_solicitado = st.number_input("Monto que desea solicitar ($)*", min_value=100, value=5000, step=100)
    plazo_deseado = st.number_input("Plazo deseado para pagar (meses)*", min_value=6, max_value=120, value=36)
    
    submitted = st.form_submit_button("🔍 Evaluar Solicitud")

# --- Procesamiento de resultados ---
if submitted:
    # Validación de datos
    errores = []
    if edad < 18 or edad > 77:
        errores.append("La edad debe estar entre 18 y 77 años")
    if ingreso_mensual <= 0:
        errores.append("El ingreso mensual debe ser mayor a $0")
    if gasto_mensual < 0:
        errores.append("Los gastos no pueden ser negativos")
    if puntaje_credito < 300 or puntaje_credito > 850:
        errores.append("El puntaje crediticio debe estar entre 300 y 850")
    if monto_solicitado < 100:
        errores.append("El monto mínimo a solicitar es $100")
    if plazo_deseado < 6 or plazo_deseado > 120:
        errores.append("El plazo debe ser entre 6 y 120 meses")
    if antiguedad_laboral < 0 or antiguedad_laboral > 600:
        errores.append("La antigüedad laboral no puede ser negativa o mayor a 600 meses")
    if tipo_empleo == "Desempleado" and ingreso_mensual > 0:
        errores.append("Si está desempleado, el ingreso debe ser $0")
    
    if errores:
        st.error("**Corrija los siguientes errores:**\n\n" + "\n".join(f"- {e}" for e in errores))
    else:
        datos = {
            'edad': edad,
            'estado_civil': estado_civil,
            'dependientes': dependientes,
            'ingreso_mensual': ingreso_mensual,
            'gasto_mensual': gasto_mensual,
            'puntaje_credito': puntaje_credito,
            'morosidad': morosidad,
            'antiguedad_laboral': antiguedad_laboral,
            'tipo_empleo': tipo_empleo,
            'monto_solicitado': monto_solicitado,
            'plazo_deseado': plazo_deseado,
            'garantia': garantia
        }
        
        resultado = evaluar_solicitud(datos)
        
        st.subheader("📊 Resultado de la Evaluación")
        
        if resultado['decision'] == 'APROBADO':
            st.markdown(f"""
            <div class='success-box'>
                <h3 style='color:#2e7d32; margin-top:0;'>✅ PRÉSTAMO APROBADO</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
                    <div>
                        <p><b>Monto aprobado:</b></p>
                        <p class='result-value'>${resultado['monto_aprobado']:,.2f}</p>
                    </div>
                    <div>
                        <p><b>Tasa de interés anual:</b></p>
                        <p class='result-value'>{resultado['tasa_interes']}%</p>
                    </div>
                    <div>
                        <p><b>Plazo aprobado:</b></p>
                        <p class='result-value'>{plazo_deseado} meses</p>
                    </div>
                    <div>
                        <p><b>Cuota estimada:</b></p>
                        <p class='result-value'>${(resultado['monto_aprobado']/plazo_deseado):,.2f}/mes</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='error-box'>
                <h3 style='color:#c62828; margin-top:0;'>❌ PRÉSTAMO DENEGADO</h3>
                <p><b>Motivo:</b></p>
                <p style='color:#c62828; font-weight:bold;'>{resultado['motivo_denegacion']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar recomendaciones
        if resultado['recomendaciones']:
            st.markdown("""
            <div class='info-box'>
                <h4 style='margin-top:0;'>📌 Recomendaciones para mejorar su perfil crediticio:</h4>
                <ul>
            """ + "\n".join([f"<li>{rec}</li>" for rec in resultado['recomendaciones']]) + """
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Barra lateral informativa
st.sidebar.header("ℹ️ Acerca del Sistema")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.markdown("""
**Este sistema evalúa solicitudes de préstamos considerando:**

🔹 **Factores clave:**
- Historial crediticio (40%)
- Capacidad de pago (35%)
- Garantías (15%)
- Estabilidad laboral (10%)

🔹 **Resultados posibles:**
- ✅ Aprobado (con monto y tasa)
- ❌ Denegado (con motivo específico)

*Los resultados son estimados y sujetos a verificación documental.*
""")