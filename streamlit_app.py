"""
Streamlit Web Demo for Interactive English Learning Quiz
A simplified web version that users can run directly on Streamlit Cloud
"""
import streamlit as st
import random
import time

# Page configuration
st.set_page_config(
    page_title="Interactive English Learning Quiz",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3em;
        color: #667eea;
        text-align: center;
        margin-bottom: 20px;
    }
    .question-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin: 20px 0;
        text-align: center;
    }
    .option-button {
        padding: 20px;
        margin: 10px;
        border-radius: 10px;
        font-size: 1.2em;
        cursor: pointer;
    }
    .stButton>button {
        width: 100%;
        padding: 20px;
        font-size: 1.2em;
        border-radius: 10px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# Questions bank
QUESTIONS = [
    {
        "id": 1,
        "question": "Which one is a fruit?",
        "options": ["Apple", "Cat"],
        "correct": 0,
        "emoji": ["🍎", "🐱"]
    },
    {
        "id": 2,
        "question": "Which animal is bigger?",
        "options": ["Dog", "Elephant"],
        "correct": 1,
        "emoji": ["🐶", "🐘"]
    },
    {
        "id": 3,
        "question": "Which shape has three sides?",
        "options": ["Triangle", "Circle"],
        "correct": 0,
        "emoji": ["🔺", "⭕"]
    },
    {
        "id": 4,
        "question": "Which one is yellow?",
        "options": ["Banana", "Rectangle"],
        "correct": 0,
        "emoji": ["🍌", "▭"]
    },
    {
        "id": 5,
        "question": "Which one can bark?",
        "options": ["Dog", "Apple"],
        "correct": 0,
        "emoji": ["🐶", "🍎"]
    },
    {
        "id": 6,
        "question": "Which is the round shape?",
        "options": ["Circle", "Rectangle"],
        "correct": 0,
        "emoji": ["⭕", "▭"]
    },
    {
        "id": 7,
        "question": "Which one is an animal?",
        "options": ["Cat", "Orange"],
        "correct": 0,
        "emoji": ["🐱", "🍊"]
    },
    {
        "id": 8,
        "question": "Which fruit is orange in color?",
        "options": ["Orange", "Banana"],
        "correct": 0,
        "emoji": ["🍊", "🍌"]
    },
    {
        "id": 9,
        "question": "Which one has four sides?",
        "options": ["Rectangle", "Triangle"],
        "correct": 0,
        "emoji": ["▭", "🔺"]
    },
    {
        "id": 10,
        "question": "Which one is the heavier animal?",
        "options": ["Elephant", "Dog"],
        "correct": 0,
        "emoji": ["🐘", "🐶"]
    }
]

# Initialize session state
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'selected_questions' not in st.session_state:
    st.session_state.selected_questions = random.sample(QUESTIONS, min(5, len(QUESTIONS)))

def reset_quiz():
    st.session_state.score = 0
    st.session_state.current_question = 0
    st.session_state.answered = False
    st.session_state.selected_questions = random.sample(QUESTIONS, min(5, len(QUESTIONS)))

def next_question():
    if st.session_state.current_question < len(st.session_state.selected_questions) - 1:
        st.session_state.current_question += 1
        st.session_state.answered = False
    else:
        st.session_state.quiz_complete = True

# Header
st.markdown('<h1 class="main-header">🎓 Interactive English Learning Quiz</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Quiz Info")
    st.metric("Score", f"{st.session_state.score}/{len(st.session_state.selected_questions)}")
    st.metric("Question", f"{st.session_state.current_question + 1}/{len(st.session_state.selected_questions)}")
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.info("""
    This is a web demo of the Interactive English Learning Quiz.
    
    **Features:**
    - Interactive quiz questions
    - Real-time scoring
    - Fun learning experience
    
    For the full desktop application with face recognition and gesture control, visit the GitHub repository.
    """)
    
    if st.button("🔄 Restart Quiz"):
        reset_quiz()
        st.rerun()

# Main content
if st.session_state.current_question < len(st.session_state.selected_questions):
    q = st.session_state.selected_questions[st.session_state.current_question]
    
    # Question display
    st.markdown(f"""
    <div class="question-box">
        <h2>{q['question']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"{q['emoji'][0]} {q['options'][0]}", key="option1", disabled=st.session_state.answered):
            if q['correct'] == 0:
                st.session_state.score += 1
                st.success(f"✅ Correct! {q['emoji'][0]} {q['options'][0]} is the right answer!")
            else:
                st.error(f"❌ Not quite. The correct answer is {q['emoji'][q['correct']]} {q['options'][q['correct']]}")
            st.session_state.answered = True
            time.sleep(1.5)
            next_question()
            st.rerun()
    
    with col2:
        if st.button(f"{q['emoji'][1]} {q['options'][1]}", key="option2", disabled=st.session_state.answered):
            if q['correct'] == 1:
                st.session_state.score += 1
                st.success(f"✅ Correct! {q['emoji'][1]} {q['options'][1]} is the right answer!")
            else:
                st.error(f"❌ Not quite. The correct answer is {q['emoji'][q['correct']]} {q['options'][q['correct']]}")
            st.session_state.answered = True
            time.sleep(1.5)
            next_question()
            st.rerun()
    
    if st.session_state.answered:
        if st.button("➡️ Next Question", key="next"):
            next_question()
            st.rerun()
else:
    # Quiz complete
    percentage = (st.session_state.score / len(st.session_state.selected_questions)) * 100
    
    st.markdown(f"""
    <div class="question-box">
        <h2>🎉 Quiz Complete! 🎉</h2>
        <h3>Your Score: {st.session_state.score}/{len(st.session_state.selected_questions)}</h3>
        <h3>Percentage: {percentage:.0f}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if percentage == 100:
        st.balloons()
        st.success("🌟 Perfect Score! You're amazing! 🌟")
    elif percentage >= 80:
        st.success("🎊 Great job! You did very well! 🎊")
    elif percentage >= 60:
        st.info("👍 Good effort! Keep practicing! 👍")
    else:
        st.warning("💪 Keep learning! You'll get better! 💪")
    
    if st.button("🔄 Play Again"):
        reset_quiz()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Made with ❤️ by <a href="https://github.com/29SalahMo" target="_blank">Salah El Dein</a></p>
    <p>Full Desktop App: <a href="https://github.com/29SalahMo/Interactive-learnig" target="_blank">GitHub Repository</a></p>
    <p>This is a simplified web demo. For full features (face recognition, gesture control), download the desktop application.</p>
</div>
""", unsafe_allow_html=True)
