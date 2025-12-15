import streamlit as st
import random
import re
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Grok Video Builder Pro", layout="wide", page_icon="🎬")

# --- MEMORIA (SESSION STATE) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'uploaded_image_name' not in st.session_state:
    st.session_state.uploaded_image_name = None
if 'generated_output' not in st.session_state:
    st.session_state.generated_output = ""

# --- TUS PERSONAJES ---
if 'characters' not in st.session_state:
    st.session_state.characters = {
        "Nada (Generar nuevo)": "",
        
        "TON (Guitarra)": """A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique, characterized by an elegant verticality and lean, wiry muscularity rather than bulk. He possesses a confident, architectural facial structure with high, defined cheekbones and a jawline that cuts a sharp geometric profile, overlaid with a texture of faint, authentic skin porosity and a meticulously groomed five o'clock shadow that maps the contours of his lower face. His hair is styled in a modern, textured quiff with a matte finish, dark chestnut strands caught in a chaotic yet deliberate motion, featuring a subtle fade at the temples that blends seamlessly into the skin. He is attired in a high-quality, charcoal-grey heavyweight cotton t-shirt that drapes loosely over his slender frame, revealing the definition of his clavicles and shoulders without clinging, paired with dark, raw selvedge denim jeans that exhibit realistic stiffness and indigo depth. The lighting is cinematic and moody, utilizing a soft-box key light from the upper left to carve out the depth of his facial features in a Rembrandt style, while a cool-toned rim light separates his dark silhouette from a blurred, neutral urban background, creating a volumetric atmosphere. The image quality exudes the characteristics of an 85mm prime lens photograph at f/1.8, capturing the wetness in his eyes and the tactile weave of the fabric with startling clarity, rendered in 8k resolution with a raw, unfiltered aesthetic. He is holding and playing a specific electric guitar model, adopting a passionate musician pose, fingers on the fretboard.""",

        "TON (Micro)": """A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique, characterized by an elegant verticality and lean, wiry muscularity rather than bulk. He possesses a confident, architectural facial structure with high, defined cheekbones and a jawline that cuts a sharp geometric profile, overlaid with a texture of faint, authentic skin porosity and a meticulously groomed five o'clock shadow that maps the contours of his lower face. His hair is styled in a modern, textured quiff with a matte finish, dark chestnut strands caught in a chaotic yet deliberate motion, featuring a subtle fade at the temples that blends seamlessly into the skin. He is attired in a high-quality, charcoal-grey heavyweight cotton t-shirt that drapes loosely over his slender frame, revealing the definition of his clavicles and shoulders without clinging, paired with dark, raw selvedge denim jeans that exhibit realistic stiffness and indigo depth. The lighting is cinematic and moody, utilizing a soft-box key light from the upper left to carve out the depth of his facial features in a Rembrandt style, while a cool-toned rim light separates his dark silhouette from a blurred, neutral urban background, creating a volumetric atmosphere. The image quality exudes the characteristics of an 85mm prime lens photograph at f/1.8, capturing the wetness in his eyes and the tactile weave of the fabric with startling clarity, rendered in 8k resolution with a raw, unfiltered aesthetic. He is holding a vintage microphone close to his mouth, singing passionately with eyes slightly closed, performing on stage.""",

        "Freya (Kayak)": """A hyper-realistic, cinematic medium shot of a 25-year-old female survivor with a statuesque, athletic 170cm and 60kg physique, exhibiting defined lean muscle mass and core tension typical of extreme exertion. She possesses a striking, symmetrical face with high cheekbones, a sharp jawline, and intense, piercing hazel eyes dilated with adrenaline; her skin texture is rendered with extreme fidelity, showcasing visible pores, vellus hair on the jawline, and uneven localized redness, all glistening with hyper-detailed water beads and sweat exhibiting realistic subsurface scattering. She is completely drenched; her heavy, dark brunette hair is matted and sodden, clinging flat against her skull and neck in distinct wet clumps, with stray strands sticking to her wet face. She is outfitted in a futuristic 'Aquatic Warcore' tactical wetsuit constructed from matte black Yamamoto 39-cell limestone neoprene featuring contrasting glossy geometric Glideskin chest panels, reinforced GBS seams, and a complex mil-spec nylon webbing harness system secured with metallic Cobra buckles and asymmetrical waterproof zippers. The scene is immersed in a turbulent marine environment during the blue hour, characterized by volumetric sea mist, driving rain, and dramatic cool-toned storm lighting that creates sharp specular highlights on the wet neoprene and skin, captured with the shallow depth of field of an 85mm f/1.8 lens, creating a raw, gritty, survivalist aesthetic in 8k resolution. She is paddling a Hyper-realistic expedition sea kayak, model Point 65 Freya 18. Geometry: Features a distinctive 'surfski-hybrid' silhouette with a razor-sharp, plumb vertical bow entry transitioning into a high-volume, bulbous foredeck designed to shed massive waves, contrasting with a tapered, low-profile stern section to minimize windage. Hull: Round hull cross-section with minimal rocker, optimized for speed, showcasing a seamless 'integrated keel rudder' ventral fin at the rear that blends organically into the carbon fiber hull structure. Cockpit: Large keyhole-shaped cockpit with a raised carbon rim, outfitted with a performance bucket seat. Storage & Hatches: Two large oval black rubber hatch covers positioned flush on the fore and aft decks. Rigging & Objects: The deck is laden with authentic 'expedition-ready' gear: a black waterproof North Water peaked deck bag strapped to the foredeck bungee matrix, a recessed Silva 70P compass, a spare split carbon paddle secured under the rear triangular bungee net. Livery & Text: High-gloss 'Black & Red' split colorway (Obsidian Black hull, Safety Red deck); bold, sans-serif white text 'FREYA' prominent on the bow flank; 'Point 65° N' logo on the side; a linear array of small colorful 'national flag stickers' representing circumnavigated countries and 'Thule' sponsor decals lining the cockpit area. Material & Light: Ray-traced gel coat finish with subsurface scattering, wet surface shaders reflecting a stormy grey ocean sky, salt spray residue on the black carbon hull. Art Style: 8k resolution, technical marine photography, Unreal Engine 5 render, highly detailed textures, dramatic atmosphere."""
    }

