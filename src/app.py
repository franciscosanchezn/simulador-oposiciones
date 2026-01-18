"""
OpoSim - Simulador de Sorteos de Temas de Oposición

Aplicación Streamlit para calcular probabilidades y simular sorteos
de temas en oposiciones españolas.

Autor: OpoSim Team
"""

import random
import time
from datetime import datetime, timedelta
from math import comb
from typing import NamedTuple

import pandas as pd
import streamlit as st


# =============================================================================
# CONSTANTES
# =============================================================================
DEFAULT_TOTAL_TOPICS = 100
DEFAULT_BALLS_DRAWN = 5
DEFAULT_STUDIED_TOPICS = 25
TIMER_DEFAULT_MINUTES = 120  # 2 horas
TIMER_REFRESH_INTERVAL = 1  # segundos


# =============================================================================
# ESTILOS CSS PERSONALIZADOS
# =============================================================================
CUSTOM_CSS = """
<style>
    /* Fuente y colores generales - Tema gris moderno */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Variables de colores grises */
    :root {
        --gray-50: #fafafa;
        --gray-100: #f5f5f5;
        --gray-200: #e5e5e5;
        --gray-300: #d4d4d4;
        --gray-400: #a3a3a3;
        --gray-500: #737373;
        --gray-600: #525252;
        --gray-700: #404040;
        --gray-800: #262626;
        --gray-900: #171717;
    }
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: var(--gray-50);
    }
    
    /* Header principal - Gris claro */
    .main-header {
        background: linear-gradient(135deg, #f5f5f5 0%, #e5e5e5 100%);
        padding: 2rem;
        border-radius: 16px;
        color: #171717;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid #d4d4d4;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        color: #171717;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        color: #404040;
    }
    
    /* Tarjetas de temas - Clickeables */
    .topic-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #737373;
        transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        cursor: pointer;
    }
    
    .topic-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        background: #f5f5f5;
    }
    
    .topic-card:active {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .topic-card.selected {
        border-left-color: #171717;
        background: #e5e5e5;
        border-left-width: 6px;
    }
    
    .topic-card.studied {
        border-left-color: #404040;
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
    }
    
    .topic-card h4 {
        margin: 0 0 0.5rem 0;
        color: #1f2937;
        font-weight: 600;
    }
    
    .topic-card p {
        margin: 0;
        color: #374151;
        font-size: 0.95rem;
    }
    
    /* Panel de probabilidad */
    .probability-panel {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
    }
    
    .probability-value {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .probability-high { color: #404040; }
    .probability-medium { color: #525252; }
    .probability-low { color: #737373; }
    .probability-critical { color: #171717; }
    
    /* Timer - Fondo claro con texto oscuro */
    .timer-container {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        color: #262626;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: 2px solid #d4d4d4;
    }
    
    .timer-display {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 4rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        margin: 1rem 0;
        color: #171717;
    }
    
    .timer-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #404040;
    }
    
    .timer-warning { color: #d97706 !important; }
    .timer-danger { color: #dc2626 !important; animation: pulse 1s infinite; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Sidebar - Fondo claro con texto oscuro */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #171717 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #262626 !important;
        font-weight: 600;
        border-bottom: 2px solid #525252;
        padding-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] label {
        color: #374151 !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stNumberInput label {
        color: #374151 !important;
    }
    
    /* Métricas del sidebar */
    [data-testid="stMetric"] {
        background: white !important;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e5e5;
    }
    
    [data-testid="stMetric"] label {
        color: #404040 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #171717 !important;
    }
    
    /* Botones personalizados - Tema gris */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
        background-color: #525252 !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        background-color: #404040 !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #404040 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #262626 !important;
    }
    
    /* Sección de fórmula */
    .formula-box {
        background: #fafafa !important;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid #d4d4d4;
    }
    
    .formula-box h3 {
        color: #171717 !important;
        margin-bottom: 1rem;
    }
    
    .formula-box p, .formula-box strong {
        color: #171717 !important;
    }
    
    /* Estilos para LaTeX/KaTeX */
    .katex, .katex-display, .katex .base, .katex .mord, .katex .mbin, 
    .katex .mrel, .katex .mopen, .katex .mclose, .katex .mpunct, 
    .katex .minner, .katex-html {
        color: #171717 !important;
    }
    
    [data-testid="stLatex"] {
        background: #f5f5f5 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border: 1px solid #e5e5e5 !important;
    }
    
    [data-testid="stLatex"] * {
        color: #171717 !important;
    }
    
    /* Containers con borde */
    [data-testid="stContainer"], 
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #fafafa !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #fafafa !important;
        border-color: #d4d4d4 !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] * {
        color: #171717 !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stVerticalBlockBorderWrapper"] li,
    [data-testid="stVerticalBlockBorderWrapper"] strong,
    [data-testid="stVerticalBlockBorderWrapper"] em,
    [data-testid="stVerticalBlockBorderWrapper"] span {
        color: #171717 !important;
    }
    
    /* Asegurar que los list items y textos dentro de markdown sean visibles */
    .stMarkdown li, .stMarkdown em, .stMarkdown strong, .stMarkdown span {
        color: #171717 !important;
    }
    
    /* Footer - Gris claro */
    .footer {
        background: linear-gradient(135deg, #f5f5f5 0%, #e5e5e5 100%);
        color: #171717;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 2rem;
        border: 1px solid #d4d4d4;
    }
    
    .footer p {
        color: #171717 !important;
    }
    
    .footer a {
        color: #525252;
        text-decoration: none;
    }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #a3a3a3, transparent);
        margin: 2rem 0;
    }
    
    /* Sliders - Tema gris */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #737373, #525252) !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: #404040 !important;
    }
    
    /* File uploader - Drag and drop area */
    [data-testid="stFileUploader"] {
        background: #f5f5f5 !important;
        border: 2px dashed #9ca3af !important;
        border-radius: 12px;
        padding: 1rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        background: #e5e5e5 !important;
        border-color: #6b7280 !important;
    }
    
    [data-testid="stFileUploader"] * {
        color: #1a1a1a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    [data-testid="stFileUploader"] section {
        background: #ebebeb !important;
        border-radius: 8px;
    }
    
    [data-testid="stFileUploader"] button {
        background: #d4d4d4 !important;
        color: #1a1a1a !important;
        border: 1px solid #a3a3a3 !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background: #c4c4c4 !important;
    }
    
    [data-testid="stFileUploader"] small {
        color: #525252 !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: white !important;
        border-color: #a3a3a3 !important;
    }
    
    .stSelectbox label {
        color: #171717 !important;
    }
    
    /* Text Area - Corregir visibilidad */
    .stTextArea textarea {
        background-color: white !important;
        color: #171717 !important;
        border: 1px solid #a3a3a3 !important;
        border-radius: 8px !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #737373 !important;
    }
    
    .stTextArea label {
        color: #171717 !important;
    }
    
    [data-testid="stSidebar"] .stTextArea textarea {
        background-color: white !important;
        color: #171717 !important;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Headers en contenido principal */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #262626 !important;
    }
    
    /* Texto general - todos los elementos de texto */
    .stMarkdown p, .stMarkdown li, .stMarkdown em, .stMarkdown strong, 
    .stMarkdown span, .stMarkdown code, .stMarkdown ul, .stMarkdown ol {
        color: #171717 !important;
    }
</style>
"""


