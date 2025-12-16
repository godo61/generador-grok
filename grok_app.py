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

# --- 3. DEFINICIONES DE DATOS ---
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

# Cine Lists (Formula Architect)
LIST_SHOT_TYPES = ["Neutral (Auto)", "✏️ Custom...", "Extreme Long Shot (Epic Scale)", "Long Shot (Full Body)", "Medium Shot (Waist Up)", "Cowboy Shot (Knees Up)", "Close-Up (Face Focus)", "Extreme Close-Up (Macro Detail)", "Over-The-Shoulder (Dialogue)"]
LIST_ANGLES = ["Neutral (Auto)", "✏️ Custom...", "Low Angle (Heroic/Ominous)", "High Angle (Vulnerable)", "Dutch Angle (Chaos/Tension)", "Bird's Eye View (Top-Down)", "Drone Aerial View (Establishing)", "POV (First Person)"]
# Nota: Lentes ordenadas para lógica random segura
LIST_LENSES = ["Neutral (Auto)", "✏️ Custom...", "16mm Wide Angle (Expansive)", "24mm Lens (Dynamic)", "35mm Prime (Street/Docu)", "50mm Lens (Natural Eye)", "85mm f/1.4 (Portrait Bokeh)", "100mm Macro (Micro Detail)", "Canon L-Series (Sharp)", "Vintage Anamorphic (Cinematic)", "Fisheye (Distorted)"]
DEMO_LIGHTING = ["Neutral (Auto)", "✏️ Custom...", "Harsh Golden Hour", "Dramatic Low-Key (Chiaroscuro)", "Soft Overcast (Diffusion)", "Neon City Glow (Cyberpunk)", "Stark Space Sunlight (Hard Shadows)", "Underwater Caustics", "Bioluminescence"]
DEMO_ASPECT_RATIOS = ["21:9 (Cinematic)", "16:9 (Landscape)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

# Audio
DEMO_AUDIO_MOOD = ["Neutral", "✏️ Custom...", "Intense Suspense", "Epic Orchestral", "Silent (breathing only)", "Horror Drone", "Upbeat Rock", "Synthwave"]
DEMO_AUDIO_ENV = ["Neutral", "✏️ Custom...", "No Background", "Mars Wind", "River Roar", "Space Hum", "City Rain", "Jungle Sounds"]
DEMO_SFX = ["None", "✏️ Custom...", "Heavy breathing", "Footsteps", "Water splashing", "Explosion", "Laser blasts"]
VOICE_TYPES = ["Neutral", "✏️ Custom...", "Male (Deep)", "Female (Soft)", "Child", "Elderly", "Robot/AI", "Monster/Growl"]
VOICE_ACCENTS = ["Neutral", "✏️ Custom...", "American (Standard)", "British (RP)", "Spanish (Castilian)", "Mexican", "French Accent", "Russian Accent"]
VOICE_EMOTIONS = ["Neutral", "✏️ Custom...", "Angry / Shouting", "Sad / Crying", "Whispering / Secretive", "Happy / Excited", "Sarcastic", "Terrified", "Flirty", "Passionate Singing"]

NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🎤 Performance Musical (Lip Sync)": "Close-up on the subject singing passionately. Mouth moves in perfect sync with the audio. Emotions range from intense focus to release. Sweat on brow, dynamic lighting reflecting the rhythm.",
    "🏃 Persecución (Sujeto vs Monstruo)": "The subject is sprinting desperately towards the camera, face contorted in panic, looking back over shoulder. Behind them, a colossal creature is charging, kicking up debris.",
    "🧟 Transformación Súbita": "At second 0, the scene is static. Suddenly, the inanimate object behind the subject rapidly transforms into a massive, living threat. The subject reacts with sheer terror.",
}

PHYSICS_LOGIC = {
    "Neutral / Estudio": [],
    "🌌 Espacio (Zero-G)": ["Zero-G floating", "No air resistance", "Vacuum silence", "Floating debris"],
    "🔴 Marte (Low-G)": ["Low gravity", "Red dust storms", "Heat distortion", "Dust settling slowly"],
    "🌊 Agua (Superficie)": ["Turbulent flow", "White foam", "Wet fabric", "Water splashes"],
    "🤿 Submarino": ["Weightless", "Light Caustics", "Bubbles", "Floating hair"],
    "❄️ Nieve": ["Falling snow", "Breath condensation", "Frost on lens"],
    "🌬️ Viento": ["High wind drag", "Fabric fluttering", "Motion blur"]
}

