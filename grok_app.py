import streamlit as st
import re
import random
from PIL import Image

# --- 1. CONFIGURACIÓN (PRIMERA LÍNEA OBLIGATORIA) ---
st.set_page_config(page_title="Grok Production Studio", layout="wide", page_icon="🎬")

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# --- 2. GESTIÓN DE MEMORIA SEGURA (CRÍTICO) ---
# Inicializamos las variables críticas SIEMPRE al principio.
# Usamos un diccionario directo para evitar errores de lógica.
defaults = {
    'generated_output': "", 
    'generated_explanation': "",
    'characters': {"TON (Base)": "striking male figure...", "FREYA (Base)": "statuesque female survivor..."}, 
    'custom_props': {"Guitarra": "vintage electric guitar", "Kayak": "carbon fiber kayak"},
    'uploader_key': 0, 
    'act_input': "",
    'last_img_name': ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 3. LISTAS MAESTRAS ---
DEMO_STYLES = ["Neutral (Auto)", "Cinematic Film Still (Kodak Portra 800)", "Hyper-realistic VFX Render (Unreal 5)", "National Geographic Wildlife Style", "Gritty Documentary Footage", "Action Movie Screengrab", "Cyberpunk Digital Art", "Vintage VHS 90s"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🛶 Dusi River (Turbulent Rapids)", "🔴 Mars Surface (Red Dust)", "🌌 Deep Space (Nebula)", "🚀 ISS Interior", "🌊 Underwater Reef", "❄️ Arctic Tundra", "🏙️ Cyberpunk City", "🌲 Mystic Forest"]
DEMO_WARDROBE = ["✏️ Custom...", "Short-sleeve grey t-shirt", "Short-sleeve tactical shirt", "Long-sleeve denim shirt", "NASA EVA Spacesuit", "Tactical Wetsuit", "Elegant Suit"]
DEMO_PROPS_LIST = ["None", "✏️ Custom...", "🛶 Kayak Paddle", "🎸 Electric Guitar", "🔫 Blaster", "📱 Datapad", "🔦 Flashlight"]

LIST_SHOT_TYPES = ["Neutral (Auto)", "Extreme Long Shot (Epic Scale)", "Long Shot (Full Body)", "Medium Shot (Waist Up)", "Close-Up (Face Focus)", "Extreme Close-Up (Macro Detail)"]
LIST_ANGLES = ["Neutral (Auto)", "Low Angle (Heroic/Ominous)", "High Angle (Vulnerable)", "Dutch Angle (Chaos/Tension)", "Bird's Eye View (Top-Down)", "Drone Aerial View (Establishing)"]
LIST_LENSES = ["Neutral (Auto)", "16mm Wide Angle (Expansive)", "35mm Prime (Street)", "50mm Lens (Natural)", "85mm f/1.4 (Portrait)", "100mm Macro (Detail)", "Fisheye (Distorted)"]
DEMO_LIGHTING = ["Neutral (Auto)", "Harsh Golden Hour", "Dramatic Low-Key (Chiaroscuro)", "Soft Overcast (Diffusion)", "Neon City Glow", "Stark Space Sunlight"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "21:9 (Cinematic)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

GEM_EXPANSION_PACK = {
    "run": "sweat and mud on a face contorted in panic, heavy motion blur",
    "correr": "sweat and mud on a face contorted in panic, heavy motion blur",
    "chase": "colossal beast breaching the ground, chaotic debris cloud",
    "persecución": "colossal beast breaching the ground, chaotic debris cloud",
    "transform": "surreal metamorphosis, plastic cracking into organic skin, glowing energy",
    "monster": "terrifying subterranean beast, organic textures, massive scale",
    "mamut": "ancient titanic mammoth, matted fur texture, massive tusks",
    "plastic": "shiny synthetic polymer texture, artificial reflection"
}

NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🎤 Performance Musical": "Close-up on subject singing passionately...",
    "🏃 Persecución (Sujeto vs Monstruo)": "The subject is sprinting desperately towards the camera...",
    "🐘 Transformación (Morphing)": "A small plastic toy elephant on a table begins to morph rapidly...",
}

PHYSICS_LOGIC = {
    "Neutral / Estudio": [],
    "🌌 Espacio": ["Zero-G floating", "No air resistance"],
    "🔴 Marte": ["Low gravity", "Red dust storms"],
    "🌊 Agua": ["Turbulent flow", "Wet fabric"],
    "🤿 Submarino": ["Weightless", "Light Caustics"],
    "❄️ Nieve": ["Falling snow", "Breath condensation"],
    "🌬️ Viento": ["High wind drag", "Fabric fluttering"]
}

# --- 4. FUNCIONES HELPER ---
def get_safe_index(options, key):
    """Devuelve un índice seguro para evitar el flash rojo."""
    current_val = st.session_state.get(key)
    try:
        return options.index(current_val)
    except (ValueError, KeyError, TypeError):
        return 0

def translate_to_english(text):
    if not text or not str(text).strip(): return ""
    try:
        if TRANSLATOR_AVAILABLE: return GoogleTranslator(source='auto', target='en').translate(str(text))
        return str(text)
    except: return str(text)

def detect_ar(image_file):
    try:
        img = Image.open(image_file)
        w, h = img.size
        ratio = w / h
        if ratio > 1.5: return 0 
        elif ratio < 0.8: return 2
        return 0
    except: return 0

def apply_smart_look_logic(text):
    txt = text.lower()
    res = {
        'shot': "Medium Shot (Waist Up)",
        'angle': "Neutral (Auto)",
        'lens': "35mm Prime (Street)",
        'lit': "Cinematic Lighting",
        'sty': "Cinematic Film Still"
    }
    if any(x in txt for x in ["transform", "morph", "cambia", "plástico"]):
        res['lens'] = "50mm Lens (Natural)"
        res['sty'] = "Hyper-realistic VFX Render (Unreal 5)"
        res['lit'] = "Dramatic Low-Key (Chiaroscuro)"
        res['shot'] = "Close-Up (Face Focus)"
    elif any(x in txt for x in ["mamut", "monster", "gigante"]):
        res['shot'] = "Extreme Long Shot (Epic Scale)"
        res['angle'] = "Low Angle (Heroic/Ominous)"
        res['lens'] = "16mm Wide Angle (Expansive)"
        res['lit'] = "Harsh Golden Hour"
    elif any(x in txt for x in ["run", "correr", "persecución"]):
        res['shot'] = "Long Shot (Full Body)"
        res['angle'] = "Drone Aerial View"
        res['lens'] = "Fisheye (Distorted)"
        res['sty'] = "Action Movie Screengrab"
    return res

def perform_smart_update():
    action = st.session_state.get('act_input', "")
    suggestions = apply_smart_look_logic(action)
    
    mappings = [
        ('shot_select', LIST_SHOT_TYPES),
        ('angle_select', LIST_ANGLES),
        ('lens_select', LIST_LENSES),
        ('lit_select', DEMO_LIGHTING),
        ('sty_select', DEMO_STYLES)
    ]
    
    for key, options in mappings:
        target_val = ""
        if key == 'shot_select': target_val = suggestions['shot']
        elif key == 'angle_select': target_val = suggestions['angle']
        elif key == 'lens_select': target_val = suggestions['lens']
        elif key == 'lit_select': target_val = suggestions['lit']
        elif key == 'sty_select': target_val = suggestions['sty']
        
        for opt in options:
            if target_val.split('(')[0] in opt:
                st.session_state[key] = opt
                break

def perform_reset():
    st.session_state['act_input'] = ""
    # Borramos claves de widgets para forzar reinicio limpio
    keys_to_clear = ['char_select', 'shot_select', 'angle_select', 'lens_select', 'lit_select', 'sty_select', 'env_select', 'ar_select', 'ward_select', 'phy_select']
    for k in keys_to_clear:
        if k in st.session_state: del st.session_state[k]
        
    st.session_state['uploader_key'] += 1 
    st.session_state['generated_output'] = ""
    st.session_state['generated_explanation'] = ""

# --- 5. BUILDER ---
class PromptBuilder:
    def __init__(self):
        self.parts = []
        self.explanation = []
    
    def add(self, text, explain=None):
        if text and text.strip() and text.strip() != ".":
            self.parts.append(text)
            if explain: self.explanation.append(explain)
    
    def expand_flavor(self, text):
        flavors = []
        txt = text.lower()
        for k, v in GEM_EXPANSION_PACK.items():
            if k in txt: flavors.append(v)
        return ". ".join(flavors)

    def get_result(self): return "\n\n".join(self.parts)

# --- 6. INTERFAZ ---
def apply_custom_styles(dark_mode=False):
    bg_color = "#0E1117" if dark_mode else "#FFFFFF"
    text_color = "#FAFAFA" if dark_mode else "#31333F"
    tab_bg = "#1E1E24" if dark_mode else "#F0F2F6"

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background-color: {bg_color}; color: {text_color}; }}
        [data-testid="stSidebar"] {{ background-color: {tab_bg}; }}
        textarea {{ font-size: 1.1rem !important; font-family: monospace !important; border-left: 5px solid #FF4B4B !important; }}
        .strategy-box {{ background-color: #262730; border-left: 5px solid #00AA00; padding: 15px; border-radius: 5px; margin-top: 10px; color: #EEE; font-style: italic; }}
        .stButton button {{ width: 100%; }}
        </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🔥 Config VFX")
    apply_custom_styles(st.toggle("🌙 Modo Oscuro", value=True))
    
    if st.button("🎲 Sugerir Look (Aplicar)"):
        perform_smart_update()
        st.toast("✨ Selectores actualizados.")
        st.rerun()

    if st.button("🗑️ Nueva Escena"):
        perform_reset()
        st.rerun()

    st.markdown("---")
    st.header("🖼️ Referencias")
    u_key = f"up_{st.session_state.uploader_key}"
    uploaded_file = st.file_uploader("Start Frame", type=["jpg", "png"], key=u_key)
    
    if uploaded_file:
        st.image(uploaded_file, caption="Ref")
        if 'last_img_name' not in st.session_state or st.session_state.last_img_name != uploaded_file.name:
            ridx = detect_ar(uploaded_file)
            st.session_state.ar_select = DEMO_ASPECT_RATIOS[ridx]
            st.session_state.last_img_name = uploaded_file.name
            st.rerun()
            
    uploaded_end = st.file_uploader("End Frame", type=["jpg", "png"], key=f"up_end_{st.session_state.uploader_key}")

# --- 7. MAIN ---
st.title("🎬 Grok Production Studio (V77)")

with st.form("main_form"):
    
    t1, t2, t3, t4, t5, t6 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cinematografía", "🎵 Audio (Suno)", "📘 Guía"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            char_opts = ["-- Seleccionar Protagonista --"]
            if uploaded_file: char_opts.insert(1, "📷 Sujeto de la Foto")
            char_opts += list(st.session_state.characters.keys())
            
            # USO DEL ÍNDICE SEGURO
            char_idx = get_safe_index(char_opts, 'char_select')
            st.selectbox("Protagonista", char_opts, index=char_idx, key="char_select")
            
            # Recuperación segura del valor
            char_sel = st.session_state.get('char_select', char_opts[0])
            if "📷" in char_sel: final_sub = "MAIN SUBJECT: The character in the provided reference image"
            elif "--" in char_sel: final_sub = ""
            else: final_sub = f"MAIN SUBJECT: {st.session_state.characters.get(char_sel, '')}"

        with c2:
            enhance_mode = st.checkbox("🔥 Modo Architect (Expandir descripción)", value=True)

        col_tmpl, col_btn = st.columns([3, 1])
        with col_tmpl:
            tpl_idx = get_safe_index(["Seleccionar..."] + list(NARRATIVE_TEMPLATES.keys()), 'tpl_select')
            tpl = st.selectbox("Plantilla Rápida", ["Seleccionar..."] + list(NARRATIVE_TEMPLATES.keys()), index=tpl_idx, key="tpl_select")
        with col_btn:
            if st.form_submit_button("📥 Pegar"):
                if tpl != "Seleccionar...":
                    st.session_state['act_input'] = NARRATIVE_TEMPLATES[tpl]
                    st.rerun()

        st.markdown("##### 📜 Descripción de la Acción")
        current_text_input = st.text_area("Describe la escena:", height=100, key="act_input")

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            e_idx = get_safe_index(DEMO_ENVIRONMENTS, 'env_select')
            e_sel = st.selectbox("Entorno", DEMO_ENVIRONMENTS, index=e_idx, key="env_select")
            final_env = st.text_input("Custom Env", key="env_cust") if "Custom" in e_sel else e_sel
            
            all_props = ["None", "✏️ Custom..."] + list(st.session_state.custom_props.keys()) + DEMO_PROPS_LIST[2:]
            p_idx = get_safe_index(all_props, 'prop_select')
            prop_sel = st.selectbox("Objeto", all_props, index=p_idx, key="prop_select")
            
            if prop_sel in st.session_state.custom_props: final_prop = st.session_state.custom_props[prop_sel]
            elif "Custom" in prop_sel: final_prop = translate_to_english(st.text_input("Objeto Nuevo", key="np"))
            elif "None" not in prop_sel: final_prop = prop_sel
            else: final_prop = ""

        with c2:
            st.info("💡 Consejo: Elige manga corta/larga explícitamente.")
            w_idx = get_safe_index(DEMO_WARDROBE, 'ward_select')
            ward_sel = st.selectbox("Vestuario", DEMO_WARDROBE, index=w_idx, key="ward_select")
            if "Custom" in ward_sel: final_ward = translate_to_english(st.text_input("Ropa Custom", key="wc"))
            else: final_ward = ward_sel

    with t3:
        c1, c2 = st.columns(2)
        with c1: 
            pm_idx = get_safe_index(list(PHYSICS_LOGIC.keys()), 'phy_select')
            phy_med = st.selectbox("Medio Físico", list(PHYSICS_LOGIC.keys()), index=pm_idx, key="phy_select")
        with c2: 
            phy_det = st.multiselect("Detalles", PHYSICS_LOGIC[phy_med])

    with t4:
        st.info("💡 Usa 'Sugerir Look' en la barra lateral para configurar esto automáticamente.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.selectbox("1. Encuadre", LIST_SHOT_TYPES, index=get_safe_index(LIST_SHOT_TYPES, 'shot_select'), key="shot_select")
            st.selectbox("4. Formato", DEMO_ASPECT_RATIOS, index=get_safe_index(DEMO_ASPECT_RATIOS, 'ar_select'), key="ar_select")
        with c2:
            st.selectbox("2. Ángulo", LIST_ANGLES, index=get_safe_index(LIST_ANGLES, 'angle_select'), key="angle_select")
            st.selectbox("5. Iluminación", DEMO_LIGHTING, index=get_safe_index(DEMO_LIGHTING, 'lit_select'), key="lit_select")
        with c3:
            st.selectbox("3. Lente", LIST_LENSES, index=get_safe_index(LIST_LENSES, 'lens_select'), key="lens_select")
            st.selectbox("6. Estilo", DEMO_STYLES, index=get_safe_index(DEMO_STYLES, 'sty_select'), key="sty_select")

    with t5:
        st.subheader("🎹 Suno AI (Generador Musical)")
        
        sc1, sc2 = st.columns(2)
        with sc1:
            s_genre = st.text_input("Género (Ej: Cinematic Rock)")
            s_inst = st.toggle("🎻 Instrumental")
        with sc2:
            s_mood = st.text_input("Mood (Ej: Epic, Scary)")
            s_dur = st.slider("Duración (Segundos)", 10, 300, 30, help="Define estructura. <30s = Jingle/Intro.")

        s_lyrics = st.text_area("Letra / Tema", placeholder="Describe el tema o pega la letra...")
        
        submit_suno = st.form_submit_button("🎵 Generar Solo Música (Suno)")
        
        st.markdown("---")
        st.caption("Configuración Video (Lip-Sync)")
        has_audio = st.checkbox("✅ Activar Lip-Sync (Audio externo)")

    with t6:
        st.header("📘 Manual Maestro de Grok Studio")
        st.markdown("""
        ### 1. Filosofía de los Dos Cerebros
        * **El Director (Botón 'Sugerir Look'):** Analiza tu texto y ajusta los controles de cámara (Lente, Ángulo, Luz) ANTES de generar.
        * **El Guionista (Modo Architect):** Trabaja en SILENCIO al generar. Enriquece tu texto añadiendo detalles sensoriales.

        ### 2. Guía Técnica de Cinematografía
        * **16mm Wide Angle:**  Paisajes épicos, Monstruos Gigantes.
        * **35mm Prime:** Cine clásico, documental.
        * **50mm Lens:** Ojo humano. Sin distorsión.
        * **85mm / 100mm Macro:**  Detalles pequeños (ojos, gotas). Fondo borroso.
        * **Low Angle:**  Poder, Amenaza.
        * **Dutch Angle:**  Terror, Locura.
        """)

    # BOTÓN GLOBAL
    st.markdown("---")
    submit_main = st.form_submit_button("✨ GENERAR PROMPT DE VÍDEO (PRO)")

# --- 8. PROCESAMIENTO ---
if submit_suno:
    if s_dur < 15: suno_struct = "[Intro] [Outro] [Jingle]"
    elif s_dur < 45: suno_struct = "[Intro] [Verse] [Outro]"
    else: suno_struct = "[Intro] [Verse] [Chorus] [Bridge] [Outro]"
    
    tags = []
    if s_inst: tags.append("[Instrumental]")
    if s_genre: tags.append(f"[{translate_to_english(s_genre)}]")
    if s_mood: tags.append(f"[{translate_to_english(s_mood)}]")
    
    st.info(f"📋 **Copia esto en Suno:**\n\n**Style:** {' '.join(tags)}\n**Lyrics:** {translate_to_english(s_lyrics) if s_lyrics else '[Instrumental]'}\n**Structure Note:** {suno_struct}")

elif submit_main:
    raw_action = current_text_input if current_text_input else st.session_state.get('act_input', "")
    eng_action = translate_to_english(raw_action)
    
    b = PromptBuilder()
    
    if uploaded_file: b.add(f"Start Frame: '{uploaded_file.name}'", "✅ Img2Vid")
    if uploaded_end: b.add(f"End Frame: '{uploaded_end.name}'")
    
    ward_anchor = f" ENSURE SUBJECT KEEPS WEARING: {final_ward}" if final_ward else ""
    b.add(f"Maintain strict visual consistency with source.{ward_anchor}", "🔒 Anclaje de Ropa")
    
    narrative = []
    if final_sub: narrative.append(final_sub)
    if final_ward: narrative.append(f"WEARING: {final_ward}")
    if final_prop: narrative.append(f"HOLDING: {final_prop}")
    
    if eng_action:
        is_morph = "transform" in eng_action.lower() or "morph" in eng_action.lower()
        header = "VISUAL EFFECTS SEQUENCE (MORPHING)" if is_morph else "VISCERAL ACTION SEQUENCE"
        
        flavor = ""
        if enhance_mode:
            flavor = b.expand_flavor(eng_action)
            if not flavor: flavor = "cinematic depth, dynamic lighting, hyper-detailed textures"
            b.add(f"{header}: {eng_action}. DETAILS: {flavor}.", "🔥 Architect Mode")
        else:
            b.add(f"ACTION: {eng_action}.")
    else:
        b.add("ACTION: Cinematic idle motion.", "⚠️ No action text")
    
    if "Custom" not in final_env and final_env: b.add(f"ENVIRONMENT: {final_env}.")
    elif enhance_mode and not final_env: b.add("ENVIRONMENT: Cinematic atmospheric background.")
    
    b.add("\n".join(narrative))
    
    atm = []
    if phy_det: atm.append(f"PHYSICS: {', '.join(phy_det)}")
    b.add(". ".join(atm))
    
    # Recuperación segura de widgets
    w_shot = st.session_state.get('shot_select', LIST_SHOT_TYPES[0])
    w_angle = st.session_state.get('angle_select', LIST_ANGLES[0])
    w_lens = st.session_state.get('lens_select', LIST_LENSES[0])
    w_lit = st.session_state.get('lit_select', DEMO_LIGHTING[0])
    w_sty = st.session_state.get('sty_select', DEMO_STYLES[0])
    
    auto_look = apply_smart_look_logic(eng_action) if enhance_mode else {}
    
    final_shot = w_shot if "Neutral" not in w_shot else auto_look.get('shot', "")
    final_angle = w_angle if "Neutral" not in w_angle else auto_look.get('angle', "")
    final_lens = w_lens if "Neutral" not in w_lens else auto_look.get('lens', "")
    final_lit = w_lit if "Neutral" not in w_lit else auto_look.get('lit', "")
    final_sty = w_sty if "Neutral" not in w_sty else auto_look.get('sty', "")
    
    cine_parts = []
    if final_lit: cine_parts.append(final_lit.split('(')[0])
    
    cam_phrase = "Shot"
    if final_lens: cam_phrase += f" on {final_lens.split('(')[0]}"
    if final_shot: cam_phrase += f" using a {final_shot.split('(')[0]}"
    if final_angle: cam_phrase += f" from a {final_angle.split('(')[0]} perspective"
    cine_parts.append(cam_phrase)
    
    b.add(f"CINEMATOGRAPHY: {'. '.join(cine_parts)}.")
    if final_sty: b.add(f"STYLE: {final_sty.split('(')[0]}")
    
    ar_val = st.session_state.get('ar_select', DEMO_ASPECT_RATIOS[0]).split('(')[0].strip()
    b.add(f"--ar {ar_val}")
    
    st.session_state.generated_output = b.get_result()
    st.session_state.generated_explanation = "\n".join(b.explanation)

# --- 9. MOSTRAR RESULTADO (ACCESO SEGURO) ---
# Usamos .get() para evitar el AttributeError final, incluso si todo lo demás falla.
output = st.session_state.get("generated_output", "")
explanation = st.session_state.get("generated_explanation", "")

if output:
    st.markdown("---")
    if explanation:
        st.markdown(f'<div class="strategy-box"><b>💡 Estrategia:</b><br>{explanation}</div>', unsafe_allow_html=True)
    st.subheader("📝 Prompt Final")
    st.code(output, language="text")