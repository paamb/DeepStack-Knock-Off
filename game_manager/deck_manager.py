import random


class Card:
    def __init__(self, suit, value) -> None:
        self.suit = suit
        self.value = value

    def __str__(self):
        return self.suit + self.value

    def __repr__(self) -> str:
        return self.__str__()


class DeckManager():
    # Spades, Hearths, Diamonds, Clubs
    suits = ['S', 'H', 'D', 'C']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    def __init__(self) -> None:
        self.create_deck_of_cards()

    def create_deck_of_cards(self):
        self.cards = [Card(suit, value)
                      for value in self.values for suit in self.suits]

    # Contains remaining cards in stack
    def shuffle_cards(self):
        random.shuffle(self.cards)

    def get_n_cards(self, num_cards):
        # This should be an illegal state
        assert len(self.cards) >= num_cards

        deal_cards = self.cards[:num_cards]
        cards_left = self.cards[num_cards:]
        self.cards = cards_left

        return deal_cards


if __name__ == '__main__':
    deckmanager = DeckManager()
    deckmanager.create_deck_of_cards()
    print(deckmanager.cards)
    deckmanager.shuffle_cards()
    print(deckmanager.cards)
    print(deckmanager.get_n_cards(2))
    print(deckmanager.cards)
