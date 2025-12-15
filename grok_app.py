import streamlit as st
import re

# --- GESTIÓN DE DEPENDENCIAS ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Grok Video Builder Pro", layout="wide", page_icon="🎬")

# --- 🎨 ESTILOS CSS PERSONALIZADOS (UI MASTER) ---
def apply_custom_styles(dark_mode=False):
    # Colores base según el modo
    if dark_mode:
        bg_color = "#0E1117"
        text_color = "#FAFAFA"
        tab_bg = "#262730"
        tab_active_bg = "#0E1117"
        tab_border = "#41444C"
    else:
        bg_color = "#FFFFFF"
        text_color = "#31333F"
        tab_bg = "#F0F2F6"
        tab_active_bg = "#FFFFFF"
        tab_border = "#E0E0E0"

    st.markdown(f"""
        <style>
        /* 1. FORZAR MODO CLARO/OSCURO GLOBALMENTE */
        [data-testid="stAppViewContainer"] {{
            background-color: {bg_color};
            color: {text_color};
        }}
        [data-testid="stSidebar"] {{
            background-color: {tab_bg};
        }}
        [data-testid="stHeader"] {{
            background-color: {bg_color};
        }}
        
        /* 2. ESTILO "SOLAPAS DE CUADERNO" (NOTEBOOK TABS) */
        /* Contenedor de las pestañas */
        div[data-baseweb="tab-list"] {{
            gap: 8px; /* Espacio entre solapas */
            border-bottom: 2px solid {tab_border};
            padding-bottom: 0px;
        }}

        /* Cada solapa individual (inactiva) */
        button[data-baseweb="tab"] {{
            background-color: {tab_bg} !important;
            border-radius: 15px 15px 0px 0px !important; /* Redondeado superior */
            border: 1px solid {tab_border} !important;
            border-bottom: none !important;
            padding: 10px 20px !important;
            margin-bottom: -2px !important; /* Para solapar con la línea de abajo */
            transition: all 0.3s ease;
            color: {text_color} !important;
            opacity: 0.7;
        }}

        /* Solapa Activa (Seleccionada) */
        button[data-baseweb="tab"][aria-selected="true"] {{
            background-color: {tab_active_bg} !important;
            border-top: 4px solid #FF4B4B !important; /* Acento rojo Streamlit */
            border-left: 1px solid {tab_border} !important;
            border-right: 1px solid {tab_border} !important;
            font-weight: bold !important;
            opacity: 1;
            z-index: 99;
        }}
        
        /* Ajuste de textos en modo oscuro */
        p, h1, h2, h3, li {{
            color: {text_color} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- MEMORIA ---
if 'history' not in st.session_state: st.session_state.history = []
if 'uploaded_image_name' not in st.session_state: st.session_state.uploaded_image_name = None
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""

# --- PERSONAJES ---
if 'characters' not in st.session_state:
    st.session_state.characters = {
        "Nada (Generar nuevo)": "",
        "TON (Base)": """A hyper-realistic, medium-shot portrait of a striking male figure (185cm, 75kg), elegant verticality and lean muscularity. High cheekbones, sharp geometric jawline, faint skin porosity, groomed five o'clock shadow. Modern textured quiff hair, dark chestnut. Cinematic lighting.""",
        "FREYA (Base)": """A hyper-realistic cinematic shot of a 25-year-old female survivor, statuesque athletic physique (170cm, 60kg). Striking symmetrical face, sharp jawline, intense hazel eyes. Wet skin texture, visible pores. Heavy dark brunette hair.""",
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

# --- INTERFAZ LATERAL (CONTROL DE TEMA) ---
with st.sidebar:
    st.title("⚙️ Configuración")
    # INTERRUPTOR DE MODO OSCURO
    is_dark_mode = st.toggle("🌙 Modo Oscuro", value=False)
    
    # APLICAR ESTILOS AHORA
    apply_custom_styles(dark_mode=is_dark_mode)

    st.markdown("---")
    st.header("🧬 Mis Personajes")
    with st.expander("Nuevo Personaje"):
        new_name = st.text_input("Nombre")
        new_desc = st.text_area("Descripción Base")
        if st.button("Guardar"):
            if new_name and new_desc:
                st.session_state.characters[new_name] = translate_to_english(new_desc)
                st.success("Guardado")
    
    st.markdown("---")
    st.header("🖼️ Imagen Base")
    uploaded_file = st.file_uploader("Sube referencia...", type=["jpg", "png"])
    if uploaded_file:
        st.session_state.uploaded_image_name = uploaded_file.name
        st.image(uploaded_file, caption="Referencia Activa")
    else:
        st.session_state.uploaded_image_name = None
    
    st.markdown("---")
    st.header("📜 Historial")
    for i, item in enumerate(reversed(st.session_state.history[:5])):
        st.text_area(f"Prompt {len(st.session_state.history)-i}", item, height=80, key=f"h{i}")

# --- LISTAS DE ACTIVOS ---
DEMO_STYLES = ["Photorealistic 8k", "Cinematic", "IMAX Quality", "Anime", "3D Render (Octane)", "Vintage VHS", "Cyberpunk", "Film Noir"]
DEMO_ENVIRONMENTS = ["✏️ Custom / Other...", "🔴 Mars Surface (Red Planet)", "🛶 Dusi River (South Africa)", "🚀 International Space Station", "🌌 Deep Space Void", "🌲 Mystic Forest", "🏙️ Cyberpunk City", "🏜️ Sahara Desert", "🏟️ Olympic Stadium"]
DEMO_WARDROBE = ["✏️ Custom / Other...", "👨‍🚀 NASA EVA Spacesuit", "👽 Sci-Fi Sleek Spacesuit", "🛶 Kayaking Gear", "🤿 Neoprene Wetsuit", "👕 Casual (T-shirt & Jeans)", "🤵 Formal Suit", "🎸 Rock Star Outfit"]
DEMO_PROPS = ["None", "✏️ Custom / Other...", "🛶 Carbon Fiber Kayak Paddle", "🎸 Electric Guitar", "🎤 Vintage Microphone", "🔫 Sci-Fi Blaster", "📱 Holographic Datapad", "🧪 Glowing Vial", "☕ Coffee Cup"]
DEMO_LIGHTING = ["Natural Daylight", "Cinematic / Dramatic", "Cyberpunk / Neon", "Studio Lighting", "Golden Hour", "Low Key / Dark", "Stark Space Sunlight"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "9:16 (Portrait)", "21:9 (Ultrawide)", "1:1 (Square)"]
DEMO_CAMERAS = ["Static", "Zoom In/Out", "Dolly In/Out", "Truck Left/Right", "Orbit", "Handheld / Shake", "FPV Drone", "Zero-G Floating Cam"]
DEMO_AUDIO_MOOD = ["No Music", "Cinematic Orchestral", "Sci-Fi Synth", "Tribal Drums", "Suspense", "Upbeat", "Silence (Space)", "✏️ Custom..."]
DEMO_AUDIO_ENV = ["No Background", "Mars Wind", "River Rapids", "Space Station Hum", "City Traffic", "✏️ Custom..."]
DEMO_SFX_COMMON = ["None", "Thrusters firing", "Water splashing", "Paddle hitting water", "Breathing in helmet", "Radio comms beep", "Footsteps", "✏️ Custom..."]

# --- ⚛️ MOTOR DE FÍSICA ---
PHYSICS_LOGIC = {
    "Neutral / None": [],
    "🌌 Space (Zero-G / Void)": ["Zero-gravity floating objects/hair", "No air resistance", "High contrast stark lighting", "Deep black shadows", "Vacuum silence atmosphere", "Floating dust particles"],
    "🔴 Mars / Planetary (Low G)": ["Low gravity movement (Slow jumps)", "Red dust storms", "Haze and heat distortion", "Fine dust settling on surfaces", "Wind sweeping across barren terrain"],
    "🌊 Water (Surface/River)": ["Turbulent muddy water flow", "White water rapids foam", "Hydrodynamic splashes", "Wet fabric adhesion", "Light refraction on ripples"],
    "🤿 Underwater (Submerged)": ["Weightless suspension", "Caustics light patterns", "Rising bubbles", "Murky depth visibility", "Muffled movement"],
    "🌬️ Air / Flight": ["High velocity wind drag", "Clouds passing rapidly", "Fabric fluttering violently", "Motion blur", "Aerodynamic trails"],
    "❄️ Snow / Ice": ["Condensation breath", "Deep snow footprints", "Falling snow flakes", "Ice reflection", "Pale lighting"]
}

# --- MOTOR DE PROMPTS ---
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
        
        # --- PROCESAMIENTO CUSTOM ---
        wardrobe_txt = p.get('wardrobe_custom') if p.get('wardrobe_custom') else (p['wardrobe'].split('(')[0].strip() if p.get('wardrobe') and "Custom" not in p['wardrobe'] else "")
        props_txt = p.get('props_custom') if p.get('props_custom') else (p['props'].split('(')[0].strip() if p.get('props') and "None" not in p['props'] and "Custom" not in p['props'] else "")
        env_txt = p.get('env_custom') if p.get('env_custom') else (p['env'].split('(')[0].strip() if p.get('env') and "Custom" not in p['env'] else "")

        # --- AUDIO ---
        audio_parts = []
        m_val = p.get('audio_mood_custom') if p.get('audio_mood_custom') else p.get('audio_mood')
        if m_val and "No Music" not in m_val and "Custom" not in m_val: audio_parts.append(f"Music: {m_val}")

        e_val = p.get('audio_env_custom') if p.get('audio_env_custom') else p.get('audio_env')
        if e_val and "No Background" not in e_val and "Custom" not in e_val: audio_parts.append(f"Ambience: {e_val}")

        s_val = p.get('audio_sfx_custom') if p.get('audio_sfx_custom') else p.get('audio_sfx')
        if s_val and "None" not in s_val and "Custom" not in s_val:
            clean_sfx = s_val.split('(')[0].strip()
            audio_parts.append(f"SFX: {clean_sfx}")
        
        final_audio = ". ".join(audio_parts)

        # --- FÍSICA ---
        physics_prompt = ""
        if p.get('physics_medium') and "Neutral" not in p['physics_medium']:
            medium = p['physics_medium'].split('(')[0].strip()
            details = [d.split('(')[0].strip() for d in p.get('physics_details', [])]
            if details: physics_prompt = f"Physics Engine: {medium} simulation ({', '.join(details)})"

        # --- CONSTRUCCIÓN ---
        segments = []
        if self.is_img2video:
            segments.append(f"Image-to-Video based on '{self.image_filename}'.")
            keep = []
            if p.get('keep_subject'): keep.append("Main Subject")
            if p.get('keep_bg'): keep.append("Background")
            if keep: segments.append(f"Maintain: {', '.join(keep)}.")
            if p.get('img_action'): segments.append(f"Action: {p['img_action']}")
        else:
            base_subj = p.get('subject', '')
            if wardrobe_txt: base_subj += f", wearing {wardrobe_txt}"
            if props_txt: base_subj += f", holding/using {props_txt}"
            if p.get('details'): base_subj += f", {p['details']}"

            visual_block = []
            if base_subj: visual_block.append(base_subj)
            if p.get('action'): visual_block.append(f"Action: {p['action']}")
            if env_txt: visual_block.append(f"Location: {env_txt}")
            
            scene = ". ".join(visual_block)
            if scene: segments.append(scene + ".")
            if p.get('style'): segments.append(f"Style: {p['style']}.")

        if p.get('light'): segments.append(f"Lighting: {p['light']}.")
        if p.get('camera'): segments.append(f"Camera: {p['camera']}.")
        if physics_prompt: segments.append(physics_prompt + ".")
        if final_audio: segments.append(f"Audio: {final_audio}.")
        if p.get('ar'): segments.append(f"--ar {p['ar'].split(' ')[0]}")

        return re.sub(' +', ' ', " ".join(segments)).strip()

# PANEL PRINCIPAL
st.title("🎬 Grok Video Builder")

if st.session_state.uploaded_image_name:
    # MODO IMAGEN
    st.info(f"Modo Imagen: {st.session_state.uploaded_image_name}")
    t1, t2, t3, t4 = st.tabs(["🖼️ Acción", "⚛️ Física", "🎥 Técnica", "🎵 Audio"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            keep_s = st.checkbox("Mantener Sujeto", True)
            keep_b = st.checkbox("Mantener Fondo", True)
        with c2: act_img = st.text_area("Acción", placeholder="Ej: flotando en gravedad cero")

    with t2:
        phy_med = st.selectbox("Medio Físico", list(PHYSICS_LOGIC.keys()), key="pm_i")
        phy_det = st.multiselect("Efectos", PHYSICS_LOGIC[phy_med], key="pd_i")

    with t3:
        c1, c2, c3 = st.columns(3)
        with c1: cam = st.selectbox("Cámara", DEMO_CAMERAS, key="c_i")
        with c2: lit = st.selectbox("Luz", DEMO_LIGHTING, key="l_i")
        with c3: ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS, key="a_i")

    with t4:
        c1, c2, c3 = st.columns(3)
        with c1: 
            m_ch = st.selectbox("Música", DEMO_AUDIO_MOOD, key="m_i")
            mus_custom_val = translate_to_english(st.text_input("Cuál:", key="mc_i")) if "Custom" in m_ch else ""
        with c2:
            e_ch = st.selectbox("Ambiente", DEMO_AUDIO_ENV, key="e_i")
            env_custom_val = translate_to_english(st.text_input("Cuál:", key="ec_i")) if "Custom" in e_ch else ""
        with c3:
            s_ch = st.selectbox("SFX", DEMO_SFX_COMMON, key="s_i")
            sfx_custom_val = translate_to_english(st.text_input("Cuál:", key="sc_i")) if "Custom" in s_ch else ""

    if st.button("✨ GENERAR (IMG)", type="primary"):
        with st.spinner("Creando..."):
            try:
                b = GrokVideoPromptBuilder()
                b.activate_img2video(st.session_state.uploaded_image_name)
                b.set_field('keep_subject', keep_s)
                b.set_field('keep_bg', keep_b)
                b.set_field('img_action', translate_to_english(act_img))
                b.set_field('physics_medium', phy_med)
                b.set_field('physics_details', phy_det)
                b.set_field('camera', cam)
                b.set_field('light', lit)
                b.set_field('ar', ar)
                
                b.set_field('audio_mood', m_ch)
                b.set_field('audio_mood_custom', mus_custom_val)
                b.set_field('audio_env', e_ch)
                b.set_field('audio_env_custom', env_custom_val)
                b.set_field('audio_sfx', s_ch)
                b.set_field('audio_sfx_custom', sfx_custom_val)
                
                res = b.build()
                st.session_state.generated_output = res
                st.session_state.history.append(res)
            except Exception as e: st.error(str(e))

else:
    # MODO TEXTO / HISTORIA
    t1, t2, t3, t4, t5 = st.tabs(["📝 Historia & Assets", "⚛️ Física", "🎨 Visual", "🎥 Técnica", "🎵 Audio"])
    
    # Declaramos variables custom vacías
    ward_custom_val = ""
    props_custom_val = ""
    env_custom_txt = ""
    
    with t1:
        st.subheader("Protagonista")
        char_sel = st.selectbox("Actor Base", list(st.session_state.characters.keys()))
        final_sub = st.session_state.characters[char_sel] if st.session_state.characters[char_sel] else translate_to_english(st.text_input("Sujeto Base"))
        
        st.subheader("Vestuario y Atrezzo (Assets)")
        c1, c2 = st.columns(2)
        with c1:
            w_ch = st.selectbox("Vestuario (Wardrobe)", DEMO_WARDROBE)
            if "Custom" in w_ch:
                ward_custom_val = translate_to_english(st.text_input("Describe Ropa", key="wc_t"))
        with c2:
            p_ch = st.selectbox("Objeto (Prop)", DEMO_PROPS)
            if "Custom" in p_ch:
                props_custom_val = translate_to_english(st.text_input("Describe Objeto", key="pc_t"))

        st.subheader("Acción")
        act = st.text_input("¿Qué está haciendo?", placeholder="Ej: caminando hacia el cohete")
        det = st.text_input("Detalles extra")

    with t2:
        phy_med = st.selectbox("Entorno Físico", list(PHYSICS_LOGIC.keys()), key="pm_t")
        phy_det = st.multiselect("Efectos Físicos", PHYSICS_LOGIC[phy_med], key="pd_t")

    with t3:
        c1, c2 = st.columns(2)
        with c1: sty = st.selectbox("Estilo", DEMO_STYLES)
        with c2:
            env_ch = st.selectbox("Lugar / Entorno", DEMO_ENVIRONMENTS)
            if "Custom" in env_ch:
                env_custom_txt = translate_to_english(st.text_input("Describe Lugar", key="ec_txt"))

    with t4:
        c1, c2, c3 = st.columns(3)
        with c1: cam = st.selectbox("Cámara", DEMO_CAMERAS, key="c_t")
        with c2: lit = st.selectbox("Luz", DEMO_LIGHTING, key="l_t")
        with c3: ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS, key="a_t")

    with t5:
        c1, c2, c3 = st.columns(3)
        with c1: 
            m_ch = st.selectbox("Música", DEMO_AUDIO_MOOD, key="m_t")
            mus_custom_txt = translate_to_english(st.text_input("Cuál:", key="mc_t")) if "Custom" in m_ch else ""
        with c2:
            e_ch = st.selectbox("Ambiente", DEMO_AUDIO_ENV, key="e_t")
            env_custom_txt_aud = translate_to_english(st.text_input("Cuál:", key="aec_t")) if "Custom" in e_ch else ""
        with c3:
            s_ch = st.selectbox("SFX", DEMO_SFX_COMMON, key="s_t")
            sfx_custom_txt = translate_to_english(st.text_input("Cuál:", key="sc_t")) if "Custom" in s_ch else ""

    if st.button("✨ GENERAR (TXT)", type="primary"):
        with st.spinner("Creando..."):
            try:
                b = GrokVideoPromptBuilder()
                
                b.set_field('subject', final_sub)
                b.set_field('action', translate_to_english(act))
                b.set_field('details', translate_to_english(det))
                b.set_field('style', translate_to_english(sty))
                b.set_field('camera', cam)
                b.set_field('light', lit)
                b.set_field('ar', ar)
                b.set_field('physics_medium', phy_med)
                b.set_field('physics_details', phy_det)

                b.set_field('wardrobe', w_ch)
                b.set_field('wardrobe_custom', ward_custom_val)
                b.set_field('props', p_ch)
                b.set_field('props_custom', props_custom_val)
                b.set_field('env', env_ch)
                b.set_field('env_custom', env_custom_txt)

                b.set_field('audio_mood', m_ch)
                b.set_field('audio_mood_custom', mus_custom_txt)
                b.set_field('audio_env', e_ch)
                b.set_field('audio_env_custom', env_custom_txt_aud)
                b.set_field('audio_sfx', s_ch)
                b.set_field('audio_sfx_custom', sfx_custom_txt)

                res = b.build()
                st.session_state.generated_output = res
                st.session_state.history.append(res)
            except Exception as e: st.error(str(e))

if st.session_state.generated_output:
    st.markdown("---")
    st.subheader("📝 Prompt Final")
    final_txt = st.text_area("Resultado:", st.session_state.generated_output, height=150)
    st.code(final_txt, language="text")