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

# --- DATOS MAESTROS (FACTORY DEFAULTS) ---
DEFAULT_CHARACTERS = {
    "TON (Base - Solo cuerpo)": "A hyper-realistic, medium-shot portrait of a striking male figure (185cm, 75kg), elegant verticality. High cheekbones, sharp geometric jawline, groomed five o'clock shadow. Modern textured quiff hair, dark chestnut. Cinematic lighting.",
    "FREYA (Base - Solo cuerpo)": "A hyper-realistic cinematic shot of a 25-year-old female survivor, statuesque athletic physique (170cm, 60kg). Striking symmetrical face, sharp jawline, intense hazel eyes. Wet skin texture. Heavy dark brunette hair.",
    "TON (Guitarra)": "A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique. He is attired in a charcoal-grey heavyweight cotton t-shirt and raw selvedge denim jeans. He is holding and playing a specific electric guitar model, adopting a passionate musician pose, fingers on the fretboard. Cinematic moody lighting.",
    "FREYA (Kayak)": "A hyper-realistic, cinematic medium shot of a 25-year-old female survivor. She is completely drenched, wearing a futuristic 'Aquatic Warcore' tactical wetsuit. She is paddling a Hyper-realistic expedition sea kayak, model Point 65 Freya 18, in a turbulent marine environment."
}

DEFAULT_PROPS = {
    "Guitarra de Ton": "A vintage 1959 sunburst electric guitar, road-worn finish, rusted hardware, missing high-E string.",
    "Kayak de Freya": "A high-tech carbon fiber expedition kayak, matte black hull with red safety stripes, scratched and battered.",
    "Mascota (Robo-Dog)": "A quadruped Boston Dynamics style robot dog, yellow casing, tactical camera sensors for head."
}

# --- MEMORIA ---
if 'history' not in st.session_state: st.session_state.history = []
if 'uploaded_image_name' not in st.session_state: st.session_state.uploaded_image_name = None
if 'uploaded_end_frame_name' not in st.session_state: st.session_state.uploaded_end_frame_name = None
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""

# Auto-Reparación de Memoria
if 'characters' not in st.session_state: st.session_state.characters = DEFAULT_CHARACTERS.copy()
else:
    for k, v in DEFAULT_CHARACTERS.items():
        if k not in st.session_state.characters: st.session_state.characters[k] = v

if 'custom_props' not in st.session_state: st.session_state.custom_props = DEFAULT_PROPS.copy()
else:
    for k, v in DEFAULT_PROPS.items():
        if k not in st.session_state.custom_props: st.session_state.custom_props[k] = v

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

