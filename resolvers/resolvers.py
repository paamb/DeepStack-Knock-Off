import numpy as np
from poker_oracle.monte_carlo import MonteCarlo
from game_manager.pivotal_parameters import pivotal_parameters as piv
from state_manager.state_manager import StateManager
from game_manager.deck_manager import DeckManager


class TreeNode():
    def __init__(self, state) -> None:
        self.state = state
        self.child_nodes = []

class PlayerNode(TreeNode):
    def __init__(self, current_player, state) -> None:
        super().__init__(state) 
        self.current_player = current_player

    def calculate_weighted_average(self, value_vectors_from_children):
        a = self.strategy_matrix
        b = value_vectors_from_children.T
        value_vector = np.einsum('ij,ij->i', a, b)
        return value_vector

    def get_opponent(self):
        opponent = list(set(self.state.players) - set([self.current_player]))[0]
        # print(opponent)
        return opponent
    
    def initialize_strategy_matrix(self, legal_actions):
        number_of_legal_actions = len(legal_actions)
        number_of_possible_hands = 1326
        # self.strategy_matrix = np.full((number_of_possible_hands, number_of_legal_actions), fill_value=1/number_of_legal_actions)
        self.strategy_matrix = np.random.rand(number_of_possible_hands, number_of_legal_actions)

    def update_ranges(self, player_ranges_for_action, action_index):
        player_ranges_for_action = dict(player_ranges_for_action)
        r_p = player_ranges_for_action[self.current_player]
        player_ranges_for_action[self.current_player] = self.bayesian_range_update(r_p, action_index, self.strategy_matrix)
        return player_ranges_for_action

    def bayesian_range_update(self, range, action_index, strategy_matrix):
        action_column = strategy_matrix[:, action_index]
        sum_of_action_column = np.sum(action_column)
        sum_of_all_actions = np.sum(strategy_matrix)
        p_of_action = sum_of_action_column / sum_of_all_actions

        range = action_column * range / p_of_action 

        return range

    

    # Consider possible actions
    # Contains strategy matrix
    pass

class EndNode(TreeNode):
    def get_value_vectors(self): 
        return np.random.rand(1326), np.random.rand(1326)
    # Showdown?
    # Fold or showdown parameter

class FoldNode(EndNode):

    pass

class NeuralNetNode(EndNode):
    pass

class ShowDownNode(EndNode):
    pass

class ChanceNode(TreeNode):

    def calculate_weighted_average(self, value_vectors_from_children):
        return np.mean(value_vectors_from_children, axis=0)
    pass    

    def update_ranges(self, player_ranges_for_action, action_index, card_to_range_indexes_to_zero):
        player_ranges_for_action = dict(player_ranges_for_action)
        cards, _ = self.child_nodes[action_index]
        for card in cards:
            indexes_to_zero = card_to_range_indexes_to_zero[str(card)]
            for player in player_ranges_for_action.keys():
                player_ranges_for_action[player][indexes_to_zero] = 0
            
        for player, range in player_ranges_for_action.items():
            player_ranges_for_action[player] = range / np.sum(range)

        return dict(player_ranges_for_action)


class Resolver():
    def __init__(self) -> None:
        self.monte_carlo = MonteCarlo()
    pass




