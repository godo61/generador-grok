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

# --- ESTILOS CSS (UI MASTER) ---
def apply_custom_styles(dark_mode=False):
    if dark_mode:
        bg_color, text_color, tab_bg, tab_active_bg, tab_border = "#0E1117", "#FAFAFA", "#262730", "#0E1117", "#41444C"
    else:
        bg_color, text_color, tab_bg, tab_active_bg, tab_border = "#FFFFFF", "#31333F", "#F0F2F6", "#FFFFFF", "#E0E0E0"

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background-color: {bg_color}; color: {text_color}; }}
        [data-testid="stSidebar"] {{ background-color: {tab_bg}; }}
        [data-testid="stHeader"] {{ background-color: {bg_color}; }}
        div[data-baseweb="tab-list"] {{ gap: 8px; border-bottom: 2px solid {tab_border}; padding-bottom: 0px; }}
        button[data-baseweb="tab"] {{
            background-color: {tab_bg} !important; border-radius: 15px 15px 0px 0px !important;
            border: 1px solid {tab_border} !important; border-bottom: none !important;
            padding: 10px 20px !important; margin-bottom: -2px !important; color: {text_color} !important; opacity: 0.7;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            background-color: {tab_active_bg} !important; border-top: 4px solid #FF4B4B !important;
            border-left: 1px solid {tab_border} !important; border-right: 1px solid {tab_border} !important;
            font-weight: bold !important; opacity: 1;
        }}
        h1, h2, h3, p, li {{ color: {text_color} !important; }}
        </style>
    """, unsafe_allow_html=True)

# --- MEMORIA (ADN DE ACTIVOS) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'uploaded_image_name' not in st.session_state: st.session_state.uploaded_image_name = None
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""

# ADN: PERSONAJES (RESTAURADOS TODOS)
if 'characters' not in st.session_state:
    st.session_state.characters = {
        # --- PRESETS COMPLETOS (ANTIGUOS) ---
        "TON (Guitarra)": """A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique... (Full description) ... He is holding and playing a specific electric guitar model, adopting a passionate musician pose, fingers on the fretboard.""",
        "TON (Micro)": """A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique... (Full description) ... He is holding a vintage microphone close to his mouth, singing passionately with eyes slightly closed, performing on stage.""",
        "FREYA (Kayak)": """A hyper-realistic, cinematic medium shot of a 25-year-old female survivor with a statuesque, athletic 170cm and 60kg physique... (Full description) ... She is paddling a Hyper-realistic expedition sea kayak, model Point 65 Freya 18.""",
        
        # --- BASES FLEXIBLES (NUEVOS) ---
        "TON (Base - Solo cuerpo)": """A hyper-realistic, medium-shot portrait of a striking male figure (185cm, 75kg), elegant verticality and lean muscularity. High cheekbones, sharp geometric jawline, faint skin porosity, groomed five o'clock shadow. Modern textured quiff hair, dark chestnut. Cinematic lighting.""",
        "FREYA (Base - Solo cuerpo)": """A hyper-realistic cinematic shot of a 25-year-old female survivor, statuesque athletic physique (170cm, 60kg). Striking symmetrical face, sharp jawline, intense hazel eyes. Wet skin texture, visible pores. Heavy dark brunette hair."""
    }

# ADN: OBJETOS
if 'custom_props' not in st.session_state:
    st.session_state.custom_props = {
        "Guitarra de Ton": "A vintage 1959 sunburst electric guitar, road-worn finish, rusted hardware, missing high-E string.",
        "Kayak de Freya": "A high-tech carbon fiber expedition kayak, matte black hull with red safety stripes, scratched and battered.",
        "Mascota (Robo-Dog)": "A quadruped Boston Dynamics style robot dog, yellow casing, tactical camera sensors for head."
    }

# --- FUNCIONES ---
def translate_to_english(text):
    if not text: return ""
    text = str(text)
    if not text.strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try:
            return GoogleTranslator(source='auto', target='en').translate(text)
        except Exception:
            return text
    return text