# =============================================================================
# MODELOS DE DATOS
# =============================================================================
class Topic(NamedTuple):
    """Representa un tema del temario."""
    numero: int
    nombre: str


# =============================================================================
# FUNCIONES DE CÁLCULO MATEMÁTICO
# =============================================================================
def calculate_probability(
    total_topics: int,
    studied_topics: int,
    balls_drawn: int
) -> float:
    """
    Calcula la probabilidad de que salga AL MENOS un tema estudiado en el sorteo.
    
    Utiliza la distribución hipergeométrica:
    
    P(X >= 1) = 1 - P(X = 0)
    
    Donde P(X = 0) representa la probabilidad de NO sacar ningún tema estudiado:
    P(X = 0) = C(N-k, n) / C(N, n)
    
    Siendo:
        N = total_topics (número total de temas en el temario)
        k = studied_topics (temas que el candidato ha estudiado)
        n = balls_drawn (bolas/temas extraídos en el sorteo)
        C(a, b) = combinaciones de 'a' elementos tomados de 'b' en 'b'
    
    Args:
        total_topics: N - Número total de temas en el temario
        studied_topics: k - Número de temas estudiados por el candidato
        balls_drawn: n - Número de bolas/temas que se extraen en el sorteo
        
    Returns:
        Probabilidad como float entre 0 y 1
        
    Raises:
        ValueError: Si los parámetros son inválidos
    """
    # Validación de parámetros
    if total_topics <= 0:
        raise ValueError("El número total de temas debe ser mayor que 0")
    if studied_topics < 0:
        raise ValueError("El número de temas estudiados no puede ser negativo")
    if balls_drawn <= 0:
        raise ValueError("El número de bolas del sorteo debe ser mayor que 0")
    if studied_topics > total_topics:
        raise ValueError("Los temas estudiados no pueden superar el total de temas")
    if balls_drawn > total_topics:
        raise ValueError("Las bolas del sorteo no pueden superar el total de temas")
    
    # Caso especial: si no se ha estudiado nada, probabilidad es 0
    if studied_topics == 0:
        return 0.0
    
    # Caso especial: si se han estudiado todos o las bolas >= temas no estudiados
    if studied_topics >= total_topics or balls_drawn > (total_topics - studied_topics):
        return 1.0
    
    # Cálculo usando distribución hipergeométrica
    # P(ninguno estudiado) = C(N-k, n) / C(N, n)
    # Usamos comb() de math para calcular combinaciones de forma eficiente
    not_studied = total_topics - studied_topics
    
    prob_none_studied = comb(not_studied, balls_drawn) / comb(total_topics, balls_drawn)
    
    # P(al menos uno) = 1 - P(ninguno)
    return 1.0 - prob_none_studied