class DeepStackResolver(Resolver):

    def generate_initial_range(self):
        n = 1326
        r = np.ones(n)
        r /= np.sum(r)
        return r

    def __init__(self) -> None:
        super().__init__()
        self.r_1 = self.generate_initial_range()
        self.r_2 = self.generate_initial_range()
        self.state_manager = StateManager()
        self.simulation_deck = DeckManager()
        self.card_to_range_indexes_to_zero = self.generate_card_to_range_indexes_to_zero_dict()

    def generate_card_to_range_indexes_to_zero_dict(self):
        all_hole_pairs = self.monte_carlo.get_all_possible_hole_pairs()

        card_to_range_indexes_to_zero = {}
        for card in self.simulation_deck.cards:
            card_str = str(card)
            card_to_range_indexes_to_zero[card_str] = []
            for i, card_pair in enumerate(all_hole_pairs):
                if card_str == card_pair[:2] or card_str == card_pair[2:]:
                    card_to_range_indexes_to_zero[card_str].append(i)

        assert len(card_to_range_indexes_to_zero.keys()) == 52
        for key, value in card_to_range_indexes_to_zero.items():
            assert len(value) == 51

        return card_to_range_indexes_to_zero

    def generate_subtree_from_node(self, node, number_of_allowed_bets, is_first_layer=False):
        if number_of_allowed_bets == 0 and isinstance(node, PlayerNode):
            # Now allowed actions will only be ['F', 'C'] or ['F', 'A']
            node.state.legal_actions = node.state.legal_actions[:2]

        if isinstance(node, PlayerNode):
            node.initialize_strategy_matrix(node.state.legal_actions)
        for action in node.state.legal_actions:
            # print(action, node)
            child_node = self.create_child_node(node, action, is_first_layer)
            node.child_nodes.append((action, child_node))
            if action == 'B':
                # print("Coming in here")
                self.generate_subtree_from_node(child_node, number_of_allowed_bets-1, False)
            else:
                self.generate_subtree_from_node(child_node, number_of_allowed_bets, False)
        # return node



    def generate_initial_subtree(self, state, player, number_of_allowed_bets):
        root = PlayerNode(player, state)
        state.set_legal_actions_from_player_node(root)
        self.generate_subtree_from_node(root, number_of_allowed_bets, True)
        return root
        # self.simulation_deck

    def get_next_state(self, node, action):
        node_types = {PlayerNode: 'player_node',
                      ChanceNode: 'chance_node',
                      FoldNode: 'end_node',
                      ShowDownNode: 'end_node',
                      NeuralNetNode: 'end_node'}
        
        node_type = node_types[type(node)]

        return self.state_manager.next_state(node, node_type, action)

    def get_current_stage(self, node):
        stages = {0: 'preflop',
                  3: 'flop',
                  4: 'turn',
                  5: 'river'}
        num_community_cards = len(node.state.community_cards)
        # print(num_community_cards)
        return stages[num_community_cards]
    
    def get_num_cards_to_deal_in_stage(self, node):
        stage = self.get_current_stage(node)

        cards = {'preflop': 3,
                 'flop': 1,
                 'turn': 1,
                 'river': 0}
        return cards[stage]

    def is_river_stage(self, node):
        return self.get_current_stage(node) == 'river'

    def create_player_node_with_swapped_current_player(self, node, next_state):
        next_current_player = node.get_opponent()
        next_node = PlayerNode(next_current_player, next_state)
        next_node.opponent = node.current_player
        return next_node

    def handle_previous_node_was_player_node(self, node, next_state, action, is_first_layer=False):
        if action == 'F':
            next_node = FoldNode(next_state)
        
        elif action == 'B' or action == 'C' and is_first_layer:
            next_node = self.create_player_node_with_swapped_current_player(node, next_state)
        
        elif action == 'C':
            # TODO: Change to fit neural network later
            next_node = self.end_or_chance_node(next_state, node)

        elif action == 'A':
            if self.other_player_should_make_move_after_all_in(next_state, node):
                next_node = self.create_player_node_with_swapped_current_player(node, next_state)
            else:
                next_node = self.end_or_chance_node(next_state, node)

        else:
            # current_bet = next_state.current_bet
            # player_chips, player_betted_chips = next_state.chips_per_player[node.current_player]

            # # Player has gone all-in. This is not a call-all-in
            # if player_betted_chips == current_bet:
            #     next_node = self.create_player_node_with_swapped_current_player(node, next_state)
            # else:
            next_node = ChanceNode(next_state)
        return next_node
    
    def other_player_should_make_move_after_all_in(self, next_state, node):
        all_in_amount = next_state.chips_per_player[node.current_player][1]
        opponent = node.get_opponent()
        opponent_chips, opponent_betted_chips = next_state.chips_per_player[opponent]

        return all_in_amount > opponent_betted_chips and not opponent_chips == 0

    def end_or_chance_node(self, next_state, node):
        if self.is_river_stage(node):
            return ShowDownNode(next_state)
        else:
            return ChanceNode(next_state)
    
    # Fold, Call, Bet, All-in
    # Fold, All-in
    # Fold, Call, All-in

    def choose_action(self, player, state): 
        resolver = self.resolve(state, player, self.r_1, self.r_2, 3)
        # TODO: return action

    def handle_previous_node_was_chance_node(self, node, next_state, action):
        next_node = NeuralNetNode(next_state)
        return next_node

    def create_child_node(self, node, action, is_first_layer):
        next_state = self.get_next_state(node, action)
        if isinstance(node, PlayerNode):
            next_node = self.handle_previous_node_was_player_node(node, next_state, action, is_first_layer)
        elif isinstance(node, ChanceNode):
            next_node = self.handle_previous_node_was_chance_node(node, next_state, action)
        
        if isinstance(next_node, PlayerNode):
            next_state.set_legal_actions_from_player_node(next_node)
        elif isinstance(next_node, ChanceNode):
            num_cards_to_deal = self.get_num_cards_to_deal_in_stage(next_node)
            next_state.set_legal_actions_from_chance_node(next_node, self.simulation_deck, num_cards_to_deal)
        
        next_node.state = next_state
        return next_node

    def subtree_traversal_rollout(self, node, player_ranges):
        if isinstance(node, EndNode):
            return node.get_value_vectors()
        
        player_1_value_vectors = []
        player_2_value_vectors = []
        for action_index, (action, child_node) in enumerate(node.child_nodes):
            # chance node has its own way of updating range, player node updates with Bayesian Update
            if isinstance(node, PlayerNode):
                player_ranges_for_action = node.update_ranges(player_ranges, action_index)
            elif isinstance(node, ChanceNode):
                player_ranges_for_action = node.update_ranges(player_ranges, action_index, self.card_to_range_indexes_to_zero)
            else:
                raise ValueError('Somthing went wrong')
            v_1, v_2 = self.subtree_traversal_rollout(child_node, player_ranges_for_action)
            player_1_value_vectors.append(v_1)
            player_2_value_vectors.append(v_2)
        player_1_value_vectors = np.array(player_1_value_vectors)
        player_2_value_vectors = np.array(player_2_value_vectors)
        
        player_1_values = node.calculate_weighted_average(player_1_value_vectors)
        player_2_values = node.calculate_weighted_average(player_2_value_vectors)

        return player_1_values, player_2_values

    def update_strategy(self, node):
        pass

    def resolve(self, s, player, r_1, r_2, t): 
        # s = state, r_1 = range of player 1, r_2 = range of player 2, T = number of rollouts
        root = self.generate_initial_subtree(s, player, piv.number_of_allowed_bets_resolver)
        
        opponent = root.get_opponent()
        player_ranges = {
            root.current_player: r_1,
            opponent: r_2,
        }
        for t in range(piv.number_of_rollouts):
            v_1, v_2 = self.subtree_traversal_rollout(root, player_ranges)
            self.update_strategy(root)



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


    # from game_manager.player import AIPlayer
    from state_manager.state_manager import State
    from game_manager.game_manager import RoundManager
    from game_manager.game_manager import GameManager
    # player = AIPlayer()
    # player.chips = 20
    # player.betted_chips = 0
    # resolver = PureRolloutResolver()
    game_manager = GameManager()
    round_manager = RoundManager(game_manager)
    state = State(round_manager)
    # state.remaining_players = 2
    # state.pot_size_if_all_remaining_players_bets = 40
    # state.pot_size_if_all_remaining_players_calls = 20
    # # state.
    # actions = ['C', 'B', 'F', 'A']
    # win_probabilities = [i/10 for i in range(0, 11)]
    # for win_probability in win_probabilities:
    #     all_expected = []
    #     for action in actions:
    #         all_expected.append((win_probability, action, resolver.expected_utility(
    #             player, action, state, win_probability)))
    #     expected_utility_sorted = sorted(
    #         all_expected, key=lambda x: x[2], reverse=True)
    #     print(expected_utility_sorted)