# --- FUNCIONES ---
def translate_to_english(text):
    if text and text.strip():
        try:
            return GoogleTranslator(source='auto', target='en').translate(text)
        except Exception as e:
            return text
    return ""

# --- LISTAS DE OPCIONES ---
DEMO_STYLES = [
    "Photorealistic 8k", "Anime / Manga", "3D Render (Octane)", "Oil Painting",
    "Vintage Film (VHS)", "Claymation", "Pixel Art (8-bit)", "Abstract / Experimental",
    "Surrealism (Dreamlike)", "Fantasy / RPG", "Cyberpunk / Sci-Fi", "Film Noir / B&W",
    "Watercolor / Ink"
]

DEMO_LIGHTING = [
    "Natural Daylight", "Cinematic / Dramatic", "Cyberpunk / Neon",
    "Studio Lighting", "Golden Hour", "Low Key / Dark"
]

DEMO_ASPECT_RATIOS = [
    "16:9 (Landscape)", "9:16 (Portrait)", "1:1 (Square)", "21:9 (Ultrawide)"
]

DEMO_CAMERAS = [
    "Static", "Zoom In", "Zoom Out", "Dolly In", "Dolly Out",
    "Truck Left", "Truck Right", "Pedestal Up", "Pedestal Down",
    "Pan", "Tilt", "Orbit", "Handheld / Shake", "FPV Drone"
]

# LISTAS DE AUDIO
DEMO_AUDIO_MOOD = [
    "No Music (Silence)", "Cinematic Orchestral (Epic)", "Cyberpunk Synthwave", 
    "Lo-Fi Chill", "Horror / Suspense", "Upbeat / Happy", "Sad / Melancholic",
    "Heavy Metal / Rock", "Ambient Drone"
]

DEMO_AUDIO_ENV = [
    "No Background Noise", "City Traffic & Sirens", "Heavy Rain & Thunder", 
    "Forest / Nature Sounds", "Ocean Waves", "Crowded Bar / Restaurant", 
    "Space Station Hum", "Battlefield Chaos", "Office Ambience"
]