# --- LISTAS ---
DEMO_STYLES = ["Photorealistic 8k", "Cinematic", "Anime", "3D Render (Octane)", "Vintage VHS", "Cyberpunk", "Film Noir"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🔴 Mars Surface", "🛶 Dusi River", "🚀 ISS Interior", "🌌 Deep Space", "🌲 Mystic Forest", "🏙️ Cyberpunk City"]
DEMO_WARDROBE = ["✏️ Custom...", "👨‍🚀 NASA Spacesuit", "👽 Sci-Fi Suit", "🛶 Kayak Gear", "🤿 Wetsuit", "👕 Casual", "🤵 Formal"]
DEMO_LIGHTING = ["Natural Daylight", "Cinematic / Dramatic", "Cyberpunk / Neon", "Studio Lighting", "Golden Hour", "Low Key / Dark", "Stark Space Sunlight"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "9:16 (Portrait)", "21:9 (Ultrawide)", "1:1 (Square)"]
DEMO_CAMERAS = ["Static", "Zoom In/Out", "Dolly In/Out", "Truck Left/Right", "Orbit", "Handheld / Shake", "FPV Drone", "Zero-G Floating"]
DEMO_PROPS = ["None", "✏️ Custom...", "🛶 Carbon Fiber Kayak Paddle", "🎸 Electric Guitar", "🎤 Vintage Microphone", "🔫 Sci-Fi Blaster", "📱 Holographic Datapad", "🧪 Glowing Vial", "☕ Coffee Cup"]
DEMO_AUDIO_MOOD = ["No Music", "Cinematic Orchestral", "Sci-Fi Synth", "Tribal Drums", "Suspense", "Upbeat", "Silence", "✏️ Custom..."]
DEMO_AUDIO_ENV = ["No Background", "Mars Wind", "River Rapids", "Space Station Hum", "City Traffic", "✏️ Custom..."]
DEMO_SFX_COMMON = ["None", "Thrusters", "Water splashes", "Breathing in helmet", "Radio beeps", "Footsteps", "✏️ Custom..."]
SUNO_STYLES = ["Cinematic Score", "Cyberpunk / Synthwave", "Epic Orchestral", "Lo-Fi Hip Hop", "Heavy Metal", "Tribal Percussion", "Ambient Space Drone"]
SUNO_STRUCTURES = ["Intro (Short)", "Full Loop", "Outro / Fade out", "Build-up", "Drop"]

PHYSICS_LOGIC = {
    "Neutral": [],
    "🌌 Space (Zero-G)": ["Zero-gravity floating", "No air resistance", "Stark lighting", "Vacuum silence"],
    "🔴 Mars (Low G)": ["Low gravity movement", "Red dust storms", "Heat distortion", "Dust settling"],
    "🌊 Water (River)": ["Turbulent flow", "White water foam", "Wet fabric adhesion", "Reflections"],
    "🤿 Underwater": ["Weightless suspension", "Caustics", "Rising bubbles", "Murky visibility"],
    "🌬️ Air / Flight": ["High wind drag", "Fabric fluttering", "Motion blur", "Aerodynamic trails"]
}

# --- BUILDER ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = {}
        self.is_img2video = False
        self.image_filename = ""
        self.end_image_filename = None

    def set_field(self, key, value):
        if value is None: self.parts[key] = ""
        elif isinstance(value, bool): self.parts[key] = value
        elif isinstance(value, list): self.parts[key] = value
        else: self.parts[key] = str(value).strip()

    def activate_img2video(self, filename, end_filename=None):
        self.is_img2video = True
        self.image_filename = filename
        self.end_image_filename = end_filename

    def build(self) -> str:
        p = self.parts
        
        # Audio
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

        # Segments
        segments = []
        if self.is_img2video:
            segments.append(f"Start Frame: '{self.image_filename}'.")
            if self.end_image_filename:
                segments.append(f"End Frame: '{self.end_image_filename}'.")
            
            keep = []
            if p.get('keep_subject'): keep.append("Subject")
            if p.get('keep_bg'): keep.append("Background")
            if keep: segments.append(f"Maintain: {', '.join(keep)}.")
            if p.get('img_action'): segments.append(f"Action: {p['img_action']}")
        else:
            base = p.get('subject', '')
            prop_val = p.get('props_custom') if p.get('props_custom') else p.get('props')
            if prop_val and "None" not in prop_val and "Custom" not in prop_val: base += f", holding/using {prop_val}"
            ward_val = p.get('wardrobe_custom') if p.get('wardrobe_custom') else p.get('wardrobe')
            if ward_val and "Custom" not in ward_val: base += f", wearing {ward_val}"
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

# --- INTERFAZ BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Config")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    if st.button("🔄 Restaurar Fábrica"):
        st.session_state.characters = DEFAULT_CHARACTERS.copy()
        st.session_state.custom_props = DEFAULT_PROPS.copy()
        st.success("¡Restaurado!")
        st.rerun()

    st.header("🧬 Banco de ADN")
    tc, to = st.tabs(["👤 Cast", "🎸 Props"])
    with tc:
        c_n = st.text_input("Nombre Actor")
        c_d = st.text_area("Descripción")
        if st.button("Guardar Actor"):
            if c_n and c_d:
                st.session_state.characters[c_n] = translate_to_english(c_d)
                st.success("OK")
                st.rerun()
    with to:
        o_n = st.text_input("Nombre Objeto")
        o_d = st.text_area("Descripción Visual")
        if st.button("Guardar Objeto"):
            if o_n and o_d:
                st.session_state.custom_props[o_n] = translate_to_english(o_d)
                st.success("OK")
                st.rerun()

    st.markdown("---")
    st.header("🖼️ Imágenes")
    u_file = st.file_uploader("Start Frame (Inicio)", type=["jpg", "png"])
    if u_file:
        st.session_state.uploaded_image_name = u_file.name
        st.image(u_file, caption="Inicio")
    else: st.session_state.uploaded_image_name = None
    
    u_end = st.file_uploader("End Frame (Final)", type=["jpg", "png"])
    if u_end:
        st.session_state.uploaded_end_frame_name = u_end.name
        st.image(u_end, caption="Final")
    else: st.session_state.uploaded_end_frame_name = None

# --- PANEL PRINCIPAL ---
st.title("🎬 Grok Production Studio")

# --- GUÍA DE AYUDA (MEGA-PROMPT DE EXTRACCIÓN) ---
with st.expander("📘 GUÍA DE USO & PROMPT MAESTRO DE EXTRACCIÓN (INGLÉS)", expanded=False):
    st.markdown("### 🧬 MASTER PROMPT: Extracción de ADN Visual")
    st.info("Copia este bloque y pégalo en **ChatGPT-4o, Claude 3.5 Sonnet o Midjourney /describe** junto con tu imagen de referencia. Este prompt generará la descripción técnica exacta que necesitas guardar en el 'Banco de ADN'.")
    
    st.code("""
    # ROLE
    You are an expert Lead Character Artist and VFX Supervisor specializing in Generative AI prompting (Midjourney/Runway). Your goal is to reverse-engineer the "Visual DNA" of the subject in the image.

    # TASK
    Analyze the uploaded image and generate a highly technical, comma-separated description of the SUBJECT ONLY. 
    Do NOT describe the background, action, or temporary lighting unless asked. Focus on the permanent features that make this subject unique.

    # OUTPUT FORMAT
    String of text, dense keywords, comma-separated.

    # ANALYSIS CATEGORIES (Include these specific details):
    1. DEMOGRAPHICS & BODY: Age range, precise ethnicity mix, gender, height estimate, somatotype (ectomorph/mesomorph/endomorph), muscle definition level.
    2. FACE STRUCTURE: Face shape (square/oval/diamond), jawline definition (sharp/soft), cheekbone prominence, forehead height.
    3. EYES: Exact color (e.g., 'piercing icy blue'), shape (almond/hooded/deep-set), eyebrow density and arch.
    4. SKIN & TEXTURE: Complexion, visible pores, freckles, scars, stubble density, skin specular highlights (sweat/oil).
    5. HAIR: Exact color code (e.g., 'raven black with midnight blue undertones'), cut style, texture (wavy/coarse), hairline.
    6. KEY FEATURES: Distinguishing marks (tattoos, moles), nose shape (aquiline/button), lip thickness.

    # EXAMPLE OUTPUT START
    "Male, 30s, mixed Japanese-Caucasian heritage, lean ectomorph build, wire-rimmed glasses, sharp jawline, high cheekbones, stubble beard, textured messy undercut hair, dark hazel eyes, slight scar on left eyebrow..."
    """, language="text")
    
    st.markdown("""
    ---
    ### ⚠️ Solución de Problemas
    * **Botón Restaurar Fábrica:** (Menú Lateral) Úsalo si borraste personajes importantes por error. Reinicia la lista de actores.
    * **Start/End Frame:** Si usas 'Image-to-Video', sube la imagen inicial. La imagen final es opcional pero ayuda a guiar la animación.
    """)

# PESTAÑAS
t1, t2, t3, t4, t5 = st.tabs(["📝 Historia", "⚛️ Física", "🎨 Visual", "🎥 Técnica", "🎵 Audio"])

# VARS
final_sub, final_act, final_env, final_ward, final_prop, det_raw = "", "", "", "", "", ""
mus_vid, env_vid, sfx_vid = "", "", ""

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        char_sel = st.selectbox("Actor", list(st.session_state.characters.keys()))
        final_sub = st.session_state.characters[char_sel]
    with c_b:
        all_props = ["None", "✏️ Custom..."] + list(st.session_state.custom_props.keys()) + DEMO_PROPS[2:]
        p_sel = st.selectbox("Objeto", all_props)
        if p_sel in st.session_state.custom_props: final_prop = st.session_state.custom_props[p_sel]
        elif "Custom" in p_sel: final_prop = translate_to_english(st.text_input("Objeto Nuevo", key="np"))
        elif "None" not in p_sel: final_prop = p_sel

    act_raw = st.text_input("Acción", placeholder="Ej: flotando hacia la cámara")
    final_act = translate_to_english(act_raw)
    det_raw = st.text_input("Detalles")

with t2:
    phy_med = st.selectbox("Medio", list(PHYSICS_LOGIC.keys()))
    phy_det = st.multiselect("Efectos", PHYSICS_LOGIC[phy_med])

with t3:
    c1, c2 = st.columns(2)
    with c1:
        sty = st.selectbox("Estilo", DEMO_STYLES)
        w_sel = st.selectbox("Vestuario", DEMO_WARDROBE)
        if "Custom" in w_sel: final_ward = translate_to_english(st.text_input("Ropa Custom", key="wc"))
        else: final_ward = w_sel
    with c2:
        e_sel = st.selectbox("Lugar", DEMO_ENVIRONMENTS)
        if "Custom" in e_sel: final_env = translate_to_english(st.text_input("Lugar Custom", key="lc"))
        else: final_env = e_sel

with t4:
    c1, c2, c3 = st.columns(3)
    with c1: cam = st.selectbox("Cámara", DEMO_CAMERAS)
    with c2: lit = st.selectbox("Luz", DEMO_LIGHTING)
    with c3: ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS)

