from typing import List
from .deck_manager import Card
from .pivotal_parameters import pivotal_parameters as piv


class Player():
    # Abstrakt
    # CardContainer
    # Chips

    def __init__(self, chips=piv.starting_chips_per_player) -> None:
        self.hand = []
        self.chips = chips
        self.betted_chips = 0
        self.is_folded = False
        pass

    def action():
        pass

    def receive_cards(self, cards: List[Card]):
        self.hand = self.hand + cards

    def fold(self):
        self.is_folded = True

    def check_or_call(self, current_bet=0):        
        amount_to_call = current_bet - self.betted_chips
        if self.chips >= amount_to_call:
            self.betted_chips += amount_to_call
            self.chips -= amount_to_call
            assert self.betted_chips == current_bet
        else:
            self.all_in()

    def bet_or_raise(self, current_bet, amount):
        assert self.chips > current_bet - self.betted_chips

        amount_to_bet = current_bet - self.betted_chips + amount
        if self.chips >= amount_to_bet:
            self.betted_chips += amount_to_bet
            self.chips -= amount_to_bet
            assert self.betted_chips == current_bet + amount
            return self.betted_chips
        else:
            return self.all_in()

    def all_in(self):
        self.betted_chips += self.chips
        self.chips = 0
        return self.betted_chips

    def receive_chips(self, amount):
        self.chips += amount

    def round_ended(self):
        self.betted_chips = 0
        self.is_folded = self.chips == 0

    def hand_over_cards(self):
        hand = self.hand
        self.hand = []
        return hand

    def __str__(self):
        return f"Hand: {self.hand}"

    def __repr__(self) -> str:
        return self.__str__()

    pass


class HumanPlayer(Player):
    # Action() (Betting. Takes in gamestate)
    def action(self, possible_actions):

        input_to_action = {action[:1]: action for action in possible_actions}

        for action in possible_actions:
            print(action + f'[{action[:1]}]')
        print('\n')
        selected_action = input(
            f'Select action [{list(input_to_action.keys())[0]}]: ')

        try:
            return input_to_action[selected_action]
        except:
            return list(input_to_action.values())[0]


class AIPlayer(Player):
    # Action() - Must go throught algorithm before making move (needs betting aswell)
    pass
