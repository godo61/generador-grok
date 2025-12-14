import streamlit as st
import random
import re
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Grok Video Builder Pro", layout="wide", page_icon="🎬")

# --- MEMORIA ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'uploaded_image_name' not in st.session_state:
    st.session_state.uploaded_image_name = None

# --- TUS PERSONAJES ---
if 'characters' not in st.session_state:
    st.session_state.characters = {
        "Nada (Generar nuevo)": "",

        # --- TON (GUITARRA) ---
        "TON (Guitarra)": """A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique, characterized by an elegant verticality and lean, wiry muscularity rather than bulk. He possesses a confident, architectural facial structure with high, defined cheekbones and a jawline that cuts a sharp geometric profile, overlaid with a texture of faint, authentic skin porosity and a meticulously groomed five o'clock shadow that maps the contours of his lower face. His hair is styled in a modern, textured quiff with a matte finish, dark chestnut strands caught in a chaotic yet deliberate motion, featuring a subtle fade at the temples that blends seamlessly into the skin. He is attired in a high-quality, charcoal-grey heavyweight cotton t-shirt that drapes loosely over his slender frame, revealing the definition of his clavicles and shoulders without clinging, paired with dark, raw selvedge denim jeans that exhibit realistic stiffness and indigo depth. The lighting is cinematic and moody, utilizing a soft-box key light from the upper left to carve out the depth of his facial features in a Rembrandt style, while a cool-toned rim light separates his dark silhouette from a blurred, neutral urban background, creating a volumetric atmosphere. The image quality exudes the characteristics of an 85mm prime lens photograph at f/1.8, capturing the wetness in his eyes and the tactile weave of the fabric with startling clarity, rendered in 8k resolution with a raw, unfiltered aesthetic. He is holding and playing a specific electric guitar model, adopting a passionate musician pose, fingers on the fretboard.""",

        # --- TON (MICRO) ---
        "TON (Micro)": """A hyper-realistic, medium-shot portrait of a striking male figure who embodies a razor-sharp 185 cm, 75 kg ecto-mesomorph physique, characterized by an elegant verticality and lean, wiry muscularity rather than bulk. He possesses a confident, architectural facial structure with high, defined cheekbones and a jawline that cuts a sharp geometric profile, overlaid with a texture of faint, authentic skin porosity and a meticulously groomed five o'clock shadow that maps the contours of his lower face. His hair is styled in a modern, textured quiff with a matte finish, dark chestnut strands caught in a chaotic yet deliberate motion, featuring a subtle fade at the temples that blends seamlessly into the skin. He is attired in a high-quality, charcoal-grey heavyweight cotton t-shirt that drapes loosely over his slender frame, revealing the definition of his clavicles and shoulders without clinging, paired with dark, raw selvedge denim jeans that exhibit realistic stiffness and indigo depth. The lighting is cinematic and moody, utilizing a soft-box key light from the upper left to carve out the depth of his facial features in a Rembrandt style, while a cool-toned rim light separates his dark silhouette from a blurred, neutral urban background, creating a volumetric atmosphere. The image quality exudes the characteristics of an 85mm prime lens photograph at f/1.8, capturing the wetness in his eyes and the tactile weave of the fabric with startling clarity, rendered in 8k resolution with a raw, unfiltered aesthetic. He is holding a vintage microphone close to his mouth, singing passionately with eyes slightly closed, performing on stage.""",

        # --- FREYA (KAYAK) ---
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
    "Photorealistic 8k",
    "Anime / Manga",
    "3D Render (Octane)",
    "Oil Painting",
    "Vintage Film (VHS)",
    "Claymation",
    "Pixel Art (8-bit)",
    "Abstract / Experimental",
    "Surrealism (Dreamlike)",
    "Fantasy / RPG",
    "Cyberpunk / Sci-Fi",
    "Film Noir / B&W",
    "Watercolor / Ink"
]

# ¡NUEVA LISTA DE ILUMINACIÓN!
DEMO_LIGHTING = [
    "Natural Daylight",
    "Cinematic / Dramatic",
    "Cyberpunk / Neon",
    "Studio Lighting",
    "Golden Hour",
    "Low Key / Dark"
]

DEMO_CAMERAS = ["Static shot", "Slow zoom in", "Fast tracking shot", "Drone flyover", "Handheld shaky cam", "Low angle"]

