class State:
    def __init__(self, round_manager):
        self.update_state(round_manager)

    def update_state(self, round_manager):
        self.community_cards = round_manager.community_cards
        self.pot = sum(player.betted_chips for player in round_manager.game_manager.players)
        self.players = round_manager.game_manager.players
        self.current_bet = round_manager.current_bet

class StateManager:

    def get_state(self, round_manager):
        return State(round_manager)