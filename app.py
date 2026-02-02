"""
MCAT Flashcard Study App - For Arsh 💜
A beautiful, comprehensive MCAT preparation application
"""

import streamlit as st
import json
import os
import random
import requests
import html
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

# ============================================
# PAGE CONFIGURATION - Must be first!
# ============================================
st.set_page_config(
    page_title="MCAT Study Hub - For Arsh 💜",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# FILE PATHS
# ============================================
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FLASHCARDS_FILE = os.path.join(DATA_DIR, 'flashcards.json')
PROGRESS_FILE = os.path.join(DATA_DIR, 'progress.json')
SRS_FILE = os.path.join(DATA_DIR, 'srs_data.json')

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'authenticated': False,
        'current_page': 'home',
        'current_card_index': 0,
        'show_answer': False,
        'score': {'correct': 0, 'incorrect': 0},
        'selected_category': 'all',
        'filtered_cards': [],
        'dark_mode': False,
        'quiz_active': False,
        'quiz_questions': [],
        'quiz_current': 0,
        'quiz_score': 0,
        'quiz_answers': [],
        'timer_active': False,
        'timer_start': None,
        'timer_duration': 60,
        'bookmarked_cards': set(),
        'study_streak': 0,
        'last_study_date': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================
# DATA LOADING FUNCTIONS
# ============================================
@st.cache_data
def load_flashcards():
    """Load flashcards from JSON file"""
    try:
        with open(FLASHCARDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"categories": [], "flashcards": []}

def load_progress():
    """Load user progress data"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'daily_scores': [], 'total_studied': 0, 'streak': 0, 'last_study_date': None}

def save_progress(progress):
    """Save user progress data"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2)

def load_srs_data():
    """Load spaced repetition data"""
    if os.path.exists(SRS_FILE):
        with open(SRS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'cards': {}}

def save_srs_data(data):
    """Save spaced repetition data"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SRS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# ============================================
# TRIVIA API FUNCTIONS
# ============================================
@st.cache_data(ttl=300)
def fetch_trivia_questions(amount: int = 10, category: int = 17) -> List[Dict]:
    """Fetch science questions from Open Trivia DB"""
    try:
        response = requests.get(
            f"https://opentdb.com/api.php?amount={amount}&category={category}&type=multiple",
            timeout=10
        )
        data = response.json()
        if data.get("response_code") == 0:
            questions = []
            for q in data.get("results", []):
                answers = [html.unescape(q["correct_answer"])] + [html.unescape(a) for a in q["incorrect_answers"]]
                random.shuffle(answers)
                questions.append({
                    "question": html.unescape(q["question"]),
                    "correct_answer": html.unescape(q["correct_answer"]),
                    "options": answers,
                    "difficulty": q["difficulty"],
                    "category": html.unescape(q["category"])
                })
            return questions
    except Exception as e:
        st.error(f"Could not fetch questions: {e}")
    return []

# ============================================
# CUSTOM CSS - Beautiful Modern Design
# ============================================
def load_css():
    """Load custom CSS for beautiful styling"""
    dark_mode = st.session_state.get('dark_mode', False)

    if dark_mode:
        bg_primary = "#1a1a2e"
        bg_secondary = "#16213e"
        bg_card = "#1f2937"
        text_primary = "#ffffff"
        text_secondary = "#a0aec0"
        accent = "#8b5cf6"
        accent_light = "#a78bfa"
        success = "#10b981"
        danger = "#ef4444"
        warning = "#f59e0b"
        border_color = "#374151"
    else:
        bg_primary = "#f8fafc"
        bg_secondary = "#ffffff"
        bg_card = "#ffffff"
        text_primary = "#1e293b"
        text_secondary = "#64748b"
        accent = "#8b5cf6"
        accent_light = "#a78bfa"
        success = "#10b981"
        danger = "#ef4444"
        warning = "#f59e0b"
        border_color = "#e2e8f0"

    st.markdown(f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');

    /* Global Styles */
    .stApp {{
        background: {bg_primary};
        font-family: 'Inter', sans-serif;
    }}

    /* Hide Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {bg_secondary};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {accent};
        border-radius: 4px;
    }}

    /* Login Container */
    .login-container {{
        max-width: 450px;
        margin: 0 auto;
        padding: 3rem;
        background: {bg_card};
        border-radius: 24px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
        border: 1px solid {border_color};
    }}

    .login-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}

    .login-logo {{
        font-size: 4rem;
        margin-bottom: 1rem;
    }}

    .login-title {{
        font-family: 'Poppins', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 0.5rem;
    }}

    .login-subtitle {{
        color: {text_secondary};
        font-size: 1rem;
    }}

    /* Main Header */
    .main-header {{
        background: linear-gradient(135deg, {accent} 0%, #ec4899 100%);
        padding: 2rem 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        position: relative;
        overflow: hidden;
    }}

    .main-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    }}

    .header-content {{
        position: relative;
        z-index: 1;
    }}

    .header-greeting {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }}

    .header-title {{
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }}

    .header-subtitle {{
        font-size: 1.1rem;
        opacity: 0.9;
    }}

    /* Navigation Cards */
    .nav-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }}

    .nav-card {{
        background: {bg_card};
        border-radius: 20px;
        padding: 2rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid {border_color};
        position: relative;
        overflow: hidden;
    }}

    .nav-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(139, 92, 246, 0.15);
        border-color: {accent};
    }}

    .nav-card-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}

    .nav-card-title {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 0.5rem;
    }}

    .nav-card-desc {{
        color: {text_secondary};
        font-size: 0.95rem;
        line-height: 1.5;
    }}

    .nav-card-badge {{
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: linear-gradient(135deg, {accent} 0%, #ec4899 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }}

    /* Flashcard Styles */
    .flashcard-container {{
        perspective: 1000px;
        margin: 2rem 0;
    }}

    .flashcard {{
        background: {bg_card};
        border-radius: 24px;
        padding: 3rem;
        min-height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        border: 2px solid {border_color};
        transition: all 0.3s ease;
        position: relative;
    }}

    .flashcard:hover {{
        box-shadow: 0 20px 60px rgba(139, 92, 246, 0.15);
        border-color: {accent};
    }}

    .flashcard-category {{
        position: absolute;
        top: 1.5rem;
        left: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .category-badge {{
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
    }}

    .badge-bio {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); }}
    .badge-chem {{ background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); }}
    .badge-physics {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }}
    .badge-psych {{ background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }}

    .high-yield-badge {{
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }}

    .flashcard-question {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: {text_primary};
        text-align: center;
        line-height: 1.6;
        max-width: 600px;
    }}

    .flashcard-answer {{
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-top: 1.5rem;
        max-width: 600px;
        border-left: 4px solid {success};
    }}

    .flashcard-answer-text {{
        font-size: 1.1rem;
        color: #065f46;
        line-height: 1.6;
    }}

    /* Stats Cards */
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }}

    .stat-card {{
        background: {bg_card};
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 2px solid {border_color};
        transition: all 0.3s ease;
    }}

    .stat-card:hover {{
        transform: translateY(-4px);
        border-color: {accent};
    }}

    .stat-icon {{
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }}

    .stat-value {{
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: {accent};
        line-height: 1;
    }}

    .stat-label {{
        color: {text_secondary};
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }}

    /* Quiz Styles */
    .quiz-option {{
        background: {bg_card};
        border: 2px solid {border_color};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
        color: {text_primary};
    }}

    .quiz-option:hover {{
        border-color: {accent};
        background: {bg_secondary};
    }}

    .quiz-option-correct {{
        border-color: {success} !important;
        background: rgba(16, 185, 129, 0.1) !important;
    }}

    .quiz-option-wrong {{
        border-color: {danger} !important;
        background: rgba(239, 68, 68, 0.1) !important;
    }}

    /* Progress Bar */
    .progress-container {{
        background: {border_color};
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        margin: 1rem 0;
    }}

    .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, {accent} 0%, #ec4899 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
    }}

    /* Timer */
    .timer-display {{
        font-family: 'Poppins', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        color: {accent};
        text-align: center;
        padding: 2rem;
        background: {bg_card};
        border-radius: 20px;
        border: 3px solid {border_color};
    }}

    .timer-warning {{
        color: {warning} !important;
    }}

    .timer-danger {{
        color: {danger} !important;
        animation: pulse 1s infinite;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}

    /* Buttons */
    .custom-button {{
        background: linear-gradient(135deg, {accent} 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 0.875rem 2rem;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .custom-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);
    }}

    .btn-success {{
        background: linear-gradient(135deg, {success} 0%, #059669 100%);
    }}

    .btn-danger {{
        background: linear-gradient(135deg, {danger} 0%, #dc2626 100%);
    }}

    /* Streak Display */
    .streak-badge {{
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }}

    /* Back Button */
    .back-button {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: {text_secondary};
        font-weight: 500;
        cursor: pointer;
        margin-bottom: 1rem;
        transition: color 0.2s ease;
    }}

    .back-button:hover {{
        color: {accent};
    }}

    /* Responsive adjustments */
    @media (max-width: 768px) {{
        .main-header {{
            padding: 1.5rem;
        }}
        .header-title {{
            font-size: 1.8rem;
        }}
        .flashcard {{
            padding: 2rem;
            min-height: 280px;
        }}
        .flashcard-question {{
            font-size: 1.2rem;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


# ============================================
# LOGIN PAGE
# ============================================
def login_page():
    """Beautiful login page with authentication"""
    load_css()

    st.markdown("""
    <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem;">
        <div class="login-container">
            <div class="login-header">
                <div class="login-logo">🩺</div>
                <div class="login-title">MCAT Study Hub</div>
                <div class="login-subtitle">Your personal MCAT preparation companion</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### 🔐 Sign In")
            email = st.text_input("📧 Email", placeholder="Enter your email address")
            password = st.text_input("🔑 Access Code", type="password", placeholder="Enter your access code")

            col_a, col_b = st.columns(2)
            with col_a:
                remember = st.checkbox("Remember me")

            submit = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

            if submit:
                if email == "ahkaur77@gmail.com" and password == "IloveyouArsh":
                    st.session_state.authenticated = True
                    st.session_state.current_page = 'home'
                    # Update streak
                    update_streak()
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; opacity: 0.7;">
            <small>Made with 💜 for Arsh's MCAT Journey</small><br>
            <small>© 2024 MCAT Study Hub</small>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# STREAK MANAGEMENT
# ============================================
def update_streak():
    """Update study streak"""
    progress = load_progress()
    today = date.today().isoformat()
    last_date = progress.get('last_study_date')

    if last_date:
        last = date.fromisoformat(last_date)
        diff = (date.today() - last).days

        if diff == 1:
            progress['streak'] = progress.get('streak', 0) + 1
        elif diff > 1:
            progress['streak'] = 1
        # If diff == 0, keep current streak
    else:
        progress['streak'] = 1

    progress['last_study_date'] = today
    save_progress(progress)
    st.session_state.study_streak = progress['streak']


# ============================================
# HOME PAGE
# ============================================
def home_page():
    """Main dashboard with navigation"""
    data = load_flashcards()
    progress = load_progress()

    # Header
    st.markdown(f"""
    <div class="main-header">
        <div class="header-content">
            <div class="header-greeting">Welcome back,</div>
            <div class="header-title">Arsh! 👋</div>
            <div class="header-subtitle">Ready to ace the MCAT? Let's study together! 💪</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats Row
    total_cards = len(data.get('flashcards', []))
    total_studied = sum(s.get('total', 0) for s in progress.get('daily_scores', []))
    avg_accuracy = 0
    if progress.get('daily_scores'):
        accuracies = [(s['correct']/s['total']*100) for s in progress['daily_scores'] if s['total'] > 0]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0

    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-value">{total_cards}</div>
            <div class="stat-label">Total Flashcards</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value">{total_studied}</div>
            <div class="stat-label">Cards Studied</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-value">{avg_accuracy:.0f}%</div>
            <div class="stat-label">Avg. Accuracy</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🔥</div>
            <div class="stat-value">{progress.get('streak', 0)}</div>
            <div class="stat-label">Day Streak</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Cards
    st.markdown("### 📖 Study Modes")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎴 **Flashcard Study**\n\nReview MCAT flashcards with spaced repetition",
                    use_container_width=True, key="nav_flashcards"):
            st.session_state.current_page = 'flashcards'
            st.rerun()

    with col2:
        if st.button("🧪 **Quiz Mode**\n\nTest yourself with science questions from online",
                    use_container_width=True, key="nav_quiz"):
            st.session_state.current_page = 'quiz'
            st.rerun()

    col3, col4 = st.columns(2)

    with col3:
        if st.button("⏱️ **Timed Practice**\n\nPractice under MCAT time pressure",
                    use_container_width=True, key="nav_timed"):
            st.session_state.current_page = 'timed'
            st.rerun()

    with col4:
        if st.button("📊 **Progress & Stats**\n\nView your study analytics and history",
                    use_container_width=True, key="nav_progress"):
            st.session_state.current_page = 'progress'
            st.rerun()

    # Quick Actions
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("🔀 Random Card", use_container_width=True):
            st.session_state.current_page = 'flashcards'
            st.session_state.current_card_index = random.randint(0, len(data.get('flashcards', [])) - 1)
            st.rerun()

    with col_b:
        if st.button("📝 Review Weak Cards", use_container_width=True):
            st.session_state.current_page = 'flashcards'
            st.session_state.selected_category = 'all'
            st.rerun()

    with col_c:
        dark_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
        if st.button(dark_label, use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    # Footer
    st.markdown("---")
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
        <div style="text-align: center; opacity: 0.6; padding: 1rem;">
            <p>💜 You've got this, Arsh! One step at a time. 💜</p>
        </div>
        """, unsafe_allow_html=True)

    # Logout in sidebar
    with st.sidebar:
        st.markdown("### 🏠 Navigation")
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            # Save current session before logout
            save_session_progress()
            st.session_state.authenticated = False
            st.session_state.current_page = 'home'
            st.session_state.score = {'correct': 0, 'incorrect': 0}
            st.rerun()


# ============================================
# FLASHCARD STUDY PAGE
# ============================================
def flashcard_page():
    """Interactive flashcard study page"""
    data = load_flashcards()

    # Back button
    if st.button("← Back to Home"):
        st.session_state.current_page = 'home'
        st.rerun()

    st.markdown("""
    <div class="main-header" style="padding: 1.5rem 2rem;">
        <div class="header-content">
            <div class="header-title" style="font-size: 2rem;">🎴 Flashcard Study</div>
            <div class="header-subtitle">Master MCAT concepts one card at a time</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Category filter
    categories = data.get('categories', [])
    flashcards = data.get('flashcards', [])

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        category_options = ['all'] + [cat['id'] for cat in categories]
        category_names = ['📚 All Categories'] + [f"{cat['icon']} {cat['name']}" for cat in categories]

        selected_idx = st.selectbox(
            "Select Category",
            range(len(category_options)),
            format_func=lambda x: category_names[x],
            key="cat_select"
        )
        st.session_state.selected_category = category_options[selected_idx]

    # Filter cards
    if st.session_state.selected_category == 'all':
        filtered_cards = flashcards
    else:
        filtered_cards = [c for c in flashcards if c['category'] == st.session_state.selected_category]

    if not filtered_cards:
        st.warning("No cards found in this category.")
        return

    st.session_state.filtered_cards = filtered_cards

    # Ensure valid index
    if st.session_state.current_card_index >= len(filtered_cards):
        st.session_state.current_card_index = 0

    current_card = filtered_cards[st.session_state.current_card_index]
    cat_info = next((c for c in categories if c['id'] == current_card['category']), None)

    # Progress
    progress_pct = (st.session_state.current_card_index + 1) / len(filtered_cards)
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>Card {st.session_state.current_card_index + 1} of {len(filtered_cards)}</span>
            <span>{progress_pct*100:.0f}%</span>
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress_pct*100}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Flashcard
    badge_class = {
        'bio_biochem': 'badge-bio',
        'chem': 'badge-chem',
        'physics': 'badge-physics',
        'psych_soc': 'badge-psych'
    }.get(current_card['category'], 'badge-bio')

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown(f"""
        <div class="flashcard">
            <div class="flashcard-category">
                <span class="category-badge {badge_class}">
                    {cat_info['icon'] if cat_info else '📚'} {cat_info['name'] if cat_info else current_card['category']}
                </span>
                {'<span class="high-yield-badge">⭐ HIGH YIELD</span>' if current_card.get('high_yield') else ''}
            </div>
            <div class="flashcard-question">
                {current_card['question']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Show/Hide Answer
        if st.button("🔍 Show Answer" if not st.session_state.show_answer else "🙈 Hide Answer",
                    use_container_width=True, type="primary"):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()

        if st.session_state.show_answer:
            st.markdown(f"""
            <div class="flashcard-answer">
                <div class="flashcard-answer-text">
                    <strong>✅ Answer:</strong><br><br>
                    {current_card['answer']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Feedback buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ I knew it!", use_container_width=True, type="primary"):
                    st.session_state.score['correct'] += 1
                    record_card_review(current_card['id'], True)
                    next_card(filtered_cards)
            with col_b:
                if st.button("❌ Need review", use_container_width=True):
                    st.session_state.score['incorrect'] += 1
                    record_card_review(current_card['id'], False)
                    next_card(filtered_cards)

    # Navigation
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("⬅️ Previous", use_container_width=True,
                    disabled=st.session_state.current_card_index == 0):
            st.session_state.current_card_index -= 1
            st.session_state.show_answer = False
            st.rerun()

    with col2:
        if st.button("🔀 Random", use_container_width=True):
            st.session_state.current_card_index = random.randint(0, len(filtered_cards) - 1)
            st.session_state.show_answer = False
            st.rerun()

    with col3:
        bookmark_label = "🔖 Bookmarked" if current_card['id'] in st.session_state.bookmarked_cards else "📌 Bookmark"
        if st.button(bookmark_label, use_container_width=True):
            if current_card['id'] in st.session_state.bookmarked_cards:
                st.session_state.bookmarked_cards.remove(current_card['id'])
            else:
                st.session_state.bookmarked_cards.add(current_card['id'])
            st.rerun()

    with col4:
        if st.button("Next ➡️", use_container_width=True,
                    disabled=st.session_state.current_card_index >= len(filtered_cards) - 1):
            st.session_state.current_card_index += 1
            st.session_state.show_answer = False
            st.rerun()

    # Session stats
    st.markdown("---")
    st.markdown("### 📊 Session Stats")

    col1, col2, col3, col4 = st.columns(4)
    total = st.session_state.score['correct'] + st.session_state.score['incorrect']
    accuracy = (st.session_state.score['correct'] / total * 100) if total > 0 else 0

    with col1:
        st.metric("✅ Correct", st.session_state.score['correct'])
    with col2:
        st.metric("❌ To Review", st.session_state.score['incorrect'])
    with col3:
        st.metric("📚 Total", total)
    with col4:
        st.metric("🎯 Accuracy", f"{accuracy:.0f}%")


def next_card(filtered_cards):
    """Move to next card"""
    if st.session_state.current_card_index < len(filtered_cards) - 1:
        st.session_state.current_card_index += 1
    else:
        st.session_state.current_card_index = 0
    st.session_state.show_answer = False
    st.rerun()


def record_card_review(card_id: int, correct: bool):
    """Record card review for SRS"""
    srs_data = load_srs_data()
    card_key = str(card_id)

    if card_key not in srs_data['cards']:
        srs_data['cards'][card_key] = {
            'reviews': 0,
            'correct': 0,
            'ease_factor': 2.5,
            'interval': 1,
            'last_review': None
        }

    srs_data['cards'][card_key]['reviews'] += 1
    if correct:
        srs_data['cards'][card_key]['correct'] += 1
        srs_data['cards'][card_key]['interval'] = min(
            srs_data['cards'][card_key]['interval'] * srs_data['cards'][card_key]['ease_factor'],
            365
        )
    else:
        srs_data['cards'][card_key]['interval'] = 1

    srs_data['cards'][card_key]['last_review'] = datetime.now().isoformat()
    save_srs_data(srs_data)


# ============================================
# QUIZ MODE PAGE
# ============================================
def quiz_page():
    """Quiz mode with trivia API questions"""

    if st.button("← Back to Home"):
        st.session_state.current_page = 'home'
        st.session_state.quiz_active = False
        st.rerun()

    st.markdown("""
    <div class="main-header" style="padding: 1.5rem 2rem;">
        <div class="header-content">
            <div class="header-title" style="font-size: 2rem;">🧪 Quiz Mode</div>
            <div class="header-subtitle">Test your knowledge with science questions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.quiz_active:
        # Quiz setup
        st.markdown("### ⚙️ Quiz Settings")

        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.slider("Number of Questions", 5, 20, 10)
        with col2:
            difficulty = st.selectbox("Difficulty", ["Any", "Easy", "Medium", "Hard"])

        st.markdown("---")

        if st.button("🚀 Start Quiz", use_container_width=True, type="primary"):
            with st.spinner("Loading questions..."):
                questions = fetch_trivia_questions(num_questions)
                if questions:
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_active = True
                    st.session_state.quiz_current = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_answers = []
                    st.rerun()
                else:
                    st.error("Could not load questions. Please try again.")
    else:
        # Active quiz
        questions = st.session_state.quiz_questions
        current_idx = st.session_state.quiz_current

        if current_idx < len(questions):
            q = questions[current_idx]

            # Progress
            progress = (current_idx + 1) / len(questions)
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between;">
                    <span>Question {current_idx + 1} of {len(questions)}</span>
                    <span>Score: {st.session_state.quiz_score}/{current_idx}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {progress*100}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Question
            st.markdown(f"""
            <div class="flashcard" style="min-height: 200px;">
                <div style="position: absolute; top: 1rem; right: 1rem;">
                    <span class="category-badge badge-chem">{q['difficulty'].title()}</span>
                </div>
                <div class="flashcard-question" style="font-size: 1.3rem;">
                    {q['question']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Answer options
            for i, option in enumerate(q['options']):
                if st.button(f"{chr(65+i)}. {option}", use_container_width=True, key=f"opt_{i}"):
                    correct = option == q['correct_answer']
                    st.session_state.quiz_answers.append({
                        'question': q['question'],
                        'selected': option,
                        'correct': q['correct_answer'],
                        'is_correct': correct
                    })
                    if correct:
                        st.session_state.quiz_score += 1
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Wrong! The answer was: {q['correct_answer']}")

                    st.session_state.quiz_current += 1
                    import time
                    time.sleep(1)
                    st.rerun()
        else:
            # Quiz complete
            score = st.session_state.quiz_score
            total = len(questions)
            pct = (score / total) * 100

            st.markdown(f"""
            <div style="text-align: center; padding: 3rem;">
                <div style="font-size: 5rem;">{'🎉' if pct >= 70 else '📚' if pct >= 50 else '💪'}</div>
                <h1 style="margin: 1rem 0;">Quiz Complete!</h1>
                <div class="stat-value" style="font-size: 4rem;">{score}/{total}</div>
                <p style="font-size: 1.5rem; opacity: 0.8;">{pct:.0f}% Accuracy</p>
            </div>
            """, unsafe_allow_html=True)

            # Review answers
            with st.expander("📝 Review Answers"):
                for i, ans in enumerate(st.session_state.quiz_answers):
                    icon = "✅" if ans['is_correct'] else "❌"
                    st.markdown(f"**Q{i+1}: {ans['question']}**")
                    st.markdown(f"Your answer: {ans['selected']} {icon}")
                    if not ans['is_correct']:
                        st.markdown(f"Correct answer: {ans['correct']}")
                    st.markdown("---")

            if st.button("🔄 Take Another Quiz", use_container_width=True, type="primary"):
                st.session_state.quiz_active = False
                st.rerun()


# ============================================
# TIMED PRACTICE PAGE
# ============================================
def timed_page():
    """Timed practice mode"""
    data = load_flashcards()

    if st.button("← Back to Home"):
        st.session_state.current_page = 'home'
        st.session_state.timer_active = False
        st.rerun()

    st.markdown("""
    <div class="main-header" style="padding: 1.5rem 2rem;">
        <div class="header-content">
            <div class="header-title" style="font-size: 2rem;">⏱️ Timed Practice</div>
            <div class="header-subtitle">Practice under MCAT-style time pressure</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.timer_active:
        st.markdown("### ⚙️ Timer Settings")

        col1, col2 = st.columns(2)
        with col1:
            duration = st.selectbox("Time per card", [30, 45, 60, 90, 120], index=2)
            st.session_state.timer_duration = duration
        with col2:
            num_cards = st.slider("Number of cards", 5, 30, 10)

        st.info(f"📝 You'll have {duration} seconds to review each of {num_cards} cards.")

        if st.button("🚀 Start Timed Session", use_container_width=True, type="primary"):
            flashcards = data.get('flashcards', [])
            st.session_state.filtered_cards = random.sample(flashcards, min(num_cards, len(flashcards)))
            st.session_state.current_card_index = 0
            st.session_state.timer_active = True
            st.session_state.timer_start = datetime.now()
            st.session_state.score = {'correct': 0, 'incorrect': 0}
            st.rerun()
    else:
        # Active timed session
        filtered_cards = st.session_state.filtered_cards

        if st.session_state.current_card_index < len(filtered_cards):
            current_card = filtered_cards[st.session_state.current_card_index]

            # Timer calculation
            elapsed = (datetime.now() - st.session_state.timer_start).total_seconds()
            remaining = max(0, st.session_state.timer_duration - elapsed)

            # Auto-advance if time's up
            if remaining <= 0:
                st.session_state.score['incorrect'] += 1
                st.session_state.current_card_index += 1
                st.session_state.timer_start = datetime.now()
                st.session_state.show_answer = False
                st.rerun()

            # Timer display
            timer_class = ""
            if remaining < 10:
                timer_class = "timer-danger"
            elif remaining < 20:
                timer_class = "timer-warning"

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div class="timer-display {timer_class}">
                    {int(remaining)}s
                </div>
                """, unsafe_allow_html=True)

            # Progress
            st.markdown(f"**Card {st.session_state.current_card_index + 1} of {len(filtered_cards)}**")
            st.progress((st.session_state.current_card_index + 1) / len(filtered_cards))

            # Card display
            st.markdown(f"""
            <div class="flashcard" style="min-height: 250px;">
                <div class="flashcard-question">
                    {current_card['question']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ I know this!", use_container_width=True, type="primary"):
                    st.session_state.score['correct'] += 1
                    st.session_state.current_card_index += 1
                    st.session_state.timer_start = datetime.now()
                    st.session_state.show_answer = False
                    st.rerun()
            with col_b:
                if st.button("❌ Skip / Don't know", use_container_width=True):
                    st.session_state.score['incorrect'] += 1
                    st.session_state.current_card_index += 1
                    st.session_state.timer_start = datetime.now()
                    st.session_state.show_answer = False
                    st.rerun()

            # Reveal answer option
            if st.button("👁️ Peek at Answer", use_container_width=True):
                st.info(f"**Answer:** {current_card['answer']}")

            # Auto-refresh for timer
            import time
            time.sleep(1)
            st.rerun()
        else:
            # Session complete
            st.session_state.timer_active = False
            total = st.session_state.score['correct'] + st.session_state.score['incorrect']
            accuracy = (st.session_state.score['correct'] / total * 100) if total > 0 else 0

            st.markdown(f"""
            <div style="text-align: center; padding: 3rem;">
                <div style="font-size: 5rem;">⏱️</div>
                <h1>Timed Session Complete!</h1>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">✅</div>
                        <div class="stat-value">{st.session_state.score['correct']}</div>
                        <div class="stat-label">Correct</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">❌</div>
                        <div class="stat-value">{st.session_state.score['incorrect']}</div>
                        <div class="stat-label">To Review</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-value">{accuracy:.0f}%</div>
                        <div class="stat-label">Accuracy</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Try Again", use_container_width=True, type="primary"):
                st.session_state.timer_active = False
                st.rerun()


# ============================================
# PROGRESS PAGE
# ============================================
def progress_page():
    """Progress and statistics page"""
    data = load_flashcards()
    progress = load_progress()

    if st.button("← Back to Home"):
        st.session_state.current_page = 'home'
        st.rerun()

    st.markdown("""
    <div class="main-header" style="padding: 1.5rem 2rem;">
        <div class="header-content">
            <div class="header-title" style="font-size: 2rem;">📊 Your Progress</div>
            <div class="header-subtitle">Track your MCAT preparation journey</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Current session stats
    st.markdown("### 📅 Current Session")

    total_today = st.session_state.score['correct'] + st.session_state.score['incorrect']
    accuracy_today = (st.session_state.score['correct'] / total_today * 100) if total_today > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Correct", st.session_state.score['correct'])
    with col2:
        st.metric("❌ To Review", st.session_state.score['incorrect'])
    with col3:
        st.metric("📚 Total", total_today)
    with col4:
        st.metric("🎯 Accuracy", f"{accuracy_today:.0f}%")

    st.markdown("---")

    # Historical data
    st.markdown("### 📈 Study History")

    if progress.get('daily_scores'):
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go

        df = pd.DataFrame(progress['daily_scores'])
        df['date'] = pd.to_datetime(df['date'])
        df['accuracy'] = df['correct'] / df['total'] * 100

        # Cards over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['total'],
            mode='lines+markers', name='Total Cards',
            line=dict(color='#8b5cf6', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['correct'],
            mode='lines+markers', name='Correct',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title='Daily Study Progress',
            xaxis_title='Date',
            yaxis_title='Cards',
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Accuracy over time
        fig2 = px.bar(df, x='date', y='accuracy',
                     title='Daily Accuracy',
                     color='accuracy',
                     color_continuous_scale='RdYlGn')
        fig2.update_layout(template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)

        # Summary stats
        st.markdown("### 📊 Overall Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Cards Studied", int(df['total'].sum()))
        with col2:
            st.metric("Average Accuracy", f"{df['accuracy'].mean():.1f}%")
        with col3:
            st.metric("Study Sessions", len(df))
        with col4:
            st.metric("Current Streak", f"{progress.get('streak', 0)} days 🔥")
    else:
        st.info("📝 No study history yet. Start studying to track your progress!")

    # Category breakdown
    st.markdown("---")
    st.markdown("### 📚 Category Overview")

    categories = data.get('categories', [])
    flashcards = data.get('flashcards', [])

    cols = st.columns(4)
    for i, cat in enumerate(categories):
        cat_cards = len([c for c in flashcards if c['category'] == cat['id']])
        high_yield = len([c for c in flashcards if c['category'] == cat['id'] and c.get('high_yield')])

        with cols[i]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{cat['icon']}</div>
                <div class="stat-value" style="font-size: 1.8rem;">{cat_cards}</div>
                <div class="stat-label">{cat['name']}</div>
                <div style="color: #ef4444; font-size: 0.8rem;">⭐ {high_yield} high yield</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================
# SAVE SESSION PROGRESS
# ============================================
def save_session_progress():
    """Save current session progress"""
    if st.session_state.score['correct'] + st.session_state.score['incorrect'] > 0:
        progress = load_progress()
        today = date.today().isoformat()

        daily_entry = {
            'date': today,
            'correct': st.session_state.score['correct'],
            'incorrect': st.session_state.score['incorrect'],
            'total': st.session_state.score['correct'] + st.session_state.score['incorrect']
        }

        # Check if we already have an entry for today
        existing = next((i for i, s in enumerate(progress['daily_scores']) if s['date'] == today), None)
        if existing is not None:
            progress['daily_scores'][existing]['correct'] += daily_entry['correct']
            progress['daily_scores'][existing]['incorrect'] += daily_entry['incorrect']
            progress['daily_scores'][existing]['total'] += daily_entry['total']
        else:
            progress['daily_scores'].append(daily_entry)

        save_progress(progress)


# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application entry point"""
    load_css()

    # Check authentication first
    if not st.session_state.authenticated:
        login_page()
        return

    # Route to appropriate page
    page = st.session_state.current_page

    if page == 'home':
        home_page()
    elif page == 'flashcards':
        flashcard_page()
    elif page == 'quiz':
        quiz_page()
    elif page == 'timed':
        timed_page()
    elif page == 'progress':
        progress_page()
    else:
        home_page()


if __name__ == "__main__":
    main()
