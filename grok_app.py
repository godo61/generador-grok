import streamlit as st
import re
import random
from PIL import Image

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
        .stTextArea textarea {{ border-left: 5px solid #FF4B4B !important; }}
        .big-warning {{ background-color: #FF4B4B20; border: 1px solid #FF4B4B; padding: 15px; border-radius: 5px; margin-bottom: 10px; }}
        .strategy-box {{ background-color: #262730; border-left: 5px solid #00AA00; padding: 15px; border-radius: 5px; margin-top: 10px; font-style: italic; color: #DDDDDD; }}
        </style>
    """, unsafe_allow_html=True)

# --- DEFINICIÓN DE LISTAS (AL PRINCIPIO PARA EVITAR ERRORES) ---
DEFAULT_CHARACTERS = {
    "TON (Base)": "a striking male figure (185cm), razor-sharp jawline, textured modern quiff hair, athletic build",
    "FREYA (Base)": "a statuesque female survivor, intense hazel eyes, wet skin texture, strong features",
}
DEFAULT_PROPS = {
    "Guitarra": "a vintage electric guitar",
    "Kayak": "a carbon fiber sea kayak",
    "Linterna Táctica": "a high-lumen tactical flashlight"
}

DEMO_STYLES = ["Neutral (Grok Default)", "Cinematic Film Still (Kodak Portra 800)", "Hyper-realistic VFX Render (Unreal 5)", "National Geographic Wildlife Style", "Gritty Documentary Footage", "Action Movie Screengrab", "Cyberpunk Digital Art", "Vintage VHS 90s"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🛶 Dusi River (Turbulent Rapids)", "🔴 Mars Surface (Red Dust)", "🌌 Deep Space (Nebula Background)", "🚀 ISS Space Station Interior", "🌊 Underwater Coral Reef", "❄️ Arctic Tundra (Snowstorm)", "🏙️ Cyberpunk City (Neon Rain)", "🌲 Mystic Forest (Fog)"]
DEMO_WARDROBE = ["✏️ Custom...", "torn sportswear and a cap", "tactical survival gear", "worn denim and leather jacket", "NASA EVA Spacesuit", "Tactical Wetsuit", "Elegant Suit"]
DEMO_LIGHTING = ["Neutral (Auto-Enhance)", "✏️ Custom...", "Harsh golden hour sunlight (long shadows)", "Dramatic low-key lighting (Chiaroscuro)", "Soft overcast diffusion", "Neon City Glow (Blue/Pink)", "Stark Space Sunlight (No Fill)", "Underwater Caustics", "Bioluminescence"]

# LISTAS PRO
LIST_SHOT_TYPES = ["Neutral (Auto-Compose)", "✏️ Custom...", "Extreme Long Shot (Gran Plano General)", "Long Shot (Plano General)", "Medium Shot (Plano Medio)", "Cowboy Shot (Plano Americano)", "Close-Up (Primer Plano)", "Extreme Close-Up (Macro Detalle)", "Over-The-Shoulder (Sobre el Hombro)"]
LIST_ANGLES = ["Neutral (Eye Level)", "✏️ Custom...", "Low Angle (Contrapicado / Heroic)", "High Angle (Picado / Vulnerable)", "Dutch Angle (Plano Holandés / Tilted)", "Bird's Eye View (Vista de Pájaro)", "Drone Aerial View (FPV)", "POV (Point of View)"]
LIST_LENSES = ["Neutral (Standard)", "✏️ Custom...", "16mm Wide Angle (Landscape/Angular)", "35mm Prime (Cinema/Street Look)", "50mm Lens (Human Eye)", "85mm f/1.4 (Portrait/Bokeh Intenso)", "100mm Macro (Micro Details)", "Canon L-Series Style (Pro Sharpness)", "Vintage Anamorphic (Lens Flares)", "Fisheye Lens (Distorted)"]

# RATIOS (ORDEN IMPORTANTE)
DEMO_ASPECT_RATIOS = ["21:9 (Cinematic)", "16:9 (Landscape)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

# AUDIO & VOZ
DEMO_AUDIO_MOOD = ["Neutral (Silent)", "✏️ Custom...", "Intense Suspense Score", "Epic Orchestral Swell", "Silent (breathing only)", "Horror Drone", "Upbeat Rock", "Synthwave"]
DEMO_AUDIO_ENV = ["Neutral (Auto)", "✏️ Custom...", "No Background", "Mars Wind", "River Rapids Roar", "Space Station Hum", "City Traffic Rain", "Jungle Sounds"]
DEMO_SFX_COMMON = ["None", "✏️ Custom...", "Heavy breathing", "Footsteps on gravel", "Water splashing", "Explosion", "Laser blasts"]
VOICE_TYPES = ["Neutral", "✏️ Custom...", "Male (Deep)", "Female (Soft)", "Child", "Elderly", "Robot/AI", "Monster/Growl"]
VOICE_ACCENTS = ["Neutral", "✏️ Custom...", "American (Standard)", "British (RP)", "Spanish (Castilian)", "Mexican", "French Accent", "Russian Accent"]
VOICE_EMOTIONS = ["Neutral", "✏️ Custom...", "Angry / Shouting", "Sad / Crying", "Whispering / Secretive", "Happy / Excited", "Sarcastic", "Terrified", "Flirty", "Passionate Singing"]

# FÍSICA
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
    "🎤 Performance Musical (Lip Sync)": "Close-up on the subject singing passionately. Mouth moves in perfect sync with the audio. Emotions range from intense focus to release. Sweat on brow, dynamic lighting reflecting the rhythm.",
    "🏃 Persecución (Sujeto vs Monstruo)": "The subject is sprinting desperately towards the camera, face contorted in panic, looking back over shoulder. Behind them, a colossal creature is charging, kicking up debris.",
    "🧟 Transformación Súbita": "At second 0, the scene is static. Suddenly, the inanimate object behind the subject rapidly transforms into a massive, living threat. The subject reacts with sheer terror.",
}

# --- INITIALIZE SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""
if 'generated_explanation' not in st.session_state: st.session_state.generated_explanation = ""
if 'characters' not in st.session_state: st.session_state.characters = DEFAULT_CHARACTERS.copy()
if 'custom_props' not in st.session_state: st.session_state.custom_props = DEFAULT_PROPS.copy()

# Variables para controlar el reseteo del uploader
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# Variables SUGERIDAS (Indices)
for k in ['rnd_lit', 'rnd_sty', 'rnd_lens', 'rnd_angle', 'rnd_shot']:
    if k not in st.session_state: st.session_state[k] = 0

# --- FUNCIONES ---
def translate_to_english(text):
    if not text or not text.strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try: return GoogleTranslator(source='auto', target='en').translate(str(text))
        except: return str(text)
    return str(text)

def detect_and_set_ar(image_file):
    """Detecta AR y FUERZA la actualización del widget."""
    try:
        img = Image.open(image_file)
        w, h = img.size
        ratio = w / h
        
        target_index = 1 # Default 16:9
        if ratio > 2.0: target_index = 0 # 21:9
        elif ratio > 1.5: target_index = 1 # 16:9
        elif ratio < 0.8: target_index = 2 # 9:16
        elif ratio < 1.2 and ratio > 0.8: target_index = 4 # 1:1
        else: target_index = 3 # 4:3
        
        # MAGIC FIX: Forzar el valor en session state para el widget con key 'ar_select'
        # Usamos el valor real del array, no el índice, porque selectbox guarda el valor
        st.session_state['ar_select'] = DEMO_ASPECT_RATIOS[target_index]
        return DEMO_ASPECT_RATIOS[target_index]
        
    except Exception as e:
        print(f"Error AR: {e}")
        return None

def suggest_cinematography(action_text, env_text):
    text_lower = (action_text + " " + env_text).lower()
    # Defaults
    s_shot, s_angle, s_lens, s_lit, s_sty = 0, 0, 0, 0, 0
    
    if "terror" in text_lower or "panic" in text_lower or "scream" in text_lower:
        s_angle = 4; s_lit = 3; s_shot = 6; s_sty = 4
    elif "run" in text_lower or "sprint" in text_lower:
        s_shot = 3; s_angle = 2; s_lens = 2; s_sty = 5
    elif "sing" in text_lower or "love" in text_lower:
        s_shot = 6; s_lens = 5; s_lit = 4
    elif "space" in text_lower or "marte" in text_lower:
        s_lit = 6; s_lens = 9; s_sty = 2
    elif "water" in text_lower or "underwater" in text_lower:
        s_lit = 7; s_angle = 7
    
    # Random fill if zero
    if s_shot == 0: s_shot = random.randint(2, len(LIST_SHOT_TYPES)-1)
    if s_angle == 0: s_angle = random.randint(2, len(LIST_ANGLES)-1)
    if s_lens == 0: s_lens = random.randint(2, len(LIST_LENSES)-1)
    if s_lit == 0: s_lit = random.randint(2, len(DEMO_LIGHTING)-1)
    if s_sty == 0: s_sty = random.randint(1, len(DEMO_STYLES)-1)
    
    return s_shot, s_angle, s_lens, s_lit, s_sty

# --- BUILDER ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = {}
        self.is_img2video = False
        self.image_filename = ""
        self.end_image_filename = None
        self.audio_filename = None
        self.explanation = []

    def set_field(self, key, value):
        self.parts[key] = str(value).strip() if isinstance(value, str) else value

    def activate_img2video(self, filename, end_filename=None):
        self.is_img2video = True
        self.image_filename = filename
        self.end_image_filename = end_filename
        
    def activate_audio_sync(self, filename):
        self.audio_filename = filename

    def build(self) -> str:
        p = self.parts
        prompt = []
        self.explanation = []

        # 1. CABECERA
        if self.is_img2video:
            prompt.append(f"Start Frame: '{self.image_filename}'.")
            self.explanation.append("✅ **Img2Vid:** Referencia visual activa.")
            if self.end_image_filename: prompt.append(f"End Frame: '{self.end_image_filename}'.")
            if self.audio_filename:
                prompt.append(f"AUDIO SOURCE: '{self.audio_filename}'. ACTION: STRICT LIP-SYNC.")
                self.explanation.append("🗣️ **Lip Sync:** Audio detectado.")
            prompt.append("Maintain strict visual consistency.")

        # 2. NARRATIVA
        narrative_block = []
        subject = p.get('subject', '')
        wardrobe = p.get('wardrobe_custom') or p.get('wardrobe', '')
        if "Custom" in wardrobe: wardrobe = ""
        
        if subject:
            sub_str = f"MAIN SUBJECT: {subject}"
            if wardrobe: sub_str += f" wearing {wardrobe}"
            narrative_block.append(sub_str + ".")
        
        action_raw = p.get('action', '')
        enhance_mode = p.get('enhance_mode', False)
        
        if action_raw:
            if enhance_mode:
                intensifiers = "extreme motion blur, sweat, panic, dynamic chaos"
                if self.audio_filename: intensifiers += ", precise singing expression"
                narrative_block.append(f"VISCERAL ACTION SEQUENCE: {action_raw}. FEATURING: {intensifiers}.")
                self.explanation.append("🔥 **VFX:** Intensidad dramática añadida.")
            else:
                narrative_block.append(f"ACTION: {action_raw}.")

        env = p.get('env_custom') or p.get('env', '')
        if "Custom" in env: env = ""
        if env: narrative_block.append(f"ENVIRONMENT: {env}.")
        elif enhance_mode: narrative_block.append("ENVIRONMENT: Cinematic background appropriate for context.")

        prompt.append("\n".join(narrative_block))

        # 3. ATMÓSFERA
        atmosphere = []
        lit_val = p.get('light', '')
        if "Custom" in lit_val or "Neutral" in lit_val: lit_val = ""
        if lit_val: atmosphere.append(f"LIGHTING: {lit_val}")
        elif enhance_mode: atmosphere.append("LIGHTING: Dramatic tone-matching lighting")

        if p.get('physics_medium') and "Neutral" not in p['physics_medium']:
            dets = [d.split('(')[0].strip() for d in p.get('physics_details', [])]
            if dets: atmosphere.append(f"PHYSICS: {', '.join(dets)}")
            
        if atmosphere: prompt.append(". ".join(atmosphere) + ".")

        # 4. CINE
        cinema = []
        for k in ['shot_type', 'angle', 'lens']:
            val = p.get(k, '')
            if val and "Neutral" not in val and "Custom" not in val:
                if k == 'lens': cinema.append(f"Shot on {val.split('(')[0]}")
                else: cinema.append(val.split('(')[0])
        
        sty = p.get('style', '')
        if "Neutral" not in sty: cinema.append(f"AESTHETIC: {sty}")
        
        if cinema: prompt.append(f"CINEMATOGRAPHY: {', '.join(cinema)}.")
        elif enhance_mode: prompt.append("CINEMATOGRAPHY: High production value.")

        # 5. AUDIO
        audio_parts = []
        m_val = p.get('audio_mood')
        if m_val and "Neutral" not in m_val and "Custom" not in m_val: audio_parts.append(f"Music: {m_val}")
        
        if audio_parts: prompt.append(f"SOUND: {'. '.join(audio_parts)}.")

        if p.get('dialogue_enabled'):
            d_txt = p.get('dialogue_text', '')
            if d_txt:
                v_char = p.get('voice_char', 'Character')
                prompt.append(f"DIALOGUE: {v_char} says: \"{d_txt}\".")

        if p.get('ar'): prompt.append(f"--ar {p['ar'].split(' ')[0]}")

        return "\n\n".join(prompt)

# --- INTERFAZ ---
with st.sidebar:
    st.title("🔥 Config VFX")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    # 1. Sugerencia Inteligente
    if st.button("🎲 Sugerir Look (Basado en Contexto)"):
        # Leemos el estado actual directamente
        curr_action = st.session_state.get('input_action', '')
        # Intentamos leer el entorno del estado si existe
        curr_env = st.session_state.get('env_select', '')
        
        s_shot, s_angle, s_lens, s_lit, s_sty = suggest_cinematography(curr_action, str(curr_env))
        
        st.session_state.rnd_shot = s_shot
        st.session_state.rnd_angle = s_angle
        st.session_state.rnd_lens = s_lens
        st.session_state.rnd_lit = s_lit
        st.session_state.rnd_sty = s_sty
        st.toast("✨ Look aplicado!")
        st.rerun()

    # 2. Reset Total (CON TRUCO DE KEY)
    if st.button("🗑️ Nueva Escena (Reset)", type="secondary"):
        st.session_state.generated_output = ""
        st.session_state.generated_explanation = ""
        for k in ['rnd_shot', 'rnd_angle', 'rnd_lens', 'rnd_lit', 'rnd_sty']: st.session_state[k] = 0
        # Forzamos cambio de key para limpiar uploader
        st.session_state.uploader_key += 1 
        # Limpiamos selección de personaje forzando None
        st.session_state.pop('char_select', None)
        st.rerun()
    
    # 3. Activos
    st.markdown("---")
    st.header("🖼️ Referencias")
    
    # UPLOAD DE IMAGEN CON AR DETECTION FIX
    # Usamos uploader_key para poder resetearlo
    u_file = st.file_uploader("Start Frame", type=["jpg", "png"], key=f"uploader_{st.session_state.uploader_key}")
    
    if u_file:
        # Check AR change logic
        if 'last_img_name' not in st.session_state or st.session_state.last_img_name != u_file.name:
            detected_val = detect_and_set_ar(u_file)
            st.session_state.last_img_name = u_file.name
            if detected_val:
                st.toast(f"📏 AR Detectado: {detected_val}")
                st.rerun() # Rerun para que el widget de abajo se actualice visualmente
    
    u_end = st.file_uploader("End Frame", type=["jpg", "png"], key=f"uploader_end_{st.session_state.uploader_key}")

# --- PANEL PRINCIPAL ---
st.title("🎬 Grok Production Studio (VFX Edition)")
enhance_mode = st.toggle("🔥 INTENSIFICADOR VFX (Modo Auto-Excellence)", value=True)

t1, t2, t3, t4, t5 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cinematografía", "🎵 Audio & Voz"])

# VARS INIT
final_sub, final_act, final_ward, final_prop, final_env = "", "", "", "", ""
final_lit, final_shot, final_angle, final_lens = "", "", "", ""
mus_vid, env_vid, sfx_vid = "", "", ""
phy_med, phy_det = "Neutral / Estudio", []
dialogue_enabled = False
voice_char, voice_type, voice_accent, voice_emotion, dialogue_text = "", "", "", "", ""

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        # LISTA DINÁMICA DE PROTAGONISTAS
        char_opts = ["-- Seleccionar Protagonista --"] 
        # Si hay fichero subido, AÑADIMOS la opción y LA SELECCIONAMOS SI NO HAY OTRA
        if u_file: char_opts.insert(1, "📷 Sujeto de la Foto (Usar Referencia)")
        char_opts += list(st.session_state.characters.keys())
        
        # LÓGICA DE PERSISTENCIA DEL SELECTOR
        # El widget usa 'key'. Si session_state['char_select'] tiene valor, lo usa.
        # Si el valor guardado ya no está en la lista (raro), se resetea.
        
        # Render del widget
        char_sel = st.selectbox("Protagonista", char_opts, key="char_select")
        
        # Procesar valor
        if "📷" in char_sel: final_sub = "" 
        elif "--" in char_sel: final_sub = ""
        else: final_sub = st.session_state.characters.get(char_sel, "")
    
    with c_b:
        tpl = st.selectbox("Plantilla de Guion", list(NARRATIVE_TEMPLATES.keys()))
        tpl_txt = NARRATIVE_TEMPLATES[tpl]

    st.markdown("##### 📜 Descripción de la Acción")
    act_val = st.text_area("Describe la escena:", value=tpl_txt, height=100, key="input_action")
    final_act = translate_to_english(act_val)

with t2:
    c1, c2 = st.columns(2)
    with c1:
        e_sel = st.selectbox("Entorno", DEMO_ENVIRONMENTS, key="env_select")
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
    # --- CINEMATOGRAFÍA ---
    # Usamos session_state.rnd_* como index para controlar desde el botón random
    # IMPORTANTE: key única para cada widget para que mantengan estado manual también
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1. Encuadre**")
        shot_sel = st.selectbox("Tipo de Plano", LIST_SHOT_TYPES, index=st.session_state.rnd_shot, key="shot_select")
        if "Custom" in shot_sel: final_shot = translate_to_english(st.text_input("Plano Custom", key="cus_shot"))
        else: final_shot = shot_sel
        
        st.markdown("**4. Formato (Auto-detect)**")
        # Aquí la key='ar_select' es CRÍTICA porque detect_and_set_ar escribe en ella
        ar = st.selectbox("Aspect Ratio", DEMO_ASPECT_RATIOS, key="ar_select")

    with c2:
        st.markdown("**2. Ángulo**")
        angle_sel = st.selectbox("Posición de Cámara", LIST_ANGLES, index=st.session_state.rnd_angle, key="angle_select")
        if "Custom" in angle_sel: final_angle = translate_to_english(st.text_input("Ángulo Custom", key="cus_ang"))
        else: final_angle = angle_sel
        
        st.markdown("**5. Iluminación**")
        lit_sel = st.selectbox("Tipo de Luz", DEMO_LIGHTING, index=st.session_state.rnd_lit, key="lit_select")
        if "Custom" in lit_sel: final_lit = translate_to_english(st.text_input("Luz Custom", key="ll"))
        else: final_lit = lit_sel

    with c3:
        st.markdown("**3. Óptica / Lente**")
        lens_sel = st.selectbox("Lente y Apertura", LIST_LENSES, index=st.session_state.rnd_lens, key="lens_select")
        if "Custom" in lens_sel: final_lens = translate_to_english(st.text_input("Lente Custom", key="cus_lens"))
        else: final_lens = lens_sel
        
        st.markdown("**6. Estilo Visual**")
        sty = st.selectbox("Look & Film Stock", DEMO_STYLES, index=st.session_state.rnd_sty, key="sty_select")

with t5:
    st.markdown("### 🎙️ Estudio de Voz y Lip Sync")
    st.markdown("""<div class="big-warning">⚠️ <b>IMPORTANTE:</b> Sube el audio real a la IA de vídeo.</div>""", unsafe_allow_html=True)
    
    # UPLOADER DE AUDIO (Resetable)
    audio_file = st.file_uploader("📂 Subir Audio (MP3/WAV)", type=["mp3", "wav", "m4a"], key=f"audio_uploader_{st.session_state.uploader_key}")
    if audio_file:
        st.audio(audio_file)
        st.success("✅ Lip Sync activado.")
        audio_name = audio_file.name
    else: audio_name = None

    dialogue_enabled = st.toggle("🗣️ Configurar Detalles de Voz", value=False)
    if dialogue_enabled:
        with st.container(border=True):
            dc1, dc2 = st.columns(2)
            with dc1:
                voice_opts = ["Protagonista Actual", "Narrador"] + list(st.session_state.characters.keys())
                v_char_sel = st.selectbox("Personaje", voice_opts)
                if "Protagonista" in v_char_sel: voice_char = "The Main Character"
                elif "Narrador" in v_char_sel: voice_char = "Narrator"
                else: voice_char = v_char_sel
                
                v_type = st.selectbox("Tipo Voz", VOICE_TYPES)
                if "Custom" in v_type: voice_type = translate_to_english(st.text_input("Tipo Custom", key="vtc"))
                else: voice_type = v_type
            with dc2:
                v_acc = st.selectbox("Acento", VOICE_ACCENTS)
                if "Custom" in v_acc: voice_accent = translate_to_english(st.text_input("Acento Custom", key="vac"))
                else: voice_accent = v_acc
                
                v_emo = st.selectbox("Emoción", VOICE_EMOTIONS)
                if "Custom" in v_emo: voice_emotion = translate_to_english(st.text_input("Emo Custom", key="vec"))
                else: voice_emotion = v_emo
            
            d_txt = st.text_area("Guion / Letra:", placeholder="Texto...")
            dialogue_text = translate_to_english(d_txt)

    st.markdown("---")
    st.markdown("### 🎵 Diseño Sonoro")
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

    st.markdown("---")
    with st.expander("🎹 Generador Musical (Suno AI)", expanded=False):
        sc1, sc2 = st.columns(2)
        with sc1:
            suno_inst = st.toggle("🎻 Instrumental")
            suno_dur = st.slider("Duración", 30, 240, 120, step=30)
            if suno_dur <= 45: struc = "[Intro] [Hook] [Outro]"
            elif suno_dur <= 90: struc = "[Intro] [Verse] [Chorus] [Outro]"
            else: struc = "[Intro] [Verse] [Chorus] [Bridge] [Outro]"
        with sc2:
            s_gen = st.text_input("Género", placeholder="Rock...")
            s_mood = st.text_input("Mood", placeholder="Epic...")
        s_lyr = st.text_area("Letra/Tema") if not suno_inst else ""
        
        if st.button("🎵 GENERAR PROMPT SUNO"):
            tags = []
            if suno_inst: tags.append("[Instrumental]")
            if s_gen: tags.append(f"[{translate_to_english(s_gen)}]")
            if s_mood: tags.append(f"[{translate_to_english(s_mood)}]")
            res_suno = f"Style: {' '.join(tags)}\nStructure:\n{struc}\n"
            if s_lyr: res_suno += f"\nLyrics:\n{translate_to_english(s_lyr)}"
            st.code(res_suno, language="text")

# GENERAR
if st.button("✨ GENERAR PROMPT PRO", type="primary"):
    b = GrokVideoPromptBuilder()
    if u_file: b.activate_img2video(u_file.name, u_end.name if u_end else None)
    if audio_name: b.activate_audio_sync(audio_name)
    
    b.set_field('enhance_mode', enhance_mode)
    b.set_field('subject', final_sub)
    b.set_field('action', final_act)
    b.set_field('wardrobe', final_ward)
    b.set_field('props', final_prop)
    b.set_field('env', final_env)
    b.set_field('physics_medium', phy_med)
    b.set_field('physics_details', phy_det)
    
    b.set_field('shot_type', final_shot)
    b.set_field('angle', final_angle)
    b.set_field('lens', final_lens)
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
    st.session_state.generated_explanation = "\n".join(b.explanation)
    st.session_state.history.append(res)

if st.session_state.generated_output:
    st.markdown("---")
    if st.session_state.generated_explanation:
        st.markdown(f'<div class="strategy-box"><b>💡 Estrategia:</b><br>{st.session_state.generated_explanation}</div>', unsafe_allow_html=True)
    st.subheader("📝 Prompt Final")
    st.code(st.session_state.generated_output, language="text")