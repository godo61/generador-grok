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

# --- DATOS MAESTROS (FACTORY) ---
DEFAULT_CHARACTERS = {
    "TON (Base)": "A hyper-realistic, medium-shot portrait of a striking male figure (185cm, 75kg), elegant verticality. High cheekbones, sharp jawline. Modern textured quiff hair.",
    "FREYA (Base)": "A hyper-realistic cinematic shot of a 25-year-old female survivor, statuesque athletic physique. Striking symmetrical face, sharp jawline. Wet skin texture.",
    "TON (Guitarra)": "Ton holding and playing a specific electric guitar model, adopting a passionate musician pose.",
    "FREYA (Kayak)": "Freya completely drenched, wearing a tactical wetsuit, paddling a sea kayak in turbulent water."
}
DEFAULT_PROPS = {
    "Guitarra Ton": "A vintage 1959 sunburst electric guitar, road-worn finish.",
    "Kayak Freya": "A high-tech carbon fiber expedition kayak, matte black hull with red stripes.",
    "Robo-Dog": "A quadruped Boston Dynamics style robot dog, yellow casing."
}

# --- MEMORIA ---
if 'history' not in st.session_state: st.session_state.history = []
if 'uploaded_image_name' not in st.session_state: st.session_state.uploaded_image_name = None
if 'uploaded_end_frame_name' not in st.session_state: st.session_state.uploaded_end_frame_name = None
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""

# Auto-Reparación
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
    if not text or not text.strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try: return GoogleTranslator(source='auto', target='en').translate(str(text))
        except: return str(text)
    return str(text)

# --- LISTAS ---
DEMO_STYLES = ["Photorealistic 8k", "Cinematic VFX", "Anime", "3D Render", "Vintage VHS", "Cyberpunk"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🔴 Mars Surface", "🛶 Dusi River", "🚀 ISS Interior", "🌲 Forest", "🏙️ Cyberpunk City"]
DEMO_WARDROBE = ["✏️ Custom...", "👨‍🚀 NASA Spacesuit", "👽 Sci-Fi Suit", "🛶 Kayak Gear", "🤿 Wetsuit", "👕 Casual", "🤵 Formal"]
DEMO_LIGHTING = ["Natural Daylight", "Cinematic / Dramatic", "Cyberpunk / Neon", "Studio Lighting", "Golden Hour", "Stark Space Sunlight"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "9:16 (Portrait)", "21:9 (Ultrawide)", "1:1 (Square)"]
DEMO_CAMERAS = ["Handheld / Shake", "Static", "Zoom In", "Drone Follow", "Orbit", "Dolly Zoom"]
DEMO_PROPS = ["None", "✏️ Custom...", "🛶 Kayak Paddle", "🎸 Electric Guitar", "🔫 Blaster", "📱 Datapad"]

DEMO_AUDIO_MOOD = ["No Music", "Cinematic Orchestral", "Sci-Fi Synth", "Suspense", "Horror", "Upbeat", "Silence", "✏️ Custom..."]
DEMO_AUDIO_ENV = ["No Background", "Mars Wind", "River Rapids", "Space Station Hum", "City Traffic", "✏️ Custom..."]
DEMO_SFX_COMMON = ["None", "Thrusters", "Water splashes", "Breathing", "Footsteps", "Explosion", "✏️ Custom..."]

SUNO_STYLES = ["Cinematic Score", "Cyberpunk", "Epic Orchestral", "Lo-Fi", "Heavy Metal", "Ambient Drone"]
SUNO_STRUCTURES = ["Intro (Short)", "Full Loop", "Outro", "Build-up", "Drop"]

PHYSICS_LOGIC = {
    "Neutral": [],
    "🌌 Space (Zero-G)": ["Zero-gravity floating", "No air resistance", "Stark lighting", "Vacuum silence"],
    "🔴 Mars (Low G)": ["Low gravity movement", "Red dust storms", "Heat distortion", "Dust settling"],
    "🌊 Water (River)": ["Turbulent flow", "White water foam", "Wet fabric adhesion", "Reflections"],
    "🤿 Underwater": ["Weightless suspension", "Caustics", "Rising bubbles", "Murky visibility"],
    "🌬️ Air / Flight": ["High wind drag", "Fabric fluttering", "Motion blur", "Aerodynamic trails"]
}

NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🧟 Transformación": "At second 0, the scene is static. Suddenly, the object behind the subject rapidly transforms into a massive, living creature. The texture changes from artificial to realistic. Simultaneously, the subject realizes the danger and reacts with sheer terror.",
    "🏃 Persecución": "The subject is running desperately towards the camera, looking back over their shoulder in panic. The background is blurred with motion. The pursuer is gaining ground aggressively.",
    "✨ Revelación": "The scene begins calmly. Slowly, magical particles begin to rise. The light intensifies, revealing a hidden structure. The subject watches in awe."
}