# =============================================================================
# FUNCIONES DE GENERACIÓN DE DATOS
# =============================================================================
def generate_default_topics(count: int = DEFAULT_TOTAL_TOPICS) -> pd.DataFrame:
    """
    Genera un listado automático de temas por defecto.
    
    Args:
        count: Número de temas a generar
        
    Returns:
        DataFrame con columnas 'Número' y 'Nombre del Tema'
    """
    topics = [
        {"Número": i, "Nombre del Tema": f"Tema {i} - Contenido del tema número {i}"}
        for i in range(1, count + 1)
    ]
    return pd.DataFrame(topics)


def parse_excel_topics(uploaded_file) -> pd.DataFrame | None:
    """
    Parsea un archivo Excel subido y extrae los temas.
    
    Args:
        uploaded_file: Archivo Excel subido por el usuario
        
    Returns:
        DataFrame con los temas o None si hay error
    """
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        
        # Buscar columnas requeridas (case-insensitive)
        columns_lower = {col.lower(): col for col in df.columns}
        
        numero_col = None
        nombre_col = None
        
        for key, original in columns_lower.items():
            if "número" in key or "numero" in key:
                numero_col = original
            if "nombre" in key or "tema" in key:
                nombre_col = original
        
        if numero_col and nombre_col:
            result = df[[numero_col, nombre_col]].copy()
            result.columns = ["Número", "Nombre del Tema"]
            return result
        
        # Si no encuentra las columnas, intenta usar las dos primeras
        if len(df.columns) >= 2:
            result = df.iloc[:, :2].copy()
            result.columns = ["Número", "Nombre del Tema"]
            return result
            
        return None
        
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        return None


def parse_text_topics(text: str) -> pd.DataFrame | None:
    """
    Parsea un bloque de texto donde cada línea es un tema.
    
    Args:
        text: Texto con temas separados por líneas
        
    Returns:
        DataFrame con los temas o None si no hay temas válidos
    """
    if not text or not text.strip():
        return None
    
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    
    if not lines:
        return None
    
    topics = [
        {"Número": i, "Nombre del Tema": line}
        for i, line in enumerate(lines, start=1)
    ]
    
    return pd.DataFrame(topics)