with t5:
    c1, c2, c3 = st.columns(3)
    with c1: 
        m_sel = st.selectbox("Música", DEMO_AUDIO_MOOD)
        mus_vid = translate_to_english(st.text_input("Mus. Custom", key="mc")) if "Custom" in m_sel else m_sel
    with c2:
        e_aud = st.selectbox("Ambiente", DEMO_AUDIO_ENV)
        env_vid = translate_to_english(st.text_input("Amb. Custom", key="ec")) if "Custom" in e_aud else e_aud
    with c3:
        s_sel = st.selectbox("SFX", DEMO_SFX_COMMON)
        sfx_vid = translate_to_english(st.text_input("SFX Custom", key="sc")) if "Custom" in s_sel else s_sel

if st.button("✨ GENERAR PROMPT", type="primary"):
    b = GrokVideoPromptBuilder()
    if st.session_state.uploaded_image_name:
        b.activate_img2video(
            st.session_state.uploaded_image_name, 
            st.session_state.uploaded_end_frame_name
        )
    
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

# --- SUNO ---
st.markdown("---")
with st.expander("🎹 SUNO AI Audio Station", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        s_gen = st.selectbox("Género", SUNO_STYLES)
        s_cus = st.text_input("Género Propio")
    with c2:
        s_str = st.selectbox("Estructura", SUNO_STRUCTURES)
        s_bpm = st.slider("BPM", 60, 180, 120)
    with c3:
        s_moo = st.text_input("Mood")
        s_ins = st.text_input("Instrumentos")

    if st.button("🎵 GENERAR SUNO"):
        fg = s_cus if s_cus else s_gen
        mo = translate_to_english(s_moo)
        ins = translate_to_english(s_ins)
        st.code(f"[{s_str}] [{fg}] [{s_bpm} BPM]\n{mo} atmosphere. Featuring {ins}.", language="text")