# LISTA DE EFECTOS PUNTUALES (SFX)
DEMO_SFX_COMMON = [
    "None (Ninguno)",
    "Footsteps on concrete (Pasos)",
    "Rain drops hitting surfaces (Gotas lluvia)",
    "Wind howling (Viento aullando)",
    "Explosion and debris (Explosión)",
    "Gunfire / Blaster shots (Disparos)",
    "Swords clashing (Espadas)",
    "Crowd cheering (Multitud vitoreando)",
    "Camera shutter clicks (Obturador)",
    "Keyboard typing (Tecleo)",
    "Siren wailing (Sirenas)",
    "Heartbeat (Latido)",
    "✏️ Custom / Other... (Escribir propio)" 
]

# --- MOTOR DE PROMPTS ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = {}
        self.is_img2video = False
        self.image_filename = ""

    # --- CORRECCIÓN DEL ERROR AQUÍ ---
    def set_field(self, key, value):
        # Si es texto, quitamos espacios. Si es Booleano (Checkbox), lo guardamos tal cual.
        if isinstance(value, str):
            self.parts[key] = value.strip()
        else:
            self.parts[key] = value

    def activate_img2video(self, filename):
        self.is_img2video = True
        self.image_filename = filename

    def build(self) -> str:
        p = self.parts
        
        # --- AUDIO COMPLEJO ---
        audio_prompt_parts = []
        if p.get('audio_mood') and "No Music" not in p['audio_mood']:
            audio_prompt_parts.append(f"Music style: {p['audio_mood']}")
        if p.get('audio_env') and "No Background" not in p['audio_env']:
            audio_prompt_parts.append(f"Environment sound: {p['audio_env']}")
        if p.get('audio_sfx') and "None" not in p['audio_sfx']:
            # Limpiamos el texto del selector (ej: quitar "(Pasos)")
            if isinstance(p['audio_sfx'], str):
                sfx_clean = p['audio_sfx'].split('(')[0].strip()
                audio_prompt_parts.append(f"Specific SFX: {sfx_clean}")
            
        final_audio_string = ". ".join(audio_prompt_parts)

        # --- MODO IMAGEN ---
        if self.is_img2video:
            segments = [f"Based on the uploaded image '{self.image_filename}'."]
            
            keep = []
            if p.get('keep_subject'): keep.append("the main subject's appearance")
            if p.get('keep_bg'): keep.append("the background composition")
            if keep: segments.append("Strictly maintain " + " and ".join(keep) + ".")

            if p.get('img_action'):
                act = p['img_action']
                segments.append(act[0].upper() + act[1:] if act else "")

            if p.get('camera'): segments.append(f"Cinematography features a {p['camera']} movement.")
            if p.get('light'): segments.append(f"Lighting matches {p['light']}.")
            
            if final_audio_string:
                segments.append(f"Audio atmosphere includes: {final_audio_string}.")
            
            if p.get('ar'):
                ar_val = p['ar'].split(' ')[0] 
                segments.append(f"--ar {ar_val}")
            
            return re.sub(' +', ' ', " ".join(segments)).strip()

        # --- MODO TEXTO ---
        else:
            visual = []
            subj = p.get('subject', '')
            if p.get('details'): subj += f", wearing or featuring {p['details']}"
            if subj: visual.append(subj)

            if p.get('action'):
                act = p['action']
                visual.append(visual[-1] + f", currently {act}" if visual else f"A scene showing {act}")

            if p.get('env'): visual.append(f"set within a {p['env']}")
            if p.get('light'): visual.append(f"illuminated by {p['light']}")

            scene = ", ".join(visual)
            if scene: scene = scene[0].upper() + scene[1:] + "."

            final = []
            if p.get('style'): final.append(f"A {p['style']} style video.")
            if scene: final.append(scene)
            if p.get('camera'): final.append(f"Cinematography features a {p['camera']} movement.")
            
            if final_audio_string:
                final.append(f"Audio atmosphere includes: {final_audio_string}.")
            
            if p.get('ar'):
                ar_val = p['ar'].split(' ')[0]
                final.append(f"--ar {ar_val}")

            return re.sub(' +', ' ', " ".join(final)).strip()

# --- INTERFAZ ---
with st.sidebar:
    st.header("🧬 Mis Personajes")
    with st.expander("Añadir Personaje Nuevo"):
        new_name = st.text_input("Nombre")
        new_desc = st.text_area("Descripción Visual")
        if st.button("Guardar en Memoria"):
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

