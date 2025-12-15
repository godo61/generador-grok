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
        bg_color, text_color, tab_bg, tab_active_bg, tab_border = "#0E1117", "#FAFAFA", "#1E1E24", "#0E1117", "#333333"
    else:
        bg_color, text_color, tab_bg, tab_active_bg, tab_border = "#FFFFFF", "#31333F", "#F0F2F6", "#FFFFFF", "#E0E0E0"

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background-color: {bg_color}; color: {text_color}; }}
        [data-testid="stSidebar"] {{ background-color: {tab_bg}; }}
        textarea {{ font-size: 1.1rem !important; font-family: monospace !important; }}
        [data-testid="sttoggle"] span {{ font-weight: bold; color: #FF4B4B; }}
        </style>
    """, unsafe_allow_html=True)

# --- DATOS MAESTROS ---
DEFAULT_CHARACTERS = {
    "TON (Base)": "a striking male figure (185cm), razor-sharp jawline, textured modern quiff hair, athletic build",
    "FREYA (Base)": "a statuesque female survivor, intense hazel eyes, wet skin texture, strong features",
}
DEFAULT_PROPS = {
    "Guitarra": "a vintage electric guitar",
    "Kayak": "a carbon fiber sea kayak",
    "Linterna Táctica": "a high-lumen tactical flashlight"
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

# --- LISTAS COMPLETAS (RESTAURADAS) ---
DEMO_STYLES = [
    "Cinematic Film Still (Kodak Portra 800)", "Hyper-realistic VFX Render (Unreal 5)", 
    "National Geographic Wildlife Style", "Gritty Documentary Footage", 
    "Action Movie Screengrab", "Cyberpunk Digital Art", "Vintage VHS 90s"
]

# ENTORNOS RESTAURADOS
DEMO_ENVIRONMENTS = [
    "✏️ Custom...", 
    "🛶 Dusi River (Turbulent Rapids)", 
    "🔴 Mars Surface (Red Dust)", 
    "🌌 Deep Space (Nebula Background)", 
    "🚀 ISS Space Station Interior", 
    "🌊 Underwater Coral Reef", 
    "❄️ Arctic Tundra (Snowstorm)", 
    "🏙️ Cyberpunk City (Neon Rain)", 
    "🌲 Mystic Forest (Fog)"
]

DEMO_WARDROBE = ["✏️ Custom...", "torn sportswear and a cap", "tactical survival gear", "worn denim and leather jacket", "NASA EVA Spacesuit", "Tactical Wetsuit", "Elegant Suit"]

# ILUMINACIÓN RESTAURADA
DEMO_LIGHTING = [
    "✏️ Custom...",
    "Harsh golden hour sunlight (long shadows)", 
    "Dramatic low-key lighting (Chiaroscuro)", 
    "Soft overcast diffusion", 
    "Neon City Glow (Blue/Pink)", 
    "Stark Space Sunlight (No Fill)", 
    "Underwater Caustics",
    "Bioluminescence"
]

DEMO_ASPECT_RATIOS = ["21:9 (Cinematic)", "16:9 (Landscape)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

# CÁMARAS RESTAURADAS
DEMO_CAMERAS = [
    "✏️ Custom...",
    "Low angle, wide lens (looking up)", 
    "Handheld dynamic shake (Chaos)", 
    "Telephoto compression (85mm, Bokeh)", 
    "Drone follow Shot (High Angle)", 
    "GoPro POV (Fisheye)", 
    "Underwater Housing (Split-level)"
]

DEMO_PROPS = ["None", "✏️ Custom...", "🛶 Kayak Paddle", "🎸 Electric Guitar", "🔫 Blaster", "📱 Datapad", "🔦 Flashlight"]

# AUDIO CUSTOM RESTAURADO
DEMO_AUDIO_MOOD = ["✏️ Custom...", "Intense Suspense Score", "Epic Orchestral Swell", "Silent (breathing only)", "Horror Drone", "Upbeat Rock", "Synthwave"]
DEMO_AUDIO_ENV = ["✏️ Custom...", "No Background", "Mars Wind", "River Rapids Roar", "Space Station Hum", "City Traffic Rain", "Jungle Sounds"]
DEMO_SFX_COMMON = ["✏️ Custom...", "None", "Heavy breathing", "Footsteps on gravel", "Water splashing", "Explosion", "Laser blasts"]

# FÍSICA COMPLETA (RESTAURADA)
PHYSICS_LOGIC = {
    "Neutral / Estudio": [],
    "🌌 Espacio (Gravedad Cero)": ["Zero-G floating", "No air resistance", "Stark lighting", "Vacuum silence", "Floating debris"],
    "🔴 Marte (Gravedad Baja)": ["Low gravity movement", "Red dust storms", "Heat distortion", "Dust settling slowly"],
    "🌊 Agua (Superficie/Río)": ["Turbulent flow", "White water foam", "Wet fabric adhesion", "Reflections", "Water splashes on lens"],
    "🤿 Submarino (Profundidad)": ["Weightless suspension", "Light Caustics", "Rising bubbles", "Murky visibility", "Floating hair"],
    "❄️ Nieve / Hielo": ["Falling snow flakes", "Breath condensation (fog)", "Slippery movement", "Frost on lens"],
    "🌬️ Aire / Vuelo": ["High wind drag", "Fabric fluttering wildly", "Motion blur", "Aerodynamic trails"]
}

# PLANTILLAS NARRATIVAS
NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🏃 Persecución (Sujeto vs Monstruo)": "The subject is sprinting desperately towards the camera, face contorted in panic, looking back over shoulder. Behind them, a colossal creature is charging, kicking up debris.",
    "🧟 Transformación Súbita": "At second 0, the scene is static. Suddenly, the inanimate object behind the subject rapidly transforms into a massive, living threat. The subject reacts with sheer terror.",
    "😱 Reacción de Pánico": "Close-up on the subject's face as they realize the danger. Expression shifts from calm to screaming panic. They scramble backward, falling.",
    "🚀 Despegue / Lanzamiento": "Smoke fills the frame. The subject looks up in awe as a massive structure begins to lift off. Debris flies everywhere. Intense vibration.",
    "🌊 Acción en el Agua": "The subject battles against the raging current. Water crashes over them. They gasp for air, paddling desperately to stay afloat."
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
        prompt = []

        # 1. CABECERA
        if self.is_img2video:
            prompt.append(f"Start Frame: '{self.image_filename}'.")
            if self.end_image_filename: prompt.append(f"End Frame: '{self.end_image_filename}'.")
            prompt.append("Maintain strict visual consistency with references.")

        # 2. NARRATIVA & VFX ENHANCER
        narrative_block = []
        
        # Sujeto
        subject = p.get('subject', '')
        wardrobe = p.get('wardrobe_custom') or p.get('wardrobe', '')
        if "Custom" in wardrobe: wardrobe = ""
        props = p.get('props_custom') or p.get('props', '')
        if "Custom" in props or "None" in props: props = ""
        
        subject_details = []
        if subject: subject_details.append(subject)
        if wardrobe: subject_details.append(f"wearing {wardrobe}")
        if props: subject_details.append(f"holding {props}")
        
        if subject_details:
            narrative_block.append(f"MAIN SUBJECT: {', '.join(subject_details)}.")

        # Acción
        action_raw = p.get('action', '')
        enhance_mode = p.get('enhance_mode', False)
        
        if action_raw:
            if enhance_mode:
                intensifiers = "extreme motion blur on limbs, sweat flying, panic-stricken facial expression, dynamic chaos, hyper-detailed textures"
                narrative_block.append(f"VISCERAL ACTION SEQUENCE: {action_raw}. FEATURING: {intensifiers}.")
            else:
                narrative_block.append(f"ACTION: {action_raw}.")

        # Entorno
        env = p.get('env_custom') or p.get('env', '')
        if "Custom" in env: env = ""
        if env: narrative_block.append(f"ENVIRONMENT: {env}.")

        prompt.append("\n".join(narrative_block))

        # 3. FÍSICA Y ATMÓSFERA
        atmosphere = []
        
        # Luz
        lit_val = p.get('light_custom') or p.get('light', '')
        if "Custom" in lit_val: lit_val = ""
        if lit_val: atmosphere.append(f"LIGHTING: {lit_val}")
        
        # Física
        if p.get('physics_medium') and "Neutral" not in p['physics_medium']:
            dets = [d.split('(')[0].strip() for d in p.get('physics_details', [])]
            if dets: atmosphere.append(f"PHYSICS & ATMOSPHERE: {', '.join(dets)}")
            
        if atmosphere: prompt.append(". ".join(atmosphere) + ".")

        # 4. CINE
        cinema = []
        cam_val = p.get('camera_custom') or p.get('camera', '')
        if "Custom" in cam_val: cam_val = ""
        if cam_val: cinema.append(cam_val)
        
        if p.get('style'): cinema.append(f"STYLE: {p['style']}")
        if cinema: prompt.append(f"CINEMATOGRAPHY: {', '.join(cinema)}.")

        # 5. AUDIO
        audio_parts = []
        m_val = p.get('audio_mood_custom') or p.get('audio_mood')
        if m_val and "Custom" not in m_val: audio_parts.append(f"Music: {m_val}")
        
        e_val = p.get('audio_env_custom') or p.get('audio_env')
        if e_val and "Custom" not in e_val: audio_parts.append(f"Ambience: {e_val}")

        s_val = p.get('audio_sfx_custom') or p.get('audio_sfx')
        if s_val and "Custom" not in s_val and "None" not in s_val: audio_parts.append(f"SFX: {s_val.split('(')[0].strip()}")
        
        if audio_parts: prompt.append(f"AUDIO: {'. '.join(audio_parts)}.")

        if p.get('ar'): prompt.append(f"--ar {p['ar'].split(' ')[0]}")

        return "\n\n".join(prompt)

# --- INTERFAZ ---
with st.sidebar:
    st.title("🔥 Config VFX")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    if st.button("🔄 Restaurar Fábrica"):
        st.session_state.characters = DEFAULT_CHARACTERS.copy()
        st.session_state.custom_props = DEFAULT_PROPS.copy()
        st.rerun()
    
    st.header("🧬 Activos")
    st.info("Para crear uno NUEVO: Escribe el nombre y dale a guardar. Para EDITAR: Escribe el nombre de uno existente.")
    
    tc, to = st.tabs(["👤 Cast", "🎸 Props"])
    with tc:
        c_n = st.text_input("Nombre Actor")
        c_d = st.text_area("Descripción")
        if st.button("Guardar Actor"):
            if c_n and c_d:
                st.session_state.characters[c_n] = translate_to_english(c_d)
                st.success(f"Actor '{c_n}' guardado.")
                st.rerun()
    with to:
        o_n = st.text_input("Nombre Objeto")
        o_d = st.text_area("Descripción Visual")
        if st.button("Guardar Objeto"):
            if o_n and o_d:
                st.session_state.custom_props[o_n] = translate_to_english(o_d)
                st.success(f"Objeto '{o_n}' guardado.")
                st.rerun()

    st.markdown("---")
    st.header("🖼️ Referencias")
    u_file = st.file_uploader("Start Frame", type=["jpg", "png"])
    if u_file:
        st.session_state.uploaded_image_name = u_file.name
        st.image(u_file, caption="Inicio")
    else: st.session_state.uploaded_image_name = None
    
    u_end = st.file_uploader("End Frame (Opcional)", type=["jpg", "png"])
    if u_end:
        st.session_state.uploaded_end_frame_name = u_end.name
        st.image(u_end, caption="Final")
    else: st.session_state.uploaded_end_frame_name = None

# --- PANEL PRINCIPAL ---
st.title("🎬 Grok Production Studio (VFX Edition)")
enhance_mode = st.toggle("🔥 INTENSIFICADOR VFX (Añadir detalle visceral, blur, sudor...)", value=True)

# PESTAÑAS (COMPLETAS)
t1, t2, t3, t4, t5 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cámara", "🎵 Audio"])

# VARS
final_sub, final_act, final_ward, final_prop, final_env = "", "", "", "", ""
final_lit, final_cam = "", ""
mus_vid, env_vid, sfx_vid = "", "", ""
phy_med, phy_det = "Neutral / Estudio", []

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        char_opts = list(st.session_state.characters.keys())
        if st.session_state.uploaded_image_name: char_opts.insert(0, "📷 Sujeto de la Foto (Usar Referencia)")
        char_sel = st.selectbox("Protagonista", char_opts)
        final_sub = "" if "📷" in char_sel else st.session_state.characters[char_sel]
    
    with c_b:
        tpl = st.selectbox("Plantilla de Guion (Opcional)", list(NARRATIVE_TEMPLATES.keys()))
        tpl_txt = NARRATIVE_TEMPLATES[tpl]

    st.markdown("##### 📜 Descripción de la Acción")
    act_val = st.text_area("Describe la escena (Inglés o Español):", 
                          value=tpl_txt, 
                          height=100, 
                          placeholder="Ej: El elefante se levanta y ataca, el sujeto corre aterrorizado...")
    final_act = translate_to_english(act_val)

with t2:
    c1, c2 = st.columns(2)
    with c1:
        e_sel = st.selectbox("Entorno", DEMO_ENVIRONMENTS)
        if "Custom" in e_sel: final_env = translate_to_english(st.text_input("Lugar Custom", key="lc"))
        else: final_env = e_sel
        
        all_props = ["None", "✏️ Custom..."] + list(st.session_state.custom_props.keys()) + DEMO_PROPS[2:]
        p_sel = st.selectbox("Objeto", all_props)
        if p_sel in st.session_state.custom_props: final_prop = st.session_state.custom_props[p_sel]
        elif "Custom" in p_sel: final_prop = translate_to_english(st.text_input("Objeto Nuevo", key="np"))
        elif "None" not in p_sel: final_prop = p_sel

    with c2:
        w_sel = st.selectbox("Vestuario", DEMO_WARDROBE)
        if "Custom" in w_sel: final_ward = translate_to_english(st.text_input("Ropa Custom", key="wc"))
        else: final_ward = w_sel

with t3:
    st.markdown("##### ⚛️ Simulación Física")
    c1, c2 = st.columns(2)
    with c1:
        phy_med = st.selectbox("Entorno Físico", list(PHYSICS_LOGIC.keys()))
    with c2:
        phy_det = st.multiselect("Detalles Activos", PHYSICS_LOGIC[phy_med])

with t4:
    c1, c2, c3 = st.columns(3)
    with c1: 
        cam_sel = st.selectbox("Cámara", DEMO_CAMERAS)
        if "Custom" in cam_sel: final_cam = translate_to_english(st.text_input("Cámara Custom", key="cc"))
        else: final_cam = cam_sel
    with c2: 
        lit_sel = st.selectbox("Iluminación", DEMO_LIGHTING)
        if "Custom" in lit_sel: final_lit = translate_to_english(st.text_input("Luz Custom", key="ll"))
        else: final_lit = lit_sel
    with c3: 
        sty = st.selectbox("Estilo", DEMO_STYLES)
        ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS)

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

# GENERAR
if st.button("✨ GENERAR PROMPT PRO", type="primary"):
    b = GrokVideoPromptBuilder()
    if st.session_state.uploaded_image_name:
        b.activate_img2video(st.session_state.uploaded_image_name, st.session_state.uploaded_end_frame_name)
    
    b.set_field('enhance_mode', enhance_mode)
    b.set_field('subject', final_sub)
    b.set_field('action', final_act)
    b.set_field('wardrobe', final_ward)
    b.set_field('props', final_prop)
    b.set_field('env', final_env)
    b.set_field('physics_medium', phy_med)
    b.set_field('physics_details', phy_det)
    b.set_field('camera', final_cam)
    b.set_field('light', final_lit)
    b.set_field('style', sty)
    b.set_field('ar', ar)
    b.set_field('audio_mood', mus_vid)
    b.set_field('audio_env', env_vid)
    b.set_field('audio_sfx', sfx_vid)
    
    res = b.build()
    st.session_state.generated_output = res
    st.session_state.history.append(res)

if st.session_state.generated_output:
    st.markdown("---")
    st.subheader("📝 Prompt Final")
    final_editable = st.text_area("Editar:", value=st.session_state.generated_output, height=350)
    st.code(st.session_state.generated_output, language="text")

# SUNO
st.markdown("---")
with st.expander("🎹 SUNO AI Audio Station", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        s_gen = st.selectbox("Género", ["Cinematic", "Cyberpunk", "Rock", "Lo-Fi", "Custom..."])
        if s_gen == "Custom...": s_gen = st.text_input("Género Custom")
    with c2:
        s_str = st.selectbox("Estructura", ["Intro", "Loop", "Outro", "Build-up"])
        s_bpm = st.slider("BPM", 60, 180, 120)
    with c3:
        s_moo = st.text_input("Mood", placeholder="Epic, Sad, Tense...")
        s_ins = st.text_input("Instrumentos", placeholder="Violin, Synth...")

    if st.button("🎵 GENERAR SUNO"):
        mo = translate_to_english(s_moo)
        ins = translate_to_english(s_ins)
        st.code(f"[{s_str}] [{s_gen}] [{s_bpm} BPM]\n{mo} atmosphere. Featuring {ins}.", language="text")