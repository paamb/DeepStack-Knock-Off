from game_manager.pivotal_parameters import pivotal_parameters as piv

class State:
    # def __init__(self):

    def set_state_from_round_manager(self, round_manager):
        self.legal_actions = ['F', 'C', 'B', 'A']
        self.community_cards = round_manager.community_cards
        self.pot = sum(
            player.betted_chips for player in round_manager.game_manager.players)

        # Has to be two players in Deepstack 
        self.players = round_manager.game_manager.players
        
        # Number of remaining chips for each player and number of betted chips for each player
        self.chips_per_player = {player: (player.chips, player.betted_chips) for player in round_manager.game_manager.players}
        
        # The most amount of money a player has put into the pot
        self.current_bet = round_manager.current_bet
        # self.remaining_players = round_manager.remaining_players()
        # self.players = round_manager.game_manager.players
        self.num_remaining_players = round_manager.num_remaining_players()
        self.pot_size_if_all_remaining_players_calls = round_manager.get_pot_size_if_all_remaining_players_calls()
        self.pot_size_if_all_remaining_players_bets = round_manager.get_pot_size_if_all_remaining_players_bets()

    def set_state_from_previous_state(self, previous_state):
        # new_community_cards = list(previous_state.community_cards)
        # print(new_community_cards)
        self.community_cards = list(previous_state.community_cards)
        self.pot = previous_state.pot
        self.chips_per_player = dict(previous_state.chips_per_player)
        self.current_bet = previous_state.current_bet
        self.legal_actions = []
        self.players = previous_state.players

        self.num_remaining_players = previous_state.num_remaining_players
        self.pot_size_if_all_remaining_players_calls = previous_state.pot_size_if_all_remaining_players_calls
        self.pot_size_if_all_remaining_players_bets = previous_state.pot_size_if_all_remaining_players_bets

        # print("Community_cards", self.community_cards)

    def update_state_player_node(self):

        # self.pot += value
        pass

    def update_state_chance_node(self):
        pass


    def player_calls(self, player):
        player_chips, player_betted_chips = self.chips_per_player[player]
        call_amount = self.current_bet - player_betted_chips
        assert player_chips > call_amount

        new_player_chips = player_chips - call_amount
        new_betted_chips = self.current_bet

        self.chips_per_player[player] = (new_player_chips, new_betted_chips)

        self.add_money_to_pot(call_amount)

    def player_bets(self, player):
        player_chips, player_betted_chips = self.chips_per_player[player]
        call_amount = self.current_bet - player_betted_chips
        bet_amount = call_amount + 2*piv.small_blind
        
        assert player_chips > bet_amount

        new_player_chips = player_chips - bet_amount
        new_betted_chips = player_betted_chips + bet_amount

        self.chips_per_player[player] = (new_player_chips, new_betted_chips)

        self.add_money_to_pot(bet_amount)
        self.set_current_bet(new_betted_chips)
    
    def player_all_in(self, player):
        player_chips, player_betted_chips = self.chips_per_player[player]
        new_betted_chips = player_betted_chips + player_chips
        new_player_chips = 0
        self.chips_per_player[player] = (new_player_chips, new_betted_chips)
        self.add_money_to_pot(player_chips)
        self.set_current_bet(new_betted_chips)

    # def set_player_legal_actions(self, player): 
    #     player_chips, player_betted_chips = self.chips_per_player[player]
    #     updated_legal_actions = ['F']
    #     if 

    def set_legal_actions_from_player_node(self, node):
        current_player = node.current_player
        player_chips, player_betted_chips = self.chips_per_player[current_player]
        call_amount = self.current_bet - player_betted_chips

        if player_chips > call_amount + 2*piv.small_blind:
            self.legal_actions = ['F', 'C', 'B', 'A']
        elif call_amount + 2*piv.small_blind >= player_chips and player_chips > call_amount:
            self.legal_actions = ['F', 'C', 'A']
        else:
            self.legal_actions = ['F', 'A']

    def set_legal_actions_from_chance_node(self, node, simulation_deck, n_cards, num_chance_node_children = piv.number_of_chance_node_children):
        self.legal_actions = [simulation_deck.get_n_cards_not_in_invalid_cards(self.community_cards, n_cards) for _ in range(num_chance_node_children)]

    def set_current_bet(self, new_betted_chips):
        self.current_bet = max(new_betted_chips, self.current_bet)

    def add_money_to_pot(self, money_to_add):
        self.pot += money_to_add

    def get_amount_to_call(self, player):
        return self.current_bet - self.chips_per_player[player][1]
    def get_amount_to_bet(self, player):
        return self.get_amount_to_call(player) + 2 * piv.small_blind


class StateManager:

    def get_state(self, round_manager):
        state = State()
        state.set_state_from_round_manager(round_manager)
        return state

    def next_state_after_chance_node(self, next_state, action):
        next_state.community_cards += action

    def next_state_after_player_node(self, player, next_state, previous_state, action):
        if action == 'F':
            next_state.legal_actions = []
        elif action == 'C':
            next_state.player_calls(player)
        elif action == 'B':
            next_state.player_bets(player)
        else:
            next_state.player_all_in(player)
        return next_state

        
        pass

    def next_state_after_end_node(self):
        pass

    def next_state(self, node, node_type, action=None):
        previous_state = node.state
        next_state = State()
        next_state.set_state_from_previous_state(previous_state)
        if node_type == 'chance_node':
            # print("Coming in here")
            self.next_state_after_chance_node(next_state, action)
        elif node_type == 'player_node':
            self.next_state_after_player_node(node.current_player, next_state, previous_state, action)
        # End node. Not coming in here
        else: 
            # print("End node")
            self.next_state_after_end_node()
        
        return next_state
            