# Variables vacías
final_sub = ""
sty, act, det, env = "", "", "", ""
lit, cam, ar = "", "", ""
aud_mood, aud_env = "", ""

# Variable especial para el SFX final
final_sfx_selection = ""

if st.session_state.uploaded_image_name:
    # --- MODO IMAGEN ---
    st.info(f"Modo Imagen Activo: {st.session_state.uploaded_image_name}")
    
    tab1, tab2, tab3 = st.tabs(["🖼️ Referencia & Acción", "🎥 Técnica", "🎵 Audio Pro"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Qué preservar")
            keep_s = st.checkbox("Mantener Sujeto", True)
            keep_b = st.checkbox("Mantener Fondo", True)
        with c2:
            st.markdown("##### Acción")
            act_img = st.text_area("¿Qué movimiento quieres?", placeholder="Ej: Que sonría lentamente", height=100)
            
    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1: cam_img = st.selectbox("Cámara", DEMO_CAMERAS)
        with c2: lit_img = st.selectbox("Iluminación", DEMO_LIGHTING)
        with c3: ar_img = st.selectbox("Formato", DEMO_ASPECT_RATIOS)
            
    with tab3:
        c_au1, c_au2 = st.columns(2)
        with c_au1: aud_mood_img = st.selectbox("Estilo Musical", DEMO_AUDIO_MOOD)
        with c_au2: aud_env_img = st.selectbox("Ambiente de Fondo", DEMO_AUDIO_ENV)
        
        # SELECTOR DE SFX INTELIGENTE
        st.markdown("##### Efectos Puntuales (SFX)")
        sfx_choice_img = st.selectbox("Selecciona Efecto", DEMO_SFX_COMMON, key="sfx_img")
        
        if "Custom" in sfx_choice_img:
            custom_sfx_val = st.text_input("Describe el efecto sonoro:", key="custom_sfx_img_input")
            final_sfx_selection = translate_to_english(custom_sfx_val)
        else:
            final_sfx_selection = sfx_choice_img

    st.markdown("---")
    if st.button("✨ GENERAR VIDEO-PROMPT (IMAGEN)", type="primary"):
        b = GrokVideoPromptBuilder()
        b.activate_img2video(st.session_state.uploaded_image_name)
        b.set_field('keep_subject', keep_s)
        b.set_field('keep_bg', keep_b)
        b.set_field('img_action', translate_to_english(act_img))
        b.set_field('camera', cam_img)
        b.set_field('light', lit_img)
        b.set_field('ar', ar_img)
        b.set_field('audio_mood', aud_mood_img)
        b.set_field('audio_env', aud_env_img)
        b.set_field('audio_sfx', final_sfx_selection)
        
        st.session_state.generated_output = b.build()
        st.session_state.history.append(st.session_state.generated_output)

else:
    # --- MODO TEXTO ---
    tab_basic, tab_visual, tab_tech, tab_audio = st.tabs(["📝 Básico (Historia)", "🎨 Visual", "🎥 Técnica", "🎵 Audio Pro"])
    
    with tab_basic:
        st.subheader("El Protagonista y la Acción")
        char_sel = st.selectbox("Elige Actor:", list(st.session_state.characters.keys()))
        dna = st.session_state.characters[char_sel]

        if dna:
            st.success(f"🎭 Actuando: {char_sel}")
            final_sub = dna
        else:
            sub_raw = st.text_input("Sujeto (¿Quién?)", placeholder="Ej: Un astronauta gordo")
            final_sub = translate_to_english(sub_raw)
            
        c1, c2 = st.columns(2)
        with c1: act = st.text_input("Acción Principal", placeholder="Ej: corriendo asustado")
        with c2: det = st.text_input("Detalles Temporales", placeholder="Ej: ropa mojada, sucio")

    with tab_visual:
        st.subheader("Estética de la escena")
        c1, c2 = st.columns(2)
        with c1:
            sty = st.selectbox("Estilo Artístico", DEMO_STYLES)
            env = st.text_input("Entorno / Lugar", placeholder="Ej: bosque futurista")
        with c2:
            lit = st.selectbox("Iluminación", DEMO_LIGHTING)

    with tab_tech:
        st.subheader("Dirección de Cámara")
        c1, c2 = st.columns(2)
        with c1: cam = st.selectbox("Movimiento de Cámara", DEMO_CAMERAS)
        with c2: ar