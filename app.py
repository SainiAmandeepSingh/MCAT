import streamlit as st
import json
import os
from datetime import datetime, date

# Page configuration
st.set_page_config(
    page_title="MCAT Flashcard Study App - For Arsh 💜",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_card_index' not in st.session_state:
    st.session_state.current_card_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'score' not in st.session_state:
    st.session_state.score = {'correct': 0, 'incorrect': 0}
if 'studied_cards' not in st.session_state:
    st.session_state.studied_cards = []
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = 'all'
if 'filtered_cards' not in st.session_state:
    st.session_state.filtered_cards = []

# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FLASHCARDS_FILE = os.path.join(DATA_DIR, 'flashcards.json')
PROGRESS_FILE = os.path.join(DATA_DIR, 'progress.json')

# Load flashcards
@st.cache_data
def load_flashcards():
    with open(FLASHCARDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load/Save progress
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'daily_scores': [], 'total_studied': 0, 'streak': 0, 'last_study_date': None}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2)

# Custom CSS
def load_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #6C63FF;
        --secondary-color: #FF6B6B;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
    }

    /* Login page styling */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }

    .login-title {
        text-align: center;
        color: white;
        font-size: 2rem;
        margin-bottom: 1rem;
    }

    /* Flashcard styling */
    .flashcard {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        padding: 2rem;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }

    .flashcard:hover {
        transform: translateY(-5px);
    }

    .flashcard-question {
        font-size: 1.4rem;
        color: #333;
        text-align: center;
        font-weight: 600;
    }

    .flashcard-answer {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        margin-top: 1rem;
    }

    /* Category badges */
    .category-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .bio-badge { background-color: #4CAF50; color: white; }
    .chem-badge { background-color: #2196F3; color: white; }
    .physics-badge { background-color: #FF9800; color: white; }
    .psych-badge { background-color: #9C27B0; color: white; }

    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6C63FF;
    }

    .stat-label {
        color: #666;
        font-size: 0.9rem;
    }

    /* Progress bar */
    .progress-container {
        background: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    /* High yield badge */
    .high-yield {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 700;
    }

    /* Welcome message */
    .welcome-message {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
    }

    .welcome-name {
        font-size: 2.5rem;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# Login page
def login_page():
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🩺 MCAT Flashcard Study App</h1>
        <p style="font-size: 1.2rem; color: #666;">Your personal MCAT preparation companion</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🔐 Login to Continue")

        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            code = st.text_input("🔑 Access Code", type="password", placeholder="Enter your access code")

            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                # Credentials for Arsh
                if email == "ahkaur77@gmail.com" and code == "IloveyouArsh":
                    st.session_state.authenticated = True
                    st.success("Welcome back, Arsh! 💜")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.9rem;">
            Made with 💜 for Arsh's MCAT Journey
        </div>
        """, unsafe_allow_html=True)

# Main app
def main_app():
    data = load_flashcards()
    progress = load_progress()

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>🩺 MCAT Study</h2>
            <p>Hi Arsh! 💜</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        page = st.radio(
            "📚 Navigation",
            ["🎴 Study Flashcards", "📊 Daily Progress"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Quick stats
        st.markdown("### 📈 Quick Stats")
        st.metric("Cards Studied Today", st.session_state.score['correct'] + st.session_state.score['incorrect'])
        st.metric("Correct Answers", st.session_state.score['correct'])

        if st.session_state.score['correct'] + st.session_state.score['incorrect'] > 0:
            accuracy = (st.session_state.score['correct'] /
                       (st.session_state.score['correct'] + st.session_state.score['incorrect'])) * 100
            st.metric("Accuracy", f"{accuracy:.1f}%")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            # Save progress before logout
            today = date.today().isoformat()
            if st.session_state.score['correct'] + st.session_state.score['incorrect'] > 0:
                daily_entry = {
                    'date': today,
                    'correct': st.session_state.score['correct'],
                    'incorrect': st.session_state.score['incorrect'],
                    'total': st.session_state.score['correct'] + st.session_state.score['incorrect']
                }
                progress['daily_scores'].append(daily_entry)
                save_progress(progress)

            st.session_state.authenticated = False
            st.session_state.score = {'correct': 0, 'incorrect': 0}
            st.rerun()

    # Main content
    if page == "🎴 Study Flashcards":
        study_flashcards_page(data)
    else:
        daily_progress_page(data, progress)

# Study flashcards page
def study_flashcards_page(data):
    st.markdown("""
    <div class="welcome-message">
        <div class="welcome-name">Ready to Study, Arsh? 📚</div>
        <p>You've got this! One card at a time. 💪</p>
    </div>
    """, unsafe_allow_html=True)

    # Category filter
    categories = data['categories']
    category_options = ['all'] + [cat['id'] for cat in categories]
    category_names = ['📚 All Categories'] + [f"{cat['icon']} {cat['name']}" for cat in categories]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_idx = st.selectbox(
            "Select Category",
            range(len(category_options)),
            format_func=lambda x: category_names[x],
            key="category_selector"
        )
        st.session_state.selected_category = category_options[selected_idx]

    # Filter cards
    all_cards = data['flashcards']
    if st.session_state.selected_category == 'all':
        filtered_cards = all_cards
    else:
        filtered_cards = [c for c in all_cards if c['category'] == st.session_state.selected_category]

    if not filtered_cards:
        st.warning("No cards found in this category.")
        return

    st.session_state.filtered_cards = filtered_cards

    # Ensure index is valid
    if st.session_state.current_card_index >= len(filtered_cards):
        st.session_state.current_card_index = 0

    current_card = filtered_cards[st.session_state.current_card_index]

    # Progress indicator
    st.markdown(f"**Card {st.session_state.current_card_index + 1} of {len(filtered_cards)}**")
    st.progress((st.session_state.current_card_index + 1) / len(filtered_cards))

    # Get category info
    cat_info = next((c for c in categories if c['id'] == current_card['category']), None)

    # Display flashcard
    st.markdown("---")

    # Category and difficulty badges
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        badge_class = {
            'bio_biochem': 'bio-badge',
            'chem': 'chem-badge',
            'physics': 'physics-badge',
            'psych_soc': 'psych-badge'
        }.get(current_card['category'], 'bio-badge')

        badge_html = f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <span class="category-badge {badge_class}">{cat_info['icon'] if cat_info else '📚'} {cat_info['name'] if cat_info else current_card['category']}</span>
            <span style="margin-left: 0.5rem; color: #666;">| {current_card['subcategory']}</span>
            {'<span class="high-yield" style="margin-left: 0.5rem;">⭐ HIGH YIELD</span>' if current_card.get('high_yield') else ''}
        </div>
        """
        st.markdown(badge_html, unsafe_allow_html=True)

        # Question card
        st.markdown(f"""
        <div class="flashcard">
            <div class="flashcard-question">
                ❓ {current_card['question']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Show/Hide answer button
        if st.button("🔍 Show Answer" if not st.session_state.show_answer else "🙈 Hide Answer",
                    use_container_width=True, type="primary"):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()

        # Answer section
        if st.session_state.show_answer:
            st.markdown(f"""
            <div class="flashcard-answer" style="margin-top: 1rem; padding: 1.5rem; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 15px;">
                <strong>✅ Answer:</strong><br><br>
                {current_card['answer']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Feedback buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ I knew it!", use_container_width=True, type="primary"):
                    st.session_state.score['correct'] += 1
                    st.session_state.studied_cards.append({
                        'card_id': current_card['id'],
                        'correct': True,
                        'timestamp': datetime.now().isoformat()
                    })
                    next_card()
            with col_b:
                if st.button("❌ Need to review", use_container_width=True):
                    st.session_state.score['incorrect'] += 1
                    st.session_state.studied_cards.append({
                        'card_id': current_card['id'],
                        'correct': False,
                        'timestamp': datetime.now().isoformat()
                    })
                    next_card()

    st.markdown("---")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=st.session_state.current_card_index == 0):
            st.session_state.current_card_index -= 1
            st.session_state.show_answer = False
            st.rerun()
    with col2:
        if st.button("🔀 Random Card", use_container_width=True):
            import random
            st.session_state.current_card_index = random.randint(0, len(filtered_cards) - 1)
            st.session_state.show_answer = False
            st.rerun()
    with col3:
        if st.button("➡️ Next", use_container_width=True, disabled=st.session_state.current_card_index >= len(filtered_cards) - 1):
            st.session_state.current_card_index += 1
            st.session_state.show_answer = False
            st.rerun()

    # Session summary
    st.markdown("---")
    st.markdown("### 📊 Current Session")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Correct", st.session_state.score['correct'])
    with col2:
        st.metric("❌ To Review", st.session_state.score['incorrect'])
    with col3:
        total = st.session_state.score['correct'] + st.session_state.score['incorrect']
        st.metric("📚 Total Studied", total)
    with col4:
        if total > 0:
            acc = (st.session_state.score['correct'] / total) * 100
            st.metric("🎯 Accuracy", f"{acc:.1f}%")
        else:
            st.metric("🎯 Accuracy", "N/A")

def next_card():
    """Move to the next card"""
    if st.session_state.current_card_index < len(st.session_state.filtered_cards) - 1:
        st.session_state.current_card_index += 1
    else:
        st.session_state.current_card_index = 0  # Loop back to start
    st.session_state.show_answer = False
    st.rerun()

# Daily progress page
def daily_progress_page(data, progress):
    st.markdown("""
    <div class="welcome-message">
        <div class="welcome-name">Your Progress 📈</div>
        <p>Keep up the great work, Arsh! You're doing amazing! 🌟</p>
    </div>
    """, unsafe_allow_html=True)

    # Today's summary
    st.markdown("### 📅 Today's Session")

    col1, col2, col3, col4 = st.columns(4)

    total_today = st.session_state.score['correct'] + st.session_state.score['incorrect']
    accuracy_today = (st.session_state.score['correct'] / total_today * 100) if total_today > 0 else 0

    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number" style="color: #4CAF50;">""" + str(st.session_state.score['correct']) + """</div>
            <div class="stat-label">Correct</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number" style="color: #FF6B6B;">""" + str(st.session_state.score['incorrect']) + """</div>
            <div class="stat-label">To Review</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number" style="color: #2196F3;">""" + str(total_today) + """</div>
            <div class="stat-label">Total Cards</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number" style="color: #9C27B0;">""" + f"{accuracy_today:.1f}%" + """</div>
            <div class="stat-label">Accuracy</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Historical data
    st.markdown("### 📊 Study History")

    if progress['daily_scores']:
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go

        df = pd.DataFrame(progress['daily_scores'])
        df['date'] = pd.to_datetime(df['date'])
        df['accuracy'] = df['correct'] / df['total'] * 100

        # Line chart for progress
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['total'],
            mode='lines+markers',
            name='Cards Studied',
            line=dict(color='#6C63FF', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['correct'],
            mode='lines+markers',
            name='Correct',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title='Daily Study Progress',
            xaxis_title='Date',
            yaxis_title='Number of Cards',
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Accuracy chart
        fig2 = px.bar(
            df,
            x='date',
            y='accuracy',
            title='Daily Accuracy (%)',
            color='accuracy',
            color_continuous_scale='RdYlGn'
        )
        fig2.update_layout(template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)

        # Summary statistics
        st.markdown("### 📈 Overall Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            total_cards = df['total'].sum()
            st.metric("Total Cards Studied", total_cards)

        with col2:
            avg_accuracy = df['accuracy'].mean()
            st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")

        with col3:
            study_days = len(df)
            st.metric("Days Studied", study_days)

        # Recent sessions table
        st.markdown("### 📋 Recent Sessions")
        recent_df = df.tail(10).copy()
        recent_df['date'] = recent_df['date'].dt.strftime('%Y-%m-%d')
        recent_df['accuracy'] = recent_df['accuracy'].round(1).astype(str) + '%'
        recent_df = recent_df.rename(columns={
            'date': 'Date',
            'correct': 'Correct',
            'incorrect': 'Incorrect',
            'total': 'Total',
            'accuracy': 'Accuracy'
        })
        st.dataframe(recent_df[['Date', 'Correct', 'Incorrect', 'Total', 'Accuracy']],
                    use_container_width=True, hide_index=True)
    else:
        st.info("📝 No historical data yet. Start studying to track your progress!")

        # Motivational message
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 20px; margin-top: 2rem;">
            <h3>🌟 Tips for MCAT Success</h3>
            <ul style="text-align: left; max-width: 500px; margin: 0 auto;">
                <li>Study a little bit every day - consistency is key!</li>
                <li>Focus on understanding concepts, not just memorizing</li>
                <li>Take breaks - your brain needs time to consolidate</li>
                <li>Review cards you got wrong more frequently</li>
                <li>You've got this, Arsh! 💪</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Category breakdown
    st.markdown("---")
    st.markdown("### 📚 Category Overview")

    categories = data['categories']
    flashcards = data['flashcards']

    cols = st.columns(4)
    for i, cat in enumerate(categories):
        cat_cards = len([c for c in flashcards if c['category'] == cat['id']])
        high_yield = len([c for c in flashcards if c['category'] == cat['id'] and c.get('high_yield')])

        with cols[i]:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.08);">
                <div style="font-size: 2rem;">{cat['icon']}</div>
                <div style="font-weight: 600; color: {cat['color']};">{cat['name']}</div>
                <div style="color: #666; font-size: 0.9rem;">{cat_cards} cards</div>
                <div style="color: #FF6B6B; font-size: 0.8rem;">⭐ {high_yield} high yield</div>
            </div>
            """, unsafe_allow_html=True)

# Main execution
def main():
    load_custom_css()

    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