# =============================================================================
# FUNCIONES DE SIMULACIÓN
# =============================================================================
def simulate_draw(topics_df: pd.DataFrame, balls_drawn: int) -> pd.DataFrame:
    """
    Simula un sorteo de temas aleatorio.
    
    Args:
        topics_df: DataFrame con todos los temas
        balls_drawn: Número de temas a extraer
        
    Returns:
        DataFrame con los temas seleccionados
    """
    if balls_drawn > len(topics_df):
        balls_drawn = len(topics_df)
    
    selected_indices = random.sample(range(len(topics_df)), balls_drawn)
    return topics_df.iloc[selected_indices].reset_index(drop=True)


# =============================================================================
# FUNCIONES DE UI - TEMPORIZADOR
# =============================================================================
def init_timer_state() -> None:
    """Inicializa el estado del temporizador si no existe."""
    if "timer_end" not in st.session_state:
        st.session_state.timer_end = None
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
    if "timer_paused" not in st.session_state:
        st.session_state.timer_paused = False
    if "timer_remaining" not in st.session_state:
        st.session_state.timer_remaining = None
    if "selected_topic" not in st.session_state:
        st.session_state.selected_topic = None


def start_timer(duration_minutes: int) -> None:
    """Inicia el temporizador con la duración especificada."""
    st.session_state.timer_end = datetime.now() + timedelta(minutes=duration_minutes)
    st.session_state.timer_running = True
    st.session_state.timer_paused = False
    st.session_state.timer_remaining = None


def pause_timer() -> None:
    """Pausa el temporizador guardando el tiempo restante."""
    if st.session_state.timer_running and not st.session_state.timer_paused:
        remaining = st.session_state.timer_end - datetime.now()
        st.session_state.timer_remaining = max(remaining, timedelta(0))
        st.session_state.timer_paused = True


def resume_timer() -> None:
    """Reanuda el temporizador desde donde se pausó."""
    if st.session_state.timer_paused and st.session_state.timer_remaining:
        st.session_state.timer_end = datetime.now() + st.session_state.timer_remaining
        st.session_state.timer_paused = False
        st.session_state.timer_remaining = None


def stop_timer() -> None:
    """Detiene y reinicia el temporizador."""
    st.session_state.timer_end = None
    st.session_state.timer_running = False
    st.session_state.timer_paused = False
    st.session_state.timer_remaining = None


def get_remaining_time() -> timedelta:
    """Obtiene el tiempo restante del temporizador."""
    if st.session_state.timer_paused and st.session_state.timer_remaining:
        return st.session_state.timer_remaining
    if st.session_state.timer_end is None:
        return timedelta(0)
    remaining = st.session_state.timer_end - datetime.now()
    return max(remaining, timedelta(0))


def format_time(td: timedelta) -> str:
    """Formatea un timedelta en formato HH:MM:SS."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# =============================================================================
# FUNCIONES DE UI - COMPONENTES
# =============================================================================
def display_probability_panel(probability: float) -> None:
    """
    Muestra el panel de probabilidad con feedback visual dinámico.
    
    Args:
        probability: Probabilidad calculada (0-1)
    """
    percentage = probability * 100
    
    # Determinar clase de color y mensaje
    if probability >= 0.75:
        color_class = "probability-high"
        emoji = "🎯"
        message = "¡Excelentes probabilidades! Tienes muy buenas opciones."
        alert_type = "success"
    elif probability >= 0.50:
        color_class = "probability-medium"
        emoji = "📈"
        message = "Probabilidades moderadas. Más de la mitad a tu favor."
        alert_type = "info"
    elif probability >= 0.25:
        color_class = "probability-low"
        emoji = "⚠️"
        message = "Probabilidades bajas. Conviene estudiar más temas."
        alert_type = "warning"
    else:
        color_class = "probability-critical"
        emoji = "🚨"
        message = "Riesgo muy alto. Amplía los temas estudiados."
        alert_type = "error"
    
    st.markdown(f"""
    <div class="probability-panel">
        <p style="margin: 0; font-size: 1rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em;">
            {emoji} Probabilidad de Éxito
        </p>
        <p class="probability-value {color_class}">{percentage:.1f}%</p>
        <p style="margin: 0; color: #475569; font-size: 1.1rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de progreso visual
    st.progress(probability)


