import json
import random
import os
from datetime import datetime, timedelta


class Flashcard:
    def __init__(self, front, back, tags=None, difficulty=1):
        self.front = front  # Front side (question/term)
        self.back = back  # Back side (answer/definition)
        self.tags = tags or []
        self.difficulty = difficulty  # Difficulty level 1-5
        self.last_reviewed = None
        self.review_count = 0
        self.correct_count = 0
        self.created_date = datetime.now()

    def update_review(self, is_correct):
        """Update review record"""
        self.last_reviewed = datetime.now()
        self.review_count += 1
        if is_correct:
            self.correct_count += 1
            # Decrease difficulty when answered correctly
            if self.difficulty > 1:
                self.difficulty -= 1
        else:
            # Increase difficulty when answered incorrectly
            if self.difficulty < 5:
                self.difficulty += 1

    def get_success_rate(self):
        if self.review_count == 0:
            return 0
        return (self.correct_count / self.review_count) * 100

    def needs_review(self):
        if self.last_reviewed is None:
            return True

        # Set review intervals based on difficulty level
        intervals = {1: 7, 2: 5, 3: 3, 4: 2, 5: 1}  # days
        interval_days = intervals.get(self.difficulty, 1)

        return datetime.now() - self.last_reviewed >= timedelta(days=interval_days)


class FlashcardDeck:
    def __init__(self, name):
        self.name = name
        self.cards = []

    def add_card(self, front, back, tags=None, difficulty=1):
        card = Flashcard(front, back, tags, difficulty)
        self.cards.append(card)
        return len(self.cards) - 1  # Return new card index

    def edit_card(self, index, front=None, back=None, tags=None):
        if 0 <= index < len(self.cards):
            card = self.cards[index]
            if front is not None:
                card.front = front
            if back is not None:
                card.back = back
            if tags is not None:
                card.tags = tags
            return True
        return False

    def remove_card(self, index):
        if 0 <= index < len(self.cards):
            removed = self.cards.pop(index)
            return removed
        return None

    def get_cards_for_review(self):
        return [card for card in self.cards if card.needs_review()]

    def get_difficult_cards(self):
        return [card for card in self.cards if card.difficulty >= 4]

    def get_cards_by_tag(self, tag):
        return [card for card in self.cards if tag in card.tags]


