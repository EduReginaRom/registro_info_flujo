import streamlit as st
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import time

# ESTILOS CSS PARA MÓVIL Y PARA CAMPOS EN MISMA FILA
st.markdown("""
    <style>
    .block-container {
        padding: 1rem;
    }
    input, textarea, select {
        font-size: 16px !important;
    }
    .stTextInput > div > input,
    .stSelectbox > div > div {
        width: 100% !important;
    }
    @media (max-width: 600px) {
        .stColumn {
            display: block;
            width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# CONFIGURACIÓN GOOGLE SHEETS DESDE SECRETO
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1RSgRXDGd0ol_LsxFRbDfi6o4yd4uVGDzY4y45qwVQn0/edit")
sheet = spreadsheet.sheet1
back_in_stock_sheet = spreadsheet.worksheet("Back in stock - Tiendas fisicas")

# MENÚ PRINCIPAL
st.title("Registro Diario Clientas")
opcion_tienda = st.selectbox("Selecciona tienda:", ["Seleccionar", "Monte Líbano", "Midtown"])

if opcion_tienda != "Seleccionar":
    st.subheader(f"Formulario - {opcion_tienda}")

    st.markdown("""
    **Instrucciones:**
    1. Selecciona la fecha  
    2. Selecciona la hora  
    3. Selecciona la vendedora  
    4. Ingresa la cantidad de personas que visitaron la tienda en el día.  
    5. Ingresa la cantidad de personas que compraron  
    6. Comentarios acerca de incidencias
    """)

    fecha = st.date_input("Fecha", datetime.today())
    hora = st.time_input("Hora")

    if opcion_tienda == "Monte Líbano":
        vendedora = st.selectbox("Vendedora:", ["Patricia Cedillo", "Rebeca Tellez"])
    elif opcion_tienda == "Midtown":
        vendedora = st.selectbox("Vendedora:", ["Ana Isabel Osuna"])

    col1, col2 = st.columns([2, 1])
    with col1:
        personas_entraron = st.number_input("Personas que ingresaron", min_value=0, step=1)
        personas_compraron = st.number_input("Personas que compraron", min_value=0, step=1)
    with col2:
        conversion = (personas_compraron / personas_entraron * 100) if personas_entraron > 0 else 0
        st.markdown(f"<div style='margin-top:35px; font-size:20px; font-weight:bold;'>Conversión de venta:<br>{conversion:.2f}%</div>", unsafe_allow_html=True)

    comentarios = st.text_area("Comentarios u observaciones (opcional)")

    st.markdown("### Modelos Solicitados")

    st.markdown("""
    **Instrucciones:**  
    1. Ingresa los modelos, colores y tallas que no tuvimos disponibles a la venta durante el día.
    """)

    modelos_data = []
    for i in range(10):
        cols = st.columns([3, 3, 2], gap="small")
        modelo = cols[0].text_input("", key=f"modelo_{i}", placeholder="Modelo")
        color = cols[1].text_input("", key=f"color_{i}", placeholder="Color")
        talla = cols[2].text_input("", key=f"talla_{i}", placeholder="Talla")
        if modelo or color or talla:
            modelos_data.append((modelo, color, talla))

    if st.button("Enviar registro"):
        # Guardar datos generales en hoja principal
        datos_generales = [fecha.strftime("%Y-%m-%d"), hora.strftime("%H:%M"), opcion_tienda, vendedora,
                          personas_entraron, personas_compraron, f"{conversion:.2f}%", comentarios]
        sheet.append_row(datos_generales)

        # Guardar modelos back in stock en hoja separada
        for m in modelos_data:
            fila_back = [fecha.strftime("%Y-%m-%d"), hora.strftime("%H:%M"), opcion_tienda, vendedora, m[0], m[1], m[2]]
            back_in_stock_sheet.append_row(fila_back)
            time.sleep(1)  # Evita error 429 por exceso de escritura simultánea

        st.success("Registro exitoso.")
