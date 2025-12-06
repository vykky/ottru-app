import streamlit as st
import pandas as pd
import os
import sqlite3
import unicodedata
import time
from google import genai

# 1. PAGE SETUP (Sidebar Expanded)
st.set_page_config(
    layout="wide", 
    page_title="Ottru", 
    page_icon="✍️", 
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if 'input_content' not in st.session_state:
    st.session_state.input_content = "" 

# --- CLEAR BUTTON CALLBACK (FIXED) ---
def clear_text_callback():
    st.session_state.input_content = ""
    st.session_state.input_key = "" 

# --- API KEY SECURITY ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except:
    client = None

# --- CSS STYLES ---
st.markdown("""
<style>
/* ============================================================ */
/* 1. GOOGLE FONT IMPORT                                        */
/* ============================================================ */
@import url('https://fonts.googleapis.com/css2?family=Hind+Madurai:wght@700&family=Mukta+Malar:wght@800&display=swap');

/* Apply font to general content */
.stTextArea textarea, .stMarkdown p, .stRadio label, .results-box {
    font-family: 'Hind Madurai', 'Nirmala UI', sans-serif !important;
}

/* ============================================================ */
/* 2. HERO HEADER DESIGN                                        */
/* ============================================================ */
.hero-container { padding-bottom: 20px; }
.hero-title {
    font-family: 'Mukta Malar', sans-serif; font-size: 7rem; font-weight: 900; color: #4A0404;
    margin-bottom: -15px; line-height: 1.1; text-shadow: 3px 3px 0px rgba(0,0,0,0.1);
}
.hero-tagline-wrapper { display: flex; align-items: center; margin-top: 5px; }
.hero-red-bar { width: 6px; height: 32px; background-color: #C62828; margin-right: 15px; border-radius: 2px; }
.hero-tagline-text {
    font-size: 1.6rem; color: #555; font-weight: 700; font-family: 'Hind Madurai', sans-serif;
    letter-spacing: 0.5px; margin-bottom: 0px !important;
}

/* ============================================================ */
/* 3. SIDEBAR & TECH LOGO                                       */
/* ============================================================ */
.tech-logo-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 25px; }
.tech-box {
    position: relative; width: 110px; height: 110px; background-color: #0d0d0d; border-radius: 22px;        
    border: 2px solid #00FFFF; box-shadow: 0 0 15px #00FFFF, inset 0 0 15px rgba(0, 255, 255, 0.15);
    display: flex; align-items: center; justify-content: center;
}
.tech-letter {
    color: #ffffff; font-size: 70px; font-weight: 800; margin-top: 15px; text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
    font-family: 'Mukta Malar', sans-serif !important; line-height: 1; position: relative; z-index: 1;
}
.tech-dot {
    position: absolute; top: 18px; left: 50%; transform: translateX(-50%); width: 14px; height: 14px;
    background-color: #00FFFF; border-radius: 50%; box-shadow: 0 0 8px #00FFFF; z-index: 10;
    animation: glowPulse 2s infinite alternate;
}
.tech-title {
    font-size: 28px; font-weight: 900; color: #4A0404; letter-spacing: 3px; margin-top: 15px;
    text-transform: uppercase; font-family: 'Arial', sans-serif !important;
}
/* Sidebar Toggle Button Fix */
[data-testid="stSidebarCollapsedControl"] {
    position: fixed !important; top: 20px !important; left: 20px !important; z-index: 999999 !important;
    background-color: #4A0404 !important; color: white !important; border-radius: 50% !important;
    padding: 5px !important; border: 2px solid white !important; height: 40px !important; width: 40px !important;
}

/* ============================================================ */
/* 4. LEARNED WORDS BOX STYLE (CLEANED UP)                      */
/* ============================================================ */
.learned-words-box {
    /* Light Blue Color Change */
    background-color: #e6f7ff; 
    color: #004085; 
    border-left: 5px solid #007bff; 
    
    /* Layout & Stability */
    padding: 15px; 
    border-radius: 10px; 
    margin-bottom: 20px;
    transition: all 0.3s ease-in-out; 
}

/* ============================================================ */
/* 5. UI ELEMENTS & LOADER                                      */
/* ============================================================ */
div[role="radiogroup"] label > div:first-child { display: none !important; }
div[role="radiogroup"] { display: flex; flex-direction: row; gap: 12px; flex-wrap: wrap; }
div[role="radiogroup"] label {
    background-color: #4A0404 !important; padding: 10px 24px !important; border-radius: 50px !important;
    border: 2px solid #4A0404 !important; cursor: pointer !important; text-align: center !important; min-width: 120px !important;
}
div[role="radiogroup"] label p { color: white !important; font-weight: bold !important; font-size: 16px !important; }
div[role="radiogroup"] label:has(input:checked) { background-color: #ffffff !important; transform: scale(1.05) !important; }
div[role="radiogroup"] label:has(input:checked) p { color: #4A0404 !important; }

/* Buttons & Text Area */
div.stButton > button {
    background-color: #4A0404 !important; color: white !important; border-radius: 50px !important;
    font-weight: 900 !important; font-size: 16px !important; text-transform: uppercase !important; height: 3.5em !important; width: 100% !important;
}
.stTextArea textarea { height: 400px !important; min-height: 400px !important; border-radius: 12px !important; border: 2px solid #ccc !important; font-size: 18px !important; }
.results-box { min-height: 400px !important; background-color: white !important; padding: 30px !important; border-radius: 12px !important; border: 2px solid #4A0404 !important; margin-top: 28px !important; line-height: 2.8 !important; }

/* Improved Train Animation */
@keyframes moveTrain {
    0% { transform: translateX(-150%); }
    100% { transform: translateX(150%); }
}
.train-track {
    width: 100%; background-color: #f0f0f0; border-bottom: 4px solid #555;
    padding: 20px 0; margin-top: 60px; border-radius: 8px; overflow: hidden; position: relative; white-space: nowrap;
}
.train-mover {
    display: inline-block; animation: moveTrain 3s linear infinite;
}
.train-bogie {
    display: inline-block; padding: 10px 15px; margin: 0 2px;
    background-color: #D32F2F; color: white; font-weight: bold; font-size: 20px; border-radius: 4px; border: 2px solid #B71C1C;
}

/* Tooltips & Colors */
.ottru-correct { background-color: #E3F9E5; color: #155724; padding: 4px 8px; border-radius: 4px; font-weight: bold; border-bottom: 2px solid #28A745; }
.spell-fix { background-color: #E3F2FD; color: #0D47A1; padding: 4px 8px; border-radius: 4px; font-weight: bold; border-bottom: 2px solid #2196F3; }
.ottru-wrong { color: #B02A37; text-decoration: underline; text-decoration-style: wavy; font-weight: bold; }
.tooltip-container { position: relative; display: inline-block; cursor: pointer; }
.tooltiptext { visibility: hidden; width: 220px; background-color: #1a1a1a; color: #fff; text-align: center; border-radius: 6px; padding: 10px; font-size: 14px; position: absolute; z-index: 9999; bottom: 135%; left: 50%; margin-left: -110px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
.tooltip-container:hover .tooltiptext { visibility: visible; }

/* --- 15 SECOND FADE OUT ANIMATION (FIXED FOR STABILITY) --- */
@keyframes fadeOutAnimation {
    0% { opacity: 1; visibility: visible; }
    93.33% { opacity: 1; visibility: visible; } /* Stay opaque for 14 seconds */
    100% { opacity: 0; visibility: hidden; } /* Fade out over the final 1 second */
}
.fade-out-box {
    animation: fadeOutAnimation 15s forwards;
}
</style>
""", unsafe_allow_html=True)

# --- DATABASE & LOGIC ---
@st.cache_resource
def get_db_connection():
    return sqlite3.connect("ottru.db", check_same_thread=False)

def get_word_from_db(word):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT type, rule_name FROM words WHERE word = ?", (word,))
        row = cursor.fetchone()
        if row: return {"type": row[0], "rule_name": row[1]}
    except: return None
    return None

@st.cache_data
def load_dictionary():
    file_path = "tamil_words.csv"
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip()
            df = df.set_index('word')
            return df.to_dict(orient='index')
        except: return {}
    return {}

DICTIONARY = load_dictionary()
VALLINAM_MAP = {"க": "க்", "ச": "ச்", "த": "த்", "ப": "ப்"}
def get_ottru(word): return VALLINAM_MAP.get(word[0], None) if word else None

# --- AUTO LEARN ---
def auto_learn_words(text):
    words = text.split()
    conn = get_db_connection()
    cursor = conn.cursor()
    new_words_list = []
    
    for word in words:
        clean_word = unicodedata.normalize('NFC', word.strip(".,!?-"))
        if len(clean_word) < 2: continue
        cursor.execute("SELECT word FROM words WHERE word = ?", (clean_word,))
        if cursor.fetchone(): continue
        w_type = "noun"; rule = "விதி: பெயர்ச்சொல் (Auto)"
        if clean_word.endswith(("க்கு", "ச்சு", "ட்டு", "த்து", "ப்பு", "ற்று")): w_type = "van_thodar"; rule = "விதி: வன்றொடர்"
        elif clean_word.endswith("ை"): rule = "விதி: ஐகாரம்"
        try:
            cursor.execute("INSERT INTO words (word, type, rule_name) VALUES (?, ?, ?)", (clean_word, w_type, rule))
            new_words_list.append(clean_word)
        except: pass
        
    if new_words_list: conn.commit()
    return new_words_list

# --- AI LOGIC ---
@st.cache_data
def ask_ai_expert(sentence, word):
    if not client: return "UNKNOWN", None, None, None
    try:
        prompt = (f"Analyze '{word}' in '{sentence}'. 1. Spelling (Mayangoli/Confusing letters): 'பலம்' eating?->'பழம்'. 2. POS: 'கத்தி'(Knife)=NOUN. 'கத்தி'(Action)=VERB. Response: STATUS: CORRECT/WRONG, CORRECTION: word, POS: NOUN/VERB")
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config={"temperature": 0.0})
        text = response.text
        status = "CORRECT"; correction = None; reason = None; pos = None
        if "STATUS: WRONG" in text:
            status = "WRONG"
            for line in text.split('\n'):
                if "CORRECTION:" in line: correction = line.split(":")[1].strip()
        if "VERB" in text: pos = "VERB"
        elif "NOUN" in text: pos = "NOUN"
        return status, correction, reason, pos
    except: return "UNKNOWN", None, None, None

