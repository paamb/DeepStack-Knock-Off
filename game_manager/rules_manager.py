from collections import defaultdict
from player import Player
from deck_manager import Card


class RuleManager():
    card_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
                   '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}

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
        # players_with_4oak = self.get_players_with_best_4oak(players)
        # if len(players_with_4oak > 0):
        #     return players_with_4oak

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

        return players

    def find_players_with_highest_value_card(self, player_card_tuples):
        highest_value_card = max(player_card_tuples, key=lambda x: x[1])[1]
        return [player for player, card_value in player_card_tuples if card_value == highest_value_card]

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
            players_with_highest_straight_flush = self.find_players_with_highest_value_card(
                players_with_straight_flush)
            return players_with_highest_straight_flush
        else:
            return []

    def player_has_4oak(self, cards):
        # In Texas holdem we will loop over 4 possible 4oaks
        num_cards_in_4oak = 4
        num_possible_4oak = len(cards) - num_cards_in_4oak + 1
        for i in range(len(cards) - 1, len(cards) - num_possible_4oak - 1, -1):
            print(i)

            for j in range(i-1, i-num_cards_in_4oak, -1):
                print(j)
                if cards[i] != cards[j]:
                    break
            else:
                return
            print("__________________________________")
            # return (True, max_value)
            # return (False, 0)

    def get_players_with_best_4oak(self, player_cards):
        players_with_4oak = []
        for (player, cards) in player_cards.items():
            if self.player_has_4oak(cards):
                players_with_4oak.append(player)
        return players_with_4oak

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
