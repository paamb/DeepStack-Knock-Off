import numpy as np
from poker_oracle.monte_carlo import MonteCarlo
from game_manager.pivotal_parameters import pivotal_parameters as piv


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
            player, state.community_cards, num_opponents=state.num_active_players - 1)

        # Want to add potsize later
        expected_utility = []
        for action in state.possible_actions:
            utility = self.expected_utility(
                player, action, state.current_bet, win_probability, len(state.players))
            expected_utility.append((action, utility))

        expected_utility_sorted = sorted(
            expected_utility, key=lambda x: x[1], reverse=True)

        return expected_utility_sorted[0][0]

        expected_winnings = 3 + np.tanh(win_probability - 0.5)*5
        std_dev = 0.5
        print("EXPval:", expectation_value)

        x_value_for_action = np.random.normal(expectation_value, std_dev)
        print("WIN:", win_probability, x_value_for_action)

        if x_value_for_action < 1:
            # Fold
            return 'F'
        elif x_value_for_action > 1 and x_value_for_action < 4:
            return 'C'
        elif x_value_for_action > 4 and x_value_for_action < 5:
            return 'B'
        else:
            return 'A'

    def expected_utility(self, player, action, current_bet, win_probability, n_players):
        if action == 'F':
            win_probability = 0

        hypothetical_won_money_estimate = {
            'F': 0,
            'C': player.chips + n_players * current_bet,
            'B': player.chips + n_players * (current_bet + 2 * piv.small_blind),
            'A': n_players * player.chips
        }

        hypothetical_loss_money_estimate = {
            'F': player.chips,
            'C': player.chips - (current_bet - player.betted_chips),
            'B': player.chips - (current_bet - player.betted_chips + 2 * piv.small_blind),
            'A': 0
        }

        expected_utility = win_probability * (self.utility_of_money(hypothetical_won_money_estimate[action], player.risk_averseness)) + (
            1-win_probability) * self.utility_of_money(hypothetical_loss_money_estimate[action], player.risk_averseness)
        # expected_utility_from_normal_distribution = np.random.normal(expected_utility, 0.005)
        expected_utility_from_normal_distribution = expected_utility
        return expected_utility_from_normal_distribution

    def utility_of_money(self, money, risk_averseness):
        money = max(money, 0)
        return money**risk_averseness