def analyze_text(word, next_word, mode, full_sentence):
    clean_word = unicodedata.normalize('NFC', word.strip(".,!?-"))
    clean_next = unicodedata.normalize('NFC', next_word.strip(".,!?-"))
    result = {"type": "normal", "word": word, "tooltip": ""}
    if not clean_word or not clean_next: return result
    ottru = get_ottru(clean_next)
    is_casual = ("பேச்சு" in mode) or ("Casual" in mode)

    if not is_casual and ottru:
        if clean_word in ["திரு", "பொது", "புது"] and ottru:
            result["type"] = "ottru_add"; result["word"] = f"{clean_word}{ottru}"; result["original"] = clean_word; result["tooltip"] = f"அசல்: {clean_word} | விதி: முற்றியலுகரம்"
            return result
        if len(clean_word) == 1 and clean_word in ["தீ", "பூ", "கை", "தை"] and ottru:
            result["type"] = "ottru_add"; result["word"] = f"{clean_word}{ottru}"; result["original"] = clean_word; result["tooltip"] = f"அசல்: {clean_word} | விதி: ஓரெழுத்து ஒருமொழி"
            return result

    if clean_word.endswith("ம்") and len(clean_word) > 2 and ottru:
        result["type"] = "ottru_add" 
        base = clean_word.removesuffix("ம்")
        result["word"] = f"{base}{ottru}"; result["tooltip"] = f"அசல்: {clean_word} | விதி: மகர ஈறு"
        return result

    watch_list = ["கத்தி", "படி", "மாலை", "சிரி", "பலம்", "பழம்", "மரம்", "மறம்"]
    ai_pos = None
    if clean_word in watch_list:
        status, correction, reason, pos = ask_ai_expert(full_sentence, clean_word)
        ai_pos = pos
        if status == "WRONG" and correction:
            result["type"] = "spelling"; result["word"] = correction; result["tooltip"] = f"பிழை: {clean_word} | திருத்தம்: {correction}"
            return result

    db_data = get_word_from_db(clean_word)
    if not db_data and clean_word in DICTIONARY: db_data = DICTIONARY[clean_word]
    action = "NONE"; rule_name = ""
    
    if db_data:
        if db_data['type'] in ['vinaithogai', 'ummaithogai', 'peyarecham']: action = "BLOCK"; rule_name = db_data.get('rule_name')
    
    if action == "NONE":
        if ai_pos == "VERB" and ottru: action = "ALLOW"; rule_name = "விதி: வினையெச்சம் (AI)"
        elif ai_pos == "NOUN": action = "PASS"; rule_name = "விதி: பெயர்ச்சொல் (AI)"

    if not is_casual and action == "NONE":
        if clean_word.endswith("ை") and len(clean_word) > 1: action = "ALLOW"; rule_name = "விதி: ஐகாரம்"
        elif clean_word.endswith("க்கு"): action = "ALLOW"; rule_name = "விதி: 4-ம் வேற்றுமை"
        elif clean_word.endswith(("டித்து", "ர்த்து", "த்து")): action = "ALLOW"; rule_name = "விதி: வினையெச்சம்"

    if action == "ALLOW" and ottru:
        result["type"] = "ottru_add"; result["word"] = f"{clean_word}{ottru}"; result["tooltip"] = f"அசல்: {clean_word} | {rule_name}"
    elif action == "BLOCK": result["type"] = "ottru_block"; result["word"] = clean_word; result["tooltip"] = f"{rule_name}"
    
    return result