# --- BUILDER ---
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
        
        # Procesar Audio Custom
        audio_parts = []
        m_val = p.get('audio_mood_custom') or p.get('audio_mood')
        if m_val and "No Music" not in m_val and "Custom" not in m_val: audio_parts.append(f"Music: {m_val}")
        e_val = p.get('audio_env_custom') or p.get('audio_env')
        if e_val and "No Background" not in e_val and "Custom" not in e_val: audio_parts.append(f"Ambience: {e_val}")
        s_val = p.get('audio_sfx_custom') or p.get('audio_sfx')
        if s_val and "None" not in s_val and "Custom" not in s_val: audio_parts.append(f"SFX: {s_val.split('(')[0].strip()}")
        final_audio = ". ".join(audio_parts)

        # Procesar Física
        physics_txt = ""
        if p.get('physics_medium') and "Neutral" not in p['physics_medium']:
            med = p['physics_medium'].split('(')[0].strip()
            dets = [d.split('(')[0].strip() for d in p.get('physics_details', [])]
            if dets: physics_txt = f"{med} simulation ({', '.join(dets)})"

        # --- MODO NARRATIVA (GUION) ---
        if p.get('narrative_mode'):
            prompt = []
            prompt.append("6-second action VFX video clip.")
            if self.is_img2video:
                prompt.append(f"Based strictly on reference '{self.image_filename}'.")
                if self.end_image_filename: prompt.append(f"Ends at '{self.end_image_filename}'.")
            
            # Historia
            action_block = p.get('action', '')
            subject_desc = p.get('subject', '')
            wardrobe = p.get('wardrobe_custom') or p.get('wardrobe', '')
            if "Custom" in wardrobe: wardrobe = ""
            
            narrative = ""
            if action_block: narrative += f"{action_block} "
            if subject_desc: 
                narrative += f"The main character is {subject_desc}"
                if wardrobe: narrative += f", wearing {wardrobe}."
                if p.get('props'): narrative += f", holding {p['props']}."
            
            prompt.append(narrative)
            
            # Física en Narrativa
            if physics_txt: prompt.append(f"Physics Environment: {physics_txt}.")
            
            # Técnica
            env_txt = p.get('env_custom') or p.get('env', '')
            if "Custom" in env_txt: env_txt = ""
            
            tech = []
            if env_txt: tech.append(f"Env: {env_txt}")
            if p.get('light'): tech.append(f"Light: {p['light']}")
            if p.get('camera'): tech.append(f"Cam: {p['camera']}")
            
            if tech: prompt.append(". ".join(tech))
            if final_audio: prompt.append(f"AUDIO: {final_audio}.")
            if p.get('ar'): prompt.append(f"--ar {p['ar'].split(' ')[0]}")
            
            return "\n\n".join(prompt)

        # --- MODO CLÁSICO (TAGS) ---
        else:
            segments = []
            if self.is_img2video:
                segments.append(f"Start Frame: '{self.image_filename}'.")
                if self.end_image_filename: segments.append(f"End Frame: '{self.end_image_filename}'.")
            
            base = p.get('subject', '')
            ward = p.get('wardrobe_custom') or p.get('wardrobe')
            if ward and "Custom" not in ward: base += f", wearing {ward}"
            if p.get('props'): base += f", holding {p['props']}"
            if base: segments.append(base)
            
            if p.get('action'): segments.append(f"Action: {p['action']}")
            if physics_txt: segments.append(f"Physics: {physics_txt}")
            
            env_val = p.get('env_custom') or p.get('env')
            if env_val and "Custom" not in env_val: segments.append(f"Loc: {env_val}")
            
            if p.get('light'): segments.append(f"Light: {p['light']}")
            if p.get('camera'): segments.append(f"Cam: {p['camera']}")
            if final_audio: segments.append(f"Audio: {final_audio}")
            if p.get('ar'): segments.append(f"--ar {p['ar'].split(' ')[0]}")
            
            return ". ".join(segments)

# --- INTERFAZ ---
with st.sidebar:
    st.title("⚙️ Config")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    if st.button("🔄 Restaurar Fábrica"):
        st.session_state.characters = DEFAULT_CHARACTERS.copy()
        st.session_state.custom_props = DEFAULT_PROPS.copy()
        st.success("OK")
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
    u_file = st.file_uploader("Start Frame", type=["jpg", "png"])
    if u_file:
        st.session_state.uploaded_image_name = u_file.name
        st.image(u_file, caption="Inicio")
    else: st.session_state.uploaded_image_name = None
    u_end = st.file_uploader("End Frame", type=["jpg", "png"])
    if u_end:
        st.session_state.uploaded_end_frame_name = u_end.name
        st.image(u_end, caption="Final")
    else: st.session_state.uploaded_end_frame_name = None

