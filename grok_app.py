import streamlit as st
import re
import random
from PIL import Image

# --- 1. CONFIGURACIÓN E IMPORTACIONES ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

st.set_page_config(page_title="Grok Production Studio", layout="wide", page_icon="🎬")

# --- 2. ESTILOS CSS ---
def apply_custom_styles(dark_mode=False):
    bg_color = "#0E1117" if dark_mode else "#FFFFFF"
    text_color = "#FAFAFA" if dark_mode else "#31333F"
    tab_bg = "#1E1E24" if dark_mode else "#F0F2F6"

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background-color: {bg_color}; color: {text_color}; }}
        [data-testid="stSidebar"] {{ background-color: {tab_bg}; }}
        textarea {{ font-size: 1.1rem !important; font-family: monospace !important; }}
        .big-warning {{ background-color: #FF4B4B20; border: 1px solid #FF4B4B; padding: 15px; border-radius: 5px; margin-bottom: 10px; }}
        .strategy-box {{ background-color: #262730; border-left: 5px solid #00AA00; padding: 15px; border-radius: 5px; margin-top: 10px; color: #EEE; font-style: italic; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. DEFINICIONES DE DATOS (GLOBALES) ---
# Activos
DEFAULT_CHARACTERS = {
    "TON (Base)": "a striking male figure (185cm), razor-sharp jawline, textured modern quiff hair, athletic build",
    "FREYA (Base)": "a statuesque female survivor, intense hazel eyes, wet skin texture, strong features",
}
DEFAULT_PROPS = {
    "Guitarra": "a vintage electric guitar",
    "Kayak": "a carbon fiber sea kayak",
    "Linterna": "a high-lumen tactical flashlight"
}

# Listas Visuales
DEMO_STYLES = ["Neutral (Grok Default)", "Cinematic Film Still (Kodak Portra 800)", "Hyper-realistic VFX Render (Unreal 5)", "National Geographic Wildlife Style", "Gritty Documentary Footage", "Action Movie Screengrab", "Cyberpunk Digital Art", "Vintage VHS 90s"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🛶 Dusi River (Turbulent Rapids)", "🔴 Mars Surface (Red Dust)", "🌌 Deep Space (Nebula Background)", "🚀 ISS Space Station Interior", "🌊 Underwater Coral Reef", "❄️ Arctic Tundra (Snowstorm)", "🏙️ Cyberpunk City (Neon Rain)", "🌲 Mystic Forest (Fog)"]
DEMO_WARDROBE = ["✏️ Custom...", "torn sportswear and a cap", "tactical survival gear", "worn denim and leather jacket", "NASA EVA Spacesuit", "Tactical Wetsuit", "Elegant Suit"]
DEMO_PROPS_LIST = ["None", "✏️ Custom...", "🛶 Kayak Paddle", "🎸 Electric Guitar", "🔫 Blaster", "📱 Datapad", "🔦 Flashlight"]

# Cine Lists
LIST_SHOT_TYPES = ["Neutral (Auto)", "✏️ Custom...", "Extreme Long Shot (Gran Plano General)", "Long Shot (Plano General)", "Medium Shot (Plano Medio)", "Cowboy Shot (Plano Americano)", "Close-Up (Primer Plano)", "Extreme Close-Up (Macro Detalle)", "Over-The-Shoulder (Sobre el Hombro)"]
LIST_ANGLES = ["Neutral (Auto)", "✏️ Custom...", "Low Angle (Contrapicado)", "High Angle (Picado)", "Dutch Angle (Plano Holandés)", "Bird's Eye View (Vista de Pájaro)", "Drone Aerial View (FPV)", "POV (Point of View)"]
LIST_LENSES = ["Neutral (Auto)", "✏️ Custom...", "16mm Wide Angle", "35mm Prime (Cinema)", "50mm Lens (Human Eye)", "85mm f/1.4 (Portrait)", "100mm Macro", "Canon L-Series Style", "Vintage Anamorphic", "Fisheye Lens"]
DEMO_LIGHTING = ["Neutral (Auto)", "✏️ Custom...", "Harsh Golden Hour", "Dramatic Low-Key (Chiaroscuro)", "Soft Overcast", "Neon City Glow", "Stark Space Sunlight", "Underwater Caustics", "Bioluminescence"]
DEMO_ASPECT_RATIOS = ["21:9 (Cinematic)", "16:9 (Landscape)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

# Audio
DEMO_AUDIO_MOOD = ["Neutral", "✏️ Custom...", "Intense Suspense", "Epic Orchestral", "Silent (breathing only)", "Horror Drone", "Upbeat Rock", "Synthwave"]
DEMO_AUDIO_ENV = ["Neutral", "✏️ Custom...", "No Background", "Mars Wind", "River Roar", "Space Hum", "City Rain", "Jungle Sounds"]
DEMO_SFX = ["None", "✏️ Custom...", "Heavy breathing", "Footsteps", "Water splashing", "Explosion", "Laser blasts"]
VOICE_TYPES = ["Neutral", "✏️ Custom...", "Male (Deep)", "Female (Soft)", "Child", "Elderly", "Robot/AI", "Monster/Growl"]
VOICE_ACCENTS = ["Neutral", "✏️ Custom...", "American (Standard)", "British (RP)", "Spanish (Castilian)", "Mexican", "French Accent", "Russian Accent"]
VOICE_EMOTIONS = ["Neutral", "✏️ Custom...", "Angry / Shouting", "Sad / Crying", "Whispering / Secretive", "Happy / Excited", "Sarcastic", "Terrified", "Flirty", "Passionate Singing"]

# Plantillas
NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🎤 Performance Musical (Lip Sync)": "Close-up on the subject singing passionately. Mouth moves in perfect sync with the audio. Emotions range from intense focus to release. Sweat on brow, dynamic lighting reflecting the rhythm.",
    "🏃 Persecución (Sujeto vs Monstruo)": "The subject is sprinting desperately towards the camera, face contorted in panic, looking back over shoulder. Behind them, a colossal creature is charging, kicking up debris.",
    "🧟 Transformación Súbita": "At second 0, the scene is static. Suddenly, the inanimate object behind the subject rapidly transforms into a massive, living threat. The subject reacts with sheer terror.",
}

# Física
PHYSICS_LOGIC = {
    "Neutral / Estudio": [],
    "🌌 Espacio (Zero-G)": ["Zero-G floating", "No air resistance", "Vacuum silence", "Floating debris"],
    "🔴 Marte (Low-G)": ["Low gravity", "Red dust storms", "Heat distortion", "Dust settling slowly"],
    "🌊 Agua (Superficie)": ["Turbulent flow", "White foam", "Wet fabric", "Water splashes"],
    "🤿 Submarino": ["Weightless", "Light Caustics", "Bubbles", "Floating hair"],
    "❄️ Nieve": ["Falling snow", "Breath condensation", "Frost on lens"],
    "🌬️ Viento": ["High wind drag", "Fabric fluttering", "Motion blur"]
}

# --- 4. GESTIÓN DE ESTADO (PERSISTENCIA) ---
# Inicializar variables críticas
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""
if 'generated_explanation' not in st.session_state: st.session_state.generated_explanation = ""
if 'characters' not in st.session_state: st.session_state.characters = DEFAULT_CHARACTERS.copy()
if 'custom_props' not in st.session_state: st.session_state.custom_props = DEFAULT_PROPS.copy()
if 'history' not in st.session_state: st.session_state.history = []
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# Inicialización de widgets con valores por defecto
# Usamos un diccionario para asegurar que todas las keys existan
default_widget_values = {
    'act_input': "",
    'char_select': "-- Seleccionar Protagonista --",
    'shot_select': LIST_SHOT_TYPES[0],
    'angle_select': LIST_ANGLES[0],
    'lens_select': LIST_LENSES[0],
    'lit_select': DEMO_LIGHTING[0],
    'sty_select': DEMO_STYLES[0],
    'env_select': DEMO_ENVIRONMENTS[0],
    'ar_select': DEMO_ASPECT_RATIOS[1], # 16:9
    'phy_select': "Neutral / Estudio"
}

for key, val in default_widget_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 5. FUNCIONES LÓGICAS ---
def translate_to_english(text):
    if not text or not text.strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try: return GoogleTranslator(source='auto', target='en').translate(str(text))
        except: return str(text)
    return str(text)

def detect_and_set_ar(image_file):
    """Detecta el Ratio de la imagen y actualiza el estado"""
    try:
        img = Image.open(image_file)
        w, h = img.size
        ratio = w / h
        
        idx = 1 # Default 16:9
        if ratio > 2.0: idx = 0 # 21:9
        elif ratio > 1.5: idx = 1 # 16:9
        elif ratio < 0.8: idx = 2 # 9:16
        elif ratio < 1.2 and ratio > 0.8: idx = 4 # 1:1
        else: idx = 3 # 4:3
        
        # Actualizamos la variable de estado que controla el widget
        st.session_state['ar_select'] = DEMO_ASPECT_RATIOS[idx]
        return DEMO_ASPECT_RATIOS[idx]
    except Exception as e:
        return None

def apply_smart_look(action_text, env_text):
    """Analiza el texto y selecciona opciones de las listas"""
    txt = (action_text + " " + env_text).lower()
    
    # Elección aleatoria segura (saltando los primeros índices 'Neutral'/'Custom')
    s_shot = random.choice(LIST_SHOT_TYPES[2:])
    s_angle = random.choice(LIST_ANGLES[2:])
    s_lens = random.choice(LIST_LENSES[2:])
    s_lit = random.choice(DEMO_LIGHTING[2:])
    s_sty = random.choice(DEMO_STYLES[1:])
    
    # Lógica de reglas
    if "terror" in txt or "miedo" in txt or "panic" in txt:
        s_angle = "Dutch Angle (Plano Holandés)"
        s_lit = "Dramatic Low-Key (Chiaroscuro)"
        s_sty = "Gritty Documentary Footage"
        s_shot = "Close-Up (Primer Plano)"
    
    elif "correr" in txt or "run" in txt or "persecución" in txt:
        s_shot = "Long Shot (Plano General)"
        s_angle = "Low Angle (Contrapicado)"
        s_lens = "16mm Wide Angle"
        s_sty = "Action Movie Screengrab"
        
    elif "espacio" in txt or "space" in txt or "marte" in txt:
        s_lit = "Stark Space Sunlight"
        s_lens = "Fisheye Lens"
        s_sty = "Hyper-realistic VFX Render (Unreal 5)"
        
    elif "agua" in txt or "water" in txt or "rio" in txt:
        s_lit = "Underwater Caustics"
        s_angle = "Drone Aerial View (FPV)"

    # Aplicar SOLO si los valores existen en las listas (seguridad)
    if s_shot in LIST_SHOT_TYPES: st.session_state['shot_select'] = s_shot
    if s_angle in LIST_ANGLES: st.session_state['angle_select'] = s_angle
    if s_lens in LIST_LENSES: st.session_state['lens_select'] = s_lens
    if s_lit in DEMO_LIGHTING: st.session_state['lit_select'] = s_lit
    if s_sty in DEMO_STYLES: st.session_state['sty_select'] = s_sty

def perform_reset():
    """Resetea todos los campos a sus valores por defecto"""
    st.session_state['act_input'] = ""
    st.session_state['char_select'] = "-- Seleccionar Protagonista --"
    st.session_state['shot_select'] = LIST_SHOT_TYPES[0]
    st.session_state['angle_select'] = LIST_ANGLES[0]
    st.session_state['lens_select'] = LIST_LENSES[0]
    st.session_state['lit_select'] = DEMO_LIGHTING[0]
    st.session_state['sty_select'] = DEMO_STYLES[0]
    st.session_state['env_select'] = DEMO_ENVIRONMENTS[0]
    st.session_state['uploader_key'] += 1 # Truco para limpiar file_uploader
    st.session_state['generated_output'] = ""
    st.session_state['generated_explanation'] = ""

# --- 6. CLASE BUILDER ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = []
        self.explanation = []
        
    def add(self, text, explain=None):
        if text:
            self.parts.append(text)
            if explain: self.explanation.append(explain)
            
    def get_prompt(self): return "\n\n".join(self.parts)

# --- 7. INTERFAZ: SIDEBAR ---
with st.sidebar:
    st.title("🔥 Config VFX")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    # BOTÓN SUGERIR
    if st.button("🎲 Sugerir Look (Inteligente)"):
        # Leemos el estado actual
        act = st.session_state.get('act_input', "")
        env = st.session_state.get('env_select', "")
        apply_smart_look(act, env)
        st.toast("✨ Look aplicado según el contexto!")
        st.rerun()

    # BOTÓN RESET
    if st.button("🗑️ Nueva Escena (Limpiar Todo)", type="secondary"):
        perform_reset()
        st.rerun()

    st.markdown("---")
    st.header("🖼️ Referencias")
    
    # Uploader con key dinámica
    u_key = f"up_{st.session_state.uploader_key}"
    uploaded_file = st.file_uploader("Start Frame", type=["jpg", "png"], key=u_key)
    
    # Detección automática de AR al subir
    if uploaded_file:
        st.image(uploaded_file, caption="Ref")
        # Si es un archivo nuevo que no hemos analizado
        if 'last_img_name' not in st.session_state or st.session_state.last_img_name != uploaded_file.name:
            detected_ar = detect_and_set_ar(uploaded_file)
            st.session_state.last_img_name = uploaded_file.name
            if detected_ar:
                st.toast(f"📏 Formato detectado: {detected_ar}")
                st.rerun() # Recargar para actualizar el selector de AR
    
    uploaded_end = st.file_uploader("End Frame", type=["jpg", "png"], key=f"up_end_{st.session_state.uploader_key}")

# --- 8. INTERFAZ: PRINCIPAL ---
st.title("🎬 Grok Production Studio (VFX Edition)")
enhance_mode = st.toggle("🔥 INTENSIFICADOR VFX (Modo Auto-Excellence)", value=True)

t1, t2, t3, t4, t5 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cinematografía", "🎵 Audio & Voz"])

# Variables para el builder
final_sub, final_act = "", ""

with t1:
    c1, c2 = st.columns(2)
    with c1:
        # CONSTRUIR OPCIONES DE PROTAGONISTA
        char_opts = ["-- Seleccionar Protagonista --"]
        if uploaded_file: char_opts.insert(1, "📷 Sujeto de la Foto (Usar Referencia)")
        char_opts += list(st.session_state.characters.keys())
        
        # Verificar que la selección actual siga siendo válida
        if st.session_state.char_select not in char_opts:
            st.session_state.char_select = char_opts[0]
            
        char_sel = st.selectbox("Protagonista", char_opts, key="char_select")
        
        # Lógica de texto
        if "📷" in char_sel: final_sub = "MAIN SUBJECT: The character in the provided reference image"
        elif "--" in char_sel: final_sub = ""
        else: final_sub = f"MAIN SUBJECT: {st.session_state.characters.get(char_sel, '')}"

    with c2:
        tpl = st.selectbox("Plantilla Rápida", ["Seleccionar..."] + list(NARRATIVE_TEMPLATES.keys()))
        if tpl != "Seleccionar...":
            st.session_state['act_input'] = NARRATIVE_TEMPLATES[tpl]
            # No forzamos rerun, el usuario verá el cambio instantáneo en el text_area

    st.markdown("##### 📜 Descripción de la Acción")
    act_val = st.text_area("Describe la escena:", height=100, key="act_input")
    final_act = translate_to_english(act_val)

with t2:
    c1, c2 = st.columns(2)
    with c1:
        e_sel = st.selectbox("Entorno", DEMO_ENVIRONMENTS, key="env_select")
        final_env = st.text_input("Custom Env", key="env_cust") if "Custom" in e_sel else e_sel
        
        # Construir lista de props dinámica
        all_props = ["None", "✏️ Custom..."] + list(st.session_state.custom_props.keys()) + DEMO_PROPS_LIST[2:]
        prop_sel = st.selectbox("Objeto", all_props, key="prop_select")
        
        if prop_sel in st.session_state.custom_props: final_prop = st.session_state.custom_props[prop_sel]
        elif "Custom" in prop_sel: final_prop = translate_to_english(st.text_input("Objeto Nuevo", key="np"))
        elif "None" not in prop_sel: final_prop = prop_sel
        else: final_prop = ""

    with c2:
        ward_sel = st.selectbox("Vestuario", DEMO_WARDROBE, key="ward_select")
        if "Custom" in ward_sel: final_ward = translate_to_english(st.text_input("Ropa Custom", key="wc"))
        else: final_ward = ward_sel

with t3:
    st.markdown("##### ⚛️ Física")
    c1, c2 = st.columns(2)
    with c1: phy_med = st.selectbox("Medio Físico", list(PHYSICS_LOGIC.keys()), key="phy_select")
    with c2: phy_det = st.multiselect("Detalles", PHYSICS_LOGIC[phy_med])

with t4:
    # CINE PRO (Widgets conectados a st.session_state)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("1. Encuadre", LIST_SHOT_TYPES, key="shot_select")
        st.selectbox("4. Formato (Auto)", DEMO_ASPECT_RATIOS, key="ar_select")
    with c2:
        st.selectbox("2. Ángulo", LIST_ANGLES, key="angle_select")
        st.selectbox("5. Iluminación", DEMO_LIGHTING, key="lit_select")
    with c3:
        st.selectbox("3. Lente", LIST_LENSES, key="lens_select")
        st.selectbox("6. Estilo", DEMO_STYLES, key="sty_select")

with t5:
    st.markdown("### 🎙️ Audio & Lip Sync")
    st.info("Sube aquí el audio SOLO para activar el Lip-Sync en el prompt.")
    aud_file = st.file_uploader("Audio (MP3/WAV)", type=["mp3","wav"], key=f"aud_{st.session_state.uploader_key}")
    
    # --- SUNO AI SECTION (INTEGRADA) ---
    st.markdown("---")
    with st.expander("🎹 Generador Musical (Suno AI)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            # Variable segura para evitar el error anterior
            suno_is_instrumental = st.toggle("🎻 Instrumental", key="suno_inst_check")
            suno_dur = st.slider("Duración", 30, 240, 120)
            
            if suno_dur <= 45: struc = "[Intro] [Hook] [Outro]"
            elif suno_dur <= 90: struc = "[Intro] [Verse] [Chorus] [Outro]"
            else: struc = "[Intro] [Verse] [Chorus] [Bridge] [Outro]"
                
        with c2:
            s_gen = st.text_input("Género", placeholder="Rock...")
            s_mood = st.text_input("Mood", placeholder="Epic...")
        
        s_lyr = ""
        if not suno_is_instrumental:
            s_lyr = st.text_area("Letra/Tema:", placeholder="Escribe la letra o describe el tema...", key="suno_lyrics_input")

        if st.button("🎵 GENERAR PROMPT SUNO", key="btn_suno"):
            tags = []
            if suno_is_instrumental: tags.append("[Instrumental]")
            if s_gen: tags.append(f"[{translate_to_english(s_gen)}]")
            if s_mood: tags.append(f"[{translate_to_english(s_mood)}]")
            
            res_suno = f"Style Prompts: {' '.join(tags)}\n\nStructure:\n{struc}\n"
            if s_lyr: res_suno += f"\nLyrics / Topic:\n{translate_to_english(s_lyr)}"
            
            st.code(res_suno, language="text")
            
    # Configuración de voz normal
    st.markdown("---")
    dialogue_enabled = st.toggle("🗣️ Configurar Detalles de Voz (TTS)", value=False)
    
    if dialogue_enabled:
        with st.container(border=True):
            dc1, dc2 = st.columns(2)
            with dc1:
                v_char_sel = st.selectbox("Personaje que habla", ["Protagonista Actual", "Narrador"] + list(st.session_state.characters.keys()))
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
            
            d_txt = st.text_area("Guion / Diálogo:", placeholder="Texto a hablar...")
            dialogue_text = translate_to_english(d_txt)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: 
        m_sel = st.selectbox("Música (Video)", DEMO_AUDIO_MOOD)
        mus_vid = translate_to_english(st.text_input("Mus. Custom", key="mc")) if "Custom" in m_sel else m_sel
    with c2:
        s_sel = st.selectbox("SFX", DEMO_SFX)
        sfx_vid = translate_to_english(st.text_input("SFX Custom", key="sc")) if "Custom" in s_sel else s_sel

# --- 9. GENERACIÓN DEL PROMPT FINAL ---
if st.button("✨ GENERAR PROMPT PRO", type="primary"):
    b = GrokVideoPromptBuilder()
    
    # 1. Cabecera
    if uploaded_file: b.add(f"Start Frame: '{uploaded_file.name}'", "✅ Img2Vid")
    if uploaded_end: b.add(f"End Frame: '{uploaded_end.name}'")
    if aud_file: b.add(f"AUDIO SOURCE: '{aud_file.name}'. ACTION: STRICT LIP-SYNC.", "🗣️ Lip Sync")
    b.add("Maintain strict visual consistency.")
    
    # 2. Narrativa
    narrative = []
    if final_sub: narrative.append(final_sub)
    if "Custom" not in final_ward: narrative.append(f"WEARING: {final_ward}")
    if "Custom" not in final_prop and "None" not in final_prop: narrative.append(f"HOLDING: {final_prop}")
    
    if final_act:
        if enhance_mode:
            ints = "extreme motion blur, sweat, panic, dynamic chaos"
            if aud_file: ints += ", singing expression"
            narrative.append(f"VISCERAL ACTION: {final_act}. FEATURING: {ints}.")
            b.explanation.append("🔥 VFX Mode: Acción intensificada.")
        else:
            narrative.append(f"ACTION: {final_act}.")
    
    if "Custom" not in final_env: narrative.append(f"ENVIRONMENT: {final_env}.")
    elif enhance_mode and not final_env: narrative.append("ENVIRONMENT: Cinematic background.")
    
    b.add("\n".join(narrative))
    
    # 3. Atmósfera
    atm = []
    lit = st.session_state.lit_select
    if "Neutral" not in lit and "Custom" not in lit: atm.append(f"LIGHTING: {lit}")
    elif enhance_mode: atm.append("LIGHTING: Dramatic tone-matching.")
    
    if phy_det: atm.append(f"PHYSICS: {', '.join(phy_det)}")
    b.add(". ".join(atm))
    
    # 4. Cine
    cine = []
    for k in ['shot_select', 'angle_select', 'lens_select']:
        val = st.session_state[k]
        if "Neutral" not in val and "Custom" not in val: cine.append(val.split('(')[0])
    
    sty = st.session_state.sty_select
    if "Neutral" not in sty: cine.append(f"STYLE: {sty}")
    
    if cine: b.add(f"CINEMATOGRAPHY: {', '.join(cine)}.")
    elif enhance_mode: b.add("CINEMATOGRAPHY: High production value.")
    
    # 5. Params
    ar_val = st.session_state.ar_select.split('(')[0].strip()
    b.add(f"--ar {ar_val}")
    
    # 6. Audio/Dialogo
    if mus_vid and "Neutral" not in mus_vid: b.add(f"MUSIC: {mus_vid}")
    if dialogue_enabled and dialogue_text:
        b.add(f"DIALOGUE: {voice_char} ({voice_type}, {voice_emotion}) says: \"{dialogue_text}\"")
    
    res = b.get_prompt()
    st.session_state.generated_output = res
    st.session_state.generated_explanation = "\n".join(b.explanation)

if st.session_state.generated_output:
    st.markdown("---")
    if st.session_state.generated_explanation:
        st.markdown(f'<div class="strategy-box"><b>💡 Estrategia:</b><br>{st.session_state.generated_explanation}</div>', unsafe_allow_html=True)
    st.subheader("📝 Prompt Final")
    st.code(st.session_state.generated_output, language="text")
    st.caption("👆 Pulsa el icono de 'Copiar' en la esquina superior derecha del bloque negro.")