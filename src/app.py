"""
OpoSim - Simulador de Sorteos de Temas de Oposición

Aplicación Streamlit para calcular probabilidades y simular sorteos
de temas en oposiciones españolas.

Autor: OpoSim Team
"""

import random
import time
import hashlib
from datetime import datetime, timedelta
from math import comb
from typing import NamedTuple

import pandas as pd
import streamlit as st
from supabase import create_client, Client


# =============================================================================
# CONSTANTES
# =============================================================================
DEFAULT_TOTAL_TOPICS = 100
DEFAULT_BALLS_DRAWN = 5
DEFAULT_STUDIED_TOPICS = 25
TIMER_DEFAULT_MINUTES = 120  # 2 horas
TIMER_REFRESH_INTERVAL = 1  # segundos

# Colores para estados de temas
STATE_COLORS = {
    "sin_evaluar": "#e5e7eb",  # Gris claro
    "rojo": "#ef4444",          # Estado 1-3
    "naranja": "#f97316",       # Estado 4-5
    "amarillo": "#eab308",      # Estado 6-7
    "verde": "#22c55e",         # Estado 8-10
    "azul": "#3b82f6",          # Planeado
    "descartado": "#9ca3af",    # Gris
}


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
    
    /* Pestañas / Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f5f5f5;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #e5e5e5;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        color: #525252;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e5e5e5;
        color: #171717;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #171717 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
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
    
    /* Mapa de temas - Grid responsive */
    .topic-map {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
        gap: 8px;
        padding: 1rem;
        max-width: 100%;
    }
    
    .topic-cell {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        border: 2px solid transparent;
        color: #1f2937;
    }
    
    .topic-cell:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 10;
    }
    
    .topic-cell.descartado {
        text-decoration: line-through;
        opacity: 0.6;
    }
    
    .topic-cell.selected {
        border-color: #1f2937;
        box-shadow: 0 0 0 3px rgba(31, 41, 55, 0.3);
    }
    
    /* Panel de estadísticas */
    .stats-panel {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
    }
    
    .stat-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
    }
    
    .stat-card .label {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }
    
    /* Leyenda de colores */
    .color-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        padding: 1rem;
        background: #f9fafb;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
    }
    
    .legend-color {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        border: 1px solid rgba(0,0,0,0.1);
    }
    
    /* Panel de edición de tema */
    .edit-panel {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin-top: 1rem;
    }
    
    .edit-panel h3 {
        margin: 0 0 1rem 0;
        color: #1f2937;
    }
    
    /* Estilos para inputs en el editor de temas */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #171717 !important;
        border: 1px solid #d4d4d4 !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #525252 !important;
        box-shadow: 0 0 0 2px rgba(82, 82, 82, 0.2) !important;
    }
    
    .stTextInput label {
        color: #171717 !important;
        font-weight: 500 !important;
    }
    
    /* Sliders en el editor */
    .stSlider > div > div > div > div {
        background-color: #525252 !important;
    }
    
    .stSlider label {
        color: #171717 !important;
        font-weight: 500 !important;
    }
    
    .stSlider [data-baseweb="slider"] div {
        color: #171717 !important;
    }
    
    /* Min/Max labels del slider - VISIBLES */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: #171717 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: relative !important;
        padding-top: 4px !important;
    }
    
    /* Contenedor de tick bar */
    .stSlider [class*="TickBar"] {
        display: flex !important;
        justify-content: space-between !important;
        visibility: visible !important;
        opacity: 1 !important;
        margin-top: 4px !important;
    }
    
    .stSlider p {
        color: #171717 !important;
    }
    
    /* Number input */
    .stNumberInput > div > div > input {
        background-color: white !important;
        color: #171717 !important;
        border: 1px solid #d4d4d4 !important;
        border-radius: 8px !important;
    }
    
    .stNumberInput label {
        color: #171717 !important;
        font-weight: 500 !important;
    }
    
    /* Checkboxes */
    .stCheckbox label {
        color: #171717 !important;
        font-weight: 500 !important;
    }
    
    .stCheckbox label span {
        color: #171717 !important;
    }
    
    /* Container con borde (usado en el editor) */
    [data-testid="stVerticalBlock"] > div:has(> div > .stTextInput),
    [data-testid="stVerticalBlock"] > div:has(> div > .stSlider) {
        background: #fafafa;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    
    /* Login form */
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Formularios de login/registro */
    .stForm {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e5e5;
    }
    
    /* Botones del mapa de temas con colores dinámicos */
    .topic-btn-green button {
        background-color: #22c55e !important;
        border-color: #22c55e !important;
        color: white !important;
    }
    
    .topic-btn-yellow button {
        background-color: #eab308 !important;
        border-color: #eab308 !important;
        color: #171717 !important;
    }
    
    .topic-btn-orange button {
        background-color: #f97316 !important;
        border-color: #f97316 !important;
        color: white !important;
    }
    
    .topic-btn-red button {
        background-color: #ef4444 !important;
        border-color: #ef4444 !important;
        color: white !important;
    }
    
    .topic-btn-blue button {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
        color: white !important;
    }
    
    .topic-btn-gray button {
        background-color: #9ca3af !important;
        border-color: #9ca3af !important;
        color: white !important;
        text-decoration: line-through !important;
    }
    
    .topic-btn-neutral button {
        background-color: #e5e7eb !important;
        border-color: #d4d4d4 !important;
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
# FUNCIONES DE SUPABASE Y AUTENTICACIÓN
# =============================================================================
@st.cache_resource
def get_supabase_client() -> Client | None:
    """Obtiene el cliente de Supabase."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error conectando con Supabase: {e}")
        return None


def hash_pin(pin: str) -> str:
    """Hashea el PIN del usuario."""
    return hashlib.sha256(pin.encode()).hexdigest()


def register_user(user_code: str, pin: str) -> bool:
    """Registra un nuevo usuario."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        pin_hash = hash_pin(pin)
        supabase.table("users").insert({
            "user_code": user_code.lower().strip(),
            "pin_hash": pin_hash
        }).execute()
        return True
    except Exception as e:
        if "duplicate" in str(e).lower():
            st.error("Este código de usuario ya existe. Elige otro.")
        else:
            st.error(f"Error al registrar: {e}")
        return False


def verify_user(user_code: str, pin: str) -> bool:
    """Verifica las credenciales del usuario."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        pin_hash = hash_pin(pin)
        result = supabase.table("users").select("*").eq(
            "user_code", user_code.lower().strip()
        ).eq("pin_hash", pin_hash).execute()
        return len(result.data) > 0
    except Exception:
        return False


def user_exists(user_code: str) -> bool:
    """Verifica si un usuario existe."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        result = supabase.table("users").select("user_code").eq(
            "user_code", user_code.lower().strip()
        ).execute()
        return len(result.data) > 0
    except Exception:
        return False


def get_user_progress(user_code: str) -> dict:
    """Obtiene el progreso de todos los temas del usuario."""
    supabase = get_supabase_client()
    if not supabase:
        return {}
    
    try:
        result = supabase.table("topic_progress").select("*").eq(
            "user_code", user_code.lower().strip()
        ).execute()
        
        # Convertir a diccionario indexado por tema_numero
        progress = {}
        for row in result.data:
            progress[row["tema_numero"]] = {
                "nombre_tema": row.get("nombre_tema", ""),
                "estado": row.get("estado", 0),
                "repasos": row.get("repasos", 0),
                "descartado": row.get("descartado", False),
                "planeado": row.get("planeado", False),
            }
        return progress
    except Exception as e:
        st.error(f"Error al cargar progreso: {e}")
        return {}


def save_topic_progress(user_code: str, tema_numero: int, data: dict) -> bool:
    """Guarda o actualiza el progreso de un tema."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        record = {
            "user_code": user_code.lower().strip(),
            "tema_numero": tema_numero,
            "nombre_tema": data.get("nombre_tema", ""),
            "estado": data.get("estado", 0),
            "repasos": data.get("repasos", 0),
            "descartado": data.get("descartado", False),
            "planeado": data.get("planeado", False),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Upsert: insertar o actualizar si existe
        supabase.table("topic_progress").upsert(
            record, 
            on_conflict="user_code,tema_numero"
        ).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False


def save_user_temario(user_code: str, temario_csv: str) -> bool:
    """Guarda el temario del usuario en Supabase."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Actualizar el campo temario_csv en la tabla users
        result = supabase.table("users").update({
            "temario_csv": temario_csv,
            "updated_at": datetime.now().isoformat(),
        }).eq("user_code", user_code.lower().strip()).execute()
        
        # Verificar si se actualizó algún registro
        if result.data and len(result.data) > 0:
            return True
        else:
            st.warning(f"No se encontró el usuario {user_code} para actualizar el temario")
            return False
    except Exception as e:
        st.error(f"Error al guardar temario: {e}")
        return False


def get_user_temario(user_code: str) -> str | None:
    """Obtiene el temario guardado del usuario."""
    supabase = get_supabase_client()
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").select("temario_csv").eq(
            "user_code", user_code.lower().strip()
        ).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0].get("temario_csv")
        return None
    except Exception:
        return None