# --- LISTAS FIJAS ---
DEMO_STYLES = ["Photorealistic 8k", "Cinematic", "Anime", "3D Render (Octane)", "Vintage VHS", "Cyberpunk", "Film Noir"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🔴 Mars Surface", "🛶 Dusi River", "🚀 ISS Interior", "🌌 Deep Space", "🌲 Mystic Forest", "🏙️ Cyberpunk City"]
DEMO_WARDROBE = ["✏️ Custom...", "👨‍🚀 NASA Spacesuit", "👽 Sci-Fi Suit", "🛶 Kayak Gear", "🤿 Wetsuit", "👕 Casual", "🤵 Formal"]
DEMO_LIGHTING = ["Natural Daylight", "Cinematic / Dramatic", "Cyberpunk / Neon", "Studio Lighting", "Golden Hour", "Low Key / Dark", "Stark Space Sunlight"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "9:16 (Portrait)", "21:9 (Ultrawide)", "1:1 (Square)"]
DEMO_CAMERAS = ["Static", "Zoom In/Out", "Dolly In/Out", "Truck Left/Right", "Orbit", "Handheld / Shake", "FPV Drone", "Zero-G Floating"]
DEMO_PROPS = ["None", "✏️ Custom...", "🛶 Carbon Fiber Kayak Paddle", "🎸 Electric Guitar", "🎤 Vintage Microphone", "🔫 Sci-Fi Blaster", "📱 Holographic Datapad", "🧪 Glowing Vial", "☕ Coffee Cup"]

# AUDIO LISTS
DEMO_AUDIO_MOOD = ["No Music", "Cinematic Orchestral", "Sci-Fi Synth", "Tribal Drums", "Suspense", "Upbeat", "Silence", "✏️ Custom..."]
DEMO_AUDIO_ENV = ["No Background", "Mars Wind", "River Rapids", "Space Station Hum", "City Traffic", "✏️ Custom..."]
DEMO_SFX_COMMON = ["None", "Thrusters", "Water splashes", "Breathing in helmet", "Radio beeps", "Footsteps", "✏️ Custom..."]

# SUNO LISTS
SUNO_STYLES = ["Cinematic Score", "Cyberpunk / Synthwave", "Epic Orchestral", "Lo-Fi Hip Hop", "Heavy Metal", "Tribal Percussion", "Ambient Space Drone"]
SUNO_STRUCTURES = ["Intro (Short)", "Full Loop", "Outro / Fade out", "Build-up", "Drop"]

# FÍSICA
PHYSICS_LOGIC = {
    "Neutral": [],
    "🌌 Space (Zero-G)": ["Zero-gravity floating", "No air resistance", "Stark lighting", "Vacuum silence"],
    "🔴 Mars (Low G)": ["Low gravity movement", "Red dust storms", "Heat distortion", "Dust settling"],
    "🌊 Water (River)": ["Turbulent flow", "White water foam", "Wet fabric adhesion", "Reflections"],
    "🤿 Underwater": ["Weightless suspension", "Caustics", "Rising bubbles", "Murky visibility"],
    "🌬️ Air / Flight": ["High wind drag", "Fabric fluttering", "Motion blur", "Aerodynamic trails"]
}

# --- CLASE BUILDER ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = {}
        self.is_img2video = False
        self.image_filename = ""

    def set_field(self, key, value):
        if value is None: self.parts[key] = ""
        elif isinstance(value, bool): self.parts[key] = value
        elif isinstance(value, list): self.parts[key] = value
        else: self.parts[key] = str(value).strip()

    def activate_img2video(self, filename):
        self.is_img2video = True
        self.image_filename = filename

    def build(self) -> str:
        p = self.parts
        
        # Audio Logic
        audio_parts = []
        m_val = p.get('audio_mood_custom') if p.get('audio_mood_custom') else p.get('audio_mood')
        if m_val and "No Music" not in m_val and "Custom" not in m_val: audio_parts.append(f"Music: {m_val}")
        
        e_val = p.get('audio_env_custom') if p.get('audio_env_custom') else p.get('audio_env')
        if e_val and "No Background" not in e_val and "Custom" not in e_val: audio_parts.append(f"Ambience: {e_val}")
        
        s_val = p.get('audio_sfx_custom') if p.get('audio_sfx_custom') else p.get('audio_sfx')
        if s_val and "None" not in s_val and "Custom" not in s_val: audio_parts.append(f"SFX: {s_val.split('(')[0].strip()}")
        final_audio = ". ".join(audio_parts)

        # Physics
        physics_prompt = ""
        if p.get('physics_medium') and "Neutral" not in p['physics_medium']:
            med = p['physics_medium'].split('(')[0].strip()
            dets = [d.split('(')[0].strip() for d in p.get('physics_details', [])]
            if dets: physics_prompt = f"Physics: {med} ({', '.join(dets)})"

        # Build Segments
        segments = []
        if self.is_img2video:
            segments.append(f"Img2Vid: '{self.image_filename}'.")
            keep = []
            if p.get('keep_subject'): keep.append("Subject")
            if p.get('keep_bg'): keep.append("Background")
            if keep: segments.append(f"Maintain: {', '.join(keep)}.")
            if p.get('img_action'): segments.append(f"Action: {p['img_action']}")
        else:
            base = p.get('subject', '')
            
            # Objetos Custom (ADN) o Genericos
            prop_val = p.get('props_custom') if p.get('props_custom') else p.get('props')
            if prop_val and "None" not in prop_val and "Custom" not in prop_val:
                base += f", holding/using {prop_val}"
                
            ward_val = p.get('wardrobe_custom') if p.get('wardrobe_custom') else p.get('wardrobe')
            if ward_val and "Custom" not in ward_val:
                base += f", wearing {ward_val}"
            
            if p.get('details'): base += f", {p['details']}"
            
            segments.append(base)
            if p.get('action'): segments.append(f"Action: {p['action']}")
            
            env_val = p.get('env_custom') if p.get('env_custom') else p.get('env')
            if env_val and "Custom" not in env_val: segments.append(f"Loc: {env_val}")
            
            if p.get('style'): segments.append(f"Style: {p['style']}.")

        if p.get('light'): segments.append(f"Light: {p['light']}.")
        if p.get('camera'): segments.append(f"Cam: {p['camera']}.")
        if physics_prompt: segments.append(physics_prompt + ".")
        if final_audio: segments.append(f"Audio: {final_audio}.")
        if p.get('ar'): segments.append(f"--ar {p['ar'].split(' ')[0]}")

        return re.sub(' +', ' ', " ".join(segments)).strip()

# --- INTERFAZ BARRA LATERAL (ADN) ---
with st.sidebar:
    st.title("⚙️ Config")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    st.header("🧬 Banco de ADN")
    
    tab_char, tab_obj = st.tabs(["👤 Personajes", "🎸 Objetos"])
    
    with tab_char:
        c_name = st.text_input("Nombre Actor")
        c_desc = st.text_area("Descripción Actor")
        if st.button("Guardar Actor"):
            if c_name and c_desc:
                st.session_state.characters[c_name] = translate_to_english(c_desc)
                st.success("Actor Guardado")
                st.rerun()

    with tab_obj:
        o_name = st.text_input("Nombre Objeto")
        o_desc = st.text_area("Descripción Visual Objeto")
        if st.button("Guardar Objeto"):
            if o_name and o_desc:
                st.session_state.custom_props[o_name] = translate_to_english(o_desc)
                st.success("Objeto Guardado")
                st.rerun()

    st.markdown("---")
    st.header("🖼️ Imagen")
    uploaded_file = st.file_uploader("Referencia", type=["jpg", "png"])
    if uploaded_file:
        st.session_state.uploaded_image_name = uploaded_file.name
        st.image(uploaded_file, caption="Ref Activa")
    else:
        st.session_state.uploaded_image_name = None

# --- PANEL PRINCIPAL ---
st.title("🎬 Grok Production Studio")

# PESTAÑAS PRINCIPALES
t1, t2, t3, t4, t5 = st.tabs(["📝 Historia & Assets", "⚛️ Física", "🎨 Visual", "🎥 Técnica", "🎵 Audio"])

# VARIABLES TEMPORALES
final_sub = ""
final_act = ""
final_env = ""
final_ward = ""
final_prop = ""
det_raw = ""

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### 🎭 Casting")
        char_keys = list(st.session_state.characters.keys())
        char_sel = st.selectbox("Actor", char_keys)
        final_sub = st.session_state.characters[char_sel]
        
    with col_b:
        st.markdown("##### 🎒 Utilería (Props)")
        prop_options = ["None", "✏️ Custom..."] + list(st.session_state.custom_props.keys()) + DEMO_PROPS[2:]
        p_sel = st.selectbox("Objeto en mano", prop_options)
        
        if p_sel in st.session_state.custom_props:
            final_prop = st.session_state.custom_props[p_sel] 
        elif "Custom" in p_sel:
            final_prop = translate_to_english(st.text_input("Describe objeto nuevo", key="new_prop"))
        elif "None" not in p_sel:
            final_prop = p_sel

    st.markdown("##### 🎬 Acción")
    act_raw = st.text_input("¿Qué ocurre?", placeholder="Ej: tocando la guitarra en el espacio")
    final_act = translate_to_english(act_raw)
    det_raw = st.text_input("Detalles extra")

with t2:
    phy_med = st.selectbox("Medio Físico", list(PHYSICS_LOGIC.keys()))
    phy_det = st.multiselect("Efectos Activos", PHYSICS_LOGIC[phy_med])

with t3:
    c1, c2 = st.columns(2)
    with c1:
        sty = st.selectbox("Estilo", DEMO_STYLES)
        ward_sel = st.selectbox("Vestuario", DEMO_WARDROBE)
        if "Custom" in ward_sel: final_ward = translate_to_english(st.text_input("Ropa Custom"))
        else: final_ward = ward_sel
    with c2:
        env_sel = st.selectbox("Lugar", DEMO_ENVIRONMENTS)
        if "Custom" in env_sel: final_env = translate_to_english(st.text_input("Lugar Custom"))
        else: final_env = env_sel

with t4:
    c1, c2, c3 = st.columns(3)
    with c1: cam = st.selectbox("Cámara", DEMO_CAMERAS)
    with c2: lit = st.selectbox("Luz", DEMO_LIGHTING)
    with c3: ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS)

