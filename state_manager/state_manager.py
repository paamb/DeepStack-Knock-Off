class State:
    def __init__(self, round_manager):
        self.round_manager = round_manager
        self.update_state()
        self.possible_actions = ['F', 'C', 'B', 'A']

    def update_state(self):
        self.community_cards = self.round_manager.community_cards
        self.pot = sum(
            player.betted_chips for player in self.round_manager.game_manager.players)
        self.players = self.round_manager.game_manager.players
        self.remaining_players = self.round_manager.remaining_players()
        self.num_remaining_players = self.round_manager.num_remaining_players()
        self.pot_size_if_all_remaining_players_calls = self.round_manager.get_pot_size_if_all_remaining_players_calls()
        self.pot_size_if_all_remaining_players_bets = self.round_manager.get_pot_size_if_all_remaining_players_bets()

    def get_amount_to_call(self, player):
        return self.round_manager.get_amount_to_call(player)

    def get_amount_to_bet(self, player):
        return self.round_manager.get_amount_to_bet(player)


class StateManager:

    def get_state(self, round_manager):
        return State(round_manager)
