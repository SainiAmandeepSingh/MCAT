"""
Trivia API Integration Module
Fetches science, biology, medicine, and chemistry questions from The Trivia API
"""

import requests
import html
import random
from typing import List, Dict, Optional

# API Endpoints
TRIVIA_API_BASE = "https://the-trivia-api.com/v2/questions"
OPENTDB_API_BASE = "https://opentdb.com/api.php"

# Category mappings for The Trivia API
TRIVIA_API_CATEGORIES = {
    "science": "science",
    "biology": "science",  # Use science category with biology tag
    "chemistry": "science",
    "medicine": "science",
}

# Tags for filtering
MCAT_RELEVANT_TAGS = ["biology", "medicine", "anatomy", "chemistry", "science", "physics"]

# OpenTDB category IDs
OPENTDB_CATEGORIES = {
    "science": 17,  # Science & Nature
    "computers": 18,  # Science: Computers
    "mathematics": 19,  # Science: Mathematics
}


def fetch_trivia_api_questions(
    limit: int = 10,
    category: str = "science",
    difficulty: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict]:
    """
    Fetch questions from The Trivia API

    Args:
        limit: Number of questions (max 50)
        category: Category to fetch from
        difficulty: easy, medium, or hard
        tags: List of tags to filter by (biology, medicine, anatomy, etc.)

    Returns:
        List of question dictionaries
    """
    params = {
        "limit": min(limit, 50),
        "categories": category
    }

    if difficulty:
        params["difficulties"] = difficulty

    if tags:
        params["tags"] = ",".join(tags)

    try:
        response = requests.get(TRIVIA_API_BASE, params=params, timeout=10)
        response.raise_for_status()

        questions = response.json()

        # Format questions for our app
        formatted = []
        for q in questions:
            formatted.append({
                "id": q.get("id", ""),
                "question": q.get("question", {}).get("text", ""),
                "correct_answer": q.get("correctAnswer", ""),
                "incorrect_answers": q.get("incorrectAnswers", []),
                "category": q.get("category", "science"),
                "difficulty": q.get("difficulty", "medium"),
                "tags": q.get("tags", []),
                "source": "trivia_api"
            })

        return formatted

    except requests.RequestException as e:
        print(f"Error fetching from Trivia API: {e}")
        return []


