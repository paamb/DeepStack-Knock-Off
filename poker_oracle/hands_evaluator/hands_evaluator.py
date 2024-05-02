from typing import Dict, List
# from game_manager.player import Player
from game_manager.deck_manager import Card
from .utils import *
from game_manager.constants import constants as const


class HandsEvaluator():

    def sort_on_value(self, cards):
        return sorted(cards, key=lambda card: const.card_values[card.value], reverse=True)

    def create_player_card_dictionary(self, players, community_cards):
        return {player: self.sort_on_value(
            player.hand + community_cards) for player in players}

    def get_winner(self, players, community_cards=[]):

        player_cards = self.create_player_card_dictionary(
            players, community_cards)

        # check if someone or multiple people have royal flush
        players_with_royal_flush = self.get_players_with_royal_flush(
            player_cards)
        if len(players_with_royal_flush) > 0:
            return players_with_royal_flush

        # check if someone or multiple people have straight flush
        players_with_straight_flush = self.get_players_with_best_straight_flush(
            player_cards)
        if len(players_with_straight_flush) > 0:
            return players_with_straight_flush

        # check if someone or multiple people have 4 of a kind
        players_with_4oak = self.get_players_with_best_4oak_hand(player_cards)
        if len(players_with_4oak) > 0:
            return players_with_4oak

        # # check if someone or multiple people have full house
        players_with_full_house = self.get_players_with_best_full_house(
            player_cards)
        if len(players_with_full_house) > 0:
            return players_with_full_house

        # # check if someone or multiple people have flush
        players_with_flush = self.get_players_with_best_flush(player_cards)
        if len(players_with_flush) > 0:
            return players_with_flush

        # # check if someone or multiple people have straight
        players_with_straight = self.get_players_with_best_straight(
            player_cards)
        if len(players_with_straight) > 0:
            return players_with_straight

        # check if someone or multiple people have 3 of a kind
        players_with_3oak = self.get_players_with_best_3oak(player_cards)
        if len(players_with_3oak) > 0:
            return players_with_3oak

        # # check if someone or multiple people have 2 pairs
        players_with_two_pairs = self.get_players_with_best_two_pairs(
            player_cards)
        if len(players_with_two_pairs) > 0:
            return players_with_two_pairs

        # # check if someone or multiple people have one pair
        players_with_one_pair = self.get_players_with_best_one_pair(
            player_cards)
        if len(players_with_one_pair) > 0:
            return players_with_one_pair

        # # check if someone or multiple people have high card
        players_with_high_card = self.get_players_with_best_high_card(
            player_cards)
        if len(players_with_high_card) > 0:
            return players_with_high_card
        return players

    def check_straight_flush_from_start_card(self, cards: List[Card], min_value: int, max_value: int):
        previous_value = max_value
        unique_cards_counter = 1
        straight = False
        suit_count = {}
        for card in (cards):
            if const.card_values[card.value] < previous_value - 1:
                # Return something indicating that we dont have a straight-flush
                return False

            if const.card_values[card.value] != previous_value:
                unique_cards_counter += 1

            # Increment count suits
            suit_count[card.suit] = suit_count.get(card.suit, 0) + 1

            # Can break if we have reached the min value of the straight
            if const.card_values[card.value] == min_value and unique_cards_counter == const.length_of_player_hand:
                straight = True
                break

            # Count the suit to check if we have flush
            previous_value = const.card_values[card.value]

        # Check if we have 5 the same suit
        return straight and any(count >= 5 for count in suit_count.values())

    # EVALUATION FUNCTIONS ### metode: returner nøkkelverdier for hvevr hånd for senere sammenligning

    def player_has_royal_flush(self, cards: List[Card]):
        has_straight_flush, highest_card = self.player_has_straight_flush(
            cards)
        return has_straight_flush and highest_card == 14

    def get_players_with_royal_flush(self, player_cards: Dict[Player, List[Card]]):
        players_with_royal_flush = []
        for (player, cards) in player_cards.items():
            if self.player_has_royal_flush(cards):
                players_with_royal_flush.append(player)
        return players_with_royal_flush

    def player_has_straight_flush(self, cards: List[Card]):
        has_flush, flush_cards = self.player_has_flush(cards)
        if not has_flush:
            return (False, 0)

        return self.player_has_straight(flush_cards)

    def get_players_with_best_straight_flush(self, player_cards: Dict[Player, List[Card]]):
        players_with_straight_flush = []
        for (player, cards) in player_cards.items():
            has_straight, highest_card_in_straight = self.player_has_straight_flush(
                cards)
            if has_straight:
                players_with_straight_flush.append(
                    (player, highest_card_in_straight))

        if len(players_with_straight_flush) > 0:
            players_with_highest_straight_flush, value_of_highest_card = find_players_with_highest_card_from_single_card(
                players_with_straight_flush)
            return players_with_highest_straight_flush
        else:
            return []

    def player_has_n_oak(self, cards: List[Card], n: int):
        value_count = {}
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1

        sorted_cards_count = sorted(value_count.items(),
                                    key=lambda x: const.card_values[x[0]], reverse=True)

        # Find highest value that is not in n_oak

        # [('K', 3), ('Q',3), ()]
        kickers = []
        total_num_kickers = const.length_of_player_hand - n
        num_kickers = 0
        for value, count in sorted_cards_count:
            if count != n and num_kickers < total_num_kickers:
                kickers.append(const.card_values[value])
                num_kickers += 1

        # Check for n of a kind
        for value, count in value_count.items():
            if count == n:
                return (True, const.card_values[value], kickers)
        return (False, 0, [])

    def player_has_4oak(self, cards):
        # In Texas holdem we will loop over 4 possible 4oak's
        # If player has 4-of-a-kind the function will return the integer value of the cards in the 4-of-a-kind
        return self.player_has_n_oak(cards, 4)

    def get_players_with_best_high_card(self, player_cards: Dict[Player, List[Card]]):
        # Find highest card for each player
        player_and_highest_card = find_player_and_highest_card_for_each_player(
            player_cards)

        # Find players with the highest card
        players_with_highest_card, value_of_highest_card = find_players_with_highest_card_from_single_card(
            player_and_highest_card)

        return players_with_highest_card

    def get_players_with_4oak(self, player_cards: Dict[Player, List[Card]]) -> Tuple[List[Tuple[Player, int, int]]]:
        players_with_4oak = []
        for (player, cards) in player_cards.items():
            has_4oak, value_of_4oak, value_of_kicker = self.player_has_4oak(
                cards)
            if has_4oak:
                players_with_4oak.append(
                    (player, value_of_4oak, value_of_kicker[0]))
        return players_with_4oak

    def get_players_with_highest_4oak_and_kicker(self, players_with_4oak: List[Tuple[Player, int, int]]) -> List[Player]:
        sorted_players_with_4oak = sorted(
            players_with_4oak, key=lambda x: (x[1], x[2]), reverse=True)

        # Contains 4oak + kicker
        best_4oak = sorted_players_with_4oak[0][1], sorted_players_with_4oak[0][2]

        # Find the players that have the best 4oak and kickers
        best_players = [player_tuple[0] for player_tuple in players_with_4oak if (
            player_tuple[1], player_tuple[2]) == best_4oak]

        return best_players

    def get_players_with_best_4oak_hand(self, player_cards: Dict[Player, List[Card]]):
        players_with_4oak = self.get_players_with_4oak(
            player_cards)
        if len(players_with_4oak) == 1:
            return [players_with_4oak[0][0]]

        elif len(players_with_4oak) > 1:
            # Checks for the best 4-of-a-kind: List[(Player1, 'K'), (Player2, 'K)]
            players_with_highest_4oak_and_kicker = self.get_players_with_highest_4oak_and_kicker(
                players_with_4oak)

            return players_with_highest_4oak_and_kicker
        else:
            return []

    def player_has_full_house(self, cards):
        value_count = {}
        card_value_in_3oak = 0
        card_value_in_2oak = 0
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1
        for value, count in value_count.items():
            if count == 3 and card_value_in_3oak == 0:
                card_value_in_3oak = value
            elif count >= 2 and card_value_in_2oak == 0:
                card_value_in_2oak = value
        if card_value_in_3oak and card_value_in_2oak:
            return (True, card_value_in_3oak, card_value_in_2oak)
        return (False, 0, 0)

    def get_players_with_best_full_house(self, player_cards):
        players_with_full_house = []
        for (player, cards) in player_cards.items():
            has_full_house, card_value_in_3oak, card_value_in_2oak = self.player_has_full_house(
                cards)
            if has_full_house:
                players_with_full_house.append(
                    (player, card_value_in_3oak, card_value_in_2oak))

        if not players_with_full_house:
            return []
        sorted_players_with_full_house = sorted(
            players_with_full_house, key=lambda x: (const.card_values[x[1]], const.card_values[x[2]]), reverse=True)
        best_full_house = sorted_players_with_full_house[0][1], sorted_players_with_full_house[0][2]

        best_players = [player_tuple[0] for player_tuple in players_with_full_house if (
            player_tuple[1], player_tuple[2]) == best_full_house]
        # print(best_players)
        return best_players

    def player_has_flush(self, cards):
        suit_count = {}
        flush_cards = []
        for card in cards:
            # Count the suit to check if we have flush
            suit_count[card.suit] = suit_count.get(card.suit, 0) + 1

        if not any(count >= 5 for count in suit_count.values()):
            return (False, [])

        for suit, count in suit_count.items():
            if count >= 5:
                flush_suit = suit
                break

        flush_cards = [card for card in cards if card.suit == flush_suit]
        return (True, flush_cards)

    def get_players_with_best_flush(self, player_cards):
        players_with_flush = []
        for (player, cards) in player_cards.items():
            has_flush, flush_cards = self.player_has_flush(
                cards)
            if has_flush:
                players_with_flush.append(
                    (player, get_list_of_card_values(flush_cards)))

        if len(players_with_flush) == 1:
            return [players_with_flush[0][0]]

        elif len(players_with_flush) > 1:
            players_with_highest_flush = get_players_with_best_high_card_from_tuple(
                players_with_flush)
            return players_with_highest_flush
        else:
            return []

    def check_straight_from_start_card(self, cards: List[Card], min_value: int, max_value: int):
        previous_value = max_value
        unique_cards_counter = 1
        straight = False
        for card in cards:
            if const.card_values[card.value] < previous_value - 1:
                # Return something indicating that we dont have a straight-flush
                return False

            if const.card_values[card.value] != previous_value:
                unique_cards_counter += 1
            # Can break if we have reached the min value of the straight
            if const.card_values[card.value] == min_value and unique_cards_counter == const.length_of_player_hand:
                straight = True
                break

            previous_value = const.card_values[card.value]

        return straight

    def add_low_ace_cards(self, cards):
        cards_to_add = []
        for card in cards:
            if card.value == 'A':
                cards_to_add.append(Card(card.suit, 'AL'))
        return cards + cards_to_add

    def player_has_straight(self, cards: List[Card]):
        # In Texas holdem we will loop over 3 possible straights
        cards = self.add_low_ace_cards(cards)

        num_possible_straights = len(cards) - const.length_of_player_hand + 1
        for i in range(num_possible_straights):
            max_value = const.card_values[cards[i].value]

            # The last card in the straight is 4 lower than highest
            min_value = max_value - 4

            if (self.check_straight_from_start_card(
                    cards[i:], min_value, max_value)):
                return (True, max_value)
        return (False, 0)

    def get_players_with_best_straight(self, player_cards: Dict[Player, List[Card]]):
        players_with_straight = []
        for (player, cards) in player_cards.items():
            has_straight, highest_card_in_straight = self.player_has_straight(
                cards)
            if has_straight:
                players_with_straight.append(
                    (player, highest_card_in_straight))
        if len(players_with_straight) > 0:
            players_with_highest_straight, value_of_highest_card = find_players_with_highest_card_from_single_card(
                players_with_straight)

            return players_with_highest_straight
        else:
            return []

    def player_has_3oak(self, cards):
        # In Texas holdem we will loop over 4 possible 4oak's
        # If player has 4-of-a-kind the function will return the integer value of the cards in the 4-of-a-kind
        return self.player_has_n_oak(cards, 3)

    def get_players_with_3oak(self, player_cards: Dict[Player, List[Card]]) -> Tuple[List[Tuple[Player, str]], str]:
        players_with_3oak = []
        for (player, cards) in player_cards.items():

            # Returns value of 3oak and 2 kickers
            has_3oak, value_of_3oak, value_of_kickers = self.player_has_3oak(
                cards)
            if has_3oak:
                players_with_3oak.append(
                    (player, value_of_3oak, value_of_kickers[0], value_of_kickers[1]))
        return players_with_3oak

    def get_players_with_highest_3oak_and_kicker(self, players_with_3oak: List[Tuple[Player, int, int, int]]) -> List[Player]:
        sorted_players_with_3oak = sorted(
            players_with_3oak, key=lambda x: (x[1], x[2], x[3]), reverse=True)

        # The best 3oak + 2 kickers
        best_3oak = sorted_players_with_3oak[0][1], sorted_players_with_3oak[0][2], sorted_players_with_3oak[0][3]

        # Find players with best 3oak + 2 kickers
        best_players = [player_tuple[0] for player_tuple in players_with_3oak if (
            player_tuple[1], player_tuple[2], player_tuple[3]) == best_3oak]

        return best_players

    def get_players_with_best_3oak(self, player_cards):
        players_with_3oak = self.get_players_with_3oak(
            player_cards)

        if len(players_with_3oak) == 1:
            return [players_with_3oak[0][0]]

        elif len(players_with_3oak) > 1:
            players_with_highest_3oak_and_kicker = self.get_players_with_highest_3oak_and_kicker(
                players_with_3oak)

            return players_with_highest_3oak_and_kicker
        else:
            return []

    def player_has_2_pairs(self, cards):
        value_count = {}
        high_card = 0
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1

        # Sort first on looking at 2nd element
        sorted_cards_count = sorted(value_count.items(),
                                    key=lambda x: (x[1], const.card_values[x[0]]), reverse=True)

        if sorted_cards_count[0][1] == 2 and sorted_cards_count[1][1] == 2:
            high_pair = sorted_cards_count[0][0]
            low_pair = sorted_cards_count[1][0]
            high_card = sorted_cards_count[2][0]
            return (True, const.card_values[high_pair], const.card_values[low_pair], const.card_values[high_card])
        return (False, 0, 0, 0)

    def get_players_with_best_two_pairs_and_kicker(self, players_with_2oak: List[Tuple[Player, int, int, int]]) -> List[Player]:
        sorted_players_with_2oak = sorted(
            players_with_2oak, key=lambda x: (x[1], x[2], x[3]), reverse=True)
        best_2oak = sorted_players_with_2oak[0][1], sorted_players_with_2oak[0][2], sorted_players_with_2oak[0][3]

        best_players = [player_tuple[0] for player_tuple in players_with_2oak if (
            player_tuple[1], player_tuple[2], player_tuple[3]) == best_2oak]

        return best_players

    def get_players_with_best_two_pairs(self, player_cards):
        players_with_two_pairs = []
        for (player, cards) in player_cards.items():
            has_2oak, high_pair, low_pair, high_card = self.player_has_2_pairs(
                cards)
            if has_2oak:
                players_with_two_pairs.append(
                    (player, high_pair, low_pair, high_card))

        if len(players_with_two_pairs) == 1:
            return [players_with_two_pairs[0][0]]

        elif len(players_with_two_pairs) > 1:
            players_with_highest_2oak_and_kicker = self.get_players_with_best_two_pairs_and_kicker(
                players_with_two_pairs)
            return players_with_highest_2oak_and_kicker

        else:
            return []

    def get_players_with_best_pair_and_kicker(self, players_with_2oak: List[Tuple[Player, int, int, int, int]]) -> List[Player]:
        sorted_players_with_2oak = sorted(
            players_with_2oak, key=lambda x: (x[1], x[2], x[3], x[4]), reverse=True)

        # Best pair with 3 kickers
        best_pair_hand = sorted_players_with_2oak[0][1], sorted_players_with_2oak[
            0][2], sorted_players_with_2oak[0][3], sorted_players_with_2oak[0][4]

        # Find best player with best hand
        best_players = [player_tuple[0] for player_tuple in players_with_2oak if (
            player_tuple[1], player_tuple[2], player_tuple[3], player_tuple[4]) == best_pair_hand]

        return best_players

    def player_has_one_pair(self, cards):
        return self.player_has_n_oak(cards, 2)

    def get_players_with_one_pair(self, player_cards):
        players_with_one_pair = []
        for (player, cards) in player_cards.items():
            has_one_pair, value_of_pair,  value_of_kickers = self.player_has_one_pair(
                cards)
            if has_one_pair:
                players_with_one_pair.append(
                    (player, value_of_pair, value_of_kickers[0], value_of_kickers[1], value_of_kickers[2]))

        return players_with_one_pair

    def get_players_with_best_one_pair(self, player_cards):
        players_with_one_pair = self.get_players_with_one_pair(player_cards)
        if len(players_with_one_pair) == 1:
            return [players_with_one_pair[0][0]]

        elif len(players_with_one_pair) > 1:
            players_with_best_one_pair_and_kicker = self.get_players_with_best_pair_and_kicker(
                players_with_one_pair)
            return players_with_best_one_pair_and_kicker

        else:
            return []

    def get_players_with_best_high_card(self, player_cards):
        player_cards_tuples = [(player, get_list_of_card_values(cards))
                               for player, cards in player_cards.items()]
        best_players = get_players_with_best_high_card_from_tuple(
            player_cards_tuples)

        return best_players


# if __name__ == '__main__':

#     torstein = Player()
#     torstein.receive_cards([Card('S', '3'), Card('S', '8')])
#     paal = Player()
#     paal.receive_cards([Card('S', '2'), Card('S', '3')])

#     card1 = Card('S', '4')
#     card2 = Card('S', '5')
#     card3 = Card('S', '6')
#     card4 = Card('S', '7')
#     card5 = Card('S', '9')

#     community_cards = [card1, card2, card3, card4, card5]

#     hands_evaluator = HandsEvaluator()
