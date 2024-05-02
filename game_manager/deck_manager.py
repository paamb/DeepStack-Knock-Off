import random
from game_manager.constants import constants as const

class Card:
    def __init__(self, suit, value) -> None:
        if not isinstance(suit, str) or not isinstance(value, str):
            raise TypeError
        self.suit: str = suit
        self.value: str = value

    def __str__(self):
        return self.suit + self.value

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other_card) -> bool:
        return self.suit == other_card.suit and self.value == other_card.value


class DeckManager():

    def __init__(self, custom_deck_without_certain_cards=False, invalid_cards=[]) -> None:
        if not custom_deck_without_certain_cards:
            self.create_deck_of_cards()
        else:
            self.create_deck_of_cards_without_cards(invalid_cards)

    def create_deck_of_cards(self):
        self.cards = [Card(suit, value)
                      for value in const.ranks for suit in const.suits]

    def create_deck_of_cards_without_cards(self, invalid_cards):
        cards = []
        for value in const.ranks:
            for suit in const.suits:
                new_card = Card(suit, value)
                if new_card not in invalid_cards:
                    cards.append(new_card)
        self.cards = cards

    def shuffle_cards(self):
        random.shuffle(self.cards)

    def get_n_cards(self, num_cards):
        # This should be an illegal state
        assert len(self.cards) >= num_cards

        deal_cards = self.cards[:num_cards]
        cards_left = self.cards[num_cards:]
        self.cards = cards_left

        return deal_cards
    
    def get_n_cards_not_in_invalid_cards(self, invalid_cards, n):
        valid_cards = [card for card in self.cards if card not in invalid_cards]
        return random.sample(valid_cards, n)

    def receive_cards(self, cards):
        self.cards = self.cards + cards


if __name__ == '__main__':
    deckmanager = DeckManager()
    deckmanager.create_deck_of_cards()
    print(deckmanager.cards)
    deckmanager.shuffle_cards()
    print(deckmanager.cards)
    print(deckmanager.get_n_cards(2))
    print(deckmanager.cards)
