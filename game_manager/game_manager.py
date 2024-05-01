from typing import List
from game_manager.player import Player, HumanPlayer, AIPlayer
from poker_oracle.hands_evaluator.hands_evaluator import HandsEvaluator
from state_manager.state_manager import StateManager, State
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
        self.state_manager = StateManager()
        self.community_cards = []
        self.burnt_cards = []
        self.starting_player_index = 0
        self.initialize_round()

    def initialize_round(self):
        # Initialized for each new round
        self.current_bet = 2 * piv.small_blind

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
            if player.chips == 0:
                continue
            cards = self.deck_manager.get_n_cards(number_of_cards_per_player)
            player.receive_cards(cards)

    def remaining_players(self):
        return [player for player in self.game_manager.players if not player.is_folded]

    def num_remaining_players(self):
        return len(self.remaining_players())

    def players_with_betted_chips(self):
        return list(filter(lambda player: player.betted_chips > 0, self.game_manager.players))

    def display_possible_actions(self, player):
        possible_actions = self.get_possible_actions(player)
        self.game_manager.user_interface.display_possible_actions(
            player, possible_actions, self.current_bet, piv.small_blind * 2)
        
    def get_and_perform_action(self, player):
        state = self.state_manager.get_state(self)
        action = player.action(state)
        action_bet, update_starting_index = self.game_manager.action_manager.perform_action(
            player, action, self.current_bet)
        return action_bet, update_starting_index

    def play_player_round(self, player):
        
        # this is where the action from a player is requested and performed
        self.display_possible_actions(player)
        action_bet, update_starting_index = self.get_and_perform_action(player)

        if action_bet > self.current_bet:
            self.current_bet = action_bet
        return update_starting_index
    
    def increment_current_player_index_and_number_of_actions(self, current_player_index, number_of_actions):
        current_player_index = current_player_index + 1
        if current_player_index == len(self.game_manager.players):
            current_player_index = 0
        number_of_actions = number_of_actions + 1
        return current_player_index, number_of_actions

    def round_of_actions(self):
        # a round continues until everyone have had a turn, and everyone have bet the same amount (or all in)
        current_player_index = self.starting_player_index
        number_of_actions = 0
        while not self.round_is_over(number_of_actions):
            player = self.game_manager.players[current_player_index]

            if not player.is_folded and not player.chips == 0:
                self.game_manager.user_interface.display_state(
                    self.game_manager.players, self.community_cards, current_player_index)
                update_starting_index = self.play_player_round(player)
                if update_starting_index:
                    self.starting_player_index = current_player_index
                
            current_player_index, number_of_actions =self.increment_current_player_index_and_number_of_actions(current_player_index, number_of_actions)
            

    def get_amount_to_call(self, player):
        return self.current_bet - player.betted_chips

    def get_amount_to_bet(self, player):
        return self.get_amount_to_call(player) + 2 * piv.small_blind

    def get_pot_size_if_all_remaining_players_calls(self):
        # Theoretical pot size used when calculated expected utility for PureRolloutResolver
        return self.current_bet * self.num_remaining_players()

    def get_pot_size_if_all_remaining_players_bets(self):
        # Theoretical pot size used when calculated expected utility for PureRolloutResolver
        return self.num_remaining_players() * (self.current_bet + 2 * piv.small_blind)

    def bet_small_blinds(self, player, n_small_blinds):
        bet_amount = piv.small_blind * n_small_blinds
        if player.chips > bet_amount:
            self.game_manager.action_manager.perform_action(
                player, 'B', bet=bet_amount)
        else:
            self.game_manager.action_manager.perform_action(player, 'A')

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
        self.starting_player_index = self.starting_player_index + 1
        if self.starting_player_index == len(self.game_manager.players):
            self.starting_player_index = 0

    def get_possible_actions(self, player):
        return self.game_manager.action_manager.get_possible_actions(player, self.current_bet)

    def reset_round_manager(self):
        self.current_bet = 0

    def total_pot(self):
        total_pot = sum(
            player.betted_chips for player in self.game_manager.players)
        return total_pot


class ActionManager():
    ACTIONS = [
        'C',  # call/check
        'B',  # bet/raise
        'F',  # fold
        'A',  # all-in
    ]

    def __init__(self):
        pass

    def get_possible_actions(self, player, current_bet: int = 0, raise_amount: int = 2 * piv.small_blind):
        possible_actions = []
        if player.chips + player.betted_chips > current_bet:
            possible_actions.append('C')
        if player.chips + player.betted_chips > current_bet + raise_amount:
            possible_actions.append('B')
        possible_actions = possible_actions + ['F', 'A']

        assert all(
            possible_action in self.ACTIONS for possible_action in possible_actions)
        return possible_actions

    def perform_action(self, player: Player, action: str, current_bet: int = 0, bet: int = 2 * piv.small_blind):
        if not action in self.get_possible_actions(player, current_bet, bet):
            if action in ['C', 'B']:
                action = 'A'

        update_starting_index = False
        if action == 'F':
            player.fold()
        elif action == 'C':
            player.check_or_call(current_bet)
        elif action == 'B':
            current_bet = player.bet_or_raise(current_bet, bet)
            update_starting_index = True
        elif action == 'A':
            if player.chips + player.betted_chips > current_bet:
                update_starting_index = True
            current_bet = player.all_in()
        else:
            raise ValueError('No action was performed')

        return current_bet, update_starting_index


