import streamlit as st
import random
import re
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Grok Video Builder Pro", layout="wide", page_icon="🎬")

# --- 1. GESTIÓN DEL ESTADO (MEMORIA) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'uploaded_image_name' not in st.session_state:
    st.session_state.uploaded_image_name = None

# --- 2. FUNCIONES DE AYUDA ---
def translate_to_english(text):
    """Traduce al inglés."""
    if text and text.strip():
        try:
            return GoogleTranslator(source='auto', target='en').translate(text)
        except Exception as e:
            return text # Fallback si falla la traducción
    return ""

# Datos para "Sorpréndeme" (Versión Texto a Video)
DEMO_STYLES = ["Photorealistic 8k", "Cinematic Film Stock", "3D Render (Unreal Engine 5)", "Anime Studio Ghibli Style", "Cyberpunk Noir"]
DEMO_SUBJECTS = ["Un robot samurái", "Un gato astronauta", "Un coche deportivo clásico", "Una guerrera elfa"]
DEMO_DETAILS = ["armadura dorada oxidada", "traje espacial blanco brillante", "cromados y rayas rojas", "tatuajes azules brillantes"]
DEMO_ACTIONS = ["luchando con una espada láser", "flotando en gravedad cero", "derrapando a alta velocidad", "lanzando un hechizo mágico"]
DEMO_ENVS = ["una calle de Tokio futurista", "la superficie de Marte", "una autopista desierta", "un bosque mágico antiguo"]
DEMO_CAMERAS = ["Slow motion zoom in", "Fast tracking shot", "Drone flyover", "Handheld shaky cam"]
DEMO_AUDIOS = ["lluvia golpeando metal", "motor rugiendo", "destellos mágicos y viento", "música épica"]

def randomize_text_fields():
    """Rellena los campos de texto con valores aleatorios."""
    st.session_state.k_style = random.choice(DEMO_STYLES)
    st.session_state.k_subject = random.choice(DEMO_SUBJECTS)
    st.session_state.k_details = random.choice(DEMO_DETAILS)
    st.session_state.k_action = random.choice(DEMO_ACTIONS)
    st.session_state.k_env = random.choice(DEMO_ENVS)
    st.session_state.k_light = ""
    st.session_state.k_audio = random.choice(DEMO_AUDIOS)
    st.session_state.k_camera = random.choice(DEMO_CAMERAS)

# --- 3. EL MOTOR (Constructor de Prompts) ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = {}
        self.is_img2video = False
        self.image_filename = ""

    def set_field(self, key, value):
        self.parts[key] = value.strip()

    def activate_img2video(self, filename):
        self.is_img2video = True
        self.image_filename = filename

    def build(self) -> str:
        p = self.parts
        
        # --- LÓGICA PARA IMAGEN A VIDEO ---
        if self.is_img2video:
            # Estructura específica: Referencia + Qué mantener + Qué animar
            prompt_segments = []
            
            # 1. Referencia a la imagen (Crucial para que Grok sepa que la usa)
            prompt_segments.append(f"Based on the uploaded image '{self.image_filename}'.")
            
            # 2. Instrucciones de Preservación (FLUX)
            keep_list = []
            if p.get('keep_subject'):
                 keep_list.append("the main subject's appearance and identity")
            if p.get('keep_bg'):
                 keep_list.append("the background composition")
            
            if keep_list:
                 preservation_text = "Strictly maintain " + " and ".join(keep_list) + "."
                 prompt_segments.append(preservation_text)

            # 3. Instrucciones de Animación/Cambio (Aurora)
            animation_actions = []
            if p.get('img_action'):
                 animation_actions.append(p['img_action'])
            
            if animation_actions:
                 # Unir acciones y asegurar que empiecen con mayúscula
                 action_text = ". ".join(animation_actions)
                 if not action_text.endswith('.'): action_text += '.'
                 prompt_segments.append(action_text[0].upper() + action_text[1:])

            # 4. Elementos Técnicos Adicionales
            if p.get('camera'):
                 prompt_segments.append(f"Cinematography features a {p['camera']}.")
            if p.get('audio'):
                 prompt_segments.append(f"Audio atmosphere includes {p['audio']}.")
            
            return re.sub(' +', ' ', " ".join(prompt_segments)).strip()

        # --- LÓGICA PARA TEXTO A VIDEO (La original) ---
        else:
            visual_core = []
            subject_phrase = p.get('subject', '')
            if p.get('details'):
                subject_phrase += f", made of or wearing {p['details']}"
            if subject_phrase:
                visual_core.append(subject_phrase)

            if p.get('action'):
                action_text = p['action']
                if visual_core:
                    visual_core[-1] += f", currently {action_text}"
                else:
                    visual_core.append(f"A scene showing {action_text}")

            if p.get('env'):
                visual_core.append(f"set within a {p['env']}")
            if p.get('light'):
                visual_core.append(f"illuminated by {p['light']} lighting")

            scene_text = ", ".join(visual_core)
            if scene_text:
                scene_text = scene_text[0].upper() + scene_text[1:] + "."

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

