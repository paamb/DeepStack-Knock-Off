import numpy as np
from poker_oracle.monte_carlo import MonteCarlo

from game_manager.pivotal_parameters import pivotal_parameters as piv
from state_manager.state_manager import StateManager
from game_manager.deck_manager import DeckManager


NUM_HOLE_PAIRS = 1326

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
        number_of_possible_hands = 1326
        self.strategy_matrix = np.full((number_of_possible_hands, number_of_legal_actions), fill_value=1/number_of_legal_actions)
        # self.strategy_matrix = np.random.rand(number_of_possible_hands, number_of_legal_actions)

    def update_ranges(self, player_ranges_for_action, action_index):
        # player_ranges_for_action = dict(player_ranges_for_action)
        new_player_ranges_for_action = {key: value.copy() for key, value in player_ranges_for_action.items()}
        r_p = new_player_ranges_for_action[self.current_player]
        new_player_ranges_for_action[self.current_player] = self.bayesian_range_update(r_p, action_index, self.strategy_matrix)
        return new_player_ranges_for_action

    def print_player_ranges(self, range_1):
        hole_pairs = MonteCarlo().get_all_possible_hole_pairs()
        # community_cards = node.state.community_cards
        # r_1 = player_ranges[node.current_player]
        # opponent = node.get_opponent()
        # r_2 = player_ranges[opponent]
        with open('ranges_in_bayesian_update_output.txt', 'w') as file:
            # file.write(community_cards)
            # for card in community_cards:
            #     file.write(str(card))
            file.write("Hole pair | r_1 | r_2 \n")
            for i in range(len(hole_pairs)):
                file.write(f"{hole_pairs[i]} | {range_1[i]} \n")

    def bayesian_range_update(self, range, action_index, strategy_matrix):
        # print(action_index)
        action_column = strategy_matrix[:, action_index]
        sum_of_action_column = np.sum(action_column)
        sum_of_all_actions = np.sum(strategy_matrix)
        print("Bayesian update: ", sum_of_action_column, sum_of_all_actions, sum_of_action_column/sum_of_all_actions)
        p_of_action = sum_of_action_column / sum_of_all_actions

        range = action_column * range / p_of_action 
        self.print_player_ranges(range)
        return range

    

    # Consider possible actions
    # Contains strategy matrix
    pass