class TexasHoldemRoundManager(RoundManager):
    def __init__(self, game_manager) -> None:
        super().__init__(game_manager)

    def play_preflop(self):
        super().deal_hole_cards(2)
        # TOOO: choose the two previous active players, not just from player list (since all players, inluded busted players, are here)
        player_small_blind, player_big_blind = self.get_small_and_big_blind_players()
        
        self.bet_small_blinds(player_small_blind, 1)
        self.bet_small_blinds(player_big_blind, 2)
        self.round_of_actions()

    def play_flop(self):
        super().deal_community_cards(3)
        self.round_of_actions()

    def play_turn_river(self):
        super().deal_community_cards(1)
        self.round_of_actions()

    def play_round(self):
        super().initialize_round()

        stages = [
            self.play_preflop,
            self.play_flop,
            self.play_turn_river,
            self.play_turn_river,
        ]

        for stage in stages:
            # calling each stage-function in stages sequentially, checking if round of poker should be ended
            stage()
            if self.round_of_poker_is_over():
                self.finalize_round(winners=self.remaining_players())
                break
        else:
            # if poker game never ends early: no winner has been determined
            self.finalize_round()
        self.set_starting_player_index()
    
    def round_of_poker_is_over(self):
        # all players except one have folded
        return len(self.remaining_players()) == 1

    def get_small_and_big_blind_players(self):
        index = self.starting_player_index
        small_blind_player = None
        big_blind_player = None
        while not small_blind_player:
            if not self.game_manager.players[index].is_folded:
                small_blind_player = self.game_manager.players[index]
            index = index - 1
        while not big_blind_player:
            if not self.game_manager.players[index].is_folded:
                big_blind_player = self.game_manager.players[index]
            index = index - 1

        return small_blind_player, big_blind_player

    def finalize_round(self, winners=None):
        # show cards

        if not winners:
            winners = self.game_manager.hands_evaluator.get_winner(
                self.remaining_players(), self.community_cards)
        self.game_manager.user_interface.round_over(
            self.game_manager.players, self.community_cards, winners)
        self.game_manager.pot_manager.distribute_pot(
            self.players_with_betted_chips(), winners)

        for player in self.game_manager.players:
            player.round_ended()


class PotManager():
    # self.subpots contains the pot as a subpot with all the players contributing, in addition to all eventual subpots.
    # this is the actual money to be distributed

    def __init__(self):
        pass

    def distribute_pot(self, all_players, winners):
        # items: (subpot_total, [...players_contributed_to_subpot])
        subpots = self.create_subpots(all_players)

        for (subpot_total, contributing_players) in subpots:
            # winners of subpot is the intersection of all the winners and the contributors to the subpot
            contributing_winners = list(
                set(contributing_players) & set(winners))
            if len(contributing_winners) == 0:
                # no winners in subpot => subpot is going back to its contributors
                self.distribute_subpot_to_players(
                    subpot_total, contributing_players)
            else:
                # subpot is distributed to the winners of its contributors
                self.distribute_subpot_to_players(
                    subpot_total, contributing_winners)

    def distribute_subpot_to_players(self, subpot_total, receiving_players):
        chips_to_each = subpot_total / len(receiving_players)
        for player in receiving_players:
            player.receive_chips(chips_to_each)

    def create_subpots(self, all_players):
        # items: (subpot_total, [...players_contributed_to_subpot])
        subpots = []
        all_players_sorted = sorted(
            all_players, key=lambda player: player.betted_chips)

        # create subpots, keeping track of its contributors
        for i in range(len(all_players_sorted)):
            player = all_players_sorted[i]
            # if the player has 0 chips, no new subpot needs to be made
            if player.betted_chips == 0:
                continue

            subpot_total = player.betted_chips * (len(all_players_sorted) - i)
            # removing the amount from each player that have somthing left
            # since we always handle the player with the least betted chips first, the players to the right will never have betted less than this
            chips_to_subtract = player.betted_chips
            for j in range(i, len(all_players_sorted)):
                all_players_sorted[j].betted_chips = all_players_sorted[j].betted_chips - \
                    chips_to_subtract

            contributing_players = all_players_sorted[i:]

            subpots.append((subpot_total, contributing_players))

        return subpots


class GameManager:
    """
    General for every types of rounds. Keeps track of players at the table.
    Starts and ends each round.
    """
    players = []

    def __init__(self) -> None:
        self.create_players()
        self.set_round_manager()
        self.set_hands_evaluator()
        self.set_user_interface()
        self.set_action_manager()
        self.set_pot_manager()

    def set_pot_manager(self):
        self.pot_manager = PotManager()

    def set_hands_evaluator(self):
        self.hands_evaluator = HandsEvaluator()

    def set_user_interface(self):
        self.user_interface = UserInterface()

    def set_action_manager(self):
        self.action_manager = ActionManager()

    def create_players(self):
        self.players = [HumanPlayer()
                        for _ in range(piv.number_of_human_players)]
        self.players += [AIPlayer(hide_cards=True)
                         for _ in range(piv.number_of_AI_players)]

    def set_round_manager(self):
        if piv.game == 'texasHoldem':
            self.round_manager = TexasHoldemRoundManager(self)
        else:
            self.round_manager = TexasHoldemRoundManager(self)

    def game_over(self):
        return len(list(filter(lambda player: player.chips > 0, self.players))) == 1

    def determine_winner(self):
        players_with_chips_left = [
            player for player in self.players if player.chips > 0]
        assert len(players_with_chips_left) == 1
        return players_with_chips_left[0]

    def play_game(self):
        while not self.game_over():
            self.round_manager.play_round()

        winner = self.determine_winner()
        return winner
    pass


if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.play_game()
