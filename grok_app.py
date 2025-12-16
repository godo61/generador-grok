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

# --- 3. DATOS ---
DEFAULT_CHARACTERS = {"TON (Base)": "striking male figure...", "FREYA (Base)": "statuesque female survivor..."}
DEFAULT_PROPS = {"Guitarra": "vintage electric guitar", "Kayak": "carbon fiber kayak"}

# Listas
DEMO_STYLES = ["Neutral (Auto)", "Cinematic Film Still (Kodak Portra 800)", "Hyper-realistic VFX Render (Unreal 5)", "National Geographic Wildlife Style", "Gritty Documentary Footage", "Action Movie Screengrab", "Cyberpunk Digital Art", "Vintage VHS 90s"]
DEMO_ENVIRONMENTS = ["✏️ Custom...", "🛶 Dusi River (Turbulent Rapids)", "🔴 Mars Surface (Red Dust)", "🌌 Deep Space (Nebula)", "🚀 ISS Interior", "🌊 Underwater Reef", "❄️ Arctic Tundra", "🏙️ Cyberpunk City", "🌲 Mystic Forest"]
DEMO_WARDROBE = [
    "✏️ Custom...", 
    "Short-sleeve grey t-shirt (Cotton texture)", 
    "Short-sleeve tactical shirt (Ripstop)",
    "Long-sleeve denim shirt (Rolled up)", 
    "NASA EVA Spacesuit (Bulky)", 
    "Tactical Wetsuit (Neoprene)", 
    "Elegant Suit (Three piece)"
]
DEMO_PROPS_LIST = ["None", "✏️ Custom...", "🛶 Kayak Paddle", "🎸 Electric Guitar", "🔫 Blaster", "📱 Datapad", "🔦 Flashlight"]