class EndNode(TreeNode):
    def get_value_vectors(self, node, player_ranges): 
        opponent = node.get_opponent()

        value_vectors = {
            node.current_player: np.random.rand(1326),
            opponent: np.random.rand(1326)
        }
        return value_vectors
    # Showdown?
    # Fold or showdown parameter

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
        # players = list(player_ranges_for_action.keys())

        new_player_ranges_for_action = {key: value.copy() for key, value in player_ranges_for_action.items()}
        # new_player_ranges_for_action = {
        #     player[0] = player_ranges_for_action[players[0]].copy(),
        # }
        # print(players[0])

        # new_r_1 = player_ranges_for_action[players[0]].copy()
        # print(type(new_player_ranges_for_action[player_ranges_for_action.keys()[0]]))
        # new_r_1 = list([])
        cards, _ = self.child_nodes[action_index]
        for card in cards:
            indexes_to_zero = card_to_range_indexes_to_zero[str(card)]
            for player in new_player_ranges_for_action.keys():
                new_player_ranges_for_action[player][indexes_to_zero] = 0
            
        for player, range in new_player_ranges_for_action.items():
            new_player_ranges_for_action[player] = range / np.sum(range)

        return new_player_ranges_for_action


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

    # def initialize_player_range_dictionary(self, root):
    #     r_1 = self.generate_initial_range()
    #     r_2 = self.generate_initial_range()
    #     player_ranges = {
    #         root.current_player: r_1,
    #         opponent: r_2,
    #     }

    def __init__(self) -> None:
        from poker_oracle.utility_matrix import UtilityMatrixHandler
        super().__init__()
        self.r_1 = self.generate_initial_range()
        self.r_2 = self.generate_initial_range()
        self.state_manager = StateManager()
        self.simulation_deck = DeckManager()
        self.utility_matrix_handler = UtilityMatrixHandler()
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
            next_node = FoldNode(node.current_player, next_state)
        
        elif action == 'B' or action == 'C' and is_first_layer:
            next_node = self.create_player_node_with_swapped_current_player(node, next_state)
        
        elif action == 'C':
            # TODO: Change to fit neural network later
            next_node = self.end_or_chance_node(next_state, node, self.utility_matrix_handler)

        elif action == 'A':
            if self.other_player_should_make_move_after_all_in(next_state, node):
                next_node = self.create_player_node_with_swapped_current_player(node, next_state)
            else:
                next_node = self.end_or_chance_node(next_state, node, self.utility_matrix_handler)

        else:
            raise ValueError("Illegal action")
        return next_node
    
    def other_player_should_make_move_after_all_in(self, next_state, node):
        all_in_amount = next_state.chips_per_player[node.current_player][1]
        opponent = node.get_opponent()
        opponent_chips, opponent_betted_chips = next_state.chips_per_player[opponent]

        return all_in_amount > opponent_betted_chips and not opponent_chips == 0

    def end_or_chance_node(self, next_state, node, utility_matrix_handler):
        if self.is_river_stage(node):
            return ShowDownNode(node.current_player, next_state, utility_matrix_handler)
        else:
            return ChanceNode(node.current_player, next_state)
    
    # Fold, Call, Bet, All-in
    # Fold, All-in
    # Fold, Call, All-in



    def handle_previous_node_was_chance_node(self, node, next_state, action):
        next_node = NeuralNetNode(node.current_player, next_state)
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

    def print_player_ranges(self, player_ranges, node):
        hole_pairs = MonteCarlo().get_all_possible_hole_pairs()
        community_cards = node.state.community_cards
        r_1 = player_ranges[node.current_player]
        opponent = node.get_opponent()
        r_2 = player_ranges[opponent]
        with open('ranges_output.txt', 'w') as file:
            # file.write(community_cards)
            for card in community_cards:
                file.write(str(card))
            file.write("Hole pair | r_1 | r_2 \n")
            for i in range(len(hole_pairs)):
                file.write(f"{hole_pairs[i]} | {r_1[i]} | {r_2[i]} \n")

    def subtree_traversal_rollout(self, node, player_ranges):
        if isinstance(node, EndNode):
            # self.print_player_ranges(player_ranges, node)
            # input()
            node_value_vectors = node.get_value_vectors(node, player_ranges)
            # node.node_value_vectors = node_value_vectors
            new_node_value_vectors = {key: value.copy() for key, value in node_value_vectors.items()}
            node.node_value_vectors = new_node_value_vectors

            opponent = node.get_opponent()
            self.print_value_vectors(new_node_value_vectors[node.current_player], new_node_value_vectors[opponent], node.state.community_cards)
            input("New node value vector")
            return node_value_vectors
        
        # new_value_vectors stores all the values returned from each subnode/action. the value in the dictionary is a list of values returned from subnodes
        # this is used for calculating the weighted average when all the subnodes have returned their values.
        opponent = node.get_opponent()
        all_subnodes_value_vectors = {
            node.current_player: [],
            opponent: []
        }

        # looping over all actions from node, to perform recursive call.
        # For us, a chance-event is handled the same way as an action.
        for action_index, (action, child_node) in enumerate(node.child_nodes):

            # chance node has its own way of updating range, player node updates with Bayesian Update
            if isinstance(node, PlayerNode):
                player_ranges_for_action = node.update_ranges(player_ranges, action_index)
            elif isinstance(node, ChanceNode):
                player_ranges_for_action = node.update_ranges(player_ranges, action_index, self.card_to_range_indexes_to_zero)
            else:
                raise ValueError('Somthing went wrong')
            
            # recursive call
            # collects values in a dictionary all_subnodes_value_vectors
            subnode_value_vectors = self.subtree_traversal_rollout(child_node, player_ranges_for_action)
            for player in subnode_value_vectors.keys():
                all_subnodes_value_vectors[player].append(subnode_value_vectors[player])
        
        # taking the weighted average of the values returned from subnodes.
        # for a player-node, the strategy is used as a weight.
        # for a chance-node, the weights are completely even, meaning it is a normal average.
        node_value_vectors = {}
        for player, subnode_values in all_subnodes_value_vectors.items():
            node_value_vectors[player] = node.calculate_weighted_average(np.array(subnode_values))
            
        # Set this to be used when calculating regret
        node.node_value_vectors = {key: value.copy() for key, value in node_value_vectors.items()}

        # new_node_value_vectors = {key: value.copy() for key, value in player_ranges_for_action.items()}
        # node.node_value_vectors = new_node_value_vectors
        return node_value_vectors

    def initial_player_range_update(self, player_ranges, already_dealt_cards):
        # player_ranges = dict(player_ranges)
        new_player_ranges = {key: value.copy() for key, value in player_ranges.items()}
        cards_string = [str(card) for card in already_dealt_cards]
        for card in cards_string:
            indexes_to_zero = self.card_to_range_indexes_to_zero[str(card)]
            for player in new_player_ranges.keys():
                new_player_ranges[player][indexes_to_zero] = 0
            
        for player, range in new_player_ranges.items():
            new_player_ranges[player] /= np.sum(range)

        return new_player_ranges


    def get_action_from_strategy(self, player, mean_strategy, state):
        player_hand_to_string = player.get_player_hand_as_string()
        # print("Playerhand", player_hand_to_string)
        hole_pair_index = self.monte_carlo.get_hole_pair_index_in_all_possible_hole_pairs_list(player_hand_to_string)
        # print("Hole pair index", hole_pair_index)
        strategy_given_hole_pair = mean_strategy[hole_pair_index]
        print("Strategy_give_hole_pair", strategy_given_hole_pair)
        input()
        # print("Strategy given hole", strategy_given_hole_pair)
        index_of_best_action = np.argmax(strategy_given_hole_pair)
        # print("Index_of_action: ", index_of_best_action, state.legal_actions)
        best_action = state.legal_actions[index_of_best_action]
        return best_action, index_of_best_action

    def print_strategy_matrix(self, community_cards, strategy_matrix):
        # hole_pairs = MonteCarlo().get_all_possible_hole_pairs()
        hole_pairs = MonteCarlo().get_all_possible_hole_pairs()
        
        with open('strategy_output.txt', 'w') as file:
            # file.write(community_cards)
            for card in community_cards:
                file.write(str(card))
            file.write("Hole pair | Strategy\n")
            for i in range(len(hole_pairs)):
                file.write(f"{hole_pairs[i]} | {strategy_matrix[i]}\n")
        # print("Hole pair | Stategy")
        # for i in range(len(hole_pairs)):
        #     print(hole_pairs[i], strategy_matrix[i])


    def update_strategy(self, node, root_node):
        for action, child_node in node.child_nodes:
            self.update_strategy(child_node, False)
        
        if isinstance(node, PlayerNode):
            all_regrets = []
            for action, child_node in node.child_nodes:
                if root_node:
                    print("Action: ", action, "Node value vector: ", child_node.node_value_vectors[node.current_player])
                regret = child_node.node_value_vectors[node.current_player] - node.node_value_vectors[node.current_player]
                # Sets every negative element to 0
                positive_regret = np.maximum(regret, 0)
                all_regrets.append(positive_regret)

            all_regrets = np.array(all_regrets)

            normalizer = np.sum(all_regrets, axis=0)
            new_strategy = node.strategy_matrix.copy()
            # print("Normalizer", normalizer)
            # print("All regrets shape", all_regrets.shape)
            # print("New strategy", new_strategy.shape)
            # print("All regrets", all_regrets)
            if root_node:
                print("Normalizer", normalizer)
                print("All regrets shape", all_regrets.shape)
                print("New strategy", new_strategy.shape)
                print("All regrets", all_regrets)
            for i in range(len(node.state.legal_actions)):
                for j in range(NUM_HOLE_PAIRS):
                    if normalizer[j] == 0:
                        continue
                    new_strategy[j, i] = all_regrets[i][j] / normalizer[j]
                    # new_strategy[j, i] /= normalizer[j]
            
            if root_node:
                print("New Strategy", new_strategy)
            node.strategy_matrix = new_strategy
            
            return node.strategy_matrix    


                


    def print_value_vectors(self, v_1, v_2, community_cards):
        hole_pairs = MonteCarlo().get_all_possible_hole_pairs()
        
        with open('value_vector_output.txt', 'w') as file:
            # file.write(community_cards)
            sum_v1 = np.sum(v_1)
            sum_v2 = np.sum(v_2)
            file.write(f"Sums: {sum_v1}, {sum_v2} \n", )
            for card in community_cards:
                file.write(str(card))
            file.write("Hole pair | V_1 | V_2\n")
            for i in range(len(hole_pairs)):
                file.write(f"{hole_pairs[i]} | {v_1[i]} | {v_2[i]} \n")


    def resolve(self, s, player, r_1, r_2, num_rollouts): 
        # s = state, r_1 = range of player 1, r_2 = range of player 2, T = number of rollouts
        root = self.generate_initial_subtree(s, player, piv.number_of_allowed_bets_resolver)
        
        opponent = root.get_opponent()
        player_ranges = {
            root.current_player: r_1,
            opponent: r_2,
        }

        all_strategies = []
        for t in range(1):
            player_ranges = self.initial_player_range_update(player_ranges, root.state.community_cards)
            node_value_vectors = self.subtree_traversal_rollout(root, player_ranges)
            strategy_t = self.update_strategy(root, True)
            all_strategies.append(strategy_t)
        


        all_strategies = np.array(all_strategies)
        
        last_strategy = all_strategies[-1]
        print("Lenght: ", len(all_strategies))
        if len(root.state.community_cards) == 5:
            self.print_strategy_matrix(root.state.community_cards, last_strategy)
            self.print_value_vectors(node_value_vectors[root.current_player], node_value_vectors[opponent], root.state.community_cards)
        # print(last_strategy)

        # ones = 0
        # zeros = 0
        # point = 0
        # for i in range(len(last_strategy)):
        #     if last_strategy[i][-1] == 1:
        #         print(last_strategy[i])
        #         hole_pairs = MonteCarlo().get_all_possible_hole_pairs()
        #         print(hole_pairs[i])
        #         ones += 1
        #     elif last_strategy[i][-1] == 0: 
        #         zeros += 1 
        #     elif last_strategy[i][-1] == 0.25:
        #         point += 1 
        # print("Counters", ones, zeros, point, ones+zeros+point)
        # hole_pairs = MonteCarlo().get_all_possible_hole_pairs()
        # print(hole_pairs)
        # print(MonteCarlo().get_all_possible_hole_pairs())
            # for j in range(len(last_stra
            #tegy[0])):
        # mean_strategy = np.mean(all_strategies, axis=0)
        # mean_strategy = all_strategies[]
        player_action, action_index = self.get_action_from_strategy(player, last_strategy, root.state) 
        r_1_given_action = root.bayesian_range_update(player_ranges[root.current_player], action_index, last_strategy)
        print("Chosen action: ", player_action)
        print("R1", r_1_given_action)
        input()
        return 'C', r_1_given_action, r_2

    def choose_action(self, player, state): 
        player_action, updated_r_1, r_2 = self.resolve(state, player, self.r_1, self.r_2, 20)
        # print(updated_r_1)
        # input()
        return player_action


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