# --- UI START ---
with st.sidebar:
    st.markdown("""
    <div class="tech-logo-wrapper">
        <div class="tech-box">
            <span class="tech-letter">க</span>
            <div class="tech-dot"></div>
        </div>
        <div class="tech-title">OTTRU</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.title("💡 உதவி")
    st.markdown("""
    **வண்ணக்குறிப்புகள்:**
    
    * <span style="color:#155724; background-color:#E3F9E5; padding:2px 6px; border-radius:4px; font-weight:bold;">பச்சை (Green)</span> : ஒற்று (க்,ச்,த்,ப்) சேர்க்கப்பட்டுள்ளது.
    * <span style="color:#B02A37; font-weight:bold;">சிவப்பு (Red)</span> : தேவையற்ற ஒற்று நீக்கப்பட்டுள்ளது.
    * <span style="color:#0D47A1; background-color:#E3F2FD; padding:2px 6px; border-radius:4px; font-weight:bold;">நீலம் (Blue)</span> : மயங்கொலி பிழை திருத்தம் (எ.கா: பலம் -> பழம்).
    
    **பயன்படுத்தும் முறை:**
    1. தமிழை உள்ளிடவும்.
    2. 'எழுத்து நடையை' தேர்வு செய்யவும்.
    3. 'ஒற்று திருத்து' அழுத்தவும்.
    """, unsafe_allow_html=True)
    st.caption("Min E Kavi")

# --- HEADER SECTION ---
st.markdown('<div class="hero-container">', unsafe_allow_html=True)
st.markdown('<div class="hero-title">ஒற்று</div>', unsafe_allow_html=True)
st.markdown("""
<div class="hero-tagline-wrapper">
    <div class="hero-red-bar"></div>
    <div class="hero-tagline-text">இலக்கணம் அறிந்திடு...! - ஒற்று திருத்திடு...!</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- LAYOUT ---
st.markdown('<div style="font-size: 20px; font-weight: 900; color: #333; margin-bottom: 15px;">எழுத்து நடையை தேர்ந்தெடுங்கள்:</div>', unsafe_allow_html=True)

mode = st.radio("Style Selection", ["இலக்கியம்", "ஊடகம்", "பேச்சு வழக்கு"], horizontal=True, label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("### ✍️ உள்ளீடு")
    
    user_text = st.text_area("", key='input_key', 
                             value=st.session_state.get('input_content', ""),
                             height=400,
                             placeholder="எழுத்தாளர்களே தங்களின் உள்ளீட்டை இங்கு எழுதவும்...")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        # Using on_click callback
        st.button("🗑️ நீக்கு", on_click=clear_text_callback)
            
    with c2:
        check_button = st.button("✨ ஒற்று திருத்து")

with col_right:
    st.markdown("### 🎯 முடிவு")
    result_placeholder = st.empty()
    
    if check_button:
        # Loader
        result_placeholder.markdown("""
        <div class="results-box" style="text-align: center;">
            <div class="train-track">
                <div class="train-mover">
                    <span class="train-bogie">க</span><span class="train-bogie">ச</span><span class="train-bogie">ட</span><span class="train-bogie">த</span><span class="train-bogie">ப</span><span class="train-bogie">ற</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        learned_words = auto_learn_words(user_text)
        
        time.sleep(1)

        # --- ATTRACTIVE LEARNING BOX (USING CLEAN CLASS) ---
        if learned_words:
            display_words = learned_words[:5]
            words_str = ", ".join(display_words)
            if len(learned_words) > 5:
                words_str += ", ..."
            
            # Using the cleaned-up CSS class
            st.markdown(f"""
            <div class="fade-out-box learned-words-box"> 
                <h4 style="margin:0; font-size:18px; font-family: 'Hind Madurai', sans-serif;">🎉 புதிய வார்த்தைகள்!</h4>
                <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold; font-family: 'Hind Madurai', sans-serif;">
                    {words_str}
                </p>
                <p style="margin-top: 5px; font-size: 14px; font-style: italic; font-family: 'Hind Madurai', sans-serif;">
                    தங்களால் இந்த புதிய வார்த்தைகளை நான் கற்றுக்கொண்டேன் நன்றி!
                </p>
            </div>
            """, unsafe_allow_html=True)

        result_html = '<div class="output-text">'
        words = user_text.split()
        skip_next = False
        full_sentence = user_text
        for i, word in enumerate(words):
            if skip_next: skip_next = False; continue
            clean_word = unicodedata.normalize('NFC', word.strip(".,!?-"))
            punctuation = word[len(clean_word):] if len(clean_word) > 0 else ""
            if i + 1 < len(words):
                next_word_raw = words[i+1]
                clean_next = unicodedata.normalize('NFC', next_word_raw.strip(".,!?-"))
            else: next_word_raw = ""; clean_next = ""
            
            res = analyze_text(clean_word, clean_next, mode, full_sentence)
            
            if res["type"] == "spelling":
                html = f"""<span class="tooltip-container"><span class="spell-fix">{res['word']}</span><span class="tooltiptext">{res['tooltip']}</span></span>"""
                result_html += f"{html}{punctuation} "
            elif res["type"] == "ottru_add":
                html = f"""<span class="tooltip-container"><span class="ottru-correct">{res['word']}</span><span class="tooltiptext">{res['tooltip']}</span></span>"""
                result_html += f"{html}{punctuation} {next_word_raw} "
                skip_next = True
            elif res["type"] == "ottru_block":
                html = f"""<span class="tooltip-container"><span class="ottru-wrong">{res['word']}</span><span class="tooltiptext">{res['tooltip']}</span></span>"""
                result_html += f"{html}{punctuation} {next_word_raw} "
                skip_next = True
            elif res["type"] == "normal" and res["tooltip"]:
                html = f"""<span class="tooltip-container">{res['word']}<span class="tooltiptext">{res['tooltip']}</span></span>"""
                result_html += f"{html}{punctuation} {next_word_raw} "
                skip_next = True
            else:
                result_html += f"{word} "
        result_html += "</div>"
        
        result_placeholder.markdown(f"""<div class="results-box">{result_html}</div>""", unsafe_allow_html=True)
    
    else:
        result_placeholder.markdown("""<div class="results-box" style="display: flex; align-items: center; justify-content: center; color: #888;"><i>முடிவுகள் இங்கே தோன்றும்...</i></div>""", unsafe_allow_html=True)

# --- ADD VERTICAL SPACE BEFORE FIXED FOOTER ---
st.markdown("<br>" * 10, unsafe_allow_html=True)


# --- FOOTER SECTION (FIXED & BOLD) ---
st.markdown("""
<div style='
    position: fixed; 
    bottom: 0; 
    left: 0; 
    right: 0; 
    text-align: center; 
    padding: 10px; 
    font-size: 14px; 
    color: #444; 
    background-color: #f0f0f0; 
    border-top: 1px solid #ccc;
    z-index: 1000;
    font-weight: bold;
'>
    © All rights reserved by MIN E KAVI (மின் கவி)
    <br>
    Developed & Designed by VIGNESH M | FOUNDER OF MIN E KAVI
</div>
""", unsafe_allow_html=True)