# BARRA LATERAL: CARGA DE IMAGEN Y HISTORIAL
with st.sidebar:
    st.header("🖼️ Imagen Base (Opcional)")
    st.markdown("Sube una imagen para usarla como referencia.")
    uploaded_file = st.file_uploader("Elige una imagen...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        # Mostrar la imagen y guardar su nombre
        st.image(uploaded_file, caption="Imagen cargada", use_column_width=True)
        st.session_state.uploaded_image_name = uploaded_file.name
        st.success(f"✅ Imagen '{uploaded_file.name}' lista para usar.")
    else:
        st.session_state.uploaded_image_name = None

    st.markdown("---")
    st.header("📜 Historial")
    for i, item in enumerate(reversed(st.session_state.history[:5])):
        st.text_area(f"Prompt #{len(st.session_state.history)-i}", item, height=80, key=f"hist_{i}")

# AREA PRINCIPAL
st.title("🎬 Grok Video Builder Pro")

# Detectar el modo automáticamente
modo_imagen = st.session_state.uploaded_image_name is not None

if modo_imagen:
    # --- MODO IMAGEN A VIDEO ---
    st.info(f"🛠️ **Modo Activado: Imagen a Vídeo** (Usando '{st.session_state.uploaded_image_name}')")
    st.markdown("Define cómo quieres que cobre vida tu imagen.")

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.subheader("1. Qué Mantener (Preservar)")
        keep_subject_in = st.checkbox("Mantener apariencia exacta del sujeto/persona", value=True)
        keep_bg_in = st.checkbox("Mantener el fondo y la composición original", value=True)
        st.caption("Si desmarcas esto, FLUX tendrá libertad para cambiarlo.")

    with col_i2:
        st.subheader("2. Qué Animar (Acción)")
        # Aquí pedimos verbos de acción directa
        img_action_in = st.text_area("Describe el movimiento EN la imagen", placeholder="Ej: Haz que la persona sonría lentamente y parpadee. Que el viento mueva su pelo y las hojas del fondo.", height=100)

    st.subheader("3. Técnica Adicional")
    col_i3, col_i4 = st.columns(2)
    with col_i3:
         camera_img_in = st.selectbox("Movimiento de Cámara", ["Static shot (Fijo)", "Slow zoom in", "Slow pan right", "Handheld drift"], index=0)
    with col_i4:
         audio_img_in = st.text_input("Audio / Ambiente Sonoro", placeholder="Ej: sonido de olas suaves y gaviotas")

    st.markdown("---")
    if st.button("✨ GENERAR PROMPT DE VÍDEO", type="primary"):
        with st.spinner("Creando prompt basado en imagen..."):
            builder = GrokVideoPromptBuilder()
            builder.activate_img2video(st.session_state.uploaded_image_name)
            
            # Configurar campos de preservación
            builder.set_field('keep_subject', keep_subject_in)
            builder.set_field('keep_bg', keep_bg_in)
            
            # Traducir y configurar campos de acción y técnica
            builder.set_field('img_action', translate_to_english(img_action_in))
            builder.set_field('camera', camera_img_in.split(" (")[0]) # Limpiar el texto del selector
            builder.set_field('audio', translate_to_english(audio_img_in))
            
            final_prompt = builder.build()
            st.session_state.history.append(final_prompt)
            st.success("¡Prompt de Imagen a Vídeo Listo!")
            st.code(final_prompt, language="text")
            st.caption("Copia este texto. En Grok, sube tu imagen primero y luego pega este prompt.")

else:
    # --- MODO TEXTO A VIDEO (El clásico) ---
    st.markdown("Modo: **Texto a Vídeo**. (Sube una imagen en la barra lateral para cambiar de modo).")
    if st.button("🎲 Sorpréndeme (Texto)", type="secondary", on_click=randomize_text_fields): pass
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("La Escena")
        style_in = st.selectbox("Estilo Visual", DEMO_STYLES, key="k_style")
        subject_in = st.text_input("Sujeto", placeholder="Ej: Un robot", key="k_subject")
        details_in = st.text_input("Detalles", placeholder="Ej: oxidado", key="k_details")
        action_in = st.text_input("Acción (gerundio)", placeholder="Ej: corriendo", key="k_action")
    with col2:
        st.subheader("Técnica")
        env_in = st.text_input("Entorno", placeholder="Ej: Marte", key="k_env")
        light_in = st.text_input("Iluminación", placeholder="Ej: neón", key="k_light")
        camera_in = st.selectbox("Cámara", DEMO_CAMERAS, key="k_camera")
        audio_in = st.text_input("Audio", placeholder="Ej: viento", key="k_audio")

    st.markdown("---")
    if st.button("✨ TRADUCIR Y GENERAR (TEXTO)", type="primary"):
        with st.spinner("Procesando..."):
            builder = GrokVideoPromptBuilder()
            builder.set_field('style', translate_to_english(style_in))
            builder.set_field('subject', translate_to_english(subject_in))
            builder.set_field('details', translate_to_english(details_in))
            builder.set_field('action', translate_to_english(action_in))
            builder.set_field('env', translate_to_english(env_in))
            builder.set_field('light', translate_to_english(light_in))
            builder.set_field('camera', camera_in)
            builder.set_field('audio', translate_to_english(audio_in))
            
            final_prompt = builder.build()
            st.session_state.history.append(final_prompt)
            st.success("¡Prompt de Texto a Vídeo Listo!")
            st.code(final_prompt, language="text")