# --- 4. GESTIÓN DE ESTADO ---
# Inicializar variables
init_vars = {
    'generated_output': "",
    'generated_explanation': "",
    'characters': DEFAULT_CHARACTERS.copy(),
    'custom_props': DEFAULT_PROPS.copy(),
    'history': [],
    'uploader_key': 0,
    'act_input': "",
    'char_select': "-- Seleccionar Protagonista --",
    'shot_select': LIST_SHOT_TYPES[0],
    'angle_select': LIST_ANGLES[0],
    'lens_select': LIST_LENSES[0],
    'lit_select': DEMO_LIGHTING[0],
    'sty_select': DEMO_STYLES[0],
    'env_select': DEMO_ENVIRONMENTS[0],
    'ar_select': DEMO_ASPECT_RATIOS[1],
    'phy_select': "Neutral / Estudio",
    'last_img_name': ""
}

for k, v in init_vars.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 5. FUNCIONES LÓGICAS ---
def translate_to_english(text):
    if not text or not text.strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try: return GoogleTranslator(source='auto', target='en').translate(str(text))
        except: return str(text)
    return str(text)

def detect_and_set_ar(image_file):
    try:
        img = Image.open(image_file)
        w, h = img.size
        ratio = w / h
        idx = 1
        if ratio > 2.0: idx = 0
        elif ratio > 1.5: idx = 1
        elif ratio < 0.8: idx = 2
        elif ratio < 1.2 and ratio > 0.8: idx = 4
        else: idx = 3
        st.session_state['ar_select'] = DEMO_ASPECT_RATIOS[idx]
        return DEMO_ASPECT_RATIOS[idx]
    except: return None

def apply_smart_look(action_text, env_text):
    txt = (action_text + " " + env_text).lower()
    
    # --- LÓGICA DE SELECCIÓN SEGURA ---
    # 1. Definir pools de opciones "seguras" (Excluyendo Macro, Fisheye, etc para random)
    safe_shots = [s for s in LIST_SHOT_TYPES if "Macro" not in s and "Extreme Close" not in s and "Neutral" not in s and "Custom" not in s]
    safe_angles = [a for a in LIST_ANGLES if "Neutral" not in a and "Custom" not in a]
    safe_lenses = [l for l in LIST_LENSES if "Macro" not in l and "Fisheye" not in l and "Neutral" not in l and "Custom" not in l]
    safe_lits = [l for l in DEMO_LIGHTING if "Neutral" not in l and "Custom" not in l]
    safe_styles = [s for s in DEMO_STYLES if "Neutral" not in s]

    # 2. Selección por defecto (Random Seguro)
    s_shot = random.choice(safe_shots)
    s_angle = random.choice(safe_angles)
    s_lens = random.choice(safe_lenses)
    s_lit = random.choice(safe_lits)
    s_sty = random.choice(safe_styles)
    
    # 3. Reglas Contextuales (Overrides Específicos)
    # Regla: MONSTRUO / GIGANTE / MAMUT
    if any(x in txt for x in ["mamut", "mammoth", "colossal", "gigante", "monster", "beast", "titan", "elefante"]):
        s_shot = "Extreme Long Shot (Epic Scale)" # Para ver el tamaño
        s_angle = "Low Angle (Heroic/Ominous)" # Para que parezca grande
        s_lens = "16mm Wide Angle (Expansive)" # Escala épica
        s_lit = "Harsh Golden Hour" # O dramatic
        s_sty = "Action Movie Screengrab"

    # Regla: PERSECUCIÓN / CORRER
    elif any(x in txt for x in ["run", "correr", "chase", "persecución", "flee", "huyendo"]):
        s_shot = "Long Shot (Full Body)"
        s_angle = "Drone Aerial View (Establishing)" # O Low Angle
        s_lens = "24mm Lens (Dynamic)"
        s_sty = "Gritty Documentary Footage"

    # Regla: TERROR / MIEDO
    elif any(x in txt for x in ["terror", "fear", "panic", "miedo", "scream"]):
        s_angle = "Dutch Angle (Chaos/Tension)"
        s_lit = "Dramatic Low-Key (Chiaroscuro)"
        s_shot = "Close-Up (Face Focus)" # Aquí sí vale close up para la cara de miedo

    # Regla: DETALLE PEQUEÑO (Solo aquí usamos Macro)
    elif any(x in txt for x in ["insect", "eye", "drop", "insecto", "ojo", "detalle", "detail"]):
        s_lens = "100mm Macro (Micro Detail)"
        s_shot = "Extreme Close-Up (Macro Detail)"

    # 4. Aplicar al estado
    if s_shot in LIST_SHOT_TYPES: st.session_state['shot_select'] = s_shot
    if s_angle in LIST_ANGLES: st.session_state['angle_select'] = s_angle
    if s_lens in LIST_LENSES: st.session_state['lens_select'] = s_lens
    if s_lit in DEMO_LIGHTING: st.session_state['lit_select'] = s_lit
    if s_sty in DEMO_STYLES: st.session_state['sty_select'] = s_sty

