from typing import Dict, List
from ..player import Player
from ..deck_manager import Card
from .utils import *


class RuleManager():

    def sort_on_value(self, cards):
        return sorted(cards, key=lambda card: card_values[card.value])

    def get_winner(self, players, community_cards=[]):

        player_cards = {player: self.sort_on_value(
            player.hand + community_cards) for player in players}

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
        # players_with_full_house = self.get_players_with_best_full_house(
        #     players)
        # if len(players_with_full_house) > 0:
        #     return players_with_full_house

        # # check if someone or multiple people have flush
        # players_with_flush = self.get_players_with_best_flush(players)
        # if len(players_with_flush) > 0:
        #     return players_with_flush

        # # check if someone or multiple people have straight
        # players_with_straight = self.get_players_with_best_straight(players)
        # if len(players_with_straight) > 0:
        #     return players_with_straight

        # # check if someone or multiple people have 3 of a kind
        # players_with_3oak = self.get_players_with_best_3oak(players)
        # if len(players_with_3oak) > 0:
        #     return players_with_3oak

        # # check if someone or multiple people have 2 pairs
        # players_with_two_pairs = self.get_players_with_best_two_pairs(players)
        # if len(players_with_two_pairs) > 0:
        #     return players_with_two_pairs

        # # check if someone or multiple people have one pair
        # players_with_one_pair = self.get_players_with_best_one_pair(players)
        # if len(players_with_one_pair) > 0:
        #     return players_with_one_pair

        # # check if someone or multiple people have high card
        # players_with_high_card = self.get_players_with_best_high_card(players)
        # if len(players_with_high_card) > 0:
        #     return players_with_high_card

    def check_straight_flush_from_start_card(self, cards: List[Card], min_value: int, max_value: int):
        previous_value = max_value

        suit_count = {}
        for card in reversed(cards):
            if card_values[card.value] < previous_value - 1:
                # Return something indicating that we dont have a straight-flush
                return False

            # Count the suit to check if we have 5 of a kind
            suit_count[card.suit] = suit_count.get(card.suit, 0) + 1

            # Can break if we have reached the min value of the straight
            if card_values[card.value] == min_value:
                break

            previous_value = card_values[card.value]

        # Check if we have 5 the same suit
        return any(count >= 5 for count in suit_count.values())

    # EVALUATION FUNCTIONS ### metode: returner nøkkelverdier for hvevr hånd for senere sammenligning

    def player_has_royal_flush(self, cards: List[Card]):
        min_value = 10
        max_value = 14

        return self.check_straight_flush_from_start_card(cards, min_value, max_value)

    def get_players_with_royal_flush(self, player_cards: Dict[Player, List[Card]]):
        players_with_royal_flush = []
        for (player, cards) in player_cards.items():
            if self.player_has_royal_flush(cards):
                players_with_royal_flush.append(player)
        return players_with_royal_flush

    def player_has_straight_flush(self, cards: List[Card]):
        # In Texas holdem we will loop over 3 possible straights
        num_possible_straights = len(cards) - 5 + 1

        for i, card in enumerate(reversed(cards[-num_possible_straights:])):
            max_value = card_values[card.value]

            # The last card in the straight is 4 lower than highest
            min_value = max_value - 4

            if (self.check_straight_flush_from_start_card(
                    cards[:-i], min_value, max_value)):
                return (True, max_value)
        return (False, 0)

    def get_players_with_best_straight_flush(self, player_cards: Dict[Player, List[Card]]):
        players_with_straight_flush = []
        for (player, cards) in player_cards.items():
            has_straight, highest_card_in_straight = self.player_has_straight_flush(
                cards)
            if has_straight:
                players_with_straight_flush.append(
                    (player, highest_card_in_straight))

        if len(players_with_straight_flush) > 0:
            players_with_highest_straight_flush = find_players_with_highest_card_from_single_card(
                players_with_straight_flush)
            return players_with_highest_straight_flush
        else:
            return []

    def player_has_n_oak(self, cards: List[Card], n: int):
        value_count = {}
        for card in cards:
            value_count[card.value] = value_count.get(card.value, 0) + 1
        for value, count in value_count.items():
            if count == n:
                return (True, card_values[value])
        return (False, 0)

    def player_has_4oak(self, cards):
        # In Texas holdem we will loop over 4 possible 4oak's
        # If player has 4-of-a-kind the function will return the integer value of the cards in the 4-of-a-kind
        return self.player_has_n_oak(cards, 4)

    def get_players_with_best_high_card(self, player_cards: Dict[Player, List[Card]]):
        # Find highest card for each player
        player_and_highest_card = find_player_and_highest_card_for_each_player(
            player_cards)

        # Find players with the highest card
        players_with_highest_card = find_players_with_highest_card_from_single_card(
            player_and_highest_card)

        return players_with_highest_card

    def get_players_with_4oak(self, player_cards: Dict[Player, List[Card]]) -> Tuple[List[Tuple[Player, int]], int]:
        players_with_4oak = []
        for (player, cards) in player_cards.items():
            has_4oak, value_of_4oak = self.player_has_4oak(cards)
            if has_4oak:
                players_with_4oak.append((player, value_of_4oak))
        return (players_with_4oak, value_of_4oak)

    def get_players_with_highest_4oak(self, players_with_4oak: List[Tuple[Player, int]]) -> List[Player]:
        return find_players_with_highest_card_from_single_card(
            players_with_4oak)

    def create_player_hands_excluding_value(player_cards: Dict[Player, List[Card]], value_to_exclude: int) -> Dict[Player, List[Card]]:
        player_cards_excluding_value = {}
        for player, cards in player_cards_excluding_value.items():
            cards_excluding_value = get_cards_excluding_value(
                cards, value_to_exclude)
            player_cards_excluding_value[player] = cards_excluding_value
        return player_cards_excluding_value

    def create_player_hands_excluding_4oak_cards(self, cards_of_players_with_4oak: Dict[Player, List[Card]], value_of_4oak: int) -> Dict[Player, List[Card]]:
        return create_player_hands_excluding_value(cards_of_players_with_4oak, value_of_4oak)

    def get_players_with_best_4oak_hand(self, player_cards: Dict[Player, List[Card]]):
        players_with_4oak, value_of_4oak = self.get_players_with_4oak(
            player_cards)

        if len(players_with_4oak) == 1:
            return players_with_4oak

        elif len(players_with_4oak) > 1:
            # Checks for the best 4-of-a-kind: List[(Player1, 'K'), (Player2, 'K)]
            players_with_highest_4oak = self.get_players_with_highest_4oak(
                players_with_4oak)

            # If one player has higher value on the 4 cards in 4-of-a-kind.
            # This person is the winner
            if len(players_with_highest_4oak) == 1:
                return players_with_highest_4oak

            # Find player with best kicker
            elif len(players_with_highest_4oak) > 1:

                # Add to dictionary only the players with equal 4-of-a-kind
                cards_of_players_with_4oak = {
                    player: player_cards[player] for player in players_with_highest_4oak}

                print(cards_of_players_with_4oak)
                print("Val: ", value_of_4oak)
                # Find the player with the highest kicker
                player_cards_excluding_4oak = self.create_player_hands_excluding_4oak_cards(
                    cards_of_players_with_4oak, value_of_4oak)
                print(player_cards_excluding_4oak)
                # Checks for the highest kicker if several players has the same 4-of-a-kind
                player_and_highest_card_tuple = find_player_and_highest_card_for_each_player(
                    player_cards_excluding_4oak)
                print("-------------")
                print(player_and_highest_card_tuple)
                player_with_best_kicker = find_players_with_highest_card_from_single_card(
                    player_and_highest_card_tuple)
                return player_with_best_kicker
        else:
            return []

    def get_players_with_best_full_house(self, player_cards):
        pass

    def get_players_with_best_flush(self, player_cards):
        pass

    def get_players_with_best_straight(self, player_cards):
        pass

    def get_players_with_best_3oak(self, player_cards):
        pass

    def get_players_with_best_two_pairs(self, player_cards):
        pass

    def get_players_with_best_one_pair(self, player_cards):
        pass

    def get_players_with_best_high_card(self, player_cards):
        pass


if __name__ == '__main__':
    torstein = Player()
    torstein.receive_cards([Card('S', '3'), Card('S', '8')])
    paal = Player()
    paal.receive_cards([Card('S', '2'), Card('S', '3')])

    card1 = Card('S', '4')
    card2 = Card('S', '5')
    card3 = Card('S', '6')
    card4 = Card('S', '7')
    card5 = Card('S', '9')

    community_cards = [card1, card2, card3, card4, card5]

    rule_manager = RuleManager()
    # print(rule_manager.get_winner([torstein, paal], community_cards))
    # rule_manager.player_has_4oak([1, 2, 3, 4, 5, 6, 7])

    # print