def get_topic_color(estado: int, descartado: bool, planeado: bool) -> str:
    """Determina el color de un tema basado en su estado."""
    if descartado:
        return STATE_COLORS["descartado"]
    if planeado:
        return STATE_COLORS["azul"]
    if estado == 0:
        return STATE_COLORS["sin_evaluar"]
    if estado <= 3:
        return STATE_COLORS["rojo"]
    if estado <= 5:
        return STATE_COLORS["naranja"]
    if estado <= 7:
        return STATE_COLORS["amarillo"]
    return STATE_COLORS["verde"]


def get_topic_css_class(estado: int, descartado: bool, planeado: bool) -> str:
    """Determina la clase CSS para el botón de un tema."""
    if descartado:
        return "topic-btn-gray"
    if planeado:
        return "topic-btn-blue"
    if estado == 0:
        return "topic-btn-neutral"
    if estado <= 3:
        return "topic-btn-red"
    if estado <= 5:
        return "topic-btn-orange"
    if estado <= 7:
        return "topic-btn-yellow"
    return "topic-btn-green"


def calculate_stats(progress: dict) -> dict:
    """Calcula estadísticas del progreso."""
    if not progress:
        return {
            "total": 0,
            "evaluados": 0,
            "buenos": 0,
            "planeados": 0,
            "descartados": 0,
            "promedio": 0,
            "total_repasos": 0,
        }
    
    evaluados = [p for p in progress.values() if p["estado"] > 0]
    buenos = [p for p in progress.values() if p["estado"] >= 8 and not p["descartado"]]
    planeados = [p for p in progress.values() if p["planeado"] and not p["descartado"]]
    descartados = [p for p in progress.values() if p["descartado"]]
    total_repasos = sum(p["repasos"] for p in progress.values())
    
    promedio = 0
    if evaluados:
        promedio = sum(p["estado"] for p in evaluados) / len(evaluados)
    
    return {
        "total": len(progress),
        "evaluados": len(evaluados),
        "buenos": len(buenos),
        "planeados": len(planeados),
        "descartados": len(descartados),
        "promedio": promedio,
        "total_repasos": total_repasos,
    }


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
# FUNCIONES DE UI - PROGRESO DE TEMAS
# =============================================================================
def display_login_form() -> bool:
    """Muestra el formulario de login/registro. Retorna True si está logueado."""
    
    # Ya verificamos cookies en main(), solo checar session_state
    if "logged_user" in st.session_state and st.session_state.logged_user:
        return True
    
    st.markdown("### 🔐 Accede a tu progreso")
    st.markdown("Inicia sesión o regístrate para guardar tu progreso de estudio.")
    
    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
    with tab_login:
        with st.form("login_form"):
            user_code = st.text_input(
                "Código de usuario",
                placeholder="ej: juan123",
                help="El código que elegiste al registrarte",
                key="login_user_code"
            )
            pin = st.text_input(
                "PIN",
                type="password",
                placeholder="Tu PIN secreto",
                key="login_pin"
            )
            
            if st.form_submit_button("Entrar", use_container_width=True):
                if user_code and pin:
                    if verify_user(user_code, pin):
                        st.session_state.logged_user = user_code.lower().strip()
                        st.success("✅ ¡Bienvenido de nuevo!")
                        st.rerun()
                    else:
                        st.error("❌ Código o PIN incorrectos")
                else:
                    st.warning("Completa todos los campos")
    
    with tab_register:
        with st.form("register_form"):
            new_user_code = st.text_input(
                "Elige un código de usuario",
                placeholder="ej: maria_opo",
                help="Solo letras, números y guiones. Mínimo 3 caracteres.",
                key="register_user_code"
            )
            new_pin = st.text_input(
                "Elige un PIN",
                type="password",
                placeholder="Un PIN que recuerdes",
                help="Mínimo 4 caracteres",
                key="register_pin"
            )
            confirm_pin = st.text_input(
                "Confirma el PIN",
                type="password",
                placeholder="Repite el PIN",
                key="register_confirm_pin"
            )
            
            if st.form_submit_button("Registrarse", use_container_width=True):
                if not new_user_code or len(new_user_code) < 3:
                    st.error("El código debe tener al menos 3 caracteres")
                elif not new_pin or len(new_pin) < 4:
                    st.error("El PIN debe tener al menos 4 caracteres")
                elif new_pin != confirm_pin:
                    st.error("Los PINs no coinciden")
                elif user_exists(new_user_code):
                    st.error("Este código ya está en uso. Elige otro.")
                elif register_user(new_user_code, new_pin):
                    st.session_state.logged_user = new_user_code.lower().strip()
                    st.success("✅ ¡Registro exitoso! Ya puedes usar tu progreso.")
                    st.rerun()
    
    return False