with t5:
    c1, c2, c3 = st.columns(3)
    with c1: 
        mus_sel = st.selectbox("Música (Video)", DEMO_AUDIO_MOOD)
        mus_vid = translate_to_english(st.text_input("Música Custom")) if "Custom" in mus_sel else mus_sel
    with c2:
        env_aud_sel = st.selectbox("Ambiente (Video)", DEMO_AUDIO_ENV)
        env_vid = translate_to_english(st.text_input("Ambiente Custom")) if "Custom" in env_aud_sel else env_aud_sel
    with c3:
        sfx_sel = st.selectbox("SFX (Video)", DEMO_SFX_COMMON)
        sfx_vid = translate_to_english(st.text_input("SFX Custom")) if "Custom" in sfx_sel else sfx_sel

# BOTÓN GENERAR VIDEO
if st.button("✨ GENERAR PROMPT DE VIDEO", type="primary"):
    b = GrokVideoPromptBuilder()
    if st.session_state.uploaded_image_name:
        b.activate_img2video(st.session_state.uploaded_image_name)
    
    b.set_field('subject', final_sub)
    b.set_field('props', final_prop)
    b.set_field('wardrobe', final_ward)
    b.set_field('action', final_act)
    b.set_field('details', translate_to_english(det_raw))
    b.set_field('physics_medium', phy_med)
    b.set_field('physics_details', phy_det)
    b.set_field('style', sty)
    b.set_field('env', final_env)
    b.set_field('camera', cam)
    b.set_field('light', lit)
    b.set_field('ar', ar)
    b.set_field('audio_mood', mus_vid)
    b.set_field('audio_env', env_vid)
    b.set_field('audio_sfx', sfx_vid)
    
    res = b.build()
    st.session_state.generated_output = res
    st.session_state.history.append(res)

