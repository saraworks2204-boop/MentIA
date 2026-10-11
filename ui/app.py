import streamlit as st
import os
import sys

# Agrega la raíz del proyecto al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.rag.pipeline import generar_keywords_pubmed, procesar_documentos_y_crear_vectorstore, generar_respuesta
from src.ingestion.pubmed_fetcher import obtener_articulos_pubmed

st.set_page_config(
    page_title="MentIA — Clinical Decision Support",
    page_icon="🧠",
    layout="wide"
)

# ==========================================
# INYECCIÓN DE ESTILOS CSS (UI/UX DASHBOARD CLÍNICO AVANZADO)
# ==========================================
st.markdown("""
<style>
    /* Estilos globales y paleta de fondo corporativa */
    .main {
        background-color: #070A12;
        color: #E2E8F0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Contenedor de tarjetas estilo dashboard clínico moderno */
    .clinical-card {
        background: linear-gradient(145deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid rgba(56, 189, 248, 0.15);
        padding: 28px;
        border-radius: 18px;
        box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
        height: 100%;
    }
    .clinical-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px -15px rgba(14, 165, 233, 0.25);
        border-color: rgba(56, 189, 248, 0.5);
    }

    /* Tipografía de títulos */
    h1, h2, h3 {
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.025em;
    }

    /* Estilización de alertas institucionales */
    .stAlert {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.2);
        color: #CBD5E1;
        border-radius: 14px;
        backdrop-filter: blur(8px);
    }

    /* Botones de acción principales */
    .stButton>button {
        background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0284C7 0%, #1D4ED8 100%);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.6);
        transform: translateY(-1px);
    }

    /* Estilización de la barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #0B0F19;
        border-right: 1px solid #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar el estado de la sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol" not in st.session_state:
    st.session_state.rol = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# BARRERA DE SEGURIDAD / PORTAL DE ACCESO
# ==========================================
if not st.session_state.autenticado:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>🧠 MentIA Clinical Suite</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 1.15rem; max-width: 700px; margin: 0 auto;'>Plataforma avanzada de soporte a la decisión clínica y educativa basada en evidencia científica indexada en PubMed.</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.warning("⚠️ **Aviso Ético y Académico:** MentIA es un prototipo de investigación para apoyo en salud mental basado en literatura biomédica. No sustituye el criterio médico profesional ni genera diagnósticos vinculantes.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### <center>Seleccione el perfil de acceso autorizado:</center>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div class="clinical-card">
            <h3 style='color: #38BDF8; margin-top: 0;'>🩺 Psiquiatra</h3>
            <p style='color: #94A3B8; font-size: 0.92rem; line-height: 1.5;'>Acceso a terminología médica avanzada, farmacología, farmacodinámica, clasificaciones DSM-5-TR / CIE-11 y ensayos clínicos.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acceder como Psiquiatra", key="btn_psi"):
            st.session_state.autenticado = True
            st.session_state.rol = "psiquiatra"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="clinical-card">
            <h3 style='color: #38BDF8; margin-top: 0;'>📚 Estudiante</h3>
            <p style='color: #94A3B8; font-size: 0.92rem; line-height: 1.5;'>Enfoque pedagógico y estructurado. Explicaciones guiadas de razonamiento clínico, fisiopatología y algoritmos terapéuticos.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acceder como Estudiante", key="btn_est"):
            st.session_state.autenticado = True
            st.session_state.rol = "estudiante"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="clinical-card">
            <h3 style='color: #38BDF8; margin-top: 0;'>👤 Paciente</h3>
            <p style='color: #94A3B8; font-size: 0.92rem; line-height: 1.5;'>Información educativa clara, accesible, empática y con estrictos protocolos de seguridad y contención clínica.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acceder como Paciente", key="btn_pac"):
            st.session_state.autenticado = True
            st.session_state.rol = "paciente"
            st.rerun()

    st.stop()

# ==========================================
# PLATAFORMA ACTIVA (SESIÓN AUTENTICADA)
# ==========================================
rol_actual = st.session_state.rol
nombres_roles = {
    "psiquiatra": "Perfil Profesional (Psiquiatría)",
    "estudiante": "Perfil Académico (Estudiante)",
    "paciente": "Perfil Educativo (Paciente / Usuario)"
}

st.sidebar.markdown("### 🧠 MentIA Dashboard")
st.sidebar.info(f"**Sesión Activa:**\n{nombres_roles.get(rol_actual, 'Desconocido')}")

st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión / Cambiar Rol"):
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.messages = []
    st.rerun()

st.title(f"🧠 MentIA — {nombres_roles.get(rol_actual)}")
st.markdown("Motor RAG conectado en tiempo real con PubMed para consulta especializada en patologías de salud mental.")

# Historial de conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escriba su consulta clínica o educativa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Procesando consulta en el pipeline RAG...", expanded=True) as status:
            st.write("🔍 Generando y optimizando palabras clave para PubMed...")
            keywords_ingles = generar_keywords_pubmed(prompt)
            st.write(f"Query PubMed: `{keywords_ingles}`")

            st.write("📚 Extrayendo literatura científica...")
            articulos = obtener_articulos_pubmed(keywords_ingles, max_results=10)

            if not articulos:
                status.update(label="La búsqueda no devolvió artículos.", state="error")
                respuesta = "No se encontró literatura clínica suficiente en PubMed para esta consulta o los términos no arrojaron resultados válidos."
                st.warning(respuesta)
            else:
                st.write(f"✅ {len(articulos)} artículos recuperados. Indexando en ChromaDB...")
                vectorstore = procesar_documentos_y_crear_vectorstore(articulos)

                st.write(f"🧠 Sintetizando respuesta adaptada ({rol_actual})...")
                respuesta = generar_respuesta(prompt, vectorstore, perfil=rol_actual)
                status.update(label="¡Respuesta generada con éxito!", state="complete")

        st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})