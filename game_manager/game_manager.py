from deck_manager import DeckManager


class RoundManager:
    def __init__(self, game_manager) -> None:
        self.deck_manager = DeckManager()
        self.game_manager = game_manager


class GameManager:
    players = []

    def __init__(self) -> None:
        pass

    def play_game(self):
        game = 1
        while game:
            round_manager = RoundManager(self)
    pass


class TexasHoldemGameManager(GameManager):
    pass