class FlashcardStudySystem:
    def __init__(self):
        self.decks = {}
        self.data_file = "flashcards_data.json"
        self.load_data()

    def create_sample_deck(self):
        if "English Vocabulary" not in self.decks:
            self.decks["English Vocabulary"] = FlashcardDeck("English Vocabulary")
            deck = self.decks["English Vocabulary"]

            sample_cards = [
                ("abandon", "to give up or leave behind", ["verb", "high-frequency"]),
                ("ability", "skill or talent", ["noun", "basic"]),
                ("absence", "the state of being away", ["noun", "basic"]),
                ("absolute", "complete or total", ["adjective", "intermediate"]),
                ("academic", "relating to education or scholarship", ["adjective", "academic"]),
                ("accelerate", "to speed up or increase", ["verb", "intermediate"]),
                ("acceptable", "satisfactory or adequate", ["adjective", "intermediate"]),
                ("access", "the ability to enter or approach", ["noun", "verb", "basic"]),
                ("accident", "an unexpected event", ["noun", "basic"]),
                ("accompany", "to go with someone", ["verb", "intermediate"])
            ]

            for front, back, tags in sample_cards:
                deck.add_card(front, back, tags)

    def main_menu(self):
        while True:
            print("\n" + "=" * 50)
            print("Smart Flashcard Study System")
            print("=" * 50)

            if not self.decks:
                print("No decks available. Create one to start studying!")
                print("1. Create Deck")
                print("0. Exit")
            else:
                print("Available Decks:")
                for i, (name, deck) in enumerate(self.decks.items(), 1):
                    card_count = len(deck.cards)
                    need_review = len(deck.get_cards_for_review())
                    difficult = len(deck.get_difficult_cards())
                    print(f"{i}. {name} ({card_count} cards, {need_review} due, {difficult} difficult)")

                print(f"\n{len(self.decks) + 1}. Create New Deck")
                print("0. Exit")

            choice = input("\nSelect option: ").strip()

            if choice == '0':
                self.save_data()
                print("Data saved. Goodbye!")
                break
            elif choice == str(len(self.decks) + 1):
                self.create_deck_menu()
            else:
                try:
                    deck_index = int(choice) - 1
                    deck_names = list(self.decks.keys())
                    if 0 <= deck_index < len(deck_names):
                        self.deck_menu(deck_names[deck_index])
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Please enter a number")

    def create_deck_menu(self):
        print("\n--- Create New Deck ---")
        name = input("Enter deck name: ").strip()
        if name:
            if name not in self.decks:
                self.decks[name] = FlashcardDeck(name)
                print(f"Created deck: {name}")
            else:
                print("Deck already exists")
        else:
            print("Name cannot be empty")

    def deck_menu(self, deck_name):
        deck = self.decks[deck_name]

        while True:
            print(f"\n--- {deck_name} ---")
            print(f"Total Cards: {len(deck.cards)}")

            if deck.cards:
                need_review = len(deck.get_cards_for_review())
                difficult = len(deck.get_difficult_cards())
                print(f"Due for Review: {need_review}")
                print(f"Difficult Cards: {difficult}")

                print("\n1. Start Study Session")
                print("2. Manage Cards")
                print("3. Deck Settings")
            else:
                print("Deck is empty")
                print("\n2. Manage Cards")
                print("3. Deck Settings")

            print("0. Back to Main Menu")

            choice = input("\nSelect option: ").strip()

            if choice == '0':
                break
            elif choice == '1' and deck.cards:
                self.study_menu(deck)
            elif choice == '2':
                self.card_management_menu(deck)
            elif choice == '3':
                self.deck_settings_menu(deck_name)
            else:
                print("Invalid selection")

    def study_menu(self, deck):
        while True:
            print(f"\n--- Study {deck.name} ---")

            need_review = len(deck.get_cards_for_review())
            difficult = len(deck.get_difficult_cards())
            total = len(deck.cards)

            print(f"1. Review Due Cards ({need_review} cards)")
            print(f"2. Practice Difficult Cards ({difficult} cards)")
            print(f"3. Review All Cards ({total} cards)")
            print("4. Study by Tag")
            print("0. Back")

            choice = input("\nSelect option: ").strip()

            if choice == '0':
                break
            elif choice == '1':
                self.start_study_session(deck, "review")
            elif choice == '2':
                self.start_study_session(deck, "difficult")
            elif choice == '3':
                self.start_study_session(deck, "all")
            elif choice == '4':
                self.study_by_tag_menu(deck)
            else:
                print("Invalid selection")

    def study_by_tag_menu(self, deck):
        all_tags = set()
        for card in deck.cards:
            all_tags.update(card.tags)

        if not all_tags:
            print("No tagged cards found")
            return

        tags = sorted(list(all_tags))
        print(f"\n--- Study by Tag ---")
        for i, tag in enumerate(tags, 1):
            count = len([c for c in deck.cards if tag in c.tags])
            print(f"{i}. {tag} ({count} cards)")

        print("0. Back")

        choice = input("\nSelect tag: ").strip()
        if choice == '0':
            return

        try:
            tag_index = int(choice) - 1
            if 0 <= tag_index < len(tags):
                selected_tag = tags[tag_index]
                cards = deck.get_cards_by_tag(selected_tag)
                self.start_study_session(deck, "tag", cards)
            else:
                print("Invalid selection")
        except ValueError:
            print("Please enter a number")

    def card_management_menu(self, deck):
        while True:
            print(f"\n--- Manage Cards - {deck.name} ---")
            print("1. Add Card")
            if deck.cards:
                print("2. View All Cards")
                print("3. Edit Card")
                print("4. Delete Card")
            print("0. Back")

            choice = input("\nSelect option: ").strip()

            if choice == '0':
                break
            elif choice == '1':
                self.add_card_menu(deck)
            elif choice == '2' and deck.cards:
                self.list_cards(deck)
            elif choice == '3' and deck.cards:
                self.edit_card_menu(deck)
            elif choice == '4' and deck.cards:
                self.delete_card_menu(deck)
            else:
                print("Invalid selection")

    def add_card_menu(self, deck):
        print(f"\n--- Add Card to {deck.name} ---")
        front = input("Front (question/term): ").strip()
        if not front:
            print("Front cannot be empty")
            return

        back = input("Back (answer/definition): ").strip()
        if not back:
            print("Back cannot be empty")
            return

        tags_input = input("Tags (comma-separated, optional): ").strip()
        tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else []

        try:
            difficulty = int(input("Difficulty level (1-5, default 1): ") or "1")
            difficulty = max(1, min(5, difficulty))
        except ValueError:
            difficulty = 1

        deck.add_card(front, back, tags, difficulty)
        print("Card added successfully!")

    def edit_card_menu(self, deck):
        self.list_cards(deck, show_index=True)

        try:
            index = int(input("\nSelect card number to edit: ")) - 1
            if 0 <= index < len(deck.cards):
                card = deck.cards[index]
                print(f"\nEditing Card #{index + 1}")
                print(f"Current Front: {card.front}")
                print(f"Current Back: {card.back}")
                print(f"Current Tags: {', '.join(card.tags)}")

                front = input("New Front (press Enter to keep current): ").strip()
                back = input("New Back (press Enter to keep current): ").strip()
                tags_input = input("New Tags (comma-separated, press Enter to keep current): ").strip()

                new_front = front if front else None
                new_back = back if back else None
                new_tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else None

                deck.edit_card(index, new_front, new_back, new_tags)
                print("Card updated successfully!")
            else:
                print("Invalid card number")
        except ValueError:
            print("Please enter a valid number")

    def delete_card_menu(self, deck):
        self.list_cards(deck, show_index=True)

        try:
            index = int(input("\nSelect card number to delete: ")) - 1
            if 0 <= index < len(deck.cards):
                card = deck.cards[index]
                confirm = input(f"Delete card '{card.front}'? (y/n): ").lower().strip()
                if confirm in ['y', 'yes']:
                    deck.remove_card(index)
                    print("Card deleted successfully!")
                else:
                    print("Deletion cancelled")
            else:
                print("Invalid card number")
        except ValueError:
            print("Please enter a valid number")

    def deck_settings_menu(self, deck_name):
        while True:
            print(f"\n--- {deck_name} Settings ---")
            print("1. Rename Deck")
            print("2. View Statistics")
            print("3. Delete Deck")
            print("0. Back")

            choice = input("\nSelect option: ").strip()

            if choice == '0':
                break
            elif choice == '1':
                self.rename_deck_menu(deck_name)
                break  # Return to main menu after rename
            elif choice == '2':
                self.show_statistics(self.decks[deck_name])
            elif choice == '3':
                if self.delete_deck_menu(deck_name):
                    break  # Return to main menu after deletion
            else:
                print("Invalid selection")

    def rename_deck_menu(self, old_name):
        new_name = input(f"Enter new name (current: {old_name}): ").strip()
        if new_name and new_name != old_name:
            if new_name not in self.decks:
                deck = self.decks.pop(old_name)
                deck.name = new_name
                self.decks[new_name] = deck
                print(f"Deck renamed to: {new_name}")
            else:
                print("Name already exists")
        else:
            print("Invalid name or no change made")

    def delete_deck_menu(self, deck_name):
        deck = self.decks[deck_name]
        print(f"Deck '{deck_name}' contains {len(deck.cards)} cards")
        confirm = input("Delete entire deck? This cannot be undone! (type 'DELETE' to confirm): ").strip()
        if confirm == 'DELETE':
            del self.decks[deck_name]
            print("Deck deleted")
            return True
        else:
            print("Deletion cancelled")
            return False

    def start_study_session(self, deck, mode, custom_cards=None):
        if custom_cards is not None:
            cards = custom_cards
        elif mode == "review":
            cards = deck.get_cards_for_review()
        elif mode == "difficult":
            cards = deck.get_difficult_cards()
        else:  # all
            cards = deck.cards.copy()

        if not cards:
            print("No cards match the criteria!")
            return

        random.shuffle(cards)
        correct = 0
        total = len(cards)

        print(f"\nStarting Study Session - {total} cards")
        print("=" * 50)

        for i, card in enumerate(cards, 1):
            print(f"\nCard {i}/{total}")
            if card.tags:
                print(f"Tags: {', '.join(card.tags)}")
            print(f"Question: {card.front}")

            input("Press Enter to reveal answer...")
            print(f"Answer: {card.back}")

            while True:
                response = input("Did you get it right? (y/n/q to quit): ").lower().strip()
                if response in ['y', 'yes']:
                    card.update_review(True)
                    correct += 1
                    print("Great! ✓")
                    break
                elif response in ['n', 'no']:
                    card.update_review(False)
                    print("Keep practicing! ✗")
                    break
                elif response in ['q', 'quit']:
                    print("Study session ended")
                    return
                else:
                    print("Please enter y (yes) or n (no)")

        # Show study results
        accuracy = (correct / total) * 100
        print(f"\nStudy Session Complete!")
        print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")

        if accuracy >= 80:
            print("🎉 Excellent performance! Keep it up!")
        elif accuracy >= 60:
            print("👍 Good work! Keep practicing!")
        else:
            print("💪 Need more practice. You've got this!")

    def list_cards(self, deck, show_index=False):
        if not deck.cards:
            print("Deck is empty")
            return

        print(f"\n--- {deck.name} Card List ---")
        for i, card in enumerate(deck.cards):
            prefix = f"{i + 1}. " if show_index else "• "
            status = "Due" if card.needs_review() else "Learned"
            tags_str = f" [{', '.join(card.tags)}]" if card.tags else ""

            print(f"{prefix}{card.front} -> {card.back}{tags_str}")
            print(f"   Difficulty: {card.difficulty}/5 | Success Rate: {card.get_success_rate():.1f}% | {status}")

    def show_statistics(self, deck):
        cards = deck.cards
        if not cards:
            print("Deck is empty")
            return

        total_cards = len(cards)
        reviewed_cards = len([c for c in cards if c.review_count > 0])
        need_review = len(deck.get_cards_for_review())
        difficult_cards = len(deck.get_difficult_cards())

        total_reviews = sum(c.review_count for c in cards)
        total_correct = sum(c.correct_count for c in cards)
        overall_accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0

        # Tag statistics
        all_tags = {}
        for card in cards:
            for tag in card.tags:
                all_tags[tag] = all_tags.get(tag, 0) + 1

        print(f"\n=== {deck.name} Statistics ===")
        print(f"Total Cards: {total_cards}")
        print(f"Cards Reviewed: {reviewed_cards}")
        print(f"Due for Review: {need_review}")
        print(f"Difficult Cards: {difficult_cards}")
        print(f"Total Reviews: {total_reviews}")
        print(f"Overall Accuracy: {overall_accuracy:.1f}%")

        if all_tags:
            print(f"\nTag Distribution:")
            for tag, count in sorted(all_tags.items()):
                print(f"  {tag}: {count} cards")

    def save_data(self):
        data = {}
        for name, deck in self.decks.items():
            data[name] = []
            for card in deck.cards:
                card_data = {
                    'front': card.front,
                    'back': card.back,
                    'tags': card.tags,
                    'difficulty': card.difficulty,
                    'review_count': card.review_count,
                    'correct_count': card.correct_count,
                    'last_reviewed': card.last_reviewed.isoformat() if card.last_reviewed else None,
                    'created_date': card.created_date.isoformat()
                }
                data[name].append(card_data)

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for deck_name, cards_data in data.items():
                    deck = FlashcardDeck(deck_name)
                    for card_data in cards_data:
                        card = Flashcard(
                            card_data['front'],
                            card_data['back'],
                            card_data.get('tags', []),
                            card_data['difficulty']
                        )
                        card.review_count = card_data['review_count']
                        card.correct_count = card_data['correct_count']
                        if card_data['last_reviewed']:
                            card.last_reviewed = datetime.fromisoformat(card_data['last_reviewed'])
                        card.created_date = datetime.fromisoformat(card_data['created_date'])
                        deck.cards.append(card)

                    self.decks[deck_name] = deck
            except Exception as e:
                print(f"Error loading data: {e}")

        # Create sample deck if no data exists
        if not self.decks:
            self.create_sample_deck()


def main():
    system = FlashcardStudySystem()
    system.main_menu()


if __name__ == "__main__":
    main()