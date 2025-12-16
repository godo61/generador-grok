import streamlit as st
import re
import random
from PIL import Image

# --- 1. CONFIGURACIÓN ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

st.set_page_config(page_title="Grok Production Studio", layout="wide", page_icon="🎬")

# --- 2. ESTILOS ---
def apply_custom_styles(dark_mode=False):
    bg_color = "#0E1117" if dark_mode else "#FFFFFF"
    text_color = "#FAFAFA" if dark_mode else "#31333F"
    tab_bg = "#1E1E24" if dark_mode else "#F0F2F6"

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background-color: {bg_color}; color: {text_color}; }}
        [data-testid="stSidebar"] {{ background-color: {tab_bg}; }}
        textarea {{ font-size: 1.1rem !important; font-family: monospace !important; border-left: 5px solid #FF4B4B !important; }}
        .big-warning {{ background-color: #FF4B4B20; border: 1px solid #FF4B4B; padding: 15px; border-radius: 5px; margin-bottom: 10px; }}
        .strategy-box {{ background-color: #262730; border-left: 5px solid #00AA00; padding: 15px; border-radius: 5px; margin-top: 10px; color: #EEE; font-style: italic; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. DEFINICIONES DE DATOS (MIVIDAS AL PRINCIPIO) ---
# Es crucial que esto esté aquí antes de pintar la interfaz
DEFAULT_CHARACTERS = {
    "TON (Base)": "a striking male figure (185cm), razor-sharp jawline, textured modern quiff hair, athletic build",
    "FREYA (Base)": "a statuesque female survivor, intense hazel eyes, wet skin texture, strong features",
}
DEFAULT_PROPS = {"Guitarra": "vintage electric guitar", "Kayak": "carbon fiber kayak", "Linterna": "tactical flashlight"}

# Listas Visuales
DEMO_STYLES = ["Neutral (Auto)", "Cinematic Film Still (Kodak Portra 800)", "Hyper-realistic VFX Render (Unreal 5)", "National Geographic Wildlife Style", "Gritty Documentary Footage", "Action Movie Screengrab", "Cyberpunk Digital Art", "Vintage VHS 90s"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🛶 Dusi River (Turbulent Rapids)", "🔴 Mars Surface (Red Dust)", "🌌 Deep Space (Nebula Background)", "🚀 ISS Space Station Interior", "🌊 Underwater Coral Reef", "❄️ Arctic Tundra (Snowstorm)", "🏙️ Cyberpunk City (Neon Rain)", "🌲 Mystic Forest (Fog)"]
DEMO_WARDROBE = ["✏️ Custom...", "torn sportswear and a cap", "tactical survival gear", "worn denim and leather jacket", "NASA EVA Spacesuit", "Tactical Wetsuit", "Elegant Suit"]
DEMO_PROPS_LIST = ["None", "✏️ Custom...", "🛶 Kayak Paddle", "🎸 Electric Guitar", "🔫 Blaster", "📱 Datapad", "🔦 Flashlight"]

# Cine Lists
LIST_SHOT_TYPES = ["Neutral (Auto)", "Extreme Long Shot (Epic Scale)", "Long Shot (Full Body)", "Medium Shot (Waist Up)", "Close-Up (Face Focus)", "Extreme Close-Up (Macro Detail)"]
LIST_ANGLES = ["Neutral (Auto)", "Low Angle (Heroic/Ominous)", "High Angle (Vulnerable)", "Dutch Angle (Chaos/Tension)", "Bird's Eye View (Top-Down)", "Drone Aerial View (Establishing)"]
LIST_LENSES = ["Neutral (Auto)", "16mm Wide Angle (Expansive)", "35mm Prime (Street/Docu)", "50mm Lens (Natural Eye)", "85mm f/1.4 (Portrait Bokeh)", "100mm Macro (Micro Detail)", "Fisheye (Distorted)"]
DEMO_LIGHTING = ["Neutral (Auto)", "Harsh Golden Hour", "Dramatic Low-Key (Chiaroscuro)", "Soft Overcast (Diffusion)", "Neon City Glow (Cyberpunk)", "Stark Space Sunlight"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "21:9 (Cinematic)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

# Audio
DEMO_AUDIO_MOOD = ["Neutral", "✏️ Custom...", "Intense Suspense", "Epic Orchestral", "Silent (breathing only)", "Horror Drone", "Upbeat Rock", "Synthwave"]
DEMO_SFX = ["None", "✏️ Custom...", "Heavy breathing", "Footsteps", "Water splashing", "Explosion", "Laser blasts"]
VOICE_TYPES = ["Neutral", "✏️ Custom...", "Male (Deep)", "Female (Soft)", "Child", "Elderly", "Robot/AI", "Monster/Growl"]
VOICE_ACCENTS = ["Neutral", "✏️ Custom...", "American (Standard)", "British (RP)", "Spanish (Castilian)", "Mexican", "French Accent", "Russian Accent"]
VOICE_EMOTIONS = ["Neutral", "✏️ Custom...", "Angry / Shouting", "Sad / Crying", "Whispering / Secretive", "Happy / Excited", "Sarcastic", "Terrified", "Flirty", "Passionate Singing"]

# GEM EXPANSION (Cerebro Creativo)
GEM_EXPANSION_PACK = {
    "run": "sweat and mud on a face contorted in absolute panic looking back, heavy motion blur on extremities",
    "correr": "sweat and mud on a face contorted in absolute panic looking back, heavy motion blur on extremities",
    "chase": "a colossal, ancient beast with jagged scales breaches the ground, kicking up a massive chaotic cloud of debris",
    "persecución": "a colossal, ancient beast with jagged scales breaches the ground, kicking up a massive chaotic cloud of debris",
    "huyendo": "sprinting desperately directly toward the camera, adrenaline fueled atmosphere",
    "monster": "terrifying subterranean beast, organic textures, massive scale, ominous presence",
    "mamut": "ancient titanic mammoth, matted fur texture, massive tusks destroying the environment, earth-shaking impact",
    "transform": "surreal visual metamorphosis, plastic texture cracking and morphing into realistic organic skin, glowing energy boundaries",
    "elefante": "hyper-realistic skin texture, wrinkled grey hide, imposing weight",
    "plastic": "shiny synthetic polymer texture, artificial reflection"
}

# Plantillas
NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🎤 Performance Musical (Lip Sync)": "Close-up on the subject singing passionately. Mouth moves in perfect sync with the audio. Emotions range from intense focus to release.",
    "🏃 Persecución (Sujeto vs Monstruo)": "The subject is sprinting desperately towards the camera, face contorted in panic. Behind them, a colossal creature is charging, kicking up debris.",
    "🧟 Transformación Súbita": "At second 0, the scene is static. Suddenly, the inanimate object behind the subject rapidly transforms into a massive, living threat.",
}

# Física (DEFINIDA AQUÍ PARA EVITAR NAME ERROR)
PHYSICS_LOGIC = {
    "Neutral / Estudio": [],
    "🌌 Espacio (Zero-G)": ["Zero-G floating", "No air resistance", "Vacuum silence"],
    "🔴 Marte (Low-G)": ["Low gravity", "Red dust storms", "Heat distortion"],
    "🌊 Agua (Superficie)": ["Turbulent flow", "White foam", "Wet fabric"],
    "🤿 Submarino": ["Weightless", "Light Caustics", "Bubbles"],
    "❄️ Nieve": ["Falling snow", "Breath condensation", "Frost on lens"],
    "🌬️ Viento": ["High wind drag", "Fabric fluttering", "Motion blur"]
}

# --- 4. GESTIÓN DE ESTADO ---
init_vars = {
    'generated_output': "",
    'generated_explanation': "",
    'characters': DEFAULT_CHARACTERS.copy(),
    'custom_props': DEFAULT_PROPS.copy(),
    'history': [],
    'uploader_key': 0,
    # Widgets
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

# --- 5. FUNCIONES ---
def translate_to_english(text):
    if not text or not str(text).strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try: return GoogleTranslator(source='auto', target='en').translate(str(text))
        except: return str(text)
    return str(text)

def expand_prompt_like_gem(text):
    """Inyecta creatividad basada en keywords"""
    txt_lower = text.lower()
    expansions = []
    for key, phrase in GEM_EXPANSION_PACK.items():
        if key in txt_lower:
            expansions.append(phrase)
    return ". ".join(expansions)

def detect_ar(image_file):
    try:
        img = Image.open(image_file)
        w, h = img.size
        ratio = w / h
        if ratio > 1.5: return 0 
        elif ratio < 0.8: return 2 
        return 0 
    except: return 0

# --- 6. INTERFAZ: SIDEBAR ---
with st.sidebar:
    st.title("🔥 Config VFX")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    if st.button("🗑️ Resetear Todo"):
        st.session_state.generated_output = ""
        st.session_state.uploader_key += 1
        st.rerun()

    st.markdown("---")
    st.header("🖼️ Referencias")
    u_key = f"up_{st.session_state.uploader_key}"
    uploaded_file = st.file_uploader("Start Frame", type=["jpg", "png"], key=u_key)
    uploaded_end = st.file_uploader("End Frame", type=["jpg", "png"], key=f"up_end_{st.session_state.uploader_key}")
    
    ar_index = 0
    if uploaded_file:
        st.image(uploaded_file, caption="Ref")
        ar_index = detect_ar(uploaded_file)

# --- 7. MAIN INTERFACE (FORMULARIO) ---
st.title("🎬 Grok Production Studio (Architect Engine)")

# INICIO DEL FORMULARIO - ¡AQUÍ ESTÁ LA CLAVE DE LA PERSISTENCIA!
with st.form("main_form"):
    
    t1, t2, t3, t4, t5 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cinematografía", "🎵 Audio"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            char_opts = ["-- Seleccionar Protagonista --"]
            if uploaded_file: char_opts.insert(1, "📷 Sujeto de la Foto")
            char_opts += list(st.session_state.characters.keys())
            char_sel = st.selectbox("Protagonista", char_opts)
        
        with c2:
            enhance_mode = st.checkbox("🔥 Modo Architect (Expandir creativamente)", value=True)

        st.markdown("##### 📜 Descripción de la Escena")
        # Este Text Area está DENTRO del form, así que no envía datos hasta el submit.
        # No se borrará solo.
        action_input = st.text_area("Describe la acción (Español o Inglés):", height=120, placeholder="Ej: Un mamut gigante persigue al protagonista...")

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            env_sel = st.selectbox("Entorno", DEMO_ENVIRONMENTS)
            env_cust = st.text_input("Entorno Personalizado") if "Custom" in env_sel else ""
            prop_sel = st.selectbox("Objeto", DEMO_PROPS_LIST)
        with c2:
            ward_sel = st.selectbox("Vestuario", DEMO_WARDROBE)

    with t3:
        # AHORA PHYSICS_LOGIC ESTÁ DEFINIDO ARRIBA, NO DARÁ ERROR
        c1, c2 = st.columns(2)
        with c1: phy_med = st.selectbox("Física", list(PHYSICS_LOGIC.keys()))
        with c2: phy_det = st.multiselect("Detalles Físicos", PHYSICS_LOGIC[phy_med])

    with t4:
        c1, c2, c3 = st.columns(3)
        with c1:
            shot_sel = st.selectbox("Plano", LIST_SHOT_TYPES)
            ar_sel = st.selectbox("Formato", DEMO_ASPECT_RATIOS, index=ar_index)
        with c2:
            angle_sel = st.selectbox("Ángulo", LIST_ANGLES)
            lit_sel = st.selectbox("Iluminación", DEMO_LIGHTING)
        with c3:
            lens_sel = st.selectbox("Lente", LIST_LENSES)
            style_sel = st.selectbox("Estilo", DEMO_STYLES)

    with t5:
        st.info("Audio para Lip-Sync")
        has_audio = st.checkbox("✅ Activar instrucciones de Lip-Sync (Audio externo)")
        
        st.markdown("---")
        st.caption("Configuración Suno (Generador de Texto)")
        s_genre = st.text_input("Género Musical")
        s_mood = st.text_input("Mood Musical")

    # --- BOTÓN DE ENVÍO ---
    # ESTE BOTÓN DEBE ESTAR DENTRO DEL BLOQUE 'with st.form(...):'
    submitted = st.form_submit_button("✨ GENERAR PROMPT (ARCHITECT)")

# --- 8. PROCESAMIENTO (FUERA DEL FORM) ---
if submitted:
    # 1. Traducción
    eng_action = translate_to_english(action_input)
    
    # 2. Expansión Creativa (Gem Engine)
    gem_additions = ""
    if enhance_mode and eng_action:
        # Pasamos texto original y traducido para asegurar keywords
        full_text = action_input + " " + eng_action
        gem_additions = expand_prompt_like_gem(full_text)
    
    # 3. Construcción
    prompt_parts = []
    explanations = []

    # Cabecera
    if uploaded_file: 
        prompt_parts.append(f"Start Frame: '{uploaded_file.name}'")
        explanations.append("✅ Img2Vid activo.")
    if uploaded_end: prompt_parts.append(f"End Frame: '{uploaded_end.name}'")
    if has_audio: prompt_parts.append("AUDIO SOURCE: [User File]. ACTION: STRICT LIP-SYNC.")
    prompt_parts.append("Maintain strict visual consistency.")

    # Sujeto
    char_text = ""
    if "📷" in char_sel: char_text = "The subject in the reference image"
    elif "--" not in char_sel: char_text = st.session_state.characters[char_sel]
    
    ward_text = f"wearing {ward_sel}" if "Custom" not in ward_sel and ward_sel else ""
    
    # Acción + Expansión (GEM LOGIC)
    final_action_block = ""
    if eng_action:
        base = f"VISCERAL ACTION: {eng_action}"
        if gem_additions:
            # Si hay expansión del Gem, la añadimos con fuerza
            base += f". DETAILS: {gem_additions}"
            explanations.append("🧬 'Gem Engine': Detalles viscerales inyectados.")
        else:
            base += ". FEATURING: cinematic depth, highly detailed textures, dynamic lighting."
        final_action_block = base
    else:
        final_action_block = "ACTION: Cinematic idle motion, subtle breathing, hyper-realistic texture detail."
        explanations.append("⚠️ Sin texto de acción: Usando 'Idle Motion'.")

    # Montaje
    narrative = []
    if char_text: narrative.append(f"SUBJECT: {char_text} {ward_text}.")
    narrative.append(final_action_block)
    
    # Entorno
    env_final = env_cust if 'env_cust' in locals() and env_cust else (env_sel if "Custom" not in env_sel else "")
    if env_final: narrative.append(f"ENVIRONMENT: {env_final}.")
    
    prompt_parts.append("\n".join(narrative))

    # Cine Técnica
    tech = []
    # Auto-selección inteligente si está en 'Neutral'
    is_monster = "monster" in gem_additions or "mamut" in eng_action.lower()
    is_morph = "morph" in gem_additions or "transform" in eng_action.lower()
    
    # Lente
    if "Neutral" not in lens_sel: tech.append(f"Shot on {lens_sel}")
    elif is_monster: tech.append("Shot on 16mm Wide Angle (to emphasize scale)")
    elif is_morph: tech.append("Shot on 50mm Prime (Focus on details)")
    
    # Angulo
    if "Neutral" not in angle_sel: tech.append(f"from a {angle_sel} perspective")
    elif is_monster: tech.append("from a Low Angle (Ominous) perspective")
    
    # Luz
    if "Neutral" not in lit_sel: tech.append(f"Lighting: {lit_sel}")
    elif is_morph: tech.append("Lighting: Dramatic Chiaroscuro")
    else: tech.append("Lighting: Cinematic Dramatic")
    
    # Estilo
    if "Neutral" not in style_sel: tech.append(f"Style: {style_sel}")
    else: tech.append("Style: Hyper-realistic VFX Render")
    
    prompt_parts.append(f"CINEMATOGRAPHY: {'. '.join(tech)}.")
    
    # Params
    prompt_parts.append(f"--ar {ar_sel.split(' ')[0]}")

    # Guardar
    st.session_state.generated_output = "\n\n".join(prompt_parts)
    st.session_state.generated_explanation = "\n".join(explanations)

# --- 9. MOSTRAR RESULTADO ---
if st.session_state.generated_output:
    st.markdown("---")
    if st.session_state.generated_explanation:
        st.markdown(f'<div class="strategy-box"><b>💡 Estrategia del Prompt:</b><br>{st.session_state.generated_explanation}</div>', unsafe_allow_html=True)
    
    st.subheader("📝 Prompt Final")
    st.code(st.session_state.generated_output, language="text")