def display_topic_card(topic: pd.Series, is_studied: bool = False, is_selected: bool = False) -> None:
    """
    Muestra una tarjeta visual para un tema.
    
    Args:
        topic: Serie con los datos del tema
        is_studied: Si el tema está marcado como estudiado
        is_selected: Si el tema está seleccionado para exponer
    """
    studied_class = "studied" if is_studied else ""
    selected_class = "selected" if is_selected else ""
    icon = "✅" if is_studied else ("🎯" if is_selected else "📄")
    badge = ""
    if is_selected:
        badge = '<span style="background: #404040; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 8px;">Seleccionado</span>'
    elif is_studied:
        badge = '<span style="background: #737373; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 8px;">Estudiado</span>'
    
    st.markdown(f"""
    <div class="topic-card {studied_class} {selected_class}">
        <h4>{icon} Tema {topic['Número']}{badge}</h4>
        <p>{topic['Nombre del Tema']}</p>
    </div>
    """, unsafe_allow_html=True)


def display_timer() -> None:
    """Muestra el componente del temporizador."""
    if not st.session_state.timer_running:
        return
    
    remaining = get_remaining_time()
    time_str = format_time(remaining)
    
    # Determinar clase de estilo según tiempo restante
    total_seconds = remaining.total_seconds()
    if total_seconds <= 0:
        timer_class = "timer-danger"
        status = "⏰ ¡TIEMPO AGOTADO!"
    elif total_seconds <= 300:  # 5 minutos
        timer_class = "timer-warning"
        status = "⚡ ¡ÚLTIMOS MINUTOS!"
    else:
        timer_class = ""
        status = "TIEMPO RESTANTE"
    
    st.markdown(f"""
    <div class="timer-container">
        <p class="timer-label">{status}</p>
        <p class="timer-display {timer_class}">{time_str}</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main() -> None:
    """Función principal de la aplicación OpoSim."""
    
    # Configuración de la página
    st.set_page_config(
        page_title="OpoSim - Simulador de Oposiciones",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inyectar estilos CSS personalizados
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Inicializar estados
    init_timer_state()
    
    if "drawn_topics" not in st.session_state:
        st.session_state.drawn_topics = None
    if "studied_list" not in st.session_state:
        st.session_state.studied_list = []
    
    # ==========================================================================
    # SIDEBAR - Configuración y Datos
    # ==========================================================================
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Cargar Temario
        st.subheader("📁 Cargar Temario")
        
        input_method = st.radio(
            "Método de entrada",
            options=["📝 Texto", "📊 Excel"],
            horizontal=True,
            help="Elige cómo quieres cargar tu temario"
        )
        
        topics_df = None
        
        if input_method == "📊 Excel":
            uploaded_file = st.file_uploader(
                "Sube tu archivo Excel (.xlsx)",
                type=["xlsx"],
                help="El archivo debe contener columnas 'Número' y 'Nombre del Tema'"
            )
            
            if uploaded_file is not None:
                topics_df = parse_excel_topics(uploaded_file)
                if topics_df is None:
                    st.warning("No se pudo parsear el archivo. Usando temas por defecto.")
                else:
                    st.success(f"✅ {len(topics_df)} temas cargados correctamente")
        
        else:  # Texto
            # Inicializar el estado del texto si no existe
            if "text_topics_input" not in st.session_state:
                st.session_state.text_topics_input = ""
            if "text_topics_loaded" not in st.session_state:
                st.session_state.text_topics_loaded = None
            
            text_input = st.text_area(
                "Pega tus temas (uno por línea)",
                height=200,
                placeholder="Tema 1: Introducción al derecho\nTema 2: La Constitución Española\nTema 3: Derechos fundamentales\n...",
                help="Escribe o pega los temas de tu temario, cada línea será un tema",
                key="text_topics_input"
            )
            
            if st.button("🔄 Cargar Temas", use_container_width=True):
                if text_input and text_input.strip():
                    parsed_topics = parse_text_topics(text_input)
                    if parsed_topics is not None:
                        st.session_state.text_topics_loaded = parsed_topics
                        st.success(f"✅ {len(parsed_topics)} temas cargados correctamente")
                    else:
                        st.warning("No se encontraron temas válidos en el texto.")
                else:
                    st.warning("Por favor, introduce al menos un tema.")
            
            # Usar los temas cargados si existen
            if st.session_state.text_topics_loaded is not None:
                topics_df = st.session_state.text_topics_loaded
        
        # Si no hay temas cargados, usar por defecto
        if topics_df is None:
            topics_df = generate_default_topics()
            st.info(f"ℹ️ Usando {len(topics_df)} temas por defecto")
        
        total_topics = len(topics_df)
        
        st.divider()
        
        # Parámetros del sorteo
        st.subheader("🎲 Parámetros del Sorteo")
        
        balls_drawn = st.slider(
            "Bolas del sorteo (n)",
            min_value=1,
            max_value=min(20, total_topics),
            value=min(DEFAULT_BALLS_DRAWN, total_topics),
            help="Cantidad de temas que se extraen en el sorteo"
        )
        
        studied_topics = st.slider(
            "Temas estudiados (k)",
            min_value=0,
            max_value=total_topics,
            value=min(DEFAULT_STUDIED_TOPICS, total_topics),
            help="Número de temas que has estudiado. Desliza para ajustar rápidamente."
        )
        
        st.divider()
        
        # Configuración del temporizador
        st.subheader("⏱️ Temporizador")
        timer_minutes = st.slider(
            "Duración del examen (minutos)",
            min_value=5,
            max_value=240,
            value=TIMER_DEFAULT_MINUTES,
            step=5,
            help="Tiempo disponible para el examen"
        )
        
        st.divider()
        
        # Estadísticas
        st.subheader("📈 Estadísticas")
        st.metric("Total de temas", total_topics)
        st.metric("Temas estudiados", studied_topics)
        st.metric("Bolas del sorteo", balls_drawn)
        st.metric("% del temario estudiado", f"{(studied_topics/total_topics)*100:.1f}%")
    
    # ==========================================================================
    # CONTENIDO PRINCIPAL
    # ==========================================================================
    
    # Header principal con diseño visual
    st.markdown("""
    <div class="main-header">
        <h1>📚 OpoSim</h1>
        <p>Simulador de Sorteos de Temas de Oposición</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Calcula tus probabilidades de éxito y practica con simulaciones de sorteo de temas.
    Configura los parámetros en la barra lateral y comienza a simular.
    """)
    
    st.divider()
    
    # ==========================================================================
    # PANEL DE PROBABILIDAD
    # ==========================================================================
    col1, col2 = st.columns([2, 1])
    
    with col1:
        try:
            probability = calculate_probability(total_topics, studied_topics, balls_drawn)
            display_probability_panel(probability)
        except ValueError as e:
            st.error(f"Error en el cálculo: {e}")
            probability = 0
    
    with col2:
        with st.container(border=True):
            st.markdown("### 📐 Fórmula Utilizada")
            st.latex(r"P(X \geq 1) = 1 - \frac{C(N-k, n)}{C(N, n)}")
            st.markdown(f"""
**Donde:**
- **N** = {total_topics} _(temas totales)_
- **k** = {studied_topics} _(temas estudiados)_
- **n** = {balls_drawn} _(bolas del sorteo)_
            """)
    
    st.divider()
    
    # ==========================================================================
    # SIMULACIÓN DE EXAMEN
    # ==========================================================================
    st.header("🎲 Simulación de Sorteo")
    
    # Botón de simulación
    col_sim1, col_sim2, col_sim3 = st.columns([1, 1, 2])
    
    with col_sim1:
        if st.button("🎯 Simular Sorteo", type="primary", use_container_width=True):
            st.session_state.drawn_topics = simulate_draw(topics_df, balls_drawn)
            st.session_state.selected_topic = None
            st.session_state.selected_topic_idx = None
            stop_timer()  # Reiniciar timer al hacer nuevo sorteo
    
    with col_sim2:
        if st.button("🗑️ Limpiar Resultados", use_container_width=True):
            st.session_state.drawn_topics = None
            st.session_state.selected_topic = None
            st.session_state.selected_topic_idx = None
            stop_timer()
    
    # Mostrar resultados del sorteo
    if st.session_state.drawn_topics is not None:
        st.markdown("### 📋 Temas Sorteados")
        st.markdown("*Haz clic en un tema para seleccionarlo*")
        
        drawn_df = st.session_state.drawn_topics
        
        # Inicializar selected_topic_idx si no existe
        if "selected_topic_idx" not in st.session_state:
            st.session_state.selected_topic_idx = None
        
        # Crear columnas para las tarjetas
        cols = st.columns(min(3, len(drawn_df)))
        
        for idx, (_, topic) in enumerate(drawn_df.iterrows()):
            with cols[idx % len(cols)]:
                # Verificar si el tema está en la lista de estudiados
                is_studied = topic["Número"] in st.session_state.studied_list
                is_selected = st.session_state.selected_topic_idx == idx
                
                # Mostrar la tarjeta visual
                display_topic_card(topic, is_studied, is_selected)
                
                # Botón para seleccionar el tema
                button_label = "✓ Seleccionado" if is_selected else "Elegir este tema"
                if st.button(
                    button_label,
                    key=f"select_topic_{idx}",
                    use_container_width=True,
                    disabled=is_selected
                ):
                    st.session_state.selected_topic_idx = idx
                    st.session_state.selected_topic = topic
                    stop_timer()  # Reiniciar timer al cambiar tema
                    st.rerun()
        
        st.divider()
        
        # Mostrar tema seleccionado y controles del temporizador
        if st.session_state.selected_topic_idx is not None:
            selected_topic = drawn_df.iloc[st.session_state.selected_topic_idx]
            st.session_state.selected_topic = selected_topic
            
            st.markdown(f"""
            ### 📝 Tema para Exponer
            **Tema {selected_topic['Número']}:** {selected_topic['Nombre del Tema']}
            """)
            
            # Controles del temporizador
            st.subheader("⏱️ Temporizador de Examen")
            
            timer_col1, timer_col2, timer_col3, timer_col4 = st.columns(4)
            
            with timer_col1:
                if not st.session_state.timer_running:
                    if st.button("▶️ Iniciar", use_container_width=True):
                        start_timer(timer_minutes)
                        st.rerun()
            
            with timer_col2:
                if st.session_state.timer_running and not st.session_state.timer_paused:
                    if st.button("⏸️ Pausar", use_container_width=True):
                        pause_timer()
                        st.rerun()
            
            with timer_col3:
                if st.session_state.timer_paused:
                    if st.button("▶️ Reanudar", use_container_width=True):
                        resume_timer()
                        st.rerun()
            
            with timer_col4:
                if st.session_state.timer_running:
                    if st.button("⏹️ Detener", use_container_width=True):
                        stop_timer()
                        st.rerun()
            
            # Mostrar el temporizador con auto-refresh usando fragment
            @st.fragment(run_every=1)
            def timer_fragment():
                """Fragment que se actualiza cada segundo para el temporizador."""
                display_timer()
            
            if st.session_state.timer_running and not st.session_state.timer_paused:
                timer_fragment()
            else:
                display_timer()
    
    else:
        st.info("👆 Haz clic en 'Simular Sorteo' para comenzar la simulación")
    
    # ==========================================================================
    # FOOTER
    # ==========================================================================
    st.divider()
    st.markdown("""
    <div class="footer">
        <p style="margin: 0;">📚 <strong>OpoSim</strong> - Simulador de Sorteos de Oposición</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.8;">Desarrollado con ❤️ usando Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    main()
