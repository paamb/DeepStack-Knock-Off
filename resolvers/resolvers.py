import numpy as np
from poker_oracle.monte_carlo import MonteCarlo


class Resolver():
    def __init__(self) -> None:
        self.monte_carlo = MonteCarlo()
    pass


class DeepStackResolver(Resolver):
    pass


class PureRolloutResolver(Resolver):

    def get_win_probability_from_hole_cards(self, player, community_cards, num_opponents=1):
        win_probability = self.monte_carlo.evaluate_player_win_probability_after_pre_flop(
            player, community_cards, num_opponents)
        return win_probability

    def choose_action(self, player, state):
        win_probability = self.get_win_probability_from_hole_cards(
            player, state.community_cards)

        print(win_probability)
        # Want to add potsize later
        expectation_value = 3 + np.tanh(win_probability - 0.5)*2
        std_dev = 1

        x_value_for_action = np.random.normal(expectation_value, std_dev)

        if x_value_for_action < 1:
            # Fold
            return 'F'
        elif x_value_for_action > 1 and x_value_for_action < 4:
            return 'C'
        elif x_value_for_action > 4 and x_value_for_action < 5:
            return 'B'
        else:
            return 'A'
