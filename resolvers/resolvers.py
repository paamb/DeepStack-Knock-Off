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
            player, state.community_cards, num_opponents=state.num_remaining_players - 1)

        # Want to add potsize later
        expected_utility = []
        for action in state.possible_actions:
            utility = self.expected_utility(
                player, action, state, win_probability)
            expected_utility.append((action, utility))

        expected_utility_sorted = sorted(
            expected_utility, key=lambda x: x[1], reverse=True)
        print(win_probability, expected_utility_sorted)

        return expected_utility_sorted[0][0]

    def expected_utility(self, player, action, state, win_probability):
        if action == 'F':
            win_probability = 0

        amount_to_call = state.get_amount_to_call(player)
        amount_to_bet = state.get_amount_to_bet(player)

        # pot_size_if_all_remaining_players_calls

        hypothetical_won_money_estimate = {
            'F': 0,
            'C': player.chips + state.pot_size_if_all_remaining_players_calls,
            'B': player.chips + state.pot_size_if_all_remaining_players_bets,
            'A': state.num_remaining_players * player.chips
        }

        hypothetical_loss_money_estimate = {
            'F': player.chips,
            'C': player.chips - amount_to_call,
            'B': player.chips - amount_to_bet,
            'A': 0
        }

        expected_utility = win_probability * (self.utility_of_money(hypothetical_won_money_estimate[action], player.risk_averseness)) + (
            1-win_probability) * self.utility_of_money(hypothetical_loss_money_estimate[action], player.risk_averseness)
        # expected_utility_from_normal_distribution = np.random.normal(expected_utility, 0.005)
        expected_utility_from_normal_distribution = expected_utility
        return expected_utility_from_normal_distribution

    def utility_of_money(self, money, risk_averseness):
        # the utility of money is often non-linear
        money = max(money, 0)
        return money**risk_averseness


if __name__ == '__main__':
    from game_manager.player import AIPlayer
    from state_manager.state_manager import State
    from game_manager.game_manager import RoundManager
    from game_manager.game_manager import GameManager
    player = AIPlayer()
    player.chips = 20
    player.betted_chips = 0
    resolver = PureRolloutResolver()
    game_manager = GameManager()
    round_manager = RoundManager(game_manager)
    state = State(round_manager)
    state.remaining_players = 2
    state.pot_size_if_all_remaining_players_bets = 40
    state.pot_size_if_all_remaining_players_calls = 20
    # state.
    actions = ['C', 'B', 'F', 'A']
    win_probabilities = [i/10 for i in range(0, 11)]
    for win_probability in win_probabilities:
        all_expected = []
        for action in actions:
            all_expected.append((win_probability, action, resolver.expected_utility(
                player, action, state, win_probability)))
        expected_utility_sorted = sorted(
            all_expected, key=lambda x: x[2], reverse=True)
        print(expected_utility_sorted)
