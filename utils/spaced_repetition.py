"""
Spaced Repetition System (SRS) Module
Implements SM-2 algorithm for optimized learning

The SM-2 algorithm calculates optimal review intervals based on:
- How well you know a card (quality rating 0-5)
- Previous review history
- Ease factor (how easy the card is for you)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import math


@dataclass
class CardReviewData:
    """Data structure for tracking card review history"""
    card_id: int
    ease_factor: float = 2.5  # Default ease factor
    interval: int = 1  # Days until next review
    repetitions: int = 0  # Number of successful reviews
    next_review: str = ""  # ISO format date
    last_review: str = ""  # ISO format date
    total_reviews: int = 0
    correct_reviews: int = 0
    is_bookmarked: bool = False
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CardReviewData':
        return cls(**data)


class SpacedRepetitionSystem:
    """
    Implements the SM-2 Spaced Repetition Algorithm

    Quality ratings:
    0 - Complete blackout, no memory
    1 - Incorrect, but remembered upon seeing answer
    2 - Incorrect, but answer seemed easy to recall
    3 - Correct with serious difficulty
    4 - Correct with some hesitation
    5 - Perfect response, instant recall
    """

    def __init__(self, data_file: str):
        """
        Initialize the SRS system

        Args:
            data_file: Path to JSON file for storing review data
        """
        self.data_file = data_file
        self.cards: Dict[int, CardReviewData] = {}
        self.load_data()

    def load_data(self):
        """Load review data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for card_id, card_data in data.get('cards', {}).items():
                        self.cards[int(card_id)] = CardReviewData.from_dict(card_data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading SRS data: {e}")
                self.cards = {}

    def save_data(self):
        """Save review data to file"""
        data = {
            'cards': {str(card_id): card.to_dict() for card_id, card in self.cards.items()},
            'last_updated': datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def get_card_data(self, card_id: int) -> CardReviewData:
        """Get or create review data for a card"""
        if card_id not in self.cards:
            self.cards[card_id] = CardReviewData(card_id=card_id)
        return self.cards[card_id]

    def calculate_sm2(self, card_id: int, quality: int) -> Tuple[int, float]:
        """
        Calculate the next review interval using SM-2 algorithm

        Args:
            card_id: The card being reviewed
            quality: Rating from 0-5

        Returns:
            Tuple of (new_interval_days, new_ease_factor)
        """
        card = self.get_card_data(card_id)

        # Clamp quality to valid range
        quality = max(0, min(5, quality))

        # Update ease factor
        # EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        new_ef = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(1.3, new_ef)  # Minimum ease factor is 1.3

        # Calculate new interval
        if quality < 3:
            # Failed review - reset
            new_interval = 1
            new_repetitions = 0
        else:
            # Successful review
            if card.repetitions == 0:
                new_interval = 1
            elif card.repetitions == 1:
                new_interval = 6
            else:
                new_interval = round(card.interval * new_ef)

            new_repetitions = card.repetitions + 1

        return new_interval, new_ef, new_repetitions

    def record_review(self, card_id: int, quality: int):
        """
        Record a review and update the card's schedule

        Args:
            card_id: The card being reviewed
            quality: Rating from 0-5 (0-2 = incorrect, 3-5 = correct)
        """
        card = self.get_card_data(card_id)

        # Calculate new values
        new_interval, new_ef, new_reps = self.calculate_sm2(card_id, quality)

        # Update card data
        card.interval = new_interval
        card.ease_factor = new_ef
        card.repetitions = new_reps
        card.last_review = datetime.now().isoformat()
        card.next_review = (datetime.now() + timedelta(days=new_interval)).isoformat()
        card.total_reviews += 1

        if quality >= 3:
            card.correct_reviews += 1

        self.save_data()

    def record_simple_review(self, card_id: int, correct: bool):
        """
        Simplified review recording (correct/incorrect)

        Args:
            card_id: The card being reviewed
            correct: True if answered correctly
        """
        # Map to quality rating
        # Correct = 4 (good response)
        # Incorrect = 1 (wrong but remembered after seeing answer)
        quality = 4 if correct else 1
        self.record_review(card_id, quality)

    def get_due_cards(self, all_card_ids: List[int]) -> List[int]:
        """
        Get cards that are due for review

        Args:
            all_card_ids: List of all available card IDs

        Returns:
            List of card IDs that are due for review, sorted by priority
        """
        now = datetime.now()
        due_cards = []

        for card_id in all_card_ids:
            card = self.get_card_data(card_id)

            if not card.next_review:
                # New card, never reviewed
                due_cards.append((card_id, 0, True))  # (id, days_overdue, is_new)
            else:
                next_review = datetime.fromisoformat(card.next_review)
                if next_review <= now:
                    days_overdue = (now - next_review).days
                    due_cards.append((card_id, days_overdue, False))

        # Sort by: new cards first, then by days overdue (most overdue first)
        due_cards.sort(key=lambda x: (not x[2], -x[1]))

        return [card_id for card_id, _, _ in due_cards]

    def get_study_queue(self, all_card_ids: List[int], limit: int = 20) -> List[int]:
        """
        Get a study queue with optimal mix of new and review cards

        Args:
            all_card_ids: List of all available card IDs
            limit: Maximum cards to return

        Returns:
            Optimized list of card IDs to study
        """
        due_cards = self.get_due_cards(all_card_ids)

        # Separate new and review cards
        new_cards = []
        review_cards = []

        for card_id in due_cards:
            card = self.get_card_data(card_id)
            if card.total_reviews == 0:
                new_cards.append(card_id)
            else:
                review_cards.append(card_id)

        # Mix: prioritize review cards, but include some new cards
        # Ratio: ~70% review, ~30% new
        review_limit = int(limit * 0.7)
        new_limit = limit - review_limit

        queue = review_cards[:review_limit] + new_cards[:new_limit]

        # If we don't have enough, fill with remaining
        remaining = limit - len(queue)
        if remaining > 0:
            all_remaining = [c for c in due_cards if c not in queue]
            queue.extend(all_remaining[:remaining])

        return queue[:limit]

    def get_card_stats(self, card_id: int) -> Dict:
        """Get statistics for a specific card"""
        card = self.get_card_data(card_id)

        accuracy = 0
        if card.total_reviews > 0:
            accuracy = (card.correct_reviews / card.total_reviews) * 100

        return {
            'card_id': card_id,
            'total_reviews': card.total_reviews,
            'correct_reviews': card.correct_reviews,
            'accuracy': round(accuracy, 1),
            'ease_factor': round(card.ease_factor, 2),
            'current_interval': card.interval,
            'next_review': card.next_review,
            'last_review': card.last_review,
            'is_bookmarked': card.is_bookmarked,
            'mastery_level': self._get_mastery_level(card)
        }

    def _get_mastery_level(self, card: CardReviewData) -> str:
        """Determine mastery level based on card performance"""
        if card.total_reviews == 0:
            return "New"
        elif card.interval >= 21 and card.ease_factor >= 2.5:
            return "Mastered"
        elif card.interval >= 7:
            return "Learning"
        elif card.repetitions >= 2:
            return "Familiar"
        else:
            return "Struggling"

    def get_overall_stats(self, all_card_ids: List[int]) -> Dict:
        """Get overall study statistics"""
        total_cards = len(all_card_ids)
        reviewed_cards = 0
        mastered_cards = 0
        struggling_cards = 0
        total_reviews = 0
        total_correct = 0

        for card_id in all_card_ids:
            card = self.get_card_data(card_id)
            if card.total_reviews > 0:
                reviewed_cards += 1
                total_reviews += card.total_reviews
                total_correct += card.correct_reviews

                mastery = self._get_mastery_level(card)
                if mastery == "Mastered":
                    mastered_cards += 1
                elif mastery == "Struggling":
                    struggling_cards += 1

        overall_accuracy = 0
        if total_reviews > 0:
            overall_accuracy = (total_correct / total_reviews) * 100

        due_count = len(self.get_due_cards(all_card_ids))

        return {
            'total_cards': total_cards,
            'reviewed_cards': reviewed_cards,
            'new_cards': total_cards - reviewed_cards,
            'mastered_cards': mastered_cards,
            'struggling_cards': struggling_cards,
            'due_for_review': due_count,
            'total_reviews': total_reviews,
            'overall_accuracy': round(overall_accuracy, 1),
            'completion_percentage': round((reviewed_cards / total_cards) * 100, 1) if total_cards > 0 else 0
        }

    def toggle_bookmark(self, card_id: int) -> bool:
        """Toggle bookmark status for a card"""
        card = self.get_card_data(card_id)
        card.is_bookmarked = not card.is_bookmarked
        self.save_data()
        return card.is_bookmarked

    def get_bookmarked_cards(self) -> List[int]:
        """Get all bookmarked card IDs"""
        return [card_id for card_id, card in self.cards.items() if card.is_bookmarked]

    def add_note(self, card_id: int, note: str):
        """Add a note to a card"""
        card = self.get_card_data(card_id)
        card.notes = note
        self.save_data()

    def get_note(self, card_id: int) -> str:
        """Get note for a card"""
        card = self.get_card_data(card_id)
        return card.notes

    def reset_card(self, card_id: int):
        """Reset a card's learning progress"""
        if card_id in self.cards:
            bookmarked = self.cards[card_id].is_bookmarked
            notes = self.cards[card_id].notes
            self.cards[card_id] = CardReviewData(
                card_id=card_id,
                is_bookmarked=bookmarked,
                notes=notes
            )
            self.save_data()


# Test the system
if __name__ == "__main__":
    import tempfile

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_file = f.name

    srs = SpacedRepetitionSystem(test_file)

    print("Testing Spaced Repetition System...")

    # Simulate some reviews
    test_cards = [1, 2, 3, 4, 5]

    # Card 1: Perfect recall
    srs.record_review(1, quality=5)
    print(f"Card 1 after perfect recall: {srs.get_card_stats(1)}")

    # Card 2: Good recall
    srs.record_review(2, quality=4)
    print(f"Card 2 after good recall: {srs.get_card_stats(2)}")

    # Card 3: Failed
    srs.record_review(3, quality=1)
    print(f"Card 3 after failure: {srs.get_card_stats(3)}")

    # Get due cards
    print(f"\nDue cards: {srs.get_due_cards(test_cards)}")

    # Get study queue
    print(f"Study queue: {srs.get_study_queue(test_cards)}")

    # Overall stats
    print(f"\nOverall stats: {srs.get_overall_stats(test_cards)}")

    # Cleanup
    os.unlink(test_file)
    print("\nTest completed successfully!")