def fetch_opentdb_questions(
    amount: int = 10,
    category: int = 17,  # Science & Nature
    difficulty: Optional[str] = None
) -> List[Dict]:
    """
    Fetch questions from Open Trivia Database

    Args:
        amount: Number of questions (max 50)
        category: Category ID (17 = Science & Nature)
        difficulty: easy, medium, or hard

    Returns:
        List of question dictionaries
    """
    params = {
        "amount": min(amount, 50),
        "category": category,
        "type": "multiple"
    }

    if difficulty:
        params["difficulty"] = difficulty

    try:
        response = requests.get(OPENTDB_API_BASE, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("response_code") != 0:
            print(f"OpenTDB error code: {data.get('response_code')}")
            return []

        # Format questions for our app
        formatted = []
        for q in data.get("results", []):
            formatted.append({
                "id": f"opentdb_{hash(q['question'])}",
                "question": html.unescape(q.get("question", "")),
                "correct_answer": html.unescape(q.get("correct_answer", "")),
                "incorrect_answers": [html.unescape(a) for a in q.get("incorrect_answers", [])],
                "category": html.unescape(q.get("category", "Science")),
                "difficulty": q.get("difficulty", "medium"),
                "tags": ["science"],
                "source": "opentdb"
            })

        return formatted

    except requests.RequestException as e:
        print(f"Error fetching from OpenTDB: {e}")
        return []


def fetch_mcat_relevant_questions(
    limit: int = 20,
    difficulty: Optional[str] = None,
    focus_area: Optional[str] = None
) -> List[Dict]:
    """
    Fetch MCAT-relevant questions from multiple sources

    Args:
        limit: Total number of questions desired
        difficulty: easy, medium, or hard
        focus_area: biology, chemistry, physics, or psychology

    Returns:
        Combined list of questions from multiple APIs
    """
    questions = []

    # Map focus areas to tags
    tag_mapping = {
        "biology": ["biology", "anatomy", "medicine"],
        "chemistry": ["chemistry", "science"],
        "physics": ["physics", "science"],
        "psychology": ["science"],  # Limited psychology content in these APIs
    }

    tags = tag_mapping.get(focus_area, MCAT_RELEVANT_TAGS[:3])

    # Fetch from The Trivia API (better for medical/biology)
    trivia_questions = fetch_trivia_api_questions(
        limit=limit // 2 + 5,
        category="science",
        difficulty=difficulty,
        tags=tags if focus_area else None
    )
    questions.extend(trivia_questions)

    # Fetch from OpenTDB (general science)
    opentdb_questions = fetch_opentdb_questions(
        amount=limit // 2 + 5,
        category=17,
        difficulty=difficulty
    )
    questions.extend(opentdb_questions)

    # Shuffle and limit
    random.shuffle(questions)
    return questions[:limit]


def format_question_for_quiz(question: Dict) -> Dict:
    """
    Format a question for the quiz interface with shuffled answers

    Args:
        question: Raw question dictionary

    Returns:
        Formatted question with shuffled options
    """
    # Combine correct and incorrect answers
    all_answers = [question["correct_answer"]] + question["incorrect_answers"]
    random.shuffle(all_answers)

    return {
        "id": question["id"],
        "question": question["question"],
        "options": all_answers,
        "correct_answer": question["correct_answer"],
        "difficulty": question["difficulty"],
        "category": question["category"],
        "tags": question.get("tags", []),
        "source": question.get("source", "unknown")
    }


def get_question_by_tags(tags: List[str], limit: int = 10) -> List[Dict]:
    """
    Get questions filtered by specific tags

    Args:
        tags: List of tags (e.g., ["biology", "anatomy"])
        limit: Number of questions

    Returns:
        List of questions matching the tags
    """
    return fetch_trivia_api_questions(
        limit=limit,
        category="science",
        tags=tags
    )


# Pre-defined question sets for different MCAT sections
def get_biology_questions(limit: int = 10, difficulty: str = None) -> List[Dict]:
    """Get biology-focused questions"""
    return fetch_trivia_api_questions(
        limit=limit,
        tags=["biology", "anatomy"],
        difficulty=difficulty
    )


def get_chemistry_questions(limit: int = 10, difficulty: str = None) -> List[Dict]:
    """Get chemistry-focused questions"""
    return fetch_trivia_api_questions(
        limit=limit,
        tags=["chemistry"],
        difficulty=difficulty
    )


def get_medicine_questions(limit: int = 10, difficulty: str = None) -> List[Dict]:
    """Get medicine-focused questions"""
    return fetch_trivia_api_questions(
        limit=limit,
        tags=["medicine", "anatomy"],
        difficulty=difficulty
    )


def get_physics_questions(limit: int = 10, difficulty: str = None) -> List[Dict]:
    """Get physics-focused questions"""
    return fetch_trivia_api_questions(
        limit=limit,
        tags=["physics"],
        difficulty=difficulty
    )


# Test function
if __name__ == "__main__":
    print("Testing Trivia API Integration...")

    # Test The Trivia API
    print("\n--- The Trivia API (Science) ---")
    questions = fetch_trivia_api_questions(limit=3, tags=["biology"])
    for q in questions:
        print(f"Q: {q['question']}")
        print(f"A: {q['correct_answer']}")
        print(f"Tags: {q['tags']}")
        print()

    # Test OpenTDB
    print("\n--- OpenTDB (Science & Nature) ---")
    questions = fetch_opentdb_questions(amount=3)
    for q in questions:
        print(f"Q: {q['question']}")
        print(f"A: {q['correct_answer']}")
        print()

    # Test combined
    print("\n--- Combined MCAT-relevant ---")
    questions = fetch_mcat_relevant_questions(limit=5, focus_area="biology")
    for q in questions:
        print(f"Q: {q['question']}")
        print(f"Source: {q['source']}")
        print()