# --- PANEL PRINCIPAL ---
st.title("🎬 Grok Production Studio")

# Toggle Modo
narrative_mode = st.toggle("📝 MODO NARRATIVA (Guion Pro)", value=True)

# PESTAÑAS (TODAS RECUPERADAS)
t1, t2, t3, t4, t5 = st.tabs(["🎬 Historia", "🎒 Assets", "⚛️ Física", "🎥 Técnica", "🎵 Audio"])

# Vars
final_sub, final_act, final_ward, final_prop, final_env = "", "", "", "", ""
mus_vid, env_vid, sfx_vid = "", "", ""
phy_med, phy_det = "Neutral", []

with t1:
    # 1. Historia
    c_a, c_b = st.columns(2)
    with c_a:
        char_opts = list(st.session_state.characters.keys())
        if st.session_state.uploaded_image_name: char_opts.insert(0, "📷 Sujeto de la Foto")
        char_sel = st.selectbox("Protagonista", char_opts)
        final_sub = "" if "📷" in char_sel else st.session_state.characters[char_sel]
    with c_b:
        # Template selector
        if narrative_mode:
            tpl = st.selectbox("Plantilla Guion", list(NARRATIVE_TEMPLATES.keys()))
            tpl_txt = NARRATIVE_TEMPLATES[tpl]
        else:
            tpl_txt = ""

    st.markdown("##### 📝 Acción / Guion")
    if narrative_mode:
        act_val = st.text_area("Escribe la secuencia:", value=tpl_txt, height=150, placeholder="At second 0...")
    else:
        act_val = st.text_input("Acción corta:", placeholder="Running fast")
    final_act = translate_to_english(act_val)

with t2:
    # 2. Assets (Wardrobe & Props)
    c1, c2 = st.columns(2)
    with c1:
        # Props con Custom y ADN
        all_props = ["None", "✏️ Custom..."] + list(st.session_state.custom_props.keys()) + DEMO_PROPS[2:]
        p_sel = st.selectbox("Objeto", all_props)
        if p_sel in st.session_state.custom_props: final_prop = st.session_state.custom_props[p_sel]
        elif "Custom" in p_sel: final_prop = translate_to_english(st.text_input("Objeto Nuevo", key="np"))
        elif "None" not in p_sel: final_prop = p_sel
    with c2:
        # Wardrobe
        w_sel = st.selectbox("Vestuario", DEMO_WARDROBE)
        if "Custom" in w_sel: final_ward = translate_to_english(st.text_input("Ropa Custom", key="wc"))
        else: final_ward = w_sel

with t3:
    # 3. Física (RECUPERADA)
    phy_med = st.selectbox("Medio Físico", list(PHYSICS_LOGIC.keys()))
    phy_det = st.multiselect("Efectos", PHYSICS_LOGIC[phy_med])

with t4:
    # 4. Técnica
    c1, c2 = st.columns(2)
    with c1:
        sty = st.selectbox("Estilo", DEMO_STYLES)
        e_sel = st.selectbox("Lugar", DEMO_ENVIRONMENTS)
        if "Custom" in e_sel: final_env = translate_to_english(st.text_input("Lugar Custom", key="lc"))
        else: final_env = e_sel
    with c2:
        cam = st.selectbox("Cámara", DEMO_CAMERAS)
        lit = st.selectbox("Luz", DEMO_LIGHTING)
        ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS)

with t5:
    # 5. Audio (CON CUSTOM)
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

# GENERAR
if st.button("✨ GENERAR PROMPT", type="primary"):
    b = GrokVideoPromptBuilder()
    if st.session_state.uploaded_image_name:
        b.activate_img2video(st.session_state.uploaded_image_name, st.session_state.uploaded_end_frame_name)
    
    b.set_field('narrative_mode', narrative_mode)
    b.set_field('subject', final_sub)
    b.set_field('action', final_act)
    b.set_field('props', final_prop)
    b.set_field('wardrobe', final_ward)
    b.set_field('physics_medium', phy_med)
    b.set_field('physics_details', phy_det)
    b.set_field('env', final_env)
    b.set_field('style', sty)
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
    st.markdown("---")
    st.text_area("Copia tu Prompt:", value=st.session_state.generated_output, height=250)

# SUNO
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