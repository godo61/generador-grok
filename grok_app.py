import streamlit as st
import random
import re
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Grok Video Builder", layout="wide", page_icon="🎬")

# --- 1. GESTIÓN DEL ESTADO (MEMORIA) ---
# Inicializamos el historial si no existe
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. FUNCIONES DE AYUDA (Traducción y Azar) ---

def translate_to_english(text):
    """Traduce del español (u otro) al inglés si hay texto."""
    if text and text.strip():
        try:
            # Usa el traductor de Google gratuito
            return GoogleTranslator(source='auto', target='en').translate(text)
        except Exception as e:
            st.error(f"Error al traducir: {e}")
            return text
    return ""

# Datos para el botón "Sorpréndeme"
DEMO_STYLES = ["Photorealistic 8k", "Cinematic Film Stock", "3D Render (Unreal Engine 5)", "Anime Studio Ghibli Style", "Vintage VHS 1980s", "Cyberpunk Noir"]
DEMO_SUBJECTS = ["Un robot samurái", "Un gato astronauta", "Un coche deportivo clásico", "Una guerrera elfa", "Un hacker futurista"]
DEMO_DETAILS = ["armadura dorada oxidada", "traje espacial blanco brillante", "cromados y rayas rojas", "tatuajes azules brillantes", "sudadera negra con cables neón"]
DEMO_ACTIONS = ["luchando con una espada láser", "flotando en gravedad cero", "derrapando a alta velocidad", "lanzando un hechizo mágico", "tecleando furiosamente"]
DEMO_ENVS = ["una calle de Tokio futurista con lluvia", "la superficie de Marte", "una autopista desierta al mediodía", "un bosque mágico antiguo", "una sala de servidores oscura"]
DEMO_CAMERAS = ["Slow motion zoom in", "Fast tracking shot", "Drone flyover", "Handheld shaky cam", "Low angle static shot"] # Cámaras mejor en inglés técnico
DEMO_AUDIOS = ["lluvia golpeando metal y música synthwave", "ruido de radio y silencio", "motor rugiendo y neumáticos chirriando", "destellos mágicos y viento", "pitidos electrónicos y bajos profundos"]

def randomize_fields():
    """Rellena los campos con valores aleatorios en español."""
    st.session_state.k_style = random.choice(DEMO_STYLES)
    st.session_state.k_subject = random.choice(DEMO_SUBJECTS)
    st.session_state.k_details = random.choice(DEMO_DETAILS)
    st.session_state.k_action = random.choice(DEMO_ACTIONS)
    st.session_state.k_env = random.choice(DEMO_ENVS)
    # Dejamos la iluminación y audio vacíos a veces para variar
    st.session_state.k_light = "" 
    st.session_state.k_audio = random.choice(DEMO_AUDIOS)
    st.session_state.k_camera = random.choice(DEMO_CAMERAS)

# --- 3. EL MOTOR (Constructor de Prompts) ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = {}

    def set_field(self, key, value):
        self.parts[key] = value.strip()

    def build(self) -> str:
        # Construcción lógica del string final en Inglés
        p = self.parts
        
        visual_core = []
        
        # Sujeto + Detalles
        subject_phrase = p.get('subject', '')
        if p.get('details'):
            subject_phrase += f", made of or wearing {p['details']}"
        if subject_phrase:
            visual_core.append(subject_phrase)

        # Acción
        if p.get('action'):
            # Truco simple para convertir verbos básicos a gerundio si el traductor no lo hizo
            # (El traductor suele manejarlo bien, pero esto ayuda)
            action_text = p['action']
            if visual_core:
                visual_core[-1] += f", currently {action_text}"
            else:
                visual_core.append(f"A scene showing {action_text}")

        # Entorno e Iluminación
        if p.get('env'):
            visual_core.append(f"set within a {p['env']}")
        if p.get('light'):
            visual_core.append(f"illuminated by {p['light']} lighting")

        # Unir escena visual
        scene_text = ", ".join(visual_core)
        if scene_text:
            scene_text = scene_text[0].upper() + scene_text[1:] + "."

        # Ensamblaje final
        final_segments = []
        if p.get('style'):
            final_segments.append(f"A {p['style']} style video.")
        
        if scene_text:
            final_segments.append(scene_text)
            
        if p.get('camera'):
            final_segments.append(f"Cinematography features a {p['camera']}.")
            
        if p.get('audio'):
            final_segments.append(f"Audio atmosphere includes {p['audio']}.")

        return re.sub(' +', ' ', " ".join(final_segments)).strip()

