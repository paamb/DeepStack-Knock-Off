from typing import List
from deck_manager import Card
import pivotal_parameters as piv


class Player():
    # Abstrakt
    # CardContainer
    # Chips

    def __init__(self) -> None:
        self.hand = []
        self.chips = piv.starting_chips_per_player
        pass

    def action():
        pass

    def recieve_cards(self, cards: List[Card]):
        self.hand = self.hand + cards

    def __str__(self):
        return f"Hand: {self.hand} | Chips: {self.chips}\n"

    def __repr__(self) -> str:
        return self.__str__()

    pass


class HumanPlayer(Player):
    # Action() (Betting. Takes in gamestate)
    pass


class AIPlayer(Player):
    # Action() - Must go throught algorithm before making move (needs betting aswell)
    pass