def perform_reset():
    st.session_state['act_input'] = ""
    st.session_state['char_select'] = "-- Seleccionar Protagonista --"
    st.session_state['shot_select'] = LIST_SHOT_TYPES[0]
    st.session_state['angle_select'] = LIST_ANGLES[0]
    st.session_state['lens_select'] = LIST_LENSES[0]
    st.session_state['lit_select'] = DEMO_LIGHTING[0]
    st.session_state['sty_select'] = DEMO_STYLES[0]
    st.session_state['env_select'] = DEMO_ENVIRONMENTS[0]
    st.session_state['phy_select'] = "Neutral / Estudio"
    st.session_state['uploader_key'] += 1 
    st.session_state['generated_output'] = ""
    st.session_state['generated_explanation'] = ""

# --- 6. BUILDER ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = []
        self.explanation = []
        
    def add_section(self, text, explain=None):
        # Filtro de seguridad: no añadir textos vacíos o que sean solo puntos
        if text and text.strip() and text.strip() != ".":
            self.parts.append(text)
            if explain: self.explanation.append(explain)
            
    def get_prompt(self): return "\n\n".join(self.parts)

# --- 7. INTERFAZ: SIDEBAR ---
with st.sidebar:
    st.title("🔥 Config VFX")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    if st.button("🎲 Sugerir Look (Inteligente)"):
        # LEER DIRECTAMENTE DE SESSION STATE
        act = st.session_state.get('act_input', "")
        env = st.session_state.get('env_select', "")
        apply_smart_look(act, env)
        st.toast(f"✨ Look aplicado para: {act[:20]}...")
        st.rerun()

    if st.button("🗑️ Nueva Escena (Limpiar Todo)", type="secondary"):
        perform_reset()
        st.rerun()

    st.markdown("---")
    st.header("🖼️ Referencias")
    
    u_key = f"up_{st.session_state.uploader_key}"
    uploaded_file = st.file_uploader("Start Frame", type=["jpg", "png"], key=u_key)
    
    if uploaded_file:
        st.image(uploaded_file, caption="Ref")
        if 'last_img_name' not in st.session_state or st.session_state.last_img_name != uploaded_file.name:
            detected_ar = detect_and_set_ar(uploaded_file)
            st.session_state.last_img_name = uploaded_file.name
            if detected_ar:
                st.toast(f"📏 Formato detectado: {detected_ar}")
                st.rerun()
    
    uploaded_end = st.file_uploader("End Frame", type=["jpg", "png"], key=f"up_end_{st.session_state.uploader_key}")

# --- 8. INTERFAZ: PRINCIPAL ---
st.title("🎬 Grok Production Studio (VFX Edition)")
enhance_mode = st.toggle("🔥 INTENSIFICADOR VFX (Modo Auto-Excellence)", value=True)

t1, t2, t3, t4, t5 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cinematografía", "🎵 Audio & Voz"])

# Variables
final_sub = ""

with t1:
    c1, c2 = st.columns(2)
    with c1:
        char_opts = ["-- Seleccionar Protagonista --"]
        if uploaded_file: char_opts.insert(1, "📷 Sujeto de la Foto (Usar Referencia)")
        char_opts += list(st.session_state.characters.keys())
        
        # Validación
        if st.session_state.char_select not in char_opts:
            st.session_state.char_select = char_opts[0]
            
        char_sel = st.selectbox("Protagonista", char_opts, key="char_select")
        
        if "📷" in char_sel: final_sub = "MAIN SUBJECT: The character in the provided reference image"
        elif "--" in char_sel: final_sub = ""
        else: final_sub = f"MAIN SUBJECT: {st.session_state.characters.get(char_sel, '')}"

    with c2:
        tpl = st.selectbox("Plantilla Rápida", ["Seleccionar..."] + list(NARRATIVE_TEMPLATES.keys()))
        if tpl != "Seleccionar...":
            st.session_state['act_input'] = NARRATIVE_TEMPLATES[tpl]

    st.markdown("##### 📜 Descripción de la Acción")
    # Este widget escribe directamente en st.session_state['act_input']
    st.text_area("Describe la escena:", height=100, key="act_input")