LIST_SHOT_TYPES = ["Neutral (Auto)", "Extreme Long Shot (Epic Scale)", "Long Shot (Full Body)", "Medium Shot (Waist Up)", "Close-Up (Face Focus)", "Extreme Close-Up (Macro Detail)"]
LIST_ANGLES = ["Neutral (Auto)", "Low Angle (Heroic/Ominous)", "High Angle (Vulnerable)", "Dutch Angle (Chaos/Tension)", "Bird's Eye View (Top-Down)", "Drone Aerial View (Establishing)"]
LIST_LENSES = ["Neutral (Auto)", "16mm Wide Angle (Expansive)", "35mm Prime (Street)", "50mm Lens (Natural)", "85mm f/1.4 (Portrait)", "100mm Macro (Detail)", "Fisheye (Distorted)"]
DEMO_LIGHTING = ["Neutral (Auto)", "Harsh Golden Hour", "Dramatic Low-Key (Chiaroscuro)", "Soft Overcast (Diffusion)", "Neon City Glow", "Stark Space Sunlight"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "21:9 (Cinematic)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

# GEM EXPANSION
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

# --- 4. ESTADO ---
init_vars = {
    'generated_output': "", 'generated_explanation': "",
    'characters': DEFAULT_CHARACTERS.copy(), 'custom_props': DEFAULT_PROPS.copy(),
    'uploader_key': 0, 'act_input': "",
    'char_select': "-- Seleccionar Protagonista --",
    'shot_select': LIST_SHOT_TYPES[0], 'angle_select': LIST_ANGLES[0],
    'lens_select': LIST_LENSES[0], 'lit_select': DEMO_LIGHTING[0],
    'sty_select': DEMO_STYLES[0], 'env_select': DEMO_ENVIRONMENTS[0],
    'ar_select': DEMO_ASPECT_RATIOS[0], 'phy_select': "Neutral / Estudio",
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
    for k, target in [('shot_select', suggestions['shot']), 
                      ('angle_select', suggestions['angle']),
                      ('lens_select', suggestions['lens']),
                      ('lit_select', suggestions['lit']),
                      ('sty_select', suggestions['sty'])]:
        if k == 'shot_select': lst = LIST_SHOT_TYPES
        elif k == 'angle_select': lst = LIST_ANGLES
        elif k == 'lens_select': lst = LIST_LENSES
        elif k == 'lit_select': lst = DEMO_LIGHTING
        elif k == 'sty_select': lst = DEMO_STYLES
        else: lst = []
        
        for item in lst:
            if target.split('(')[0] in item:
                st.session_state[k] = item
                break

def perform_reset():
    st.session_state['act_input'] = ""
    st.session_state['char_select'] = "-- Seleccionar Protagonista --"
    st.session_state['shot_select'] = LIST_SHOT_TYPES[0]
    st.session_state['angle_select'] = LIST_ANGLES[0]
    st.session_state['lens_select'] = LIST_LENSES[0]
    st.session_state['lit_select'] = DEMO_LIGHTING[0]
    st.session_state['sty_select'] = DEMO_STYLES[0]
    st.session_state['env_select'] = DEMO_ENVIRONMENTS[0]
    st.session_state['uploader_key'] += 1 
    st.session_state['generated_output'] = ""
    st.session_state['generated_explanation'] = ""

# --- 6. BUILDER ---
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

# --- 7. INTERFAZ ---
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

# --- 8. MAIN ---
st.title("🎬 Grok Production Studio (V69)")

with st.form("main_form"):
    
    t1, t2, t3, t4, t5, t6 = st.tabs(["🎬 Acción", "🎒 Assets", "⚛️ Física", "🎥 Cinematografía", "🎵 Audio (Suno)", "📘 Guía"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            char_opts = ["-- Seleccionar Protagonista --"]
            if uploaded_file: char_opts.insert(1, "📷 Sujeto de la Foto")
            char_opts += list(st.session_state.characters.keys())
            
            if st.session_state.char_select not in char_opts: st.session_state.char_select = char_opts[0]
            char_sel = st.selectbox("Protagonista", char_opts, key="char_select")
            
            if "📷" in char_sel: final_sub = "MAIN SUBJECT: The character in the provided reference image"
            elif "--" in char_sel: final_sub = ""
            else: final_sub = f"MAIN SUBJECT: {st.session_state.characters.get(char_sel, '')}"

        with c2:
            enhance_mode = st.checkbox("🔥 Modo Architect (Expandir descripción)", value=True)

        col_tmpl, col_btn = st.columns([3, 1])
        with col_tmpl:
            tpl = st.selectbox("Plantilla Rápida", ["Seleccionar..."] + list(NARRATIVE_TEMPLATES.keys()))
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
            e_sel = st.selectbox("Entorno", DEMO_ENVIRONMENTS, key="env_select")
            final_env = st.text_input("Custom Env", key="env_cust") if "Custom" in e_sel else e_sel
            
            all_props = ["None", "✏️ Custom..."] + list(st.session_state.custom_props.keys()) + DEMO_PROPS_LIST[2:]
            prop_sel = st.selectbox("Objeto", all_props, key="prop_select")
            if prop_sel in st.session_state.custom_props: final_prop = st.session_state.custom_props[prop_sel]
            elif "Custom" in prop_sel: final_prop = translate_to_english(st.text_input("Objeto Nuevo", key="np"))
            elif "None" not in prop_sel: final_prop = prop_sel
            else: final_prop = ""

        with c2:
            st.info("💡 Consejo: Elige manga corta/larga explícitamente para evitar que la IA la cambie.")
            ward_sel = st.selectbox("Vestuario", DEMO_WARDROBE, key="ward_select")
            if "Custom" in ward_sel: final_ward = translate_to_english(st.text_input("Ropa Custom", key="wc"))
            else: final_ward = ward_sel

    with t3:
        c1, c2 = st.columns(2)
        with c1: phy_med = st.selectbox("Medio Físico", list(PHYSICS_LOGIC.keys()), key="phy_select")
        with c2: phy_det = st.multiselect("Detalles", PHYSICS_LOGIC[phy_med])

    with t4:
        st.info("💡 Usa 'Sugerir Look' en la barra lateral para que la IA configure esto por ti según tu texto.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.selectbox("1. Encuadre", LIST_SHOT_TYPES, key="shot_select", help="Extreme Long: Paisajes épicos. Long: Cuerpo entero. Medium: Cintura arriba. Close-Up: Rostro y emoción.")
            st.selectbox("4. Formato", DEMO_ASPECT_RATIOS, key="ar_select")
        with c2:
            st.selectbox("2. Ángulo", LIST_ANGLES, key="angle_select", help="Low Angle: Poder/Monstruos. High Angle: Debilidad. Dutch: Tensión/Terror.")
            st.selectbox("5. Iluminación", DEMO_LIGHTING, key="lit_select", help="Chiaroscuro: Drama/Terror. Golden Hour: Épico/Bello. Neon: Futurista.")
        with c3:
            st.selectbox("3. Lente", LIST_LENSES, key="lens_select", help="16mm: Gran angular/Escala. 35mm: Cine clásico. 85mm: Retrato/Fondo borroso.")
            st.selectbox("6. Estilo", DEMO_STYLES, key="sty_select")

    with t5:
        st.subheader("🎹 Suno AI (Generador Musical)")
        st.markdown("Genera prompts optimizados para música de intros y outros.")
        
        sc1, sc2 = st.columns(2)
        with sc1:
            s_genre = st.text_input("Género (Ej: Cinematic Rock, Lo-Fi)")
            s_inst = st.toggle("🎻 Instrumental")
        with sc2:
            s_mood = st.text_input("Mood (Ej: Epic, Scary, Sad)")
            # Slider de duración CRUCIAL para intros/outros
            s_dur = st.slider("Duración (Segundos)", 10, 300, 30, help="Define la estructura del prompt. Menos de 30s genera Intro/Outro.")

        s_lyrics = st.text_area("Letra / Tema (si no es instrumental)", placeholder="Describe el tema o pega la letra...")
        
        st.markdown("---")
        st.info("Configuración de Lip-Sync para Video (No Suno):")
        has_audio = st.checkbox("✅ Activar Lip-Sync (Audio externo)")

    with t6:
        st.header("📘 Manual Maestro de Grok Studio")
        st.markdown("""
        ### 1. Filosofía de los Dos Cerebros
        * **El Director (Botón 'Sugerir Look'):** Analiza tu texto y ajusta los controles de cámara (Lente, Ángulo, Luz) ANTES de generar. Úsalo para ver qué propone la IA y modificarlo si quieres.
        * **El Guionista (Modo Architect - Checkbox):** Trabaja en SILENCIO al generar. Enriquece tu texto añadiendo detalles sensoriales (sudor, texturas, escombros) que Grok necesita para el realismo.

        ### 2. Guía Técnica de Cinematografía
        
        **🔭 Lentes (El Ojo de la Cámara)**
        * **16mm Wide Angle:**  Abre mucho el campo de visión. Fundamental para mostrar **Monstruos Gigantes**, paisajes inmensos o persecuciones donde importa el entorno.
        * **35mm Prime:** El estándar del cine y fotoperiodismo. Realista, crudo, documental.
        * **50mm Lens:** Lo más parecido al ojo humano. Sin distorsión. Ideal para escenas tranquilas o de diálogo.
        * **85mm / 100mm Macro:**  Zoom y detalle. Enfoca solo una parte (ojos, manos) y deja el fondo borroso (**Bokeh**).
        * **Fisheye:** Distorsión curva extrema. Para escenas de locura, drogas o cámaras de seguridad/GoPro.

        **📐 Ángulos (La Posición)**
        * **Low Angle (Contrapicado):**  Cámara en el suelo mirando arriba. Hace al sujeto **Poderoso, Heroico o Aterrador**.
        * **High Angle (Picado):** Cámara arriba mirando abajo. Hace al sujeto parecer pequeño, débil o vulnerable.
        * **Dutch Angle (Holandés):**  Cámara torcida. Genera ansiedad, tensión, terror o locura.

        **💡 Iluminación (El Alma)**
        * **Chiaroscuro / Low Key:**  Contrastes fuertes, muchas sombras. Cine Negro, Terror, Drama intenso.
        * **Golden Hour:** Luz solar baja, naranja y suave. Escenas épicas, finales felices, recuerdos.
        * **Soft Overcast:** Luz blanca y difusa (día nublado). Ideal para que se vea todo bien sin dramatismo exagerado.
        """)

    # BOTÓN GLOBAL
    submitted = st.form_submit_button("✨ GENERAR PROMPT PRO")

# --- 9. PROCESAMIENTO ---
if submitted:
    raw_action = current_text_input if current_text_input else st.session_state.get('act_input', "")
    eng_action = translate_to_english(raw_action)
    
    b = PromptBuilder()
    
    # 1. Cabecera + ANCLAJE
    if uploaded_file: b.add(f"Start Frame: '{uploaded_file.name}'", "✅ Img2Vid")
    if uploaded_end: b.add(f"End Frame: '{uploaded_end.name}'")
    
    ward_anchor = f" ENSURE SUBJECT KEEPS WEARING: {final_ward}" if final_ward else ""
    b.add(f"Maintain strict visual consistency with source.{ward_anchor}", "🔒 Anclaje de Ropa")
    
    # 2. Narrativa
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
    
    # 3. Cine
    w_shot = st.session_state.shot_select
    w_angle = st.session_state.angle_select
    w_lens = st.session_state.lens_select
    w_lit = st.session_state.lit_select
    w_sty = st.session_state.sty_select
    
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
    
    # 4. Generación Suno (Si aplica)
    if s_genre or s_mood:
        # Lógica de estructura basada en duración
        if s_dur < 15: suno_struct = "[Intro] [Outro] [Jingle]"
        elif s_dur < 45: suno_struct = "[Intro] [Verse] [Outro]"
        else: suno_struct = "[Intro] [Verse] [Chorus] [Bridge] [Outro]"
        
        suno_tags = []
        if s_inst: suno_tags.append("[Instrumental]")
        if s_genre: suno_tags.append(f"[{translate_to_english(s_genre)}]")
        if s_mood: suno_tags.append(f"[{translate_to_english(s_mood)}]")
        
        b.add(f"\n--- SUNO AUDIO PROMPT ---\nStyle: {' '.join(suno_tags)}\nStructure: {suno_struct}\nLyrics: {translate_to_english(s_lyrics) if s_lyrics else '[Instrumental]'}")

    ar_val = st.session_state.ar_select.split('(')[0].strip()
    b.add(f"--ar {ar_val}")
    
    st.session_state.generated_output = b.get_result()
    st.session_state.generated_explanation = "\n".join(b.explanation)

if st.session_state.generated_output:
    st.markdown("---")
    if st.session_state.generated_explanation:
        st.markdown(f'<div class="strategy-box"><b>💡 Estrategia:</b><br>{st.session_state.generated_explanation}</div>', unsafe_allow_html=True)
    st.subheader("📝 Prompt Final")
    st.code(st.session_state.generated_output, language="text")