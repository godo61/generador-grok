import streamlit as st
import re

# --- GESTIÓN DE DEPENDENCIAS ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Grok Video Builder Pro", layout="wide", page_icon="🎬")

# --- MEMORIA ---
if 'history' not in st.session_state: st.session_state.history = []
if 'uploaded_image_name' not in st.session_state: st.session_state.uploaded_image_name = None
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""

# --- PERSONAJES ---
if 'characters' not in st.session_state:
    st.session_state.characters = {
        "Nada (Generar nuevo)": "",
        "TON (Guitarra)": """A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique, characterized by an elegant verticality and lean, wiry muscularity rather than bulk. He possesses a confident, architectural facial structure with high, defined cheekbones and a jawline that cuts a sharp geometric profile, overlaid with a texture of faint, authentic skin porosity and a meticulously groomed five o'clock shadow that maps the contours of his lower face. His hair is styled in a modern, textured quiff with a matte finish, dark chestnut strands caught in a chaotic yet deliberate motion, featuring a subtle fade at the temples that blends seamlessly into the skin. He is attired in a high-quality, charcoal-grey heavyweight cotton t-shirt that drapes loosely over his slender frame, revealing the definition of his clavicles and shoulders without clinging, paired with dark, raw selvedge denim jeans that exhibit realistic stiffness and indigo depth. The lighting is cinematic and moody, utilizing a soft-box key light from the upper left to carve out the depth of his facial features in a Rembrandt style, while a cool-toned rim light separates his dark silhouette from a blurred, neutral urban background, creating a volumetric atmosphere. The image quality exudes the characteristics of an 85mm prime lens photograph at f/1.8, capturing the wetness in his eyes and the tactile weave of the fabric with startling clarity, rendered in 8k resolution with a raw, unfiltered aesthetic. He is holding and playing a specific electric guitar model, adopting a passionate musician pose, fingers on the fretboard.""",
        "TON (Micro)": """A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique, characterized by an elegant verticality and lean, wiry muscularity rather than bulk. He possesses a confident, architectural facial structure with high, defined cheekbones and a jawline that cuts a sharp geometric profile, overlaid with a texture of faint, authentic skin porosity and a meticulously groomed five o'clock shadow that maps the contours of his lower face. His hair is styled in a modern, textured quiff with a matte finish, dark chestnut strands caught in a chaotic yet deliberate motion, featuring a subtle fade at the temples that blends seamlessly into the skin. He is attired in a high-quality, charcoal-grey heavyweight cotton t-shirt that drapes loosely over his slender frame, revealing the definition of his clavicles and shoulders without clinging, paired with dark, raw selvedge denim jeans that exhibit realistic stiffness and indigo depth. The lighting is cinematic and moody, utilizing a soft-box key light from the upper left to carve out the depth of his facial features in a Rembrandt style, while a cool-toned rim light separates his dark silhouette from a blurred, neutral urban background, creating a volumetric atmosphere. The image quality exudes the characteristics of an 85mm prime lens photograph at f/1.8, capturing the wetness in his eyes and the tactile weave of the fabric with startling clarity, rendered in 8k resolution with a raw, unfiltered aesthetic. He is holding a vintage microphone close to his mouth, singing passionately with eyes slightly closed, performing on stage.""",
        "Freya (Kayak)": """A hyper-realistic, cinematic medium shot of a 25-year-old female survivor with a statuesque, athletic 170cm and 60kg physique, exhibiting defined lean muscle mass and core tension typical of extreme exertion. She possesses a striking, symmetrical face with high cheekbones, a sharp jawline, and intense, piercing hazel eyes dilated with adrenaline; her skin texture is rendered with extreme fidelity, showcasing visible pores, vellus hair on the jawline, and uneven localized redness, all glistening with hyper-detailed water beads and sweat exhibiting realistic subsurface scattering. She is completely drenched; her heavy, dark brunette hair is matted and sodden, clinging flat against her skull and neck in distinct wet clumps, with stray strands sticking to her wet face. She is outfitted in a futuristic 'Aquatic Warcore' tactical wetsuit constructed from matte black Yamamoto 39-cell limestone neoprene featuring contrasting glossy geometric Glideskin chest panels, reinforced GBS seams, and a complex mil-spec nylon webbing harness system secured with metallic Cobra buckles and asymmetrical waterproof zippers. The scene is immersed in a turbulent marine environment during the blue hour, characterized by volumetric sea mist, driving rain, and dramatic cool-toned storm lighting that creates sharp specular highlights on the wet neoprene and skin, captured with the shallow depth of field of an 85mm f/1.8 lens, creating a raw, gritty, survivalist aesthetic in 8k resolution. She is paddling a Hyper-realistic expedition sea kayak, model Point 65 Freya 18. Geometry: Features a distinctive 'surfski-hybrid' silhouette with a razor-sharp, plumb vertical bow entry transitioning into a high-volume, bulbous foredeck designed to shed massive waves, contrasting with a tapered, low-profile stern section to minimize windage. Hull: Round hull cross-section with minimal rocker, optimized for speed, showcasing a seamless 'integrated keel rudder' ventral fin at the rear that blends organically into the carbon fiber hull structure. Cockpit: Large keyhole-shaped cockpit with a raised carbon rim, outfitted with a performance bucket seat. Storage & Hatches: Two large oval black rubber hatch covers positioned flush on the fore and aft decks. Rigging & Objects: The deck is laden with authentic 'expedition-ready' gear: a black waterproof North Water peaked deck bag strapped to the foredeck bungee matrix, a recessed Silva 70P compass, a spare split carbon paddle secured under the rear triangular bungee net. Livery & Text: High-gloss 'Black & Red' split colorway (Obsidian Black hull, Safety Red deck); bold, sans-serif white text 'FREYA' prominent on the bow flank; 'Point 65° N' logo on the side; a linear array of small colorful 'national flag stickers' representing circumnavigated countries and 'Thule' sponsor decals lining the cockpit area. Material & Light: Ray-traced gel coat finish with subsurface scattering, wet surface shaders reflecting a stormy grey ocean sky, salt spray residue on the black carbon hull. Art Style: 8k resolution, technical marine photography, Unreal Engine 5 render, highly detailed textures, dramatic atmosphere."""
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

# --- LISTAS DE OPCIONES ---
DEMO_STYLES = ["Photorealistic 8k", "Anime / Manga", "3D Render (Octane)", "Oil Painting", "Vintage Film (VHS)", "Claymation", "Pixel Art (8-bit)", "Abstract / Experimental", "Surrealism", "Fantasy / RPG", "Cyberpunk", "Film Noir", "Watercolor"]
DEMO_LIGHTING = ["Natural Daylight", "Cinematic / Dramatic", "Cyberpunk / Neon", "Studio Lighting", "Golden Hour", "Low Key / Dark"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "9:16 (Portrait)", "1:1 (Square)", "21:9 (Ultrawide)"]
DEMO_CAMERAS = ["Static", "Zoom In", "Zoom Out", "Dolly In", "Dolly Out", "Truck Left", "Truck Right", "Pedestal Up", "Pedestal Down", "Pan", "Tilt", "Orbit", "Handheld / Shake", "FPV Drone"]
DEMO_AUDIO_MOOD = ["No Music", "Cinematic Orchestral", "Cyberpunk Synthwave", "Lo-Fi Chill", "Horror / Suspense", "Upbeat", "Sad", "Heavy Metal", "Ambient Drone"]
DEMO_AUDIO_ENV = ["No Background", "City Traffic", "Heavy Rain", "Forest", "Ocean Waves", "Bar / Restaurant", "Space Station", "Battlefield", "Office"]
DEMO_SFX_COMMON = ["None", "Footsteps", "Rain drops", "Wind howling", "Explosion", "Gunfire", "Swords clashing", "Crowd cheering", "Camera shutter", "Keyboard typing", "Siren", "Heartbeat", "✏️ Custom..."]

# --- 🌊 MOTOR DE FÍSICA (NUEVO) ---
# Diccionario que conecta el medio con sus propiedades físicas técnicas
PHYSICS_LOGIC = {
    "Neutral / None": [],
    
    "🌊 Water (Surface)": [
        "Hydrodynamic water displacement (Desplazamiento de agua)",
        "Wet skin & clothing shaders (Efecto mojado)",
        "Water droplets & splashing particles (Salpicaduras)",
        "Reflective water surface (Reflejos)",
        "Ripples expanding (Ondas)"
    ],
    
    "🤿 Underwater (Submerged)": [
        "Zero-gravity hair and fabric movement (Pelo ingrávido)",
        "Caustics lighting patterns on skin (Cáusticas)",
        "Volumetric underwater light rays (Rayos de luz)",
        "Rising air bubbles (Burbujas)",
        "Suspended particles / Turbidity (Partículas flotando)",
        "Muffled blurry background (Fondo desenfocado)"
    ],
    
    "🌬️ Air / Wind (Storm/Flight)": [
        "Aerodynamic fabric flapping (Ropa ondeando fuerte)",
        "Hair whipping in wind (Pelo al viento)",
        "Dust and debris swirling (Remolinos de polvo)",
        "Motion blur on edges (Desenfoque de movimiento)",
        "Turbulent atmosphere (Atmósfera turbulenta)"
    ],
    
    "❄️ Snow / Ice (Cold)": [
        "Visible breath condensation / Fog (Vaho al respirar)",
        "Snow displacement footprints (Huellas profundas)",
        "Frost texture on surfaces (Escarcha)",
        "Falling snowflakes with depth of field (Copos de nieve)",
        "Subsurface scattering on snow (Luz en la nieve)"
    ],
    
    "🔥 Heat / Desert": [
        "Heat haze distortion / Shimmer (Distorsión por calor)",
        "Sweat glistening on skin (Sudor)",
        "Dry dust clouds (Polvo seco)",
        "Harsh direct shadows (Sombras duras)"
    ]
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
        elif isinstance(value, list): self.parts[key] = value # Permitimos listas para multiselect
        else: self.parts[key] = str(value).strip()

    def activate_img2video(self, filename):
        self.is_img2video = True
        self.image_filename = filename

    def build(self) -> str:
        p = self.parts
        
        # --- AUDIO ---
        audio_prompt_parts = []
        if p.get('audio_mood') and "No Music" not in str(p['audio_mood']):
            audio_prompt_parts.append(f"Music style: {p['audio_mood']}")
        if p.get('audio_env') and "No Background" not in str(p['audio_env']):
            audio_prompt_parts.append(f"Environment sound: {p['audio_env']}")
        sfx_val = p.get('audio_sfx', '')
        if sfx_val and "None" not in sfx_val:
            sfx_clean = sfx_val.split('(')[0].strip() if "(" in sfx_val else sfx_val
            audio_prompt_parts.append(f"Specific SFX: {sfx_clean}")
        final_audio = ". ".join(audio_prompt_parts)

        # --- FÍSICA (NUEVO) ---
        physics_prompt = ""
        if p.get('physics_medium') and "Neutral" not in p['physics_medium']:
            # Añadimos el medio base
            medium_clean = p['physics_medium'].split('(')[0].strip()
            # Añadimos los detalles seleccionados
            details = p.get('physics_details', [])
            if details:
                # Limpiamos los textos (quitamos lo que hay entre paréntesis en español)
                details_clean = [d.split('(')[0].strip() for d in details]
                physics_str = ", ".join(details_clean)
                physics_prompt = f"Physics simulation: {medium_clean} environment featuring {physics_str}"

        # --- CONSTRUCCIÓN COMÚN ---
        segments = []
        if self.is_img2video:
            segments.append(f"Based on the uploaded image '{self.image_filename}'.")
            keep = []
            if p.get('keep_subject'): keep.append("the main subject's appearance")
            if p.get('keep_bg'): keep.append("the background composition")
            if keep: segments.append("Strictly maintain " + " and ".join(keep) + ".")
            
            if p.get('img_action'): segments.append(p['img_action'])
        else:
            subj = p.get('subject', '')
            if p.get('details'): subj += f", wearing {p['details']}"
            
            visual_action = []
            if subj: visual_action.append(subj)
            if p.get('action'): visual_action.append(f"currently {p['action']}" if visual_action else f"A scene showing {p['action']}")
            if p.get('env'): visual_action.append(f"set within a {p['env']}")
            
            scene = ", ".join(visual_action)
            if scene: segments.append(scene + ".")
            if p.get('style'): segments.append(f"A {p['style']} style video.")

        # Añadimos Técnica y Física
        if p.get('light'): segments.append(f"Lighting: {p['light']}.")
        if p.get('camera'): segments.append(f"Camera movement: {p['camera']}.")
        
        # INYECCIÓN DE FÍSICA
        if physics_prompt: segments.append(physics_prompt + ".")
        
        # Audio y AR
        if final_audio: segments.append(f"Audio atmosphere: {final_audio}.")
        if p.get('ar'): segments.append(f"--ar {p['ar'].split(' ')[0]}")

        return re.sub(' +', ' ', " ".join(segments)).strip()

# --- INTERFAZ ---
with st.sidebar:
    st.header("🧬 Mis Personajes")
    with st.expander("Añadir Personaje Nuevo"):
        new_name = st.text_input("Nombre")
        new_desc = st.text_area("Descripción Visual")
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

# PANEL PRINCIPAL
st.title("🎬 Grok Video Builder")

# Vars default
keep_s, keep_b = True, True
act_img = ""
final_sub, act, det = "", "", ""
sty, env, lit, cam, ar = "", "", "", "", ""
aud_mood, aud_env, final_sfx = "", "", ""
phy_med, phy_det = "Neutral / None", []

if st.session_state.uploaded_image_name:
    st.info(f"Modo Imagen: {st.session_state.uploaded_image_name}")
    t1, t2, t3, t4 = st.tabs(["🖼️ Acción", "⚛️ Física", "🎥 Técnica", "🎵 Audio"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            keep_s = st.checkbox("Mantener Sujeto", True)
            keep_b = st.checkbox("Mantener Fondo", True)
        with c2:
            act_img = st.text_area("Acción", placeholder="Ej: sonriendo")
            
    with t2:
        phy_med = st.selectbox("Medio / Entorno Físico", list(PHYSICS_LOGIC.keys()), key="phy_m_img")
        phy_det = st.multiselect("Detalles de Simulación", PHYSICS_LOGIC[phy_med], key="phy_d_img")
        
    with t3:
        c1, c2, c3 = st.columns(3)
        with c1: cam = st.selectbox("Cámara", DEMO_CAMERAS, key="c_img")
        with c2: lit = st.selectbox("Luz", DEMO_LIGHTING, key="l_img")
        with c3: ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS, key="a_img")

    with t4:
        c1, c2 = st.columns(2)
        with c1: aud_mood = st.selectbox("Música", DEMO_AUDIO_MOOD, key="am_img")
        with c2: aud_env = st.selectbox("Ambiente", DEMO_AUDIO_ENV, key="ae_img")
        sfx_ch = st.selectbox("SFX", DEMO_SFX_COMMON, key="sfx_img")
        final_sfx = translate_to_english(st.text_input("Otro SFX", key="cust_sfx_img")) if "Custom" in sfx_ch else sfx_ch

    if st.button("✨ GENERAR (IMG)", type="primary"):
        with st.spinner("Procesando..."):
            try:
                b = GrokVideoPromptBuilder()
                b.activate_img2video(st.session_state.uploaded_image_name)
                b.set_field('keep_subject', keep_s)
                b.set_field('keep_bg', keep_b)
                b.set_field('img_action', translate_to_english(act_img))
                b.set_field('physics_medium', phy_med)
                b.set_field('physics_details', phy_det) # Lista
                b.set_field('camera', cam)
                b.set_field('light', lit)
                b.set_field('ar', ar)
                b.set_field('audio_mood', aud_mood)
                b.set_field('audio_env', aud_env)
                b.set_field('audio_sfx', final_sfx)
                res = b.build()
                st.session_state.generated_output = res
                st.session_state.history.append(res)
            except Exception as e: st.error(str(e))

else:
    # MODO TEXTO
    t1, t2, t3, t4, t5 = st.tabs(["📝 Historia", "⚛️ Física", "🎨 Visual", "🎥 Técnica", "🎵 Audio"])
    
    with t1:
        char_sel = st.selectbox("Actor", list(st.session_state.characters.keys()))
        final_sub = st.session_state.characters[char_sel] if st.session_state.characters[char_sel] else translate_to_english(st.text_input("Sujeto"))
        c1, c2 = st.columns(2)
        with c1: act = st.text_input("Acción")
        with c2: det = st.text_input("Detalles")

    with t2:
        st.info("Simulación de Fluidos y Partículas")
        phy_med = st.selectbox("Medio / Entorno Físico", list(PHYSICS_LOGIC.keys()), key="phy_m_txt")
        phy_det = st.multiselect("Detalles de Simulación (Elige varios)", PHYSICS_LOGIC[phy_med], key="phy_d_txt")

    with t3:
        c1, c2 = st.columns(2)
        with c1: sty = st.selectbox("Estilo", DEMO_STYLES)
        with c2: env = st.text_input("Lugar")

    with t4:
        c1, c2, c3 = st.columns(3)
        with c1: cam = st.selectbox("Cámara", DEMO_CAMERAS, key="c_txt")
        with c2: lit = st.selectbox("Luz", DEMO_LIGHTING, key="l_txt")
        with c3: ar = st.selectbox("Formato", DEMO_ASPECT_RATIOS, key="a_txt")

    with t5:
        c1, c2 = st.columns(2)
        with c1: aud_mood = st.selectbox("Música", DEMO_AUDIO_MOOD, key="am_txt")
        with c2: aud_env = st.selectbox("Ambiente", DEMO_AUDIO_ENV, key="ae_txt")
        sfx_ch = st.selectbox("SFX", DEMO_SFX_COMMON, key="sfx_txt")
        final_sfx = translate_to_english(st.text_input("Otro SFX", key="cust_sfx_txt")) if "Custom" in sfx_ch else sfx_ch

    if st.button("✨ GENERAR (TXT)", type="primary"):
        with st.spinner("Procesando..."):
            try:
                b = GrokVideoPromptBuilder()
                b.set_field('subject', final_sub)
                b.set_field('action', translate_to_english(act))
                b.set_field('details', translate_to_english(det))
                b.set_field('physics_medium', phy_med)
                b.set_field('physics_details', phy_det)
                b.set_field('style', translate_to_english(sty))
                b.set_field('env', translate_to_english(env))
                b.set_field('camera', cam)
                b.set_field('light', lit)
                b.set_field('ar', ar)
                b.set_field('audio_mood', aud_mood)
                b.set_field('audio_env', aud_env)
                b.set_field('audio_sfx', final_sfx)
                res = b.build()
                st.session_state.generated_output = res
                st.session_state.history.append(res)
            except Exception as e: st.error(str(e))

if st.session_state.generated_output:
    st.markdown("---")
    st.subheader("📝 Prompt Final con Física")
    final_txt = st.text_area("Resultado:", st.session_state.generated_output, height=150)
    st.code(final_txt, language="text")