with t2:
    c1, c2 = st.columns(2)
    with c1:
        e_sel = st.selectbox("Entorno", DEMO_ENVIRONMENTS, key="env_select")
        final_env = st.text_input("Custom Env", key="env_cust") if "Custom" in e_sel else e_sel
        
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
    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("1. Encuadre", LIST_SHOT_TYPES, key="shot_select")
        st.selectbox("4. Formato", DEMO_ASPECT_RATIOS, key="ar_select")
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
    
    st.markdown("---")
    with st.expander("🎹 Generador Musical (Suno AI)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
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
            s_lyr = st.text_area("Letra/Tema:", key="suno_lyr_input")

        if st.button("🎵 GENERAR PROMPT SUNO", key="btn_suno"):
            tags = []
            if suno_is_instrumental: tags.append("[Instrumental]")
            if s_gen: tags.append(f"[{translate_to_english(s_gen)}]")
            if s_mood: tags.append(f"[{translate_to_english(s_mood)}]")
            st.code(f"Style: {' '.join(tags)}\nStructure:\n{struc}\nLyrics:\n{translate_to_english(s_lyr)}", language="text")
            
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
    # RECUPERAR DATOS FRESCOS DEL ESTADO
    raw_action = st.session_state.get('act_input', "")
    translated_action = translate_to_english(raw_action)
    
    b = GrokVideoPromptBuilder()
    
    # 1. Cabecera
    if uploaded_file: b.add_section(f"Start Frame: '{uploaded_file.name}'", "✅ Img2Vid")
    if uploaded_end: b.add_section(f"End Frame: '{uploaded_end.name}'")
    if aud_file: b.add_section(f"AUDIO SOURCE: '{aud_file.name}'. ACTION: STRICT LIP-SYNC.", "🗣️ Lip Sync")
    b.add_section("Maintain strict visual consistency with source.")
    
    # 2. Narrativa
    narrative = []
    if final_sub: narrative.append(final_sub)
    if "Custom" not in final_ward and final_ward: narrative.append(f"WEARING: {final_ward}")
    if final_prop: narrative.append(f"HOLDING: {final_prop}")
    
    if translated_action:
        if enhance_mode:
            ints = "extreme motion blur, sweat, panic, dynamic chaos"
            if aud_file: ints += ", precise singing expression"
            narrative.append(f"VISCERAL ACTION SEQUENCE: {translated_action}. FEATURING: {ints}.")
            b.explanation.append("🔥 VFX Mode: Acción intensificada.")
        else:
            narrative.append(f"ACTION: {translated_action}.")
    
    if "Custom" not in final_env and final_env: b.add_section(f"ENVIRONMENT: {final_env}.")
    elif enhance_mode and not final_env: b.add_section("ENVIRONMENT: Cinematic atmospheric background.")
    
    b.add_section("\n".join(narrative))
    
    # 3. Cine Architect Style
    lit = st.session_state.lit_select
    lit = "" if "Neutral" in lit else lit.split('(')[0]
    
    shot = st.session_state.shot_select
    shot = "" if "Neutral" in shot else shot.split('(')[0]
    
    angle = st.session_state.angle_select
    angle = "" if "Neutral" in angle else angle.split('(')[0]
    
    lens = st.session_state.lens_select
    lens = "" if "Neutral" in lens else lens.split('(')[0]
    
    # Construir frase fluida
    cine_parts = []
    if lit: cine_parts.append(lit)
    if shot: cine_parts.append(f"Shot as a {shot}")
    if lens: cine_parts.append(f"on {lens}")
    if angle: cine_parts.append(f"from a {angle} perspective")
    
    if cine_parts: b.add_section(f"LIGHTING & CAMERA: {'. '.join(cine_parts)}.")
    
    sty = st.session_state.sty_select
    if "Neutral" not in sty: b.add_section(f"STYLE: {sty.split('(')[0]}")
    
    # 4. Audio & Params
    if mus_vid and "Neutral" not in mus_vid: b.add_section(f"SOUND DESIGN: {mus_vid}")
    
    ar_val = st.session_state.ar_select.split('(')[0].strip()
    b.add_section(f"--ar {ar_val}")
    
    res = b.get_prompt()
    st.session_state.generated_output = res
    st.session_state.generated_explanation = "\n".join(b.explanation)

if st.session_state.generated_output:
    st.markdown("---")
    if st.session_state.generated_explanation:
        st.markdown(f'<div class="strategy-box"><b>💡 Estrategia:</b><br>{st.session_state.generated_explanation}</div>', unsafe_allow_html=True)
    st.subheader("📝 Prompt Final")
    st.code(st.session_state.generated_output, language="text")
    st.caption("👆 Pulsa el icono de 'Copiar' para llevarlo a Grok.")