from collections import defaultdict
from player import Player
from deck_manager import Card
from utils import *


class RuleManager():

    def sort_on_value(self, cards):
        return sorted(cards, key=lambda card: self.card_values[card.value])

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
        players_with_4oak = self.get_players_with_best_4oak(players)
        if len(players_with_4oak > 0):
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
    def get_card_int_value(self, card: Card):
        return self.card_values[card.value]

    def find_players_with_highest_card_from_single_card(self, player_and_highest_card_tuples):
        highest_value_card = self.find_highest_card_from_player_card_tuples(
            player_and_highest_card_tuples)
        return [player for player, card_value in player_and_highest_card_tuples if card_value == highest_value_card]

    def check_straight_flush_from_start_card(self, cards, min_value, max_value):
        previous_value = max_value

        suit_count = defaultdict(int)
        for card in reversed(cards):
            if self.card_values[card.value] < previous_value - 1:
                # Return something indicating that we dont have a straight-flush
                return False

            # Count the suit to check if we have 5 of a kind
            suit_count[card.suit] += 1

            # Can break if we have reached the min value of the straight
            if self.card_values[card.value] == min_value:
                break

            previous_value = self.card_values[card.value]

        # Check if we have 5 the same suit
        return any(count >= 5 for count in suit_count.values())

    def player_has_royal_flush(self, cards):
        min_value = 10
        max_value = 14

        return self.check_straight_flush_from_start_card(cards, min_value, max_value)

    def player_has_straight_flush(self, cards):
        # In Texas holdem we will loop over 3 possible straights
        num_possible_straights = len(cards) - 5 + 1

        for i, card in enumerate(reversed(cards[-num_possible_straights:])):
            max_value = self.card_values[card.value]

            # The last card in the straight is 4 lower than highest
            min_value = max_value - 4

            if (self.check_straight_flush_from_start_card(
                    cards[:-i], min_value, max_value)):
                return (True, max_value)
        return (False, 0)

    # EVALUATION FUNCTIONS ### metode: returner nøkkelverdier for hvevr hånd for senere sammenligning

    def get_players_with_royal_flush(self, player_cards):
        players_with_royal_flush = []
        for (player, cards) in player_cards.items():
            if self.player_has_royal_flush(cards):
                players_with_royal_flush.append(player)
        return players_with_royal_flush

    def get_players_with_best_straight_flush(self, player_cards):
        players_with_straight_flush = []
        for (player, cards) in player_cards.items():
            has_straight, highest_card_in_straight = self.player_has_straight_flush(
                cards)
            if has_straight:
                players_with_straight_flush.append(
                    (player, highest_card_in_straight))
                print(highest_card_in_straight)

        if len(players_with_straight_flush) > 0:
            players_with_highest_straight_flush = find_players_with_highest_card_from_single_card(
                players_with_straight_flush)
            return players_with_highest_straight_flush
        else:
            return []

    def player_has_n_oak(self, cards, n):
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
        return self.player_has_n_oak(self, cards, 4)

    def find_best_card(self, cards):
        return max(cards, key=lambda card: get_card_int_value(card))

    def get_players_with_best_high_card(self, player_cards):
        # for player, cards in player_cards.items():
        player_and_best_card = [(player, get_card_int_value(
            self.find_best_card(cards))) for player, cards in player_cards.items()]

        best_card = find_highest_card_from_player_card_tuples(
            player_and_best_card)

        players_with_highest_card = [
            player for player, player_best_card in player_and_best_card.items() if player_best_card == best_card]

        return players_with_highest_card

    def get_players_with_best_4oak(self, player_cards):
        players_with_4oak = []
        for (player, cards) in player_cards.items():
            has_4oak, value_of_4oak = self.player_has_4oak(cards)
            if has_4oak:
                players_with_4oak.append((player, value_of_4oak))

        if len(players_with_4oak) > 0:
            # Checks for the best 4-of-a-kind
            players_with_best_4oak = find_players_with_highest_card_from_single_card(
                players_with_4oak)
            if players_with_best_4oak > 1:
                cards_of_players_with_4oak = {
                    player: player_cards[player] for player, value_of_4oak in players_with_best_4oak}

                cards_of_players_with_4oak_excluding_4oak = {}
                for player, cards_of_player_with_4oak in cards_of_players_with_4oak.items():
                    cards_of_player_with_4oak_excluding_4oak = get_cards_excluding_value(
                        cards_of_player_with_4oak, value_of_4oak)
                    cards_of_players_with_4oak_excluding_4oak[player] = cards_of_player_with_4oak_excluding_4oak

                # Checks for the highest kicker if several players has the same 4-of-a-kind
                player_cards_without_4oak = self.get_players_with_best_high_card(
                    cards_of_players_with_4oak_excluding_4oak)

                players_with_best_4oak = find_players_with_highest_kicker(
                    players_with_4oak)
            return players_with_best_4oak
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
    torstein.recieve_cards([Card('S', '3'), Card('S', '8')])
    paal = Player()
    paal.recieve_cards([Card('S', '2'), Card('S', '3')])

    card1 = Card('S', '4')
    card2 = Card('S', '5')
    card3 = Card('S', '6')
    card4 = Card('S', '7')
    card5 = Card('S', '9')

    community_cards = [card1, card2, card3, card4, card5]

    rule_manager = RuleManager()
    # print(rule_manager.get_winner([torstein, paal], community_cards))
    rule_manager.player_has_4oak([1, 2, 3, 4, 5, 6, 7])

    # print
