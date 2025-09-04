import streamlit as st
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import time

# --- ESTILOS CSS PARA MÓVIL Y FORMATO ---
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
    .registro-exitoso {
        position: fixed;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: #e6ffe6;
        border: 2px solid green;
        padding: 1.5rem 2rem;
        font-size: 26px;
        color: green;
        font-weight: bold;
        border-radius: 10px;
        z-index: 9999;
        text-align: center;
    }
    .leyenda-tienda {
        position: absolute;
        top: 15px;
        right: 20px;
        font-size: 20px;
        font-weight: bold;
        color: #336699;
        background-color: #f0f8ff;
        padding: 8px 16px;
        border-radius: 8px;
        border: 1px solid #336699;
    }
    </style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1RSgRXDGd0ol_LsxFRbDfi6o4yd4uVGDzY4y45qwVQn0/edit")
sheet = spreadsheet.sheet1
back_in_stock_sheet = spreadsheet.worksheet("Back in stock - Tiendas fisicas")

# --- USUARIOS Y TIENDAS ---
USUARIOS_VALIDOS = {
    "phpolanco": {
        "password": "rrphpolx1",
        "tienda": "PH Polanco",
        "vendedoras": ["Martha Patricia Calderón Saucedo"]
    },
    "phperisur": {
        "password": "rrphperx1",
        "tienda": "PH Perisur",
        "vendedoras": ["María de Jesús Juarez Guzmán"]
    },
    "phdurango": {
        "password": "rrphdurx1",
        "tienda": "PH Durango",
        "vendedoras": ["Erika Sharon Bustamante Aguilar"]
    },
    "phsantafe": {
        "password": "rrphdurx1",
        "tienda": "PH Santa Fe",
        "vendedoras": ["Erika Sharon Bustamante Aguilar"]
    },
    "phmitikah": {
        "password": "rrphmitx1",
        "tienda": "PH Mitikah",
        "vendedoras": ["Maria Marina Ayuzo Fernández"]
    },
    "montelibano": {
        "password": "rrmontex1",
        "tienda": "Monte Líbano",
        "vendedoras": ["Patricia Cedillo", "Rebeca Tellez"]
    },
    "midtown": {
        "password": "rrmidx1",
        "tienda": "Midtown",
        "vendedoras": ["Ana Isabel Osuna", "Carmen Lizette Ramirez"]
    }
}

# --- AUTENTICACIÓN ---
st.title("Registro Diario de Clientas")

st.subheader("🔐 Inicia sesión")
usuario = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

if usuario in USUARIOS_VALIDOS and password == USUARIOS_VALIDOS[usuario]["password"]:
    tienda = USUARIOS_VALIDOS[usuario]["tienda"]
    vendedoras = USUARIOS_VALIDOS[usuario]["vendedoras"]

    st.markdown(f"<div class='leyenda-tienda'>📍 {tienda}</div>", unsafe_allow_html=True)
    st.success("✅ Autenticación exitosa")
    st.subheader(f"Formulario - {tienda}")

    st.markdown("""
    **Instrucciones:**
    1. Selecciona la fecha  
    2. Selecciona la hora  
    3. Selecciona la vendedora  
    4. Ingresa la cantidad de personas que visitaron la tienda en el día.  
    5. Ingresa la cantidad de personas que compraron  
    6. Ingresa el monto total vendido  
    7. Registra los modelos no disponibles
    """)

    fecha = st.date_input("Fecha", datetime.today())
    hora_raw = st.time_input("Hora")
    hora_formateada = hora_raw.strftime("%I:%M %p")

    vendedora = st.selectbox("Vendedora:", vendedoras)

    monto_venta_str = st.text_input("Cantidad monetaria vendida ($)", value="", placeholder="Ej: 1250.50")
    try:
        monto_venta = float(monto_venta_str.replace(",", "").replace("$", ""))
    except:
        monto_venta = 0.0

    monto_formateado = "${:,.2f}".format(monto_venta)
    st.markdown(f"<div style='font-size:18px; margin-top: -10px;'>💰 Monto capturado: <strong>{monto_formateado}</strong></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        personas_entraron = st.number_input("Personas que ingresaron", min_value=0, step=1)
        personas_compraron = st.number_input("Personas que compraron", min_value=0, step=1)
    with col2:
        conversion = (personas_compraron / personas_entraron * 100) if personas_entraron > 0 else 0
        st.markdown(f"<div style='margin-top:35px; font-size:20px; font-weight:bold;'>Conversión de venta:<br>{conversion:.2f}%</div>", unsafe_allow_html=True)

    comentarios = st.text_area("Comentarios u observaciones (opcional)")

    st.markdown("### Modelos Solicitados")
    st.markdown("**Instrucciones:** Ingresa los modelos, colores y tallas que no tuvimos disponibles a la venta durante el día.")

    modelos_data = []
    for i in range(10):
        cols = st.columns([3, 3, 2], gap="small")
        modelo = cols[0].text_input("", key=f"modelo_{i}", placeholder="Modelo")
        color = cols[1].text_input("", key=f"color_{i}", placeholder="Color")
        talla = cols[2].text_input("", key=f"talla_{i}", placeholder="Talla")
        if modelo or color or talla:
            modelos_data.append((modelo, color, talla))

    if st.button("Enviar registro"):
        if personas_compraron > personas_entraron:
            st.error("⚠️ El número de personas que compraron no puede ser mayor al número de personas que ingresaron.")
        elif monto_venta < 0:
            st.error("⚠️ Debes ingresar un monto mayor a cero en la cantidad monetaria vendida.")
        else:
            datos_generales = [
                fecha.strftime("%Y-%m-%d"),
                hora_formateada,
                tienda,
                vendedora,
                monto_venta,
                personas_entraron,
                personas_compraron,
                f"{conversion:.2f}%",
                comentarios
            ]
            sheet.append_row(datos_generales)

            for m in modelos_data:
                fila_back = [fecha.strftime("%Y-%m-%d"), hora_formateada, tienda, vendedora, m[0], m[1], m[2]]
                back_in_stock_sheet.append_row(fila_back)
                time.sleep(1)  # Para evitar error 429 por muchas escrituras

            st.markdown("""
            <div class='registro-exitoso'>✅ Registro exitoso</div>
            <script>
                setTimeout(function() {
                    window.location.reload();
                }, 3000);
            </script>
            """, unsafe_allow_html=True)

else:
    if usuario and password:
        st.error("❌ Usuario o contraseña incorrectos")
    st.stop()





