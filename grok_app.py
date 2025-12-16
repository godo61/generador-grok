import streamlit as st
import re

# --- GESTIÓN DE DEPENDENCIAS ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Grok Production Studio", layout="wide", page_icon="🗣️")

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
        /* Estilo para el cajón de diálogo */
        .stTextArea textarea {{ border-left: 5px solid #FF4B4B !important; }}
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

# --- LISTAS GENERALES ---
DEMO_STYLES = [
    "Cinematic Film Still (Kodak Portra 800)", "Hyper-realistic VFX Render (Unreal 5)", 
    "National Geographic Wildlife Style", "Gritty Documentary Footage", 
    "Action Movie Screengrab", "Cyberpunk Digital Art", "Vintage VHS 90s"
]
DEMO_ENVIRONMENTS = [
    "✏️ Custom...", "🛶 Dusi River (Turbulent Rapids)", "🔴 Mars Surface (Red Dust)", 
    "🌌 Deep Space (Nebula Background)", "🚀 ISS Space Station Interior", 
    "🌊 Underwater Coral Reef", "❄️ Arctic Tundra (Snowstorm)", 
    "🏙️ Cyberpunk City (Neon Rain)", "🌲 Mystic Forest (Fog)"
]
DEMO_WARDROBE = ["✏️ Custom...", "torn sportswear and a cap", "tactical survival gear", "worn denim and leather jacket", "NASA EVA Spacesuit", "Tactical Wetsuit", "Elegant Suit"]
DEMO_LIGHTING = [
    "✏️ Custom...", "Harsh golden hour sunlight (long shadows)", "Dramatic low-key lighting (Chiaroscuro)", 
    "Soft overcast diffusion", "Neon City Glow (Blue/Pink)", "Stark Space Sunlight (No Fill)", 
    "Underwater Caustics", "Bioluminescence"
]
DEMO_ASPECT_RATIOS = ["21:9 (Cinematic)", "16:9 (Landscape)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]
DEMO_CAMERAS = [
    "✏️ Custom...", "Low angle, wide lens (looking up)", "Handheld dynamic shake (Chaos)", 
    "Telephoto compression (85mm, Bokeh)", "Drone follow Shot (High Angle)", 
    "GoPro POV (Fisheye)", "Underwater Housing (Split-level)"
]
DEMO_PROPS = ["None", "✏️ Custom...", "🛶 Kayak Paddle", "🎸 Electric Guitar", "🔫 Blaster", "📱 Datapad", "🔦 Flashlight"]

# --- LISTAS AUDIO & DIÁLOGO ---
DEMO_AUDIO_MOOD = ["✏️ Custom...", "Intense Suspense Score", "Epic Orchestral Swell", "Silent (breathing only)", "Horror Drone", "Upbeat Rock", "Synthwave"]
DEMO_AUDIO_ENV = ["✏️ Custom...", "No Background", "Mars Wind", "River Rapids Roar", "Space Station Hum", "City Traffic Rain", "Jungle Sounds"]
DEMO_SFX_COMMON = ["✏️ Custom...", "None", "Heavy breathing", "Footsteps on gravel", "Water splashing", "Explosion", "Laser blasts"]

VOICE_TYPES = ["✏️ Custom...", "Male (Deep)", "Female (Soft)", "Child", "Elderly", "Robot/AI", "Monster/Growl"]
VOICE_ACCENTS = ["✏️ Custom...", "American (Standard)", "British (RP)", "Spanish (Castilian)", "Mexican", "French Accent", "Russian Accent", "Neutral"]
VOICE_EMOTIONS = ["✏️ Custom...", "Neutral", "Angry / Shouting", "Sad / Crying", "Whispering / Secretive", "Happy / Excited", "Sarcastic", "Terrified", "Flirty"]

# --- FÍSICA ---
PHYSICS_LOGIC = {
    "Neutral / Estudio": [],
    "🌌 Espacio (Gravedad Cero)": ["Zero-G floating", "No air resistance", "Stark lighting", "Vacuum silence", "Floating debris"],
    "🔴 Marte (Gravedad Baja)": ["Low gravity movement", "Red dust storms", "Heat distortion", "Dust settling slowly"],
    "🌊 Agua (Superficie/Río)": ["Turbulent flow", "White water foam", "Wet fabric adhesion", "Reflections", "Water splashes on lens"],
    "🤿 Submarino (Profundidad)": ["Weightless suspension", "Light Caustics", "Rising bubbles", "Murky visibility", "Floating hair"],
    "❄️ Nieve / Hielo": ["Falling snow flakes", "Breath condensation (fog)", "Slippery movement", "Frost on lens"],
    "🌬️ Aire / Vuelo": ["High wind drag", "Fabric fluttering wildly", "Motion blur", "Aerodynamic trails"]
}

NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🏃 Persecución (Sujeto vs Monstruo)": "The subject is sprinting desperately towards the camera, face contorted in panic, looking back over shoulder. Behind them, a colossal creature is charging, kicking up debris.",
    "🧟 Transformación Súbita": "At second 0, the scene is static. Suddenly, the inanimate object behind the subject rapidly transforms into a massive, living threat. The subject reacts with sheer terror.",
    "😱 Reacción de Pánico": "Close-up on the subject's face as they realize the danger. Expression shifts from calm to screaming panic. They scramble backward, falling.",
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

        # 2. NARRATIVA
        narrative_block = []
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

        action_raw = p.get('action', '')
        enhance_mode = p.get('enhance_mode', False)
        
        if action_raw:
            if enhance_mode:
                intensifiers = "extreme motion blur on limbs, sweat flying, panic-stricken facial expression, dynamic chaos, hyper-detailed textures"
                narrative_block.append(f"VISCERAL ACTION SEQUENCE: {action_raw}. FEATURING: {intensifiers}.")
            else:
                narrative_block.append(f"ACTION: {action_raw}.")

        env = p.get('env_custom') or p.get('env', '')
        if "Custom" in env: env = ""
        if env: narrative_block.append(f"ENVIRONMENT: {env}.")

        prompt.append("\n".join(narrative_block))

        # 3. FÍSICA Y ATMÓSFERA
        atmosphere = []
        lit_val = p.get('light_custom') or p.get('light', '')
        if "Custom" in lit_val: lit_val = ""
        if lit_val: atmosphere.append(f"LIGHTING: {lit_val}")
        
        if p.get('physics_medium') and "Neutral" not in p['physics_medium']:
            dets = [d.split('(')[0].strip() for d in p.get('physics_details', [])]
            if dets: atmosphere.append(f"PHYSICS & ATMOSPHERE: {', '.join(dets)}")
            
        if atmosphere: prompt.append(". ".join(atmosphere) + ".")

        # 4. DIÁLOGO Y VOZ
        if p.get('dialogue_enabled'):
            dialogue_text = p.get('dialogue_text', '')
            if dialogue_text:
                voice_char = p.get('voice_char', 'Character')
                v_type = p.get('voice_type', '')
                if "Custom" in v_type: v_type = ""
                v_accent = p.get('voice_accent', '')
                if "Custom" in v_accent: v_accent = ""
                v_emotion = p.get('voice_emotion', '')
                if "Custom" in v_emotion: v_emotion = ""
                
                voice_desc = []
                if v_type: voice_desc.append(v_type)
                if v_accent: voice_desc.append(f"{v_accent} accent")
                if v_emotion: voice_desc.append(f"{v_emotion} tone")
                
                voice_str = f"({', '.join(voice_desc)})" if voice_desc else ""
                prompt.append(f"DIALOGUE / LIP SYNC: {voice_char} speaks: \"{dialogue_text}\" {voice_str}.")

        # 5. CINE
        cinema = []
        cam_val = p.get('camera_custom') or p.get('camera', '')
        if "Custom" in cam_val: cam_val = ""
        if cam_val: cinema.append(cam_val)
        if p.get('style'): cinema.append(f"STYLE: {p['style']}")
        if cinema: prompt.append(f"CINEMATOGRAPHY: {', '.join(cinema)}.")

        # 6. AUDIO
        audio_parts = []
        m_val = p.get('audio_mood_custom') or p.get('audio_mood')
        if m_val and "Custom" not in m_val: audio_parts.append(f"Music: {m_val}")
        e_val = p.get('audio_env_custom') or p.get('audio_env')
        if e_val and "Custom" not in e_val: audio_parts.append(f"Ambience: {e_val}")
        s_val = p.get('audio_sfx_custom') or p.get('audio_sfx')
        if s_val and "Custom" not in s_val and "None" not in s_val: audio_parts.append(f"SFX: {s_val.split('(')[0].strip()}")
        
        if audio_parts: prompt.append(f"SOUND DESIGN: {'. '.join(audio_parts)}.")

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
    tc, to = st.tabs(["👤 Cast", "🎸 Props"])
    with tc:
        c_n = st.text_input("Nombre Actor")
        c_d = st.text_area("Descripción", key="desc_actor_unique")
        if st.button("Guardar Actor"):
            if c_n and c_d:
                st.session_state.characters[c_n] = translate_to_english(c_d)
                st.success(f"Guardado: {c_n}")
                st.rerun()
    with to:
        o_n = st.text_input("Nombre Objeto")
        o_d = st.text_area("Descripción", key="desc_prop_unique")
        if st.button("Guardar Objeto"):
            if o_n and o_d:
                st.session_state.custom_props[o_n] = translate_to_english(o_d)
                st.success(f"Guardado: {o_n}")
                st.rerun()

    st.markdown("---")
    st.header("🖼️ Referencias")
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
st.title("🎬 Grok Production Studio (VFX Edition)")
enhance_mode = st.toggle("🔥 INTENSIFICADOR VFX (Añadir detalle visceral, blur, sudor...)", value=True)

t1, t2, t3, t4, t5 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cámara", "🎵 Audio & Voz"])

# VARS INIT
final_sub, final_act, final_ward, final_prop, final_env = "", "", "", "", ""
final_lit, final_cam = "", ""
mus_vid, env_vid, sfx_vid = "", "", ""
phy_med, phy_det = "Neutral / Estudio", []
dialogue_enabled = False
voice_char, voice_type, voice_accent, voice_emotion, dialogue_text = "", "", "", "", ""

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
    act_val = st.text_area("Describe la escena (Inglés o Español):", value=tpl_txt, height=100, placeholder="Ej: El elefante ataca...")
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
    with c1: phy_med = st.selectbox("Entorno Físico", list(PHYSICS_LOGIC.keys()))
    with c2: phy_det = st.multiselect("Detalles Activos", PHYSICS_LOGIC[phy_med])

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
    st.markdown("### 🎙️ Estudio de Voz y Diálogo")
    dialogue_enabled = st.toggle("🗣️ Habilitar Diálogo / Voiceover", value=False)
    
    if dialogue_enabled:
        with st.container(border=True):
            dc1, dc2 = st.columns(2)
            with dc1:
                voice_opts = ["Protagonista Actual", "Narrador / Voiceover"] + list(st.session_state.characters.keys())
                v_char_sel = st.selectbox("Personaje que habla", voice_opts)
                if v_char_sel == "Protagonista Actual": voice_char = "The Main Character"
                elif v_char_sel == "Narrador / Voiceover": voice_char = "Narrator"
                else: voice_char = v_char_sel

                v_type = st.selectbox("Tipo de Voz", VOICE_TYPES)
                if "Custom" in v_type: voice_type = translate_to_english(st.text_input("Tipo Voz Custom", key="vtc"))
                else: voice_type = v_type

            with dc2:
                v_acc = st.selectbox("Acento", VOICE_ACCENTS)
                if "Custom" in v_acc: voice_accent = translate_to_english(st.text_input("Acento Custom", key="vac"))
                else: voice_accent = v_acc

                v_emo = st.selectbox("Emoción", VOICE_EMOTIONS)
                if "Custom" in v_emo: voice_emotion = translate_to_english(st.text_input("Emoción Custom", key="vec"))
                else: voice_emotion = v_emo
            
            d_txt = st.text_area("Guion / Diálogo:", placeholder="Escribe aquí el diálogo exacto...")
            dialogue_text = translate_to_english(d_txt)

    st.markdown("---")
    st.markdown("### 🎵 Diseño Sonoro (Música & SFX)")
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
    b.set_field('dialogue_enabled', dialogue_enabled)
    b.set_field('dialogue_text', dialogue_text)
    b.set_field('voice_char', voice_char)
    b.set_field('voice_type', voice_type)
    b.set_field('voice_accent', voice_accent)
    b.set_field('voice_emotion', voice_emotion)
    
    res = b.build()
    st.session_state.generated_output = res
    st.session_state.history.append(res)

if st.session_state.generated_output:
    st.markdown("---")
    st.subheader("📝 Prompt Final")
    final_editable = st.text_area("Editar:", value=st.session_state.generated_output, height=350)
    st.code(st.session_state.generated_output, language="text")

# --- SUNO AI AUDIO STATION (V41 UPGRADE) ---
st.markdown("---")
with st.expander("🎹 SUNO AI Audio Station", expanded=False):
    st.info("Generador de Prompts optimizado para Suno v3.5 / v4")
    
    suno_col1, suno_col2 = st.columns(2)
    
    with suno_col1:
        suno_instrumental = st.toggle("🎻 Instrumental", value=False, key="suno_instr_toggle")
        
        # Lógica de Duración (Mapeada a Estructura)
        suno_duration = st.slider("Duración Estimada", 30, 240, 120, step=30, format="%d seg", key="suno_dur")
        
        # Traducir duración a estructura sugerida
        if suno_duration <= 45:
            struct_suggestion = "[Intro] [Short Hook] [Outro]"
        elif suno_duration <= 90:
            struct_suggestion = "[Intro] [Verse] [Chorus] [Outro]"
        else:
            struct_suggestion = "[Intro] [Verse] [Chorus] [Bridge] [Chorus] [Outro]"
            
    with suno_col2:
        suno_genre = st.text_input("Estilo / Género", placeholder="Cyberpunk, Lo-Fi, Epic Orchestral...", key="suno_gen")
        suno_mood = st.text_input("Mood / Atmósfera", placeholder="Dark, Tense, Uplifting...", key="suno_mood")

    # Cajón de Letras (Solo si no es instrumental)
    suno_lyrics = ""
    if not suno_instrumental:
        suno_lyrics = st.text_area("Letra / Tema (Topic)", placeholder="Escribe la letra o describe el tema de la canción...", key="suno_lyr")

    if st.button("🎵 GENERAR PROMPT SUNO", key="btn_suno"):
        # Construcción del Prompt Suno
        meta_tags = []
        if suno_instrumental: meta_tags.append("[Instrumental]")
        if suno_genre: meta_tags.append(f"[{translate_to_english(suno_genre)}]")
        if suno_mood: meta_tags.append(f"[{translate_to_english(suno_mood)}]")
        
        # Construir salida
        final_suno = f"Style Prompts: {' '.join(meta_tags)}\n\n"
        final_suno += f"Structure Suggestion:\n{struct_suggestion}\n\n"
        
        if not suno_instrumental and suno_lyrics:
            eng_lyrics = translate_to_english(suno_lyrics)
            final_suno += f"Lyrics / Topic:\n[Verse]\n{eng_lyrics}\n\n[Chorus]\n..."
        
        st.code(final_suno, language="text")