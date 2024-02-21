from typing import List
from player import Player, HumanPlayer, AIPlayer
from deck_manager import DeckManager
import pivotal_parameters as piv


class RoundManager:
    """
    Keeps track of one round of play. Abstract class. It needs to be inherited by type of poker.

    Keeps track of pot, current call and stages of the round.
    """

    def __init__(self, game_manager) -> None:
        self.deck_manager = DeckManager()
        self.game_manager = game_manager
        self.burnt_cards = []

    def initialize_round(self):
        self.deck_manager.shuffle_cards()
        pass

    def burn_card(self):
        self.burnt_cards.append(self.deck_manager.get_n_cards(1))

    def deal_hole_cards(self, number_of_cards_per_player):
        cards = []
        for player in self.game_manager.players:
            cards = self.deck_manager.get_n_cards(number_of_cards_per_player)
            print("Player", player)
            print("cards: ", cards)
            player.recieve_cards(cards)
            print("Player cards", player.hand)

    pass


class TexasHoldemRoundManager(RoundManager):
    def __init__(self, game_manager) -> None:
        super().__init__(game_manager)

    def play_preflop(self):
        super().deal_hole_cards(2)

    def play_flop(self):
        pass

    def play_turn_river(self):
        pass

    def play_round(self):
        super().initialize_round()

        self.play_preflop()
        self.play_flop()
        self.play_turn_river()
        self.play_turn_river()


class GameManager:
    """
    General for every types of rounds. Keeps track of players at the table.
    Starts and ends each round.
    """
    players = []

    def __init__(self) -> None:
        self.create_players()
        self.set_round_manager()

    def create_players(self):
        self.players = [HumanPlayer()
                        for _ in range(piv.number_of_human_players)]
        self.players += [AIPlayer() for _ in range(piv.number_of_AI_players)]

    def set_round_manager(self):
        if piv.game == 'texasHoldem':
            self.round_manager = TexasHoldemRoundManager(self)
        else:
            self.round_manager = TexasHoldemRoundManager(self)

    def play_game(self):
        game = 1
        while game:
            self.round_manager.play_round()
            game = 0
    pass


if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.play_game()
    print(game_manager.players)
