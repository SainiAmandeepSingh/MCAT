# 🩺 MCAT Flashcard Study App

A personalized MCAT preparation flashcard application built with Streamlit, designed to help with Medical College Admission Test preparation.

## Features

### 🎴 Flashcard Study
- **100+ MCAT flashcards** covering all four test sections:
  - 🧬 Biology/Biochemistry
  - ⚗️ Chemistry (General & Organic)
  - ⚡ Physics
  - 🧠 Psychology/Sociology
- **High-yield indicators** for important concepts
- **Category filtering** to focus on specific subjects
- **Random card** feature for varied practice
- **Self-assessment** tracking (correct/incorrect)

### 📊 Progress Tracking
- **Daily score tracking** with visual charts
- **Accuracy statistics** over time
- **Study history** with detailed session data
- **Category breakdowns** showing coverage

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone this repository or download the files

2. Navigate to the project directory:
   ```bash
   cd MCAT
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

5. Open your browser and go to `http://localhost:8501`

### Login Credentials
- **Email:** ahkaur77@gmail.com
- **Access Code:** IloveyouArsh

## Project Structure

```
MCAT/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── data/
    ├── flashcards.json   # Flashcard database (100+ cards)
    └── progress.json     # User progress data
```

## Adding More Flashcards

To add more flashcards, edit the `data/flashcards.json` file. Each flashcard follows this format:

```json
{
  "id": 101,
  "category": "bio_biochem",
  "subcategory": "Topic Name",
  "question": "Your question here?",
  "answer": "Your answer here.",
  "difficulty": "easy|medium|hard",
  "high_yield": true|false
}
```

### Available Categories:
- `bio_biochem` - Biology/Biochemistry
- `chem` - Chemistry
- `physics` - Physics
- `psych_soc` - Psychology/Sociology

## Technologies Used

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive charts
- **JSON** - Data storage

## Deployment

You can deploy this app to:
- **Streamlit Cloud** (free) - https://streamlit.io/cloud
- **Heroku**
- **AWS/GCP/Azure**

---

Made with 💜 for MCAT preparation

Good luck with your MCAT journey! You've got this! 🌟
