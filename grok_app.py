import streamlit as st
import re
import random
from PIL import Image

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Grok Production Studio", layout="wide", page_icon="🎬")

# --- ESTILOS CSS ---
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
        .strategy-box {{ background-color: #262730; border-left: 5px solid #00AA00; padding: 15px; border-radius: 5px; margin-top: 10px; color: #EEE; }}
        </style>
    """, unsafe_allow_html=True)

# --- DATOS Y LISTAS ---
DEFAULT_CHARACTERS = {
    "TON (Base)": "a striking male figure (185cm), razor-sharp jawline, textured modern quiff hair, athletic build",
    "FREYA (Base)": "a statuesque female survivor, intense hazel eyes, wet skin texture, strong features",
}
DEFAULT_PROPS = {
    "Guitarra": "a vintage electric guitar",
    "Kayak": "a carbon fiber sea kayak",
    "Linterna": "a high-lumen tactical flashlight"
}

# Listas Maestras
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🛶 Dusi River (Turbulent Rapids)", "🔴 Mars Surface (Red Dust)", "🌌 Deep Space (Nebula Background)", "🚀 ISS Space Station Interior", "🌊 Underwater Coral Reef", "❄️ Arctic Tundra (Snowstorm)", "🏙️ Cyberpunk City (Neon Rain)", "🌲 Mystic Forest (Fog)"]
DEMO_WARDROBE = ["✏️ Custom...", "torn sportswear and a cap", "tactical survival gear", "worn denim and leather jacket", "NASA EVA Spacesuit", "Tactical Wetsuit", "Elegant Suit"]
DEMO_PROPS_LIST = ["None", "✏️ Custom...", "🛶 Kayak Paddle", "🎸 Electric Guitar", "🔫 Blaster", "📱 Datapad", "🔦 Flashlight"]

# Cine Lists
LIST_SHOT_TYPES = ["Neutral (Auto)", "✏️ Custom...", "Extreme Long Shot (Gran Plano General)", "Long Shot (Plano General)", "Medium Shot (Plano Medio)", "Cowboy Shot (Plano Americano)", "Close-Up (Primer Plano)", "Extreme Close-Up (Macro Detalle)", "Over-The-Shoulder (Sobre el Hombro)"]
LIST_ANGLES = ["Neutral (Auto)", "✏️ Custom...", "Low Angle (Contrapicado)", "High Angle (Picado)", "Dutch Angle (Plano Holandés)", "Bird's Eye View (Vista de Pájaro)", "Drone Aerial View (FPV)", "POV (Point of View)"]
LIST_LENSES = ["Neutral (Auto)", "✏️ Custom...", "16mm Wide Angle", "35mm Prime (Cinema)", "50mm Lens (Human Eye)", "85mm f/1.4 (Portrait)", "100mm Macro", "Canon L-Series Style", "Vintage Anamorphic", "Fisheye Lens"]
DEMO_LIGHTING = ["Neutral (Auto)", "✏️ Custom...", "Harsh Golden Hour", "Dramatic Low-Key (Chiaroscuro)", "Soft Overcast", "Neon City Glow", "Stark Space Sunlight", "Underwater Caustics", "Bioluminescence"]
DEMO_STYLES = ["Neutral (Auto)", "Cinematic Film Still (Kodak Portra 800)", "Hyper-realistic VFX (Unreal 5)", "Nat Geo Wildlife", "Gritty Documentary", "Action Movie Screengrab", "Cyberpunk Digital Art", "Vintage VHS 90s"]
DEMO_ASPECT_RATIOS = ["21:9 (Cinematic)", "16:9 (Landscape)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

# Audio
DEMO_AUDIO_MOOD = ["Neutral", "✏️ Custom...", "Intense Suspense", "Epic Orchestral", "Silent (breathing only)", "Horror Drone", "Upbeat Rock", "Synthwave"]
DEMO_AUDIO_ENV = ["Neutral", "✏️ Custom...", "No Background", "Mars Wind", "River Roar", "Space Hum", "City Rain", "Jungle Sounds"]
DEMO_SFX = ["None", "✏️ Custom...", "Heavy breathing", "Footsteps", "Water splashing", "Explosion", "Laser blasts"]

# Physics
PHYSICS_LOGIC = {
    "Neutral / Estudio": [],
    "🌌 Espacio (Zero-G)": ["Zero-G floating", "No air resistance", "Vacuum silence", "Floating debris"],
    "🔴 Marte (Low-G)": ["Low gravity", "Red dust storms", "Heat distortion"],
    "🌊 Agua (Superficie)": ["Turbulent flow", "White foam", "Wet fabric", "Water splashes"],
    "🤿 Submarino": ["Weightless", "Light Caustics", "Bubbles", "Floating hair"],
    "❄️ Nieve": ["Falling snow", "Breath condensation", "Frost on lens"],
    "🌬️ Viento": ["High wind drag", "Fabric fluttering", "Motion blur"]
}

# --- GESTIÓN DE ESTADO (INICIALIZACIÓN) ---
if 'characters' not in st.session_state: st.session_state.characters = DEFAULT_CHARACTERS.copy()
if 'custom_props' not in st.session_state: st.session_state.custom_props = DEFAULT_PROPS.copy()
if 'history' not in st.session_state: st.session_state.history = []
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0 # Para resetear uploader

# Inicializar valores de los WIDGETS si no existen
# Esto es crucial para que st.session_state[key] funcione
widget_keys = {
    'act_input': "",
    'char_select': "-- Seleccionar Protagonista --",
    'shot_select': LIST_SHOT_TYPES[0],
    'angle_select': LIST_ANGLES[0],
    'lens_select': LIST_LENSES[0],
    'lit_select': DEMO_LIGHTING[0],
    'sty_select': DEMO_STYLES[0],
    'env_select': DEMO_ENVIRONMENTS[0],
    'ar_select': DEMO_ASPECT_RATIOS[1], # 16:9 Default
    'phy_select': "Neutral / Estudio"
}

for key, default in widget_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- LÓGICA DE SUGERENCIA Y RESET ---
def apply_suggestion(action_text, env_text):
    """Modifica directamente el Session State de los widgets"""
    txt = (action_text + " " + env_text).lower()
    
    # Defaults
    s_shot = random.choice(LIST_SHOT_TYPES[2:])
    s_angle = random.choice(LIST_ANGLES[2:])
    s_lens = random.choice(LIST_LENSES[2:])
    s_lit = random.choice(DEMO_LIGHTING[2:])
    s_sty = random.choice(DEMO_STYLES[1:])
    
    # Reglas Contextuales
    if "terror" in txt or "miedo" in txt:
        s_angle = "Dutch Angle (Plano Holandés)"
        s_lit = "Dramatic Low-Key (Chiaroscuro)"
        s_sty = "Gritty Documentary"
    elif "correr" in txt or "run" in txt or "acción" in txt:
        s_shot = "Long Shot (Plano General)"
        s_lens = "16mm Wide Angle"
        s_sty = "Action Movie Screengrab"
    elif "marte" in txt or "space" in txt:
        s_lit = "Stark Space Sunlight"
        s_lens = "Fisheye Lens"
        s_sty = "Hyper-realistic VFX (Unreal 5)"
    elif "agua" in txt or "water" in txt:
        s_lit = "Underwater Caustics"
        
    # APLICAR AL ESTADO (Esto actualiza visualmente los selectores al hacer rerun)
    st.session_state['shot_select'] = s_shot
    st.session_state['angle_select'] = s_angle
    st.session_state['lens_select'] = s_lens
    st.session_state['lit_select'] = s_lit
    st.session_state['sty_select'] = s_sty

def perform_reset():
    """Limpia todo"""
    st.session_state['act_input'] = ""
    st.session_state['char_select'] = "-- Seleccionar Protagonista --"
    st.session_state['shot_select'] = LIST_SHOT_TYPES[0]
    st.session_state['angle_select'] = LIST_ANGLES[0]
    st.session_state['lens_select'] = LIST_LENSES[0]
    st.session_state['lit_select'] = DEMO_LIGHTING[0]
    st.session_state['sty_select'] = DEMO_STYLES[0]
    st.session_state['env_select'] = DEMO_ENVIRONMENTS[0]
    st.session_state['phy_select'] = "Neutral / Estudio"
    st.session_state['uploader_key'] += 1 # Cambiar key resetea el file_uploader
    st.session_state['generated_output'] = ""
    st.session_state['generated_explanation'] = ""

def detect_ar(img_file):
    try:
        img = Image.open(img_file)
        w, h = img.size
        r = w/h
        if r > 1.8: return DEMO_ASPECT_RATIOS[0] # 21:9
        if r > 1.4: return DEMO_ASPECT_RATIOS[1] # 16:9
        if r < 0.8: return DEMO_ASPECT_RATIOS[2] # 9:16
        if r < 1.2: return DEMO_ASPECT_RATIOS[4] # 1:1
        return DEMO_ASPECT_RATIOS[3] # 4:3
    except: return DEMO_ASPECT_RATIOS[1]

# --- BUILDER ---
class PromptBuilder:
    def __init__(self):
        self.parts = []
        self.explanation = []
    
    def add(self, text, explain=None):
        if text:
            self.parts.append(text)
            if explain: self.explanation.append(explain)
            
    def get_prompt(self): return "\n\n".join(self.parts)

# --- INTERFAZ ---
with st.sidebar:
    st.title("🔥 Config VFX")
    apply_custom_styles(st.toggle("🌙 Modo Oscuro", value=True))
    
    # 1. SUGERIR (Ahora lee y escribe en el estado directamente)
    if st.button("🎲 Sugerir Look (Inteligente)"):
        # Leemos el texto actual
        curr_act = st.session_state.get('act_input', "")
        curr_env = st.session_state.get('env_select', "")
        apply_suggestion(curr_act, curr_env)
        st.toast("✨ Look aplicado según el contexto!")
        st.rerun() # Obligatorio para refrescar visualmente los selectores

    # 2. RESET (Funcionalidad de borrado real)
    if st.button("🗑️ Nueva Escena (Limpiar)", type="secondary"):
        perform_reset()
        st.rerun()

    st.markdown("---")
    st.header("🖼️ Referencias")
    # Uploader con key dinámica para poder resetearlo
    uploaded_file = st.file_uploader("Start Frame", type=["jpg", "png"], key=f"up_{st.session_state.uploader_key}")
    
    # Auto-Detect AR Logic
    if uploaded_file:
        st.image(uploaded_file, caption="Ref")
        # Si acabamos de subirlo (no estaba trackeado), detectamos AR
        if 'last_img' not in st.session_state or st.session_state.last_img != uploaded_file.name:
            detected_ar = detect_ar(uploaded_file)
            st.session_state['ar_select'] = detected_ar # Forzamos el widget de AR
            st.session_state.last_img = uploaded_file.name
            st.rerun()
    else:
        # Si se borra la imagen, limpiamos rastro
        if 'last_img' in st.session_state: del st.session_state.last_img

    uploaded_end = st.file_uploader("End Frame", type=["jpg", "png"], key=f"up_end_{st.session_state.uploader_key}")

# --- APP ---
st.title("🎬 Grok Production Studio (VFX Edition)")
enhance_mode = st.toggle("🔥 INTENSIFICADOR VFX (Modo Auto-Excellence)", value=True)

t1, t2, t3, t4, t5 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cinematografía", "🎵 Audio"])

# VARS GLOBALES PARA BUILDER
final_sub, final_act, final_env = "", "", ""

with t1:
    c1, c2 = st.columns(2)
    with c1:
        # SELECTOR DE PROTAGONISTA
        # Construimos opciones. La key 'char_select' mantiene la elección.
        opts = ["-- Seleccionar Protagonista --"]
        if uploaded_file: opts.insert(1, "📷 Sujeto de la Foto")
        opts += list(st.session_state.characters.keys())
        
        # Validar que la selección actual siga existiendo (por si borramos foto)
        if st.session_state.char_select not in opts:
            st.session_state.char_select = opts[0]
            
        char_sel = st.selectbox("Protagonista", opts, key="char_select")
        
        if "📷" in char_sel: final_sub = "MAIN SUBJECT: The character in the reference image"
        elif "--" in char_sel: final_sub = ""
        else: final_sub = f"MAIN SUBJECT: {st.session_state.characters.get(char_sel, '')}"

    with c2:
        # Template (Opcional, solo escribe si se selecciona uno nuevo)
        tpl = st.selectbox("Plantilla Rápida", ["Seleccionar..."] + list(NARRATIVE_TEMPLATES.keys()))
        if tpl != "Seleccionar...":
            # Inyectar texto en el estado del text_area
            st.session_state['act_input'] = NARRATIVE_TEMPLATES[tpl]
            # Resetear el selector de template para que no moleste
            # (Truco: no se puede resetear facil un selectbox sin key dinámica, pero lo dejamos así)

    st.markdown("##### 📜 Acción")
    # TEXT AREA VINCULADO AL ESTADO 'act_input'
    act_val = st.text_area("Describe la escena:", height=100, key="act_input")
    final_act = re.sub(r'[^\w\s.,!?-]', '', act_val) # Limpieza básica

with t2:
    c1, c2 = st.columns(2)
    with c1:
        env_sel = st.selectbox("Entorno", DEMO_ENVIRONMENTS, key="env_select")
        final_env = st.text_input("Custom Env", key="env_cust") if "Custom" in env_sel else env_sel
        
        prop_sel = st.selectbox("Objeto", DEMO_PROPS_LIST)
    with c2:
        ward_sel = st.selectbox("Vestuario", DEMO_WARDROBE)

with t3:
    st.markdown("##### ⚛️ Física")
    c1, c2 = st.columns(2)
    with c1: phy_med = st.selectbox("Medio Físico", list(PHYSICS_LOGIC.keys()), key="phy_select")
    with c2: phy_det = st.multiselect("Detalles", PHYSICS_LOGIC[phy_med])

with t4:
    # CINE PRO - Widgets vinculados a keys (shot_select, etc)
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
    st.info("Sube el audio real a la IA de video. Esto configura el prompt.")
    aud_file = st.file_uploader("Audio (MP3/WAV)", type=["mp3","wav"], key=f"aud_{st.session_state.uploader_key}")
    
    st.markdown("---")
    with st.expander("🎹 Suno AI Generator", expanded=False):
        c1, c2 = st.columns(2)
        with c1: 
            s_inst = st.toggle("Instrumental")
            s_dur = st.slider("Duración", 30, 240, 120)
        with c2:
            s_gen = st.text_input("Género")
            s_mood = st.text_input("Mood")
        if st.button("Generar Prompt Suno"):
            st.code(f"[{'Instrumental' if s_inst else s_gen}] {s_mood}\nLength: {s_dur}s")

# --- GENERACIÓN ---
if st.button("✨ GENERAR PROMPT PRO", type="primary"):
    builder = PromptBuilder()
    
    # 1. Cabecera e Imagen
    if uploaded_file:
        builder.add(f"Start Frame: '{uploaded_file.name}'", "✅ Img2Vid Activado")
    if uploaded_end:
        builder.add(f"End Frame: '{uploaded_end.name}'")
    if aud_file:
        builder.add(f"AUDIO SOURCE: '{aud_file.name}'. ACTION: STRICT LIP-SYNC.", "🗣️ Lip-Sync Activado")
    
    builder.add("Maintain strict visual consistency.")
    
    # 2. Narrativa
    narrative = []
    if final_sub: narrative.append(final_sub)
    if "Custom" not in ward_sel: narrative.append(f"WEARING: {ward_sel}")
    if "Custom" not in prop_sel and "None" not in prop_sel: narrative.append(f"HOLDING: {prop_sel}")
    
    if final_act:
        if enhance_mode:
            ints = "extreme motion blur, sweat, panic, dynamic chaos"
            if aud_file: ints += ", singing expression"
            narrative.append(f"VISCERAL ACTION: {final_act}. FEATURING: {ints}.")
            builder.explanation.append("🔥 VFX Mode: Acción intensificada.")
        else:
            narrative.append(f"ACTION: {final_act}.")
    
    if "Custom" not in final_env: narrative.append(f"ENVIRONMENT: {final_env}.")
    elif enhance_mode and not final_env: narrative.append("ENVIRONMENT: Cinematic background.")
    
    builder.add("\n".join(narrative))
    
    # 3. Atmósfera y Física
    atm = []
    lit = st.session_state.lit_select
    if "Neutral" not in lit and "Custom" not in lit: atm.append(f"LIGHTING: {lit}")
    elif enhance_mode: atm.append("LIGHTING: Dramatic tone-matching.")
    
    if phy_det: atm.append(f"PHYSICS: {', '.join(phy_det)}")
    builder.add(". ".join(atm))
    
    # 4. Cine
    cine = []
    for k in ['shot_select', 'angle_select', 'lens_select']:
        val = st.session_state[k]
        if "Neutral" not in val and "Custom" not in val: cine.append(val.split('(')[0])
    
    sty = st.session_state.sty_select
    if "Neutral" not in sty: cine.append(f"STYLE: {sty}")
    
    if cine: builder.add(f"CINEMATOGRAPHY: {', '.join(cine)}.")
    elif enhance_mode: builder.add("CINEMATOGRAPHY: High production value.")
    
    # 5. Params
    ar_val = st.session_state.ar_select.split('(')[0].strip()
    builder.add(f"--ar {ar_val}")
    
    res = builder.get_prompt()
    st.session_state.generated_output = res
    st.session_state.generated_explanation = "\n".join(builder.explanation)

# --- RESULTADO ---
if st.session_state.generated_output:
    st.markdown("---")
    if st.session_state.generated_explanation:
        st.markdown(f'<div class="strategy-box"><b>💡 Estrategia:</b><br>{st.session_state.generated_explanation}</div>', unsafe_allow_html=True)
    st.subheader("📝 Prompt Final")
    st.code(st.session_state.generated_output, language="text")