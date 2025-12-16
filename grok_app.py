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

LIST_SHOT_TYPES = ["Neutral (Auto)", "Extreme Long Shot (Epic Scale)", "Long Shot (Full Body)", "Medium Shot (Waist Up)", "Close-Up (Face Focus)", "Extreme Close-Up (Macro Detail)"]
LIST_ANGLES = ["Neutral (Auto)", "Low Angle (Heroic/Ominous)", "High Angle (Vulnerable)", "Dutch Angle (Chaos/Tension)", "Bird's Eye View (Top-Down)", "Drone Aerial View (Establishing)"]
LIST_LENSES = ["Neutral (Auto)", "16mm Wide Angle (Expansive)", "35mm Prime (Street/Docu)", "50mm Lens (Natural Eye)", "85mm f/1.4 (Portrait Bokeh)", "100mm Macro (Micro Detail)", "Fisheye (Distorted)"]
DEMO_LIGHTING = ["Neutral (Auto)", "Harsh Golden Hour", "Dramatic Low-Key (Chiaroscuro)", "Soft Overcast (Diffusion)", "Neon City Glow (Cyberpunk)", "Stark Space Sunlight"]
DEMO_ASPECT_RATIOS = ["16:9 (Landscape)", "21:9 (Cinematic)", "9:16 (Social Vertical)", "4:3 (Classic)", "1:1 (Square)"]

# GEM EXPANSION
GEM_EXPANSION_PACK = {
    "run": "sweat and mud on a face contorted in absolute panic as they look back over their shoulder, heavy motion blur on extremities",
    "correr": "sweat and mud on a face contorted in absolute panic as they look back over their shoulder, heavy motion blur on extremities",
    "chase": "a colossal, ancient beast with jagged scales breaches the ground, charging and kicking up a massive chaotic cloud of dust, rock, and debris",
    "persecución": "a colossal, ancient beast with jagged scales breaches the ground, charging and kicking up a massive chaotic cloud of dust, rock, and debris",
    "huyendo": "sprinting desperately directly toward the camera, adrenaline fueled atmosphere",
    "monster": "terrifying subterranean beast, organic textures, massive scale, ominous presence",
    "mamut": "ancient titanic mammoth, matted fur texture, massive tusks destroying the environment, earth-shaking impact",
    "transform": "surreal visual metamorphosis, plastic texture cracking and morphing into realistic organic skin, glowing energy boundaries, anatomical shifting",
    "elefante": "hyper-realistic skin texture, wrinkled grey hide, imposing weight",
    "plastic": "shiny synthetic polymer texture, artificial reflection"
}

NARRATIVE_TEMPLATES = {
    "Libre (Escribir propia)": "",
    "🎤 Performance Musical (Lip Sync)": "Close-up on the subject singing passionately. Mouth moves in perfect sync with the audio. Emotions range from intense focus to release.",
    "🏃 Persecución (Sujeto vs Monstruo)": "The subject is sprinting desperately towards the camera, face contorted in panic. Behind them, a colossal creature is charging, kicking up debris.",
    "🧟 Transformación Súbita": "At second 0, the scene is static. Suddenly, the inanimate object behind the subject rapidly transforms into a massive, living threat.",
}

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
if 'characters' not in st.session_state: st.session_state.characters = DEFAULT_CHARACTERS.copy()
if 'custom_props' not in st.session_state: st.session_state.custom_props = DEFAULT_PROPS.copy()
if 'generated_output' not in st.session_state: st.session_state.generated_output = ""
if 'generated_explanation' not in st.session_state: st.session_state.generated_explanation = ""
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# Inicialización de widgets
default_vars = {
    'act_input': "",
    'char_select': "-- Seleccionar Protagonista --",
    'shot_select': LIST_SHOT_TYPES[0],
    'angle_select': LIST_ANGLES[0],
    'lens_select': LIST_LENSES[0],
    'lit_select': DEMO_LIGHTING[0],
    'sty_select': DEMO_STYLES[0],
    'env_select': DEMO_ENVIRONMENTS[0],
    'ar_select': DEMO_ASPECT_RATIOS[0],
    'phy_select': "Neutral / Estudio",
    'last_img_name': ""
}
for k, v in default_vars.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 5. FUNCIONES ---
def translate_to_english(text):
    if not text or not str(text).strip(): return ""
    if TRANSLATOR_AVAILABLE:
        try: return GoogleTranslator(source='auto', target='en').translate(str(text))
        except: return str(text)
    return str(text)

def expand_prompt_like_gem(text):
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
        if ratio > 1.5: return 0 # 16:9
        elif ratio < 0.8: return 2 # 9:16
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
        res['angle'] = "