if st.session_state.generated_output:
    st.code(st.session_state.generated_output, language="text")

# --- 🎹 ESTUDIO SUNO AI (SECCIÓN NUEVA) ---
st.markdown("---")
with st.expander("🎹 SUNO AI Audio Station (Intro / Outro Generator)", expanded=False):
    st.info("Generador de prompts optimizados para música en Suno AI.")
    
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        suno_genre = st.selectbox("Estilo Musical", SUNO_STYLES)
        suno_custom_genre = st.text_input("O escribe estilo propio", placeholder="Ej: Andean Folk mixed with Techno")
    with sc2:
        suno_struct = st.selectbox("Estructura", SUNO_STRUCTURES)
        suno_bpm = st.slider("Tempo (BPM)", 60, 180, 120)
    with sc3:
        suno_mood = st.text_input("Atmósfera / Sentimiento", placeholder="Ej: Epica, Nostálgica, Triunfal")
        suno_instr = st.text_input("Instrumentos Clave", placeholder="Ej: Guitarra eléctrica, Violonchelo")

    if st.button("🎵 GENERAR PROMPT PARA SUNO"):
        final_genre = suno_custom_genre if suno_custom_genre else suno_genre
        mood_en = translate_to_english(suno_mood)
        instr_en = translate_to_english(suno_instr)
        suno_prompt = f"[{suno_struct}] [{final_genre}] [{suno_bpm} BPM]\n{mood_en} atmosphere. Featuring {instr_en}."
        st.code(suno_prompt, language="text")