def display_stats_panel(stats: dict) -> None:
    """Muestra el panel de estadísticas."""
    st.markdown(f"""
    <div class="stats-panel">
        <div class="stat-card">
            <div class="value">{stats['evaluados']}</div>
            <div class="label">📊 Evaluados</div>
        </div>
        <div class="stat-card">
            <div class="value">{stats['buenos']}</div>
            <div class="label">✅ Buenos (8-10)</div>
        </div>
        <div class="stat-card">
            <div class="value">{stats['planeados']}</div>
            <div class="label">📅 Planeados</div>
        </div>
        <div class="stat-card">
            <div class="value">{stats['descartados']}</div>
            <div class="label">❌ Descartados</div>
        </div>
        <div class="stat-card">
            <div class="value">{stats['promedio']:.1f}</div>
            <div class="label">📈 Promedio</div>
        </div>
        <div class="stat-card">
            <div class="value">{stats['total_repasos']}</div>
            <div class="label">🔄 Repasos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_color_legend() -> None:
    """Muestra la leyenda de colores."""
    st.markdown(f"""
    <div class="color-legend">
        <div class="legend-item">
            <div class="legend-color" style="background: {STATE_COLORS['rojo']};"></div>
            <span>Estado 1-3</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {STATE_COLORS['naranja']};"></div>
            <span>Estado 4-5</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {STATE_COLORS['amarillo']};"></div>
            <span>Estado 6-7</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {STATE_COLORS['verde']};"></div>
            <span>Estado 8-10</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {STATE_COLORS['azul']};"></div>
            <span>📅 Planeado</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {STATE_COLORS['descartado']};"></div>
            <span>❌ Descartado</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {STATE_COLORS['sin_evaluar']};"></div>
            <span>Sin evaluar</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_topic_map(topics_df: pd.DataFrame, progress: dict) -> int | None:
    """
    Muestra el mapa de temas con colores.
    Retorna el número del tema clickeado o None.
    """
    # Crear grid de botones
    num_topics = len(topics_df)
    
    # Calcular columnas según el ancho (responsive)
    # En móvil serán menos columnas
    cols_per_row = 10
    
    selected_topic = None
    
    rows = (num_topics + cols_per_row - 1) // cols_per_row
    
    for row_idx in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx, col in enumerate(cols):
            topic_idx = row_idx * cols_per_row + col_idx
            if topic_idx >= num_topics:
                break
            
            topic_num = topic_idx + 1
            topic_data = progress.get(topic_num, {
                "estado": 0,
                "descartado": False,
                "planeado": False
            })
            
            color = get_topic_color(
                topic_data.get("estado", 0),
                topic_data.get("descartado", False),
                topic_data.get("planeado", False)
            )
            
            is_descartado = topic_data.get("descartado", False)
            text_style = "text-decoration: line-through; opacity: 0.6;" if is_descartado else ""
            
            with col:
                if st.button(
                    str(topic_num),
                    key=f"topic_btn_{topic_num}",
                    use_container_width=True,
                    help=f"Tema {topic_num}"
                ):
                    selected_topic = topic_num
                
                # Aplicar color con CSS
                st.markdown(f"""
                <style>
                    div[data-testid="stButton"] button[kind="secondary"]:has(p:contains("{topic_num}")) {{
                        background-color: {color} !important;
                        {text_style}
                    }}
                </style>
                """, unsafe_allow_html=True)
    
    return selected_topic


def display_topic_editor(
    topic_num: int,
    topic_name: str,
    current_data: dict,
    user_code: str
) -> None:
    """Muestra el panel de edición de un tema."""
    
    st.markdown(f"### 📝 Tema {topic_num}")
    
    # Nombre del tema (editable)
    new_name = st.text_input(
        "Nombre del tema",
        value=current_data.get("nombre_tema", topic_name),
        key=f"edit_name_{topic_num}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estado 1-10
        new_estado = st.slider(
            "Estado de dominio",
            min_value=0,
            max_value=10,
            value=current_data.get("estado", 0),
            help="0 = Sin evaluar, 1 = Muy mal, 10 = Perfecto",
            key=f"edit_estado_{topic_num}"
        )
        
        # Repasos
        new_repasos = st.number_input(
            "Número de repasos",
            min_value=0,
            max_value=100,
            value=current_data.get("repasos", 0),
            key=f"edit_repasos_{topic_num}"
        )
    
    with col2:
        # Descartado
        new_descartado = st.checkbox(
            "🚫 Está descartado (no lo voy a estudiar)",
            value=current_data.get("descartado", False),
            help="Marca si no vas a estudiar este tema",
            key=f"edit_descartado_{topic_num}"
        )
        
        # Planeado
        new_planeado = st.checkbox(
            "📌 Está planeado (próximo a estudiar)",
            value=current_data.get("planeado", False),
            help="Marca si planeas estudiar este tema próximamente",
            key=f"edit_planeado_{topic_num}"
        )
    
    # Botones de acción
    col_save, col_close = st.columns(2)
    
    with col_save:
        if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
            new_data = {
                "nombre_tema": new_name,
                "estado": new_estado,
                "repasos": new_repasos,
                "descartado": new_descartado,
                "planeado": new_planeado,
            }
            if save_topic_progress(user_code, topic_num, new_data):
                # Actualizar progreso en session_state
                if "user_progress" not in st.session_state:
                    st.session_state.user_progress = {}
                st.session_state.user_progress[topic_num] = new_data
                st.toast("✅ Guardado correctamente", icon="✅")
                # Cerrar editor y recargar para ver cambios
                st.session_state.editing_topic = None
                st.rerun()
    
    with col_close:
        if st.button("✖ Cerrar editor", use_container_width=True):
            st.session_state.editing_topic = None
            st.rerun()


def render_progress_tab(topics_df: pd.DataFrame) -> None:
    """Renderiza la pestaña de progreso de temas."""
    
    # Verificar login
    if not display_login_form():
        return
    
    user_code = st.session_state.logged_user
    
    # Mostrar usuario actual y opción de cerrar sesión
    col_user, col_logout = st.columns([3, 1])
    with col_user:
        st.markdown(f"👤 Conectado como: **{user_code}**")
    with col_logout:
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state.logged_user = None
            st.session_state.user_progress = {}
            st.session_state.user_temario_loaded = False
            st.rerun()
    
    st.divider()
    
    # Cargar progreso del usuario
    if "user_progress" not in st.session_state or not st.session_state.user_progress:
        st.session_state.user_progress = get_user_progress(user_code)
    
    progress = st.session_state.user_progress
    
    # Estadísticas
    stats = calculate_stats(progress)
    display_stats_panel(stats)
    
    # Leyenda de colores
    display_color_legend()
    
    st.divider()
    
    # Mapa de temas
    st.markdown("### 🗺️ Mapa de Temas")
    
    # Inicializar estado de edición
    if "editing_topic" not in st.session_state:
        st.session_state.editing_topic = None
    
    # Layout: Mapa a la izquierda, Editor a la derecha
    if st.session_state.editing_topic:
        col_map, col_editor = st.columns([2, 1])
    else:
        col_map = st.container()
        col_editor = None
    
    # Grid de temas como HTML visual + selector
    with col_map:
        num_topics = len(topics_df)
        cols_per_row = 10 if not st.session_state.editing_topic else 8
        
        # Crear mapa visual HTML - construir como lista y unir
        grid_items = []
        for topic_idx in range(num_topics):
            topic_num = topic_idx + 1
            topic_data = progress.get(topic_num, {"estado": 0, "descartado": False, "planeado": False})
            color = get_topic_color(
                topic_data.get("estado", 0),
                topic_data.get("descartado", False),
                topic_data.get("planeado", False)
            )
            is_descartado = topic_data.get("descartado", False)
            is_editing = st.session_state.editing_topic == topic_num
            
            text_decoration = "line-through" if is_descartado else "none"
            text_color = "#ffffff" if color not in ["#e5e7eb", "#eab308"] else "#171717"
            border = "3px solid #171717" if is_editing else "1px solid rgba(0,0,0,0.1)"
            font_weight = "700" if is_editing else "500"
            
            item_style = f"background-color:{color};color:{text_color};text-decoration:{text_decoration};border:{border};border-radius:8px;padding:8px 4px;text-align:center;font-weight:{font_weight};font-size:0.9rem;"
            grid_items.append(f'<div style="{item_style}" title="Tema {topic_num}">{topic_num}</div>')
        
        grid_style = f"display:grid;grid-template-columns:repeat({cols_per_row},1fr);gap:6px;margin-bottom:1rem;"
        html_grid = f'<div style="{grid_style}">{"".join(grid_items)}</div>'
        st.markdown(html_grid, unsafe_allow_html=True)
        
        # Selector de tema para editar
        st.markdown("**Selecciona un tema para editar:**")
        col_select, col_btn = st.columns([3, 1])
        
        with col_select:
            # Crear opciones con indicador de estado
            topic_options = []
            for i in range(1, num_topics + 1):
                td = progress.get(i, {"estado": 0, "descartado": False, "planeado": False})
                estado = td.get("estado", 0)
                emoji = "⚪"
                if td.get("descartado", False):
                    emoji = "⚫"
                elif td.get("planeado", False):
                    emoji = "🔵"
                elif estado >= 8:
                    emoji = "🟢"
                elif estado >= 6:
                    emoji = "🟡"
                elif estado >= 4:
                    emoji = "🟠"
                elif estado >= 1:
                    emoji = "🔴"
                topic_options.append(f"{emoji} Tema {i}")
            
            selected = st.selectbox(
                "Tema",
                options=topic_options,
                index=(st.session_state.editing_topic - 1) if st.session_state.editing_topic else 0,
                label_visibility="collapsed",
                key="topic_selector"
            )
            
            # Extraer número del tema seleccionado
            selected_num = int(selected.split(" ")[2])
        
        with col_btn:
            if st.button("✏️ Editar", use_container_width=True, type="primary"):
                st.session_state.editing_topic = selected_num
                st.rerun()
    
    # Panel de edición del tema seleccionado (en columna derecha)
    if st.session_state.editing_topic and col_editor:
        topic_num = st.session_state.editing_topic
        topic_row = topics_df[topics_df["Número"] == topic_num]
        topic_name = topic_row.iloc[0]["Nombre del Tema"] if len(topic_row) > 0 else f"Tema {topic_num}"
        
        current_data = progress.get(topic_num, {
            "nombre_tema": topic_name,
            "estado": 0,
            "repasos": 0,
            "descartado": False,
            "planeado": False
        })
        
        with col_editor:
            with st.container(border=True):
                display_topic_editor(topic_num, topic_name, current_data, user_code)
    
    # Botón para recargar datos
    st.divider()
    if st.button("🔄 Recargar datos desde servidor", use_container_width=True):
        st.session_state.user_progress = get_user_progress(user_code)
        st.success("Datos recargados")
        st.rerun()


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


def get_status_indicator(estado: int, descartado: bool, planeado: bool) -> tuple:
    """Retorna el emoji y color del indicador de estado."""
    if descartado:
        return "⚫", "#9ca3af", "Descartado"
    if planeado:
        return "🔵", "#3b82f6", "Planeado"
    if estado == 0:
        return "⚪", "#e5e7eb", "Sin evaluar"
    if estado <= 3:
        return "🔴", "#ef4444", f"Estado: {estado}/10"
    if estado <= 5:
        return "🟠", "#f97316", f"Estado: {estado}/10"
    if estado <= 7:
        return "🟡", "#eab308", f"Estado: {estado}/10"
    return "🟢", "#22c55e", f"Estado: {estado}/10"


def display_topic_card(topic: pd.Series, is_studied: bool = False, is_selected: bool = False, progress_data: dict = None) -> None:
    """
    Muestra una tarjeta visual para un tema.
    
    Args:
        topic: Serie con los datos del tema
        is_studied: Si el tema está marcado como estudiado
        is_selected: Si el tema está seleccionado para exponer
        progress_data: Datos de progreso del tema (estado, descartado, planeado)
    """
    studied_class = "studied" if is_studied else ""
    selected_class = "selected" if is_selected else ""
    
    # Indicador de estado basado en progreso
    status_indicator = ""
    if progress_data:
        emoji, color, tooltip = get_status_indicator(
            progress_data.get("estado", 0),
            progress_data.get("descartado", False),
            progress_data.get("planeado", False)
        )
        status_indicator = f'<span style="font-size: 1.2rem; margin-right: 8px;" title="{tooltip}">{emoji}</span>'
    
    icon = "✅" if is_studied else ("🎯" if is_selected else "📄")
    badge = ""
    if is_selected:
        badge = '<span style="background: #404040; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 8px;">Seleccionado</span>'
    elif is_studied:
        badge = '<span style="background: #737373; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 8px;">Estudiado</span>'
    
    # Añadir badge de estado si hay progreso
    estado_badge = ""
    if progress_data and progress_data.get("estado", 0) > 0:
        estado = progress_data.get("estado", 0)
        _, color, _ = get_status_indicator(estado, False, False)
        estado_badge = f'<span style="background: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: 8px;">{estado}/10</span>'
    
    st.markdown(f"""
    <div class="topic-card {studied_class} {selected_class}">
        <h4>{status_indicator}{icon} Tema {topic['Número']}{badge}{estado_badge}</h4>
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
        
        # Verificar si hay usuario logueado para cargar temario guardado
        user_has_saved_temario = False
        if "logged_user" in st.session_state and st.session_state.logged_user:
            # Intentar cargar temario guardado del usuario
            if "user_temario_loaded" not in st.session_state:
                saved_temario = get_user_temario(st.session_state.logged_user)
                if saved_temario:
                    parsed = parse_text_topics(saved_temario)
                    if parsed is not None and len(parsed) > 0:
                        st.session_state.text_topics_loaded = parsed
                        st.session_state.user_temario_loaded = True
                        user_has_saved_temario = True
                else:
                    st.session_state.user_temario_loaded = False
            else:
                user_has_saved_temario = st.session_state.user_temario_loaded
        
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
                    # Guardar en Supabase si hay usuario logueado
                    if "logged_user" in st.session_state and st.session_state.logged_user:
                        # Convertir DataFrame a texto para guardar
                        temario_text = "\n".join([
                            f"Tema {row['Número']}: {row['Nombre del Tema']}" 
                            for _, row in topics_df.iterrows()
                        ])
                        if save_user_temario(st.session_state.logged_user, temario_text):
                            st.session_state.user_temario_loaded = True
                            st.toast("📁 Temario guardado en tu cuenta", icon="✅")
        
        else:  # Texto
            # Inicializar el estado del texto si no existe
            if "text_topics_input" not in st.session_state:
                st.session_state.text_topics_input = ""
            if "text_topics_loaded" not in st.session_state:
                st.session_state.text_topics_loaded = None
            
            # Mostrar mensaje si hay temario guardado
            if user_has_saved_temario and st.session_state.text_topics_loaded is not None:
                st.success(f"📁 Temario guardado: {len(st.session_state.text_topics_loaded)} temas")
            
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
                        # Guardar en Supabase si hay usuario logueado
                        if "logged_user" in st.session_state and st.session_state.logged_user:
                            if save_user_temario(st.session_state.logged_user, text_input):
                                st.session_state.user_temario_loaded = True
                                st.toast("📁 Temario guardado en tu cuenta", icon="✅")
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
    
    # Pestañas principales
    tab_simulator, tab_progress = st.tabs(["🎲 Simulador", "📊 Mi Progreso"])
    
    # ==========================================================================
    # TAB: SIMULADOR
    # ==========================================================================
    with tab_simulator:
        st.markdown("""
        Calcula tus probabilidades de éxito y practica con simulaciones de sorteo de temas.
        Configura los parámetros en la barra lateral y comienza a simular.
        """)
        
        st.divider()
        
        # ==================================================================
        # PANEL DE PROBABILIDAD
        # ==================================================================
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
        
        # ==================================================================
        # SIMULACIÓN DE EXAMEN
        # ==================================================================
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
            
            # Obtener progreso del usuario si está logueado
            user_progress = {}
            if "logged_user" in st.session_state and st.session_state.logged_user:
                if "user_progress" not in st.session_state:
                    st.session_state.user_progress = get_user_progress(st.session_state.logged_user)
                user_progress = st.session_state.user_progress
            
            # Crear columnas para las tarjetas
            cols = st.columns(min(3, len(drawn_df)))
            
            for idx, (_, topic) in enumerate(drawn_df.iterrows()):
                with cols[idx % len(cols)]:
                    # Verificar si el tema está en la lista de estudiados
                    is_studied = topic["Número"] in st.session_state.studied_list
                    is_selected = st.session_state.selected_topic_idx == idx
                    
                    # Obtener datos de progreso para este tema
                    topic_progress = user_progress.get(topic["Número"], None)
                    
                    # Mostrar la tarjeta visual con indicador de estado
                    display_topic_card(topic, is_studied, is_selected, topic_progress)
                    
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
    # TAB: MI PROGRESO
    # ==========================================================================
    with tab_progress:
        render_progress_tab(topics_df)
    
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
