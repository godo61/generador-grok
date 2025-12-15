import streamlit as st
import re

# --- GESTIÓN DE DEPENDENCIAS ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Grok Production Studio", layout="wide", page_icon="🎬")

# --- ESTILOS CSS ---
def apply_custom_styles(dark_mode=False):
    if dark_mode:
        bg_color, text_color, tab_bg, tab_active_bg, tab_border = "#0E1117", "#FAFAFA", "#262730", "#0E1117", "#41444C"
    else:
        bg_color, text_color, tab_bg, tab_active_bg, tab_border = "#FFFFFF", "#31333F", "#F0F2F6", "#FFFFFF", "#E0E0E0"

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background-color: {bg_color}; color: {text_color}; }}
        [data-testid="stSidebar"] {{ background-color: {tab_bg}; }}
        textarea {{ font-size: 1.1rem !important; font-family: monospace !important; }}
        </style>
    """, unsafe_allow_html=True)

# --- DATOS MAESTROS ---
DEFAULT_CHARACTERS = {
    "TON (Base)": "A hyper-realistic, medium-shot portrait of a striking male figure (185cm, 75kg), elegant verticality. High cheekbones, sharp jawline, groomed stubble. Modern textured quiff hair.",
    "FREYA (Base)": "A hyper-realistic cinematic shot of a 25-year-old female survivor, statuesque athletic physique. Striking symmetrical face, sharp jawline, intense hazel eyes. Wet skin texture."
}
DEFAULT_PROPS = {
    "Guitarra Ton": "A vintage 1959 sunburst electric guitar, road-worn finish.",
    "Kayak Freya": "A high-tech carbon fiber expedition kayak, matte black hull with red stripes."
}

# --- MEMORIA ---
if 'history' not in st.session_state: st.session_state.history = []
if 'uploaded_image_name' not in st.session_state: st.session_state.uploaded_image_name = None
if 'uploaded_end_frame_name' not in st.session_state: st.session_state.uploaded_end_frame_name = None
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""
if 'characters' not in st.session_state: st.session_state.characters = DEFAULT_CHARACTERS.copy()
if 'custom_props' not in st.session_state: st.session_state.custom_props = DEFAULT_PROPS.copy()

# --- FUNCIONES ---
def translate_to_english(text):
    if not text or not text.strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try: return GoogleTranslator(source='auto', target='en').translate(str(text))
        except: return str(text)
    return str(text)

# --- LISTAS ---
DEMO_STYLES = ["Photorealistic 8k", "Cinematic VFX", "Anime", "3D Render", "Vintage VHS", "Cyberpunk"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🔴 Mars Surface", "🛶 Dusi River", "🚀 ISS Interior", "🌲 Forest"]
DEMO_CAMERAS = ["Handheld / Shake", "Static", "Zoom In", "Drone Follow", "Orbit"]
DEMO_AUDIO_MOOD = ["Suspense", "Epic Orchestral", "Horror", "Upbeat", "Silence"]

# --- PLANTILLAS DE NARRATIVA (NUEVO) ---
NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🧟 Transformación de Monstruo": "At second 0, the scene is static. Suddenly, the object behind the subject rapidly transforms into a massive, living creature. The texture changes from artificial to realistic biological details. Simultaneously, the subject realizes the danger and reacts with sheer terror, sprinting towards the camera.",
    "🏃 Persecución Intensa": "The subject is running desperately towards the camera, looking back over their shoulder in panic. The background is blurred with motion. The pursuer is gaining ground aggressively. The lighting is harsh and dynamic.",
    "✨ Revelación Mágica": "The scene begins calmly. Slowly, magical particles begin to rise from the object. The light intensifies, revealing a hidden structure. The subject watches in awe as the environment shifts around them.",
    "💥 Acción a Cámara Lenta": "Hyper-slow motion. Debris and particles float in the air. The subject is caught in mid-air action. Every muscle tension and facial micro-expression is visible. The lighting creates dramatic rim highlights."
}

# --- BUILDER (REDISEÑADO) ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = {}
        self.is_img2video = False
        self.image_filename = ""
        self.end_image_filename = None

    def set_field(self, key, value):
        self.parts[key] = str(value).strip() if isinstance(value, str) else value

    def activate_img2video(self, filename, end_filename=None):
        self.is_img2video = True
        self.image_filename = filename
        self.end_image_filename = end_filename

    def build(self) -> str:
        p = self.parts
        
        # 1. MODO NARRATIVA PRO (NUEVO)
        if p.get('narrative_mode'):
            # Estructura tipo Guion de Cine (Como tu ejemplo del Mamut)
            prompt = []
            
            # Cabecera Técnica
            prompt.append(f"6-second action VFX video clip.")
            if self.is_img2video:
                prompt.append(f"Based strictly on reference '{self.image_filename}'.")
                if self.end_image_filename: prompt.append(f"Ending at frame '{self.end_image_filename}'.")
            
            # La Historia (Núcleo)
            # Aquí combinamos Sujeto + Acción en una narrativa fluida
            subject_desc = p.get('subject', 'The subject')
            wardrobe = p.get('wardrobe_custom') or p.get('wardrobe', '')
            if "Custom" in wardrobe: wardrobe = ""
            
            action_block = p.get('action', '')
            
            # Construcción del párrafo narrativo
            narrative = ""
            if action_block:
                narrative += f"{action_block} "
            
            # Insertar detalles del sujeto si no es "Sujeto de foto"
            if subject_desc:
                narrative += f"The main character is {subject_desc}"
                if wardrobe: narrative += f", wearing {wardrobe}."
            
            prompt.append(narrative)
            
            # Atmósfera y Técnica (Integrado al final)
            env_txt = p.get('env_custom') or p.get('env', '')
            if "Custom" in env_txt: env_txt = ""
            
            tech_details = []
            if env_txt: tech_details.append(f"Environment: {env_txt}")
            if p.get('light'): tech_details.append(f"Lighting: {p['light']}")
            if p.get('camera'): tech_details.append(f"Camera: {p['camera']}")
            if p.get('style'): tech_details.append(f"Style: {p['style']}")
            
            # Audio (Si hay)
            audio_parts = []
            if p.get('audio_mood'): audio_parts.append(f"Music: {p['audio_mood']}")
            if p.get('audio_sfx'): audio_parts.append(f"SFX: {p['audio_sfx']}")
            
            full_tech = ". ".join(tech_details)
            full_audio = ". ".join(audio_parts)
            
            if full_tech: prompt.append(f"VISUALS: {full_tech}.")
            if full_audio: prompt.append(f"AUDIO: {full_audio}.")
            if p.get('ar'): prompt.append(f"--ar {p['ar'].split(' ')[0]}")
            
            return "\n\n".join(prompt)

        # 2. MODO CLÁSICO (TAGS) - Para cuando quieres algo simple
        else:
            segments = []
            if self.is_img2video:
                segments.append(f"Start Frame: '{self.image_filename}'.")
                if self.end_image_filename: segments.append(f"End Frame: '{self.end_image_filename}'.")
                
            base = p.get('subject', '')
            if p.get('props'): base += f", with {p['props']}"
            if base: segments.append(base)
            
            if p.get('action'): segments.append(f"Action: {p['action']}")
            if p.get('env'): segments.append(f"Loc: {p['env']}")
            if p.get('camera'): segments.append(f"Cam: {p['camera']}")
            
            return ". ".join(segments)

# --- INTERFAZ ---
with st.sidebar:
    st.title("⚙️ Config")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    st.header("🧬 Banco de ADN")
    # (Gestión de personajes simplificada para ahorrar espacio en este ejemplo)
    char_sel = st.selectbox("Editar Actor", list(st.session_state.characters.keys()))
    st.text_area("ADN Actor", value=st.session_state.characters[char_sel], disabled=True)

    st.markdown("---")
    st.header("🖼️ Imágenes")
    u_file = st.file_uploader("Start Frame (Inicio)", type=["jpg", "png"])
    if u_file:
        st.session_state.uploaded_image_name = u_file.name
        st.image(u_file, caption="Inicio")
    else: st.session_state.uploaded_image_name = None

# --- PANEL PRINCIPAL ---
st.title("🎬 Grok Production Studio")

# INTERRUPTOR DE MODO NARRATIVA
narrative_mode = st.toggle("📝 ACTIVAR MODO NARRATIVA PRO (Guion de Cine)", value=True)

if narrative_mode:
    st.info("💡 Modo Narrativa: Genera historias cronológicas detalladas (Ideal para Runway/Kling/Luma).")
else:
    st.warning("⚡ Modo Rápido: Genera listas de tags (Ideal para Midjourney/Stable Video).")

# PESTAÑAS
t1, t2, t3, t4 = st.tabs(["🎬 Guion & Acción", "🎨 Visual", "🎥 Técnica", "🎵 Audio"])

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        # Selector de Actor Inteligente
        char_opts = list(st.session_state.characters.keys())
        if st.session_state.uploaded_image_name: char_opts.insert(0, "📷 Sujeto de la Foto")
        char_sel = st.selectbox("Protagonista", char_opts)
        
        final_sub = "" if "📷" in char_sel else st.session_state.characters[char_sel]

    with c_b:
        # Selector de Plantillas de Guion
        template_sel = st.selectbox("📋 Usar Plantilla de Guion", list(NARRATIVE_TEMPLATES.keys()))
        template_text = NARRATIVE_TEMPLATES[template_sel]

    # CAJA DE ACCIÓN PRINCIPAL (TEXT AREA)
    st.markdown("##### 📝 Descripción de la Acción (El Guion)")
    
    if narrative_mode:
        # Si hay plantilla elegida, la ponemos como valor por defecto
        action_val = st.text_area("Describe la secuencia (Cronológicamente):", value=template_text, height=150, placeholder="At second 0... Suddenly...")
    else:
        action_val = st.text_input("Acción corta:", placeholder="Running fast")
    
    final_act = translate_to_english(action_val)

with t2:
    c1, c2 = st.columns(2)
    with c1: sty = st.selectbox("Estilo", DEMO_STYLES)
    with c2: env = st.selectbox("Entorno", DEMO_ENVIRONMENTS)
    final_env = translate_to_english(st.text_input("Otro Entorno", key="env_c")) if "Custom" in env else env

with t3:
    c1, c2, c3 = st.columns(3)
    with c1: cam = st.selectbox("Cámara", DEMO_CAMERAS)
    with c2: lit = st.selectbox("Luz", ["Cinematic", "Natural", "Neon", "Stark"])
    with c3: ar = st.selectbox("Formato", ["16:9", "9:16", "21:9"])

with t4:
    mus = st.selectbox("Música", DEMO_AUDIO_MOOD)
    sfx = st.selectbox("SFX", ["None", "Footsteps", "Explosion", "Wind", "Screams"])

# --- GENERACIÓN ---
if st.button("✨ GENERAR GUION TÉCNICO", type="primary"):
    b = GrokVideoPromptBuilder()
    if st.session_state.uploaded_image_name:
        b.activate_img2video(st.session_state.uploaded_image_name)
    
    b.set_field('narrative_mode', narrative_mode)
    b.set_field('subject', final_sub)
    b.set_field('action', final_act) # Aquí va el texto largo traducido
    b.set_field('env', final_env)
    b.set_field('style', sty)
    b.set_field('camera', cam)
    b.set_field('light', lit)
    b.set_field('ar', ar)
    b.set_field('audio_mood', mus)
    b.set_field('audio_sfx', sfx)
    
    res = b.build()
    st.session_state.generated_output = res
    st.session_state.history.append(res)

if st.session_state.generated_output:
    st.markdown("---")
    st.subheader("🎬 Resultado Final")
    st.text_area("Copia tu prompt:", value=st.session_state.generated_output, height=250)