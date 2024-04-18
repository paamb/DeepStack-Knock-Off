from poker_oracle.monte_carlo import MonteCarlo
from poker_oracle.hands_evaluator.hands_evaluator import HandsEvaluator
from game_manager.player import Player
from game_manager.deck_manager import Card

import numpy as np

class UtilityMatrixHandler:
    NUMBER_OF_HOLE_PAIRS = 1326

    def __init__(self):
        self.utility_matrix = self.generate_empty_utility_matrix()
        self.all_hole_pairs = MonteCarlo().get_all_possible_hole_pairs()
        self.player_1 = Player()
        self.player_2 = Player()

        self.player_1.hand = [Card('S', 'A'), Card('S', '2')]
        self.player_2.hand = [Card('S', '3'), Card('S', '4')]

        self.hands_evaluator = HandsEvaluator()

    def generate_empty_utility_matrix(self):
        return np.array([[0 for j in range(self.NUMBER_OF_HOLE_PAIRS)] for i in range(self.NUMBER_OF_HOLE_PAIRS)])

    def generate_utility_matrix(self, public_cards):
        self.utility_matrix = self.generate_empty_utility_matrix()

        for player_1_card_index in range(self.NUMBER_OF_HOLE_PAIRS):
            player_1_cards = [self.all_hole_pairs[player_1_card_index][:2], self.all_hole_pairs[player_1_card_index][2:]]
            self.player_1.hand = self.get_player_cards(self.player_1, player_1_cards)
            for player_2_card_index in range(player_1_card_index + 1, self.NUMBER_OF_HOLE_PAIRS):
                player_2_cards = [self.all_hole_pairs[player_2_card_index][:2], self.all_hole_pairs[player_2_card_index][2:]]

                if self.check_duplicate_cards(public_cards, player_1_cards, player_2_cards):
                    utility = 0 
                else:
                    self.player_2.hand = self.get_player_cards(self.player_2, player_2_cards)
                    utility = self.calculate_utility(public_cards)
                
                self.set_inverse_mirrored_utilities(player_1_card_index, player_2_card_index, utility)

    def set_inverse_mirrored_utilities(self, player_1_card_index, player_2_card_index, value):
        self.utility_matrix[player_1_card_index][player_2_card_index] = value
        self.utility_matrix[player_2_card_index][player_1_card_index] = -value


    def calculate_utility(self, public_cards):
        winners = self.hands_evaluator.get_winner([self.player_1, self.player_2], public_cards)
        if len(winners) == 2:
            return 0
        elif self.player_1 in winners:
            return 1
        return -1
    

    def check_duplicate_cards(self, public_cards, player_1_cards, player_2_cards):
        public_cards_as_str = [str(card) for card in public_cards]
        all_cards_as_str = public_cards_as_str + player_1_cards + player_2_cards
        return len(set(all_cards_as_str)) != len(all_cards_as_str)

    def __str__(self):
        return str(self.utility_matrix)


    def get_player_cards(self, player, cards_as_str):
        player.hand[0].suit = cards_as_str[0][0]
        player.hand[0].value = cards_as_str[0][1]
        player.hand[1].suit = cards_as_str[1][0]
        player.hand[1].value = cards_as_str[1][1]

        return player.hand
    

if __name__ == "__main__":
    utility_matrix_handler = UtilityMatrixHandler()

    public_cards = [Card('S', '6'), Card('S', '5'), Card('C', 'A'), Card('C', '2'), Card('C', '7')]
    utility_matrix_handler.generate_utility_matrix(public_cards)
    