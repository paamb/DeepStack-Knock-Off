from poker_oracle.simulation import Simulation
from poker_oracle.hands_evaluator.hands_evaluator import HandsEvaluator
from game_manager.player import Player
from game_manager.deck_manager import Card
from game_manager.constants import constants as const
from game_manager.pivotal_parameters import pivotal_parameters as piv
import numpy as np


class UtilityMatrixStorage:
    """
    Used for storing and fetching precomputed utility matrices.
    """
    def __init__(self) -> None:
        self.utility_matrices = {}
    
    def add_matrix(self, cards, utility_matrix):
        card_key = self.cards_as_string(cards)
        self.utility_matrices[card_key] = utility_matrix

    def is_utility_matrix_created(self, cards):
        card_key = self.cards_as_string(cards)
        return card_key in self.utility_matrices.keys()

    def get_utility_matrix(self, cards):
        card_key = self.cards_as_string(cards)
        return self.utility_matrices[card_key]

    def cards_as_string(self, cards):
        hand_as_string = [str(card) for card in cards]
        sorted_cards = sorted(hand_as_string, key=lambda x: (x[0], const.card_values[x[1]]))
        sorted_cars_as_string = ''.join(sorted_cards)
        return sorted_cars_as_string

class UtilityMatrixHandler:
    """
    Generates and handles utility matrices.
    """
    NUMBER_OF_HOLE_PAIRS = const.num_hole_pairs

    def __init__(self):
        self.utility_matrix = self.generate_empty_utility_matrix()
        self.all_hole_pairs = Simulation().get_all_possible_hole_pairs()

        # Used for storing and fetching pre-computed utility matrices
        self.storage = UtilityMatrixStorage()

        # Create players for simulation
        self.player_1 = Player()
        self.player_2 = Player()

        # Create player hands for simulation
        self.player_1.hand = [Card('S', 'A'), Card('S', '2')]
        self.player_2.hand = [Card('S', '3'), Card('S', '4')]

        self.hands_evaluator = HandsEvaluator()

    def generate_empty_utility_matrix(self):
        """ 
        Initilize utility matrix with zeros
        """
        return np.array([[0 for j in range(self.NUMBER_OF_HOLE_PAIRS)] for i in range(self.NUMBER_OF_HOLE_PAIRS)])

    def generate_utility_matrix(self, public_cards):
        """
        Computes utility matrix according to the set of public cards
        """
        # Initialize with zeros
        utility_matrix = self.generate_empty_utility_matrix()

        # Loop over all hole pairs
        for player_1_card_index in range(self.NUMBER_OF_HOLE_PAIRS):
            # Fetch player 1 cards like so: [(C2), (C3)]
            player_1_cards = [self.all_hole_pairs[player_1_card_index][:2], self.all_hole_pairs[player_1_card_index][2:]]

            # Set the player suit and value for player 1's hand from the card strings above
            self.player_1.hand = self.get_player_cards(self.player_1, player_1_cards)

            # Loop over player 2 cards. Starting from the next index
            for player_2_card_index in range(player_1_card_index + 1, self.NUMBER_OF_HOLE_PAIRS):
                player_2_cards = [self.all_hole_pairs[player_2_card_index][:2], self.all_hole_pairs[player_2_card_index][2:]]

                # Check if there are duplicate cards in player 1's hand and player 2's hand.
                if self.check_duplicate_cards(public_cards, player_1_cards, player_2_cards):
                    utility = 0 
                # If not duplicate. Calculate who wins
                else:
                    self.player_2.hand = self.get_player_cards(self.player_2, player_2_cards)
                    utility = self.calculate_utility(public_cards)

                # Utility is inverse symmetric. Set the inverse value for symmetric index
                self.set_inverse_mirrored_utilities(player_1_card_index, player_2_card_index, utility, utility_matrix)
        return utility_matrix

    def get_utility_matrix(self, public_cards):
        if self.storage.is_utility_matrix_created(public_cards): 
            if piv.verbose:
                print(f"Utiity matrix for public cards {public_cards} already exists. Fetching matrix...")
            utility_matrix = self.storage.get_utility_matrix(public_cards)
        else:
            if piv.verbose:
                print(f"Creating utility matrix for public cards: {public_cards}...")
            utility_matrix = self.generate_utility_matrix(public_cards)
            self.storage.add_matrix(public_cards, utility_matrix)

        return utility_matrix

    def set_inverse_mirrored_utilities(self, player_1_card_index, player_2_card_index, value, utility_matrix):
        utility_matrix[player_1_card_index][player_2_card_index] = value
        utility_matrix[player_2_card_index][player_1_card_index] = -value
        return utility_matrix


    def calculate_utility(self, public_cards):
        winners = self.hands_evaluator.get_winner([self.player_1, self.player_2], public_cards)
        if len(winners) == 2:
            return 0
        elif self.player_1 in winners:
            return 1
        return -1
    

    def check_duplicate_cards(self, public_cards, player_1_cards, player_2_cards):
        """
        Check if there are duplicate cards in player cards and public cards.
        """
        public_cards_as_str = [str(card) for card in public_cards]
        all_cards_as_str = public_cards_as_str + player_1_cards + player_2_cards
        return len(set(all_cards_as_str)) != len(all_cards_as_str)

    def __str__(self):
        return str(self.utility_matrix)


    def get_player_cards(self, player, cards_as_str):
        """
        Setting the suit and value for each player card. Using the same dummy Card object
        """
        player.hand[0].suit = cards_as_str[0][0]
        player.hand[0].value = cards_as_str[0][1]
        player.hand[1].suit = cards_as_str[1][0]
        player.hand[1].value = cards_as_str[1][1]

        return player.hand
    

if __name__ == "__main__":
    utility_matrix_handler = UtilityMatrixHandler()

    public_cards = [Card('S', '6'), Card('S', '5'), Card('C', 'J'), Card('D', 'A'), Card('C', 'A')]
    utility_matrix = utility_matrix_handler.get_utility_matrix(public_cards)

    print(utility_matrix)

    