# --- MOTOR DE PROMPTS ---
class GrokVideoPromptBuilder:
    def __init__(self):
        self.parts = {}
        self.is_img2video = False
        self.image_filename = ""

    def set_field(self, key, value):
        self.parts[key] = value.strip()

    def activate_img2video(self, filename):
        self.is_img2video = True
        self.image_filename = filename

    def build(self) -> str:
        p = self.parts
        
        # MODO IMAGEN
        if self.is_img2video:
            segments = [f"Based on the uploaded image '{self.image_filename}'."]
            
            keep = []
            if p.get('keep_subject'): keep.append("the main subject's appearance")
            if p.get('keep_bg'): keep.append("the background composition")
            if keep: segments.append("Strictly maintain " + " and ".join(keep) + ".")

            if p.get('img_action'):
                act = p['img_action']
                segments.append(act[0].upper() + act[1:] if act else "")

            if p.get('camera'): segments.append(f"Cinematography features a {p['camera']}.")
            if p.get('audio'): segments.append(f"Audio atmosphere includes {p['audio']}.")
            # Añadimos iluminación en modo imagen también por si acaso
            if p.get('light'): segments.append(f"Lighting matches {p['light']}.")
            
            return re.sub(' +', ' ', " ".join(segments)).strip()

        # MODO TEXTO (PERSONAJES)
        else:
            visual = []
            subj = p.get('subject', '')
            if p.get('details'): subj += f", wearing or featuring {p['details']}"
            if subj: visual.append(subj)

            if p.get('action'):
                act = p['action']
                visual.append(visual[-1] + f", currently {act}" if visual else f"A scene showing {act}")

            if p.get('env'): visual.append(f"set within a {p['env']}")
            # Aquí inyectamos la iluminación seleccionada
            if p.get('light'): visual.append(f"illuminated by {p['light']}")

            scene = ", ".join(visual)
            if scene: scene = scene[0].upper() + scene[1:] + "."

            final = []
            if p.get('style'): final.append(f"A {p['style']} style video.")
            if scene: final.append(scene)
            if p.get('camera'): final.append(f"Cinematography features a {p['camera']}.")
            if p.get('audio'): final.append(f"Audio atmosphere includes {p['audio']}.")
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
                st.success("Guardado (Temporal)")
    
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

if st.session_state.uploaded_image_name:
    st.info(f"Modo Imagen: {st.session_state.uploaded_image_name}")
    col1, col2 = st.columns(2)
    with col1:
        keep_s = st.checkbox("Mantener Sujeto", True)
        keep_b = st.checkbox("Mantener Fondo", True)
    with col2:
        act_img = st.text_area("¿Qué movimiento quieres?", placeholder="Ej: Que sonría")
    
    # Aquí están los selectores técnicos para imagen
    c_img1, c_img2 = st.columns(2)
    with c_img1:
        cam_img = st.selectbox("Cámara", DEMO_CAMERAS)
    with c_img2:
        # Nuevo selector de luz para modo imagen
        lit_img = st.selectbox("Iluminación", DEMO_LIGHTING)
        
    aud_img = st.text_input("Audio")

    if st.button("✨ GENERAR VIDEO-PROMPT"):
        b = GrokVideoPromptBuilder()
        b.activate_img2video(st.session_state.uploaded_image_name)
        b.set_field('keep_subject', keep_s)
        b.set_field('keep_bg', keep_b)
        b.set_field('img_action', translate_to_english(act_img))
        b.set_field('camera', cam_img)
        b.set_field('light', lit_img) # Enviamos la luz
        b.set_field('audio', translate_to_english(aud_img))
        res = b.build()
        st.session_state.history.append(res)
        st.code(res, language='text')

else:
    st.info("Modo Historia (Texto / Personajes)")
    char_sel = st.selectbox("Elige Actor:", list(st.session_state.characters.keys()))
    dna = st.session_state.characters[char_sel]

    if dna:
        st.success(f"Actuando: {char_sel}")
        final_sub = dna
    else:
        sub_raw = st.text_input("Sujeto")
        final_sub = translate_to_english(sub_raw)

    c1, c2 = st.columns(2)
    with c1:
        sty = st.selectbox("Estilo Visual", DEMO_STYLES)
        act = st.text_input("Acción", placeholder="Ej: corriendo")
        det = st.text_input("Detalles Extra", placeholder="Ej: ropa mojada")
    with c2:
        env = st.text_input("Entorno", placeholder="Ej: bosque")
        # AQUÍ ESTÁ EL CAMBIO IMPORTANTE: SELECTBOX DE LUZ
        lit = st.selectbox("Iluminación", DEMO_LIGHTING)
        cam = st.selectbox("Cámara", DEMO_CAMERAS)
        aud = st.text_input("Audio")

    if st.button("✨ GENERAR PROMPT"):
        b = GrokVideoPromptBuilder()
        b.set_field('style', translate_to_english(sty))
        b.set_field('subject', final_sub)
        b.set_field('details', translate_to_english(det))
        b.set_field('action', translate_to_english(act))
        b.set_field('env', translate_to_english(env))
        b.set_field('light', lit) # Ya no traducimos, usamos el valor directo
        b.set_field('camera', cam)
        b.set_field('audio', translate_to_english(aud))
        res = b.build()
        st.session_state.history.append(res)
        st.code(res, language='text')