from typing import List
from .player import Player, HumanPlayer, AIPlayer
from .rules_manager.rules_manager import RuleManager
from .deck_manager import DeckManager, Card
from .user_interface import UserInterface
from .pivotal_parameters import pivotal_parameters as piv


class RoundManager:
    """
    Keeps track of one round of play. Abstract class. It needs to be inherited by type of poker.

    Keeps track of pot, current call and stages of the round.
    """

    def __init__(self, game_manager: 'GameManager') -> None:
        self.deck_manager = DeckManager()
        self.game_manager = game_manager
        self.community_cards = []
        self.burnt_cards = []
        self.starting_player_index = 0
        self.initialize_round()

    def initialize_round(self):
        self.current_bet = 0

        self.collect_cards()
        self.deck_manager.shuffle_cards()

    def collect_cards(self):
        collected_cards = self.community_cards
        self.community_cards = []

        collected_cards = collected_cards + self.burnt_cards
        self.burnt_cards = []

        for player in self.game_manager.players:
            collected_cards = collected_cards + player.hand_over_cards()

        self.deck_manager.receive_cards(collected_cards)

    def burn_card(self):
        self.burnt_cards.append(self.deck_manager.get_n_cards(1))

    def deal_community_cards(self, number_of_community_cards):
        cards = self.deck_manager.get_n_cards(number_of_community_cards)
        self.community_cards = self.community_cards + cards

    def deal_hole_cards(self, number_of_cards_per_player):
        cards = []
        for player in self.game_manager.players:
            cards = self.deck_manager.get_n_cards(number_of_cards_per_player)
            player.receive_cards(cards)

    def remaining_players(self):
        return list(filter(lambda player: not player.is_folded, self.game_manager.players))

    def round_of_actions(self):
        # a round continues until everyone have had a turn, and everyone have bet the same amount (or all in)
        current_player_index = self.starting_player_index
        number_of_actions = 0
        while not self.round_is_over(number_of_actions):
            player = self.game_manager.players[current_player_index]
            if not player.is_folded and not player.chips == 0:
                self.game_manager.user_interface.display_state(
                    self.game_manager.players, self.community_cards, current_player_index)
                # this is where the action from a player is requested and performed
                action = player.action(self.get_possible_actions(player))
                action_bet, update_starting_index = self.game_manager.action_manager.perform_action(
                    player, action, self.current_bet)
                if action_bet > self.current_bet:
                    self.current_bet = action_bet
                if update_starting_index:
                    self.starting_player_index = current_player_index
            current_player_index = current_player_index + 1
            if current_player_index == len(self.game_manager.players):
                current_player_index = 0
            number_of_actions = number_of_actions + 1

    def round_is_over(self, number_of_actions):
        if number_of_actions < len(self.game_manager.players):
            return False

        for player in self.remaining_players():
            if player.chips == 0:
                continue
            elif player.betted_chips < self.current_bet:
                return False
        return True

    def set_starting_player_index(self):
        # TODO: set accurate starting player index
        self.starting_player_index = self.starting_player_index + 1
        if self.starting_player_index == len(self.game_manager.players):
            self.starting_player_index = 0

    def get_possible_actions(self, player):
        # TODO: calculate possible actions
        
        return self.game_manager.action_manager.get_possible_actions(player, self.current_bet)

    def reset_round_manager(self):
        self.current_bet = 0

    def total_pot(self):
        total_pot = sum(player.betted_chips for player in self.game_manager.players)
        return total_pot


class ActionManager():
    POSSIBLE_ACTIONS = [
        'CHECK/CALL',
        'FOLD',
        'BET/RAISE',
        'ALL-IN'
    ]

    def __init__(self):
        pass

    def get_possible_actions(self, player, current_bet: int = 0, big_blind: int = 2):
        possible_actions = []
        if player.chips + player.betted_chips > current_bet:
            possible_actions.append('CHECK/CALL')
        if player.chips + player.betted_chips > current_bet + big_blind:
            possible_actions.append('BET/RAISE')
        possible_actions = possible_actions + ['FOLD', 'ALL-IN']

        return possible_actions

    def perform_action(self, player: Player, action: str, current_bet: int = 0, big_blind: int = 2):
        if not action in self.POSSIBLE_ACTIONS:
            raise ValueError

        update_starting_index = False
        if action == 'FOLD':
            player.fold()
        if action == 'CHECK/CALL':
            player.check_or_call(current_bet)
        if action == 'BET/RAISE':
            current_bet = player.bet_or_raise(current_bet, big_blind)
            update_starting_index = True
        if action == 'ALL-IN':
            if player.chips + player.betted_chips > current_bet:
                update_starting_index = True
            current_bet = player.all_in()

        return current_bet, update_starting_index


class TexasHoldemRoundManager(RoundManager):
    def __init__(self, game_manager) -> None:
        super().__init__(game_manager)

    def play_preflop(self):
        super().deal_hole_cards(2)
        self.round_of_actions()

    def play_flop(self):
        super().deal_community_cards(3)
        self.round_of_actions()

    def play_turn_river(self):
        super().deal_community_cards(1)
        self.round_of_actions()

    def play_round(self):
        super().initialize_round()

        self.play_preflop()
        self.play_flop()
        self.play_turn_river()
        self.play_turn_river()

        self.finalize_round()

        self.set_starting_player_index()

    def finalize_round(self):
        # show cards

        winners = self.game_manager.rule_manager.get_winner(self.remaining_players(), self.community_cards)
        self.game_manager.user_interface.round_over(self.game_manager.players, self.community_cards, winners)
        total_pot = self.total_pot()
        for player in winners:
            player.receive_chips(total_pot /     len(winners))
        
        for player in self.game_manager.players:
            player.round_ended()





class GameManager:
    """
    General for every types of rounds. Keeps track of players at the table.
    Starts and ends each round.
    """
    players = []

    def __init__(self) -> None:
        self.create_players()
        self.set_round_manager()
        self.set_rule_manager()
        self.set_user_interface()
        self.set_action_manager()

    def set_rule_manager(self):
        self.rule_manager = RuleManager()

    def set_user_interface(self):
        self.user_interface = UserInterface()

    def set_action_manager(self):
        self.action_manager = ActionManager()

    def create_players(self):
        self.players = [HumanPlayer()
                        for _ in range(piv.number_of_human_players)]
        self.players += [AIPlayer() for _ in range(piv.number_of_AI_players)]

    def set_round_manager(self):
        if piv.game == 'texasHoldem':
            self.round_manager = TexasHoldemRoundManager(self)
        else:
            self.round_manager = TexasHoldemRoundManager(self)

    def game_over(self):
        return len(list(filter(lambda player:player.chips > 0, self.players))) == 1

    def play_game(self):
        while not self.game_over():
            self.round_manager.play_round()
    pass


if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.play_game()
