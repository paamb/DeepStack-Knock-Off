import numpy as np
from poker_oracle.simulation import Simulation
from game_manager.pivotal_parameters import pivotal_parameters as piv
from game_manager.constants import constants as const

NUM_HOLE_PAIRS = const.num_hole_pairs

class TreeNode():
    def __init__(self, current_player, state) -> None:
        self.state = state
        self.child_nodes = []
        self.current_player = current_player

    def get_opponent(self):
        opponent = list(set(self.state.players) - set([self.current_player]))[0]
        return opponent

class PlayerNode(TreeNode):
    def __init__(self, current_player, state) -> None:
        super().__init__(current_player, state) 
        self.current_player = current_player

    def calculate_weighted_average(self, value_vectors_from_children):
        a = self.strategy_matrix
        b = value_vectors_from_children.T
        value_vector = np.einsum('ij,ij->i', a, b)
        return value_vector
    
    def initialize_strategy_matrix(self, legal_actions):
        number_of_legal_actions = len(legal_actions)
        self.strategy_matrix = np.full((NUM_HOLE_PAIRS, number_of_legal_actions), fill_value=1/number_of_legal_actions)
        self.regret = np.zeros((NUM_HOLE_PAIRS, number_of_legal_actions))

    def update_ranges(self, player_ranges_for_action, action_index):
        # player_ranges_for_action = dict(player_ranges_for_action)
        new_player_ranges_for_action = {key: value.copy() for key, value in player_ranges_for_action.items()}
        r_p = new_player_ranges_for_action[self.current_player]
        new_player_ranges_for_action[self.current_player] = self.bayesian_range_update(r_p, action_index, self.strategy_matrix)
        return new_player_ranges_for_action

    def print_player_ranges(self, range_1):
        hole_pairs = Simulation().get_all_possible_hole_pairs()
        with open('ranges_in_bayesian_update_output.txt', 'w') as file:
            file.write("Hole pair | r_1 | r_2 \n")
            for i in range(len(hole_pairs)):
                file.write(f"{hole_pairs[i]} | {range_1[i]} \n")

    def bayesian_range_update(self, range, action_index, strategy_matrix):
        new_range = range.copy()
        action_column = strategy_matrix[:, action_index]
        sum_of_action_column = np.sum(action_column)
        sum_of_all_actions = np.sum(strategy_matrix)
        p_of_action = sum_of_action_column / sum_of_all_actions

        new_range = action_column * range / p_of_action 
        return new_range

class EndNode(TreeNode):
    def get_value_vectors(self, node, player_ranges): 
        """
        This is only used in the first stages if NeuralNetNode dont have a trained network yet.
        Returns only random values
        """
        opponent = node.get_opponent()

        value_vectors = {
            node.current_player: np.random.randn(NUM_HOLE_PAIRS),
            opponent: -np.random.randn(NUM_HOLE_PAIRS)
        }
        return value_vectors

class FoldNode(EndNode):
    def get_value_vectors(self, node, player_ranges):
        """
        Initialize value vectors to contain negative value for the 
        "current_player" which is the active player in the state.
        """
        fold_value = node.state.pot / piv.average_pot_size

        opponent = node.get_opponent()

        value_vectors = { 
            node.current_player: np.full(NUM_HOLE_PAIRS, -fold_value),
            opponent: np.full(NUM_HOLE_PAIRS, fold_value)
        }

        for player in player_ranges.keys():
            player_mask = np.ceil(player_ranges[player]).astype(int)
            value_vector = value_vectors[player]
            value_vector = value_vector * player_mask
            value_vectors[player] = value_vector
        
        return value_vectors

class NeuralNetNode(EndNode):
    pass

class ShowDownNode(EndNode):
    def __init__(self, current_player, state, utility_matrix_handler) -> None:
        super().__init__(current_player, state)
        self.utility_matrix = utility_matrix_handler.get_utility_matrix(state.community_cards)

    def get_value_vectors(self, node, player_ranges):
        scale_value = node.state.pot / piv.average_pot_size
        opponent = node.get_opponent()
        v_p = scale_value * np.dot(self.utility_matrix, player_ranges[opponent])
        v_o = scale_value * (-1) * np.dot(player_ranges[node.current_player], self.utility_matrix)

        value_vector = {
            self.current_player: v_p,
            opponent: v_o
        }
        return value_vector

class ChanceNode(TreeNode):

    def calculate_weighted_average(self, value_vectors_from_children):
        return np.mean(value_vectors_from_children, axis=0)
    pass    

    def update_ranges(self, player_ranges_for_action, action_index, card_to_range_indexes_to_zero):
        """
        Zero's elements in the range where card is dealt.
        """

        new_player_ranges_for_action = {key: value.copy() for key, value in player_ranges_for_action.items()}
        cards, _ = self.child_nodes[action_index]
        for card in cards:
            indexes_to_zero = card_to_range_indexes_to_zero[str(card)]
            for player in new_player_ranges_for_action.keys():
                new_player_ranges_for_action[player][indexes_to_zero] = 0
            
        for player, range in new_player_ranges_for_action.items():
            new_player_ranges_for_action[player] = range / np.sum(range)

        return new_player_ranges_for_action