# --- 4. INTERFAZ GRÁFICA ---

# BARRA LATERAL: HISTORIAL
with st.sidebar:
    st.header("📜 Historial Reciente")
    if not st.session_state.history:
        st.info("Aquí aparecerán tus últimos prompts.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            st.text_area(f"#{len(st.session_state.history)-i}", item, height=100, key=f"hist_{i}")
    
    if st.button("Borrar Historial"):
        st.session_state.history = []
        st.rerun()

# AREA PRINCIPAL
st.title("🎬 Generador Grok (Multi-Idioma)")
st.markdown("""
Esta herramienta **traduce automáticamente** lo que escribas en español al inglés para optimizar el prompt.
""")

if st.button("🎲 Sorpréndeme (Rellenar ideas)", type="secondary", on_click=randomize_fields):
    pass

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("La Escena")
    # Los keys (k_...) permiten que el botón de azar rellene estos campos
    style_in = st.selectbox("Estilo Visual", DEMO_STYLES, key="k_style")
    subject_in = st.text_input("Sujeto (¿Quién?)", placeholder="Ej: Un perro robot", key="k_subject")
    details_in = st.text_input("Detalles (Ropa/Material)", placeholder="Ej: metal oxidado", key="k_details")
    action_in = st.text_input("Acción (¿Qué hace?)", placeholder="Ej: corriendo rápido", key="k_action")

with col2:
    st.subheader("Técnica y Ambiente")
    env_in = st.text_input("Entorno (¿Dónde?)", placeholder="Ej: en la luna", key="k_env")
    light_in = st.text_input("Iluminación", placeholder="Ej: luz de neón rosa", key="k_light")
    camera_in = st.selectbox("Cámara", DEMO_CAMERAS, key="k_camera")
    audio_in = st.text_input("Audio", placeholder="Ej: sonido de viento", key="k_audio")

st.markdown("---")

if st.button("✨ TRADUCIR Y GENERAR", type="primary"):
    with st.spinner("Traduciendo y construyendo prompt..."):
        # 1. Instanciar constructor
        builder = GrokVideoPromptBuilder()
        
        # 2. Traducir y asignar (Solo traducimos lo que es texto libre)
        # El estilo y la cámara suelen ser términos técnicos en inglés, pero si están en español los traduce
        
        builder.set_field('style', translate_to_english(style_in))
        builder.set_field('subject', translate_to_english(subject_in))
        builder.set_field('details', translate_to_english(details_in))
        builder.set_field('action', translate_to_english(action_in))
        builder.set_field('env', translate_to_english(env_in))
        builder.set_field('light', translate_to_english(light_in))
        builder.set_field('camera', camera_in) # Los selectbox ya suelen tener términos técnicos
        builder.set_field('audio', translate_to_english(audio_in))
        
        # 3. Construir
        final_prompt = builder.build()
        
        # 4. Guardar en historial (Máximo 5)
        st.session_state.history.append(final_prompt)
        if len(st.session_state.history) > 5:
            st.session_state.history.pop(0) # Borrar el más antiguo
            
        # 5. Mostrar resultado
        st.success("¡Prompt Generado (en Inglés)!")
        st.code(final_prompt, language="text")
        st.caption("Cópialo y pégalo en Grok. Mira la barra lateral para ver tus anteriores creaciones.")