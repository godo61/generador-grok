import streamlit as st
import re

# --- GESTIÓN DE DEPENDENCIAS ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Grok Production Studio", layout="wide", page_icon="🌌")

# --- ESTILOS CSS (Grok Theme) ---
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
        </style>
    """, unsafe_allow_html=True)

# --- DATOS MAESTROS (FACTORY) ---
DEFAULT_CHARACTERS = {
    "TON (Base)": "a striking male figure with a razor-sharp jawline and textured modern quiff hair",
    "FREYA (Base)": "a statuesque female survivor with intense hazel eyes and wet skin texture",
    "TON (Guitarra)": "Ton playing a vintage electric guitar with passion",
    "FREYA (Kayak)": "Freya paddling a sea kayak in turbulent waters"
}
DEFAULT_PROPS = {
    "Guitarra Ton": "a vintage 1959 sunburst electric guitar with road-worn finish",
    "Kayak Freya": "a high-tech carbon fiber expedition kayak",
    "Robo-Dog": "a yellow Boston Dynamics style robot dog"
}

# --- MEMORIA ---
if 'history' not in st.session_state: st.session_state.history = []
if 'uploaded_image_name' not in st.session_state: st.session_state.uploaded_image_name = None
if 'uploaded_end_frame_name' not in st.session_state: st.session_state.uploaded_end_frame_name = None
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""

# Auto-Reparación
if 'characters' not in st.session_state: st.session_state.characters = DEFAULT_CHARACTERS.copy()
if 'custom_props' not in st.session_state: st.session_state.custom_props = DEFAULT_PROPS.copy()

# --- FUNCIONES ---
def translate_to_english(text):
    if not text or not text.strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try: return GoogleTranslator(source='auto', target='en').translate(str(text))
        except: return str(text)
    return str(text)

# --- LISTAS (OPTIMIZADAS PARA GROK) ---
# Grok prefiere estilos descriptivos, no solo keywords
DEMO_STYLES = [
    "Hyper-realistic Photography (Flux Style)", 
    "Cinematic Film Still (Kodak Portra)", 
    "3D Unreal Engine 5 Render", 
    "Dark Fantasy Illustration", 
    "Cyberpunk Digital Art", 
    "Vintage 90s Broadcast"
]

DEMO_ENVIRONMENTS = ["✏️ Custom...", "a dusty Martian landscape", "a turbulent river in South Africa", "the interior of a futuristic space station", "a dense mystic forest"]
DEMO_WARDROBE = ["✏️ Custom...", "a white NASA EVA spacesuit", "a sleek sci-fi armor suit", "professional kayaking gear", "a tactical black wetsuit"]
DEMO_LIGHTING = ["soft cinematic lighting", "harsh volumetric sunlight", "neon cyberpunk glow", "dramatic studio rim lighting", "golden hour sun"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "9:16 (Portrait)", "21:9 (Ultrawide)", "1:1 (Square)"]
DEMO_CAMERAS = ["shot on 35mm lens", "wide-angle GoPro shot", "telephoto 85mm portrait", "low-angle dynamic shot", "top-down drone view"]

# SONIDO
DEMO_AUDIO_MOOD = ["No Music", "Hans Zimmer Style Orchestral", "Dark Synthwave", "Intense Suspense", "Upbeat Rock", "Silence"]
DEMO_SFX_COMMON = ["None", "Thrusters firing", "Water splashing", "Heavy breathing", "Footsteps on concrete"]

# --- PLANTILLAS GROK (FLUENT STYLE) ---
# Estas plantillas usan conectores naturales, clave para Grok 2 / Flux
NARRATIVE_TEMPLATES = {
    "Libre": "",
    "📸 Retrato Cinematográfico": "A cinematic medium shot of [SUBJECT] looking directly at the camera. The background is [ENV]. The lighting is [LIGHT], highlighting the skin texture.",
    "🏃 Acción Dinámica": "An intense action scene featuring [SUBJECT] [ACTION] in [ENV]. Motion blur emphasizes the speed. The camera angle is [CAM].",
    "🧟 Transformación (VFX)": "At second 0, the object behind [SUBJECT] transforms into a living creature. The texture shifts from artificial to realistic biological details under [LIGHT].",
    "✨ Fantasía Etérea": "[SUBJECT] standing in [ENV], surrounded by floating magical particles. The atmosphere is dreamlike and hazy."
}

# --- BUILDER (MOTOR GROK FLUENT) ---
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

        # --- 1. CABECERA TÉCNICA (IMG2VID) ---
        if self.is_img2video:
            prompt.append(f"Start Frame: '{self.image_filename}'.")
            if self.end_image_filename: prompt.append(f"End Frame: '{self.end_image_filename}'.")
            prompt.append("Maintain strict visual consistency with the reference image.")

        # --- 2. CONSTRUCCIÓN GRAMATICAL (GROK STYLE) ---
        # Grok prefiere: "Sujeto + Acción + Entorno + Luz" en una frase fluida.
        
        # Preparar componentes
        subject = p.get('subject', 'A subject')
        wardrobe = p.get('wardrobe_custom') or p.get('wardrobe', '')
        if "Custom" in wardrobe: wardrobe = ""
        
        props = p.get('props_custom') or p.get('props', '')
        if "Custom" in props or "None" in props: props = ""
        
        action = p.get('action', '')
        env = p.get('env_custom') or p.get('env', '')
        if "Custom" in env: env = ""
        
        # In-Image Text (Nuevo para Grok)
        text_overlay = p.get('text_overlay', '')

        # --- ENSAMBLAJE FLUENT ---
        # Comenzamos la frase maestra
        main_sentence = ""
        
        # Si hay plantilla narrativa, úsala como base
        if p.get('narrative_mode') and action:
            # Reemplazos inteligentes en la plantilla
            narrative = action
            narrative = narrative.replace("[SUBJECT]", subject)
            narrative = narrative.replace("[ENV]", env if env else "a neutral background")
            narrative = narrative.replace("[LIGHT]", p.get('light', 'natural light'))
            narrative = narrative.replace("[ACTION]", "acting") # Fallback
            narrative = narrative.replace("[CAM]", p.get('camera', 'cinematic angle'))
            
            # Añadir detalles de vestuario/props si no están en la narrativa
            details = []
            if wardrobe: details.append(f"wearing {wardrobe}")
            if props: details.append(f"holding {props}")
            
            if details:
                narrative += f" The character is {', '.join(details)}."
            
            main_sentence = narrative

        else:
            # Construcción manual fluida
            main_sentence = f"{subject}"
            if wardrobe: main_sentence += f" wearing {wardrobe}"
            if props: main_sentence += f", holding {props}"
            
            if action: main_sentence += f", is {action}"
            else: main_sentence += ", is captured in a cinematic pose"
            
            if env: main_sentence += f" situated in {env}"
            if p.get('light'): main_sentence += f", illuminated by {p['light']}"

        prompt.append(main_sentence)

        # --- 3. DETALLES ESPECÍFICOS GROK ---
        # Texto en imagen
        if text_overlay:
            prompt.append(f"The text '{text_overlay}' is clearly visible in the scene, rendered in a realistic typography.")

        # Estilo y Cámara
        tech_sentence = ""
        if p.get('style'): tech_sentence += f"The image aesthetic is {p['style']}."
        if p.get('camera'): tech_sentence += f" Shot with a {p['camera']}."
        if tech_sentence: prompt.append(tech_sentence)

        # Física (Si aplica)
        if p.get('physics_medium') and "Neutral" not in p['physics_medium']:
            med = p['physics_medium'].split('(')[0].strip()
            dets = [d.split('(')[0].strip() for d in p.get('physics_details', [])]
            if dets: prompt.append(f"Physics Simulation: {med} environment featuring {', '.join(dets)}.")

        # --- 4. AUDIO (SOLO SI ES VIDEO) ---
        audio_parts = []
        m_val = p.get('audio_mood_custom') or p.get('audio_mood')
        if m_val and "No Music" not in m_val and "Custom" not in m_val: audio_parts.append(f"Music: {m_val}")
        s_val = p.get('audio_sfx_custom') or p.get('audio_sfx')
        if s_val and "None" not in s_val and "Custom" not in s_val: audio_parts.append(f"SFX: {s_val.split('(')[0].strip()}")
        
        if audio_parts: prompt.append(f"AUDIO ATMOSPHERE: {'. '.join(audio_parts)}.")

        # --- 5. PARÁMETROS TÉCNICOS ---
        if p.get('ar'): prompt.append(f"--ar {p['ar'].split(' ')[0]}")

        # Unir todo con saltos de línea para claridad
        return "\n\n".join(prompt)

# --- INTERFAZ ---
with st.sidebar:
    st.title("🌌 Config Grok")
    is_dark = st.toggle("🌙 Modo Oscuro", value=True)
    apply_custom_styles(is_dark)
    
    if st.button("🔄 Restaurar Fábrica"):
        st.session_state.characters = DEFAULT_CHARACTERS.copy()
        st.session_state.custom_props = DEFAULT_PROPS.copy()
        st.rerun()

    st.header("🧬 Activos (ADN)")
    tc, to = st.tabs(["👤 Cast", "🎸 Props"])
    with tc:
        c_n = st.text_input("Nombre Actor")
        c_d = st.text_area("Descripción (Grok prefiere frases)")
        if st.button("Guardar Actor"):
            if c_n and c_d:
                st.session_state.characters[c_n] = translate_to_english(c_d)
                st.rerun()
    with to:
        o_n = st.text_input("Nombre Objeto")
        o_d = st.text_area("Descripción Visual")
        if st.button("Guardar Objeto"):
            if o_n and o_d:
                st.session_state.custom_props[o_n] = translate_to_english(o_d)
                st.rerun()

    st.markdown("---")
    st.header("🖼️ Imágenes")
    u_file = st.file_uploader("Start Frame (Img2Vid)", type=["jpg", "png"])
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
st.title("🎬 Grok Production Studio (Imagine AI Edition)")

with st.expander("📘 GUÍA DE PROMPTING (GROK/FLUX)", expanded=False):
    st.markdown("""
    **Filosofía Grok Imagine AI:** Este modelo prefiere descripciones fluidas y naturales, no listas de palabras clave.
    * **MAL:** Man, beard, space, 8k, cinematic.
    * **BIEN:** A cinematic shot of a man with a beard floating in deep space.
    
    **Texto en Imagen:** Grok es capaz de escribir. Usa el campo "Texto en Imagen" para carteles, camisetas o logos.
    """)

# PESTAÑAS
t1, t2, t3, t4, t5 = st.tabs(["📝 Narrativa", "🎒 Assets", "⚛️ Física", "🎨 Estética", "🎵 Audio"])

# VARS
final_sub, final_act, final_ward, final_prop, final_env = "", "", "", "", ""
mus_vid, sfx_vid, text_overlay = "", "", ""

with t1:
    c_a, c_b = st.columns(2)
    with c_a:
        char_opts = list(st.session_state.characters.keys())
        if st.session_state.uploaded_image_name: char_opts.insert(0, "📷 Sujeto de la Foto")
        char_sel = st.selectbox("Sujeto Principal", char_opts)
        final_sub = "" if "📷" in char_sel else st.session_state.characters[char_sel]
    
    with c_b:
        # Selector de Plantillas Grok
        tpl = st.selectbox("Plantilla Narrativa (Grok Style)", list(NARRATIVE_TEMPLATES.keys()))
        tpl_txt = NARRATIVE_TEMPLATES[tpl]

    st.markdown("##### 📜 Descripción de Escena (Natural Language)")
    act_val = st.text_area("Describe qué ocurre (Rellena los corchetes si usas plantilla):", value=tpl_txt, height=120, placeholder="E.g., A massive elephant runs towards the camera...")
    final_act = translate_to_english(act_val)
    
    # NUEVO: TEXTO EN IMAGEN
    text_overlay = st.text_input("🔡 Texto dentro de la imagen (Opcional)", placeholder="Ej: 'SPACE CORP' en un neón")

with t2:
    c1, c2 = st.columns(2)
    with c1:
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
    phy_med = st.selectbox("Entorno Físico", list(PHYSICS_LOGIC.keys()))
    phy_det = st.multiselect("Detalles de Simulación", PHYSICS_LOGIC[phy_med])

with t4:
    c1, c2 = st.columns(2)
    with c1:
        sty = st.selectbox("Estilo Artístico", DEMO_STYLES)
        e_sel = st.selectbox("Entorno / Lugar", DEMO_ENVIRONMENTS)
        if "Custom" in e_sel: final_env = translate_to_english(st.text_input("Lugar Custom", key="lc"))
        else: final_env = e_sel
    with c2:
        cam = st.selectbox("Cámara", DEMO_CAMERAS)
        lit = st.selectbox("Iluminación", DEMO_LIGHTING)
        ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS)

with t5:
    c1, c2 = st.columns(2)
    with c1: 
        m_sel = st.selectbox("Música", DEMO_AUDIO_MOOD)
        mus_vid = translate_to_english(st.text_input("Mus. Custom", key="mc")) if "Custom" in m_sel else m_sel
    with c2:
        s_sel = st.selectbox("SFX", DEMO_SFX_COMMON)
        sfx_vid = translate_to_english(st.text_input("SFX Custom", key="sc")) if "Custom" in s_sel else s_sel

# GENERAR
if st.button("✨ GENERAR PROMPT (GROK FORMAT)", type="primary"):
    b = GrokVideoPromptBuilder()
    if st.session_state.uploaded_image_name:
        b.activate_img2video(st.session_state.uploaded_image_name, st.session_state.uploaded_end_frame_name)
    
    # Enviamos datos al motor inteligente
    b.set_field('narrative_mode', True) # Siempre True en esta versión Grok
    b.set_field('subject', final_sub)
    b.set_field('action', final_act)
    b.set_field('text_overlay', translate_to_english(text_overlay))
    b.set_field('props', final_prop)
    b.set_field('wardrobe', final_ward)
    
    b.set_field('physics_medium', phy_med)
    b.set_field('physics_details', phy_det)
    
    b.set_field('style', sty)
    b.set_field('env', final_env)
    b.set_field('camera', cam)
    b.set_field('light', lit)
    b.set_field('ar', ar)
    
    b.set_field('audio_mood', mus_vid)
    b.set_field('audio_sfx', sfx_vid)
    
    res = b.build()
    st.session_state.generated_output = res
    st.session_state.history.append(res)

if st.session_state.generated_output:
    st.markdown("---")
    st.subheader("📝 Grok Prompt Final")
    final_editable = st.text_area("Editar:", value=st.session_state.generated_output, height=250)
    st.code(st.session_state.generated_output, language="text")