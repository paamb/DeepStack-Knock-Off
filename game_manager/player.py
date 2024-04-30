from typing import List
from .deck_manager import Card
from .pivotal_parameters import pivotal_parameters as piv
from resolvers.resolvers import DeepStackResolver, PureRolloutResolver

import random


class Player():

    # Abstrakt
    # CardContainer
    # Chips

    def __init__(self, chips=piv.starting_chips_per_player, hide_cards=False) -> None:
        self.hand = []
        self.chips = chips
        self.betted_chips = 0
        self.is_folded = False
        self.hide_cards = hide_cards
        pass

    def get_player_hand_as_string(self):
        hand_as_string = [str(self.hand[0]), str(self.hand[1])]
        card_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
               '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2, 'AL': 1}
        sorted_hand = sorted(hand_as_string, key=lambda x: (x[0], card_values[x[1]]))
        sorted_hand_as_string = sorted_hand[0] + sorted_hand[1]
        return sorted_hand_as_string


    def action():
        pass

    def is_busted(self):
        return self.chips == 0 and self.is_folded == True

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
    def action(self, state):

        input_to_action = {
            action[:1]: action for action in state.legal_actions}

        # for action in possible_actions:
        selected_action = input(
            f'Select action [{list(input_to_action.keys())[0]}]: ')

        try:
            return input_to_action[selected_action]
        except:
            return list(input_to_action.values())[0]


class AIPlayer(Player):

    def __init__(self, chips=piv.starting_chips_per_player, hide_cards=False, probability_of_pure_rollout=0, risk_averseness=0.4):
        super().__init__(chips, hide_cards=hide_cards)
        self.probability_of_pure_rollout = probability_of_pure_rollout
        self.pure_rollout_resolver = PureRolloutResolver()
        self.deepstack_resolver = DeepStackResolver()
        self.risk_averseness = risk_averseness

    def action(self, state):
        if len(state.community_cards) == 5:
            resolver = self.deepstack_resolver
        else:
            resolver = self.pure_rollout_resolver

        # resolver = self.pure_rollout_resolver if random.random(
        # ) < self.probability_of_pure_rollout else self.deepstack_resolver
        action = resolver.choose_action(self, state)
        return action

    # Action() - Must go throught algorithm before making move (needs betting aswell)
    pass
