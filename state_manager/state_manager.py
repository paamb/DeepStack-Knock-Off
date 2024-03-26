class State:
    def __init__(self, round_manager):
        self.update_state(round_manager)
        self.possible_actions = ['F', 'C', 'B', 'A']

    def update_state(self, round_manager):
        self.community_cards = round_manager.community_cards
        self.pot = sum(
            player.betted_chips for player in round_manager.game_manager.players)
        self.players = round_manager.game_manager.players
        self.active_players = self.get_active_players()
        self.num_active_players = self.get_num_active_players()
        self.current_bet = round_manager.current_bet

    def get_active_players(self):
        return [player for player in self.players if not player.is_folded]

    def get_num_active_players(self):
        return len(self.get_active_players())


class StateManager:

    def get_state(self, round_manager):
        return State(round_manager)
