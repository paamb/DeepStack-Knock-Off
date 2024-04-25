from game_manager.deck_manager import Card, DeckManager

# from poker_oracle.hands_evaluator.utils import suits, ranks, card_values
import csv

card_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
               '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2, 'AL': 1}
suits = ['C', 'D', 'H', 'S']
ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']


class MonteCarlo:

    def generate_all_cards(self):
        all_cards = []
        for suit in suits:
            for rank in ranks:
                all_cards.append(suit+rank)
        return all_cards

    def get_all_possible_cards(self):
        # Generates a list of cards as a string values ('C2') and sorts them
        all_cards = self.generate_all_cards()
        # Sorts all cards in
        sort_cards = sorted(all_cards, key=lambda x: (x[0], card_values[x[1]]))
        return sort_cards

    def get_all_possible_hole_pairs(self):
        # List of hole pairs represented ['C2C3', 'C2C4'] to create the probabilites
        all_possible_cards = self.get_all_possible_cards()
        all_possible_hole_pair = []
        for i in range(len(all_possible_cards)):
            for j in range(i+1, len(all_possible_cards)):
                all_possible_hole_pair.append(
                    all_possible_cards[i] + all_possible_cards[j])
        return all_possible_hole_pair

    def get_hole_pair_index_in_all_possible_hole_pairs_list(self, hole_pair):
        all_possible_hole_pairs = self.get_all_possible_hole_pairs()
        for i in range(len(all_possible_hole_pairs)):
            if hole_pair == all_possible_hole_pairs[i]:
                return i

    def hole_pair_string_to_object(self, hole_pair_string):

        card_string_1 = hole_pair_string[:2]
        card_string_2 = hole_pair_string[2:]

        card_1 = Card(card_string_1[0], card_string_1[1])
        card_2 = Card(card_string_2[0], card_string_2[1])
        return [card_1, card_2]

    def write_probability_dictionary_to_file(self, win_probabilites, filename='hole_pair_win_probability'):
        # Writes the # Poker Cheat-Sheet Generator to file
        with open(f'{filename}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            for key, probability in win_probabilites.items():
                value_1, value_2, card_class = key
                writer.writerow([value_1, value_2, card_class, probability])

    def evaluate_all_hole_pair_win_probabilities(self, all_hole_pairs, n_opponents=1, community_cards=[]):
        # Returns dict = {'H3H4': 0.4}
        win_probabilities = {}
        for hole_pair in all_hole_pairs:
            win_probability = self.evaluate_hole_pair_win_probability(
                hole_pair, n_opponents, community_cards)
            win_probabilities[hole_pair] = win_probability
        return win_probabilities

    def hole_pair_to_class(self, hole_pair):
        suit_1, value_1, suit_2, value_2 = hole_pair

        if card_values[value_1] > card_values[value_2]:
            value_2, value_1 = value_1, value_2

        if value_1 == value_2:
            return (value_1, value_2, 'pair')
        elif value_1 != value_2 and suit_1 != suit_2:
            return (value_1, value_2, 'unsuited')
        elif value_1 != value_2 and suit_1 == suit_2:
            return (value_1, value_2, 'suited')

    def get_all_hole_pair_classes(self):
        all_hole_pairs = self.get_all_possible_hole_pairs()
        print(len(all_hole_pairs))
        found_hole_pair_classes = {}
        hole_pair_representatives = []
        for hole_pair in all_hole_pairs:
            hole_pair_class = self.hole_pair_to_class(hole_pair)
            if not found_hole_pair_classes.get(hole_pair_class, False):
                found_hole_pair_classes[hole_pair_class] = True
                hole_pair_representatives.append(hole_pair)
        return hole_pair_representatives

    def evaluate_all_hole_pair_win_probabilities_classes(self):
        # Poker Cheat-Sheet Generator
        all_class_representative_hole_pairs = self.get_all_hole_pair_classes()
        print(all_class_representative_hole_pairs)
        win_probabilites_for_hole_pair_representing_classes = self.evaluate_all_hole_pair_win_probabilities(
            all_class_representative_hole_pairs)
        win_probabilites_for_classes = {}
        for hole_pair_representing_class, probability in win_probabilites_for_hole_pair_representing_classes.items():
            hole_pair_class = self.hole_pair_to_class(
                hole_pair_representing_class)
            win_probabilites_for_classes[hole_pair_class] = probability
        return win_probabilites_for_classes

    def evaluate_player_win_probability_after_pre_flop(self, player_1, community_cards, n_opponents=1):
        return self.evaluate_hole_pair_win_probability(
            player_1.hand, n_opponents, community_cards)

    def deal_opponents_cards(self, deck_manager, opponents):
        for player in opponents:
            cards = deck_manager.get_n_cards(2)
            player.receive_cards(cards)

    def opponents_hand_over_cards(self, deck_manager, opponents):
        for player in opponents:
            hand = player.hand_over_cards()
            deck_manager.receive_cards(hand)

    def evaluate_hole_pair_win_probability(self, hole_pair, n_opponents, community_cards, n_rollouts=10000):
        from game_manager.player import Player
        from poker_oracle.hands_evaluator.hands_evaluator import HandsEvaluator
        if isinstance(hole_pair, str):
            hole_pair = self.hole_pair_string_to_object(hole_pair)

        # Initialize deck of cards without hole_pair and community_cards
        deck_manager = DeckManager(True, hole_pair + community_cards)

        deck_manager.shuffle_cards()

        player_1 = Player()
        opponents = [Player() for _ in range(n_opponents)]

        # Deal cards
        player_1.receive_cards(hole_pair)

        num_player_1_wins = 0
        num_public_cards_to_deal = 5 - len(community_cards)
        for _ in range(n_rollouts):
            deck_manager.shuffle_cards()
            # Deal opponents cards
            self.deal_opponents_cards(deck_manager, opponents)

            # Deal public cards
            public_cards = deck_manager.get_n_cards(
                num_public_cards_to_deal)

            # Find the winner from the rollout
            hands_evaluator = HandsEvaluator()
            winner = hands_evaluator.get_winner(
                [player_1] + opponents, public_cards + community_cards)

            if player_1 in winner:
                num_player_1_wins += 1/(len(winner))

            self.opponents_hand_over_cards(deck_manager, opponents)
            deck_manager.receive_cards(public_cards)
        return num_player_1_wins / n_rollouts


if __name__ == '__main__':
    montecarlo = MonteCarlo()
    # win_probabilites_for_classes = montecarlo.evaluate_all_hole_pair_win_probabilities_classes()
    # montecarlo.write_probability_dictionary_to_file(
    #     win_probabilites_for_classes)
    
    card = Card('C', '5')

    placard_1 = card[:2]


    string_card = str(card)


    print(string_card)
    # player = Player()
    # player.hand = [Card('H', '9'), Card('H', 'K')]
    # community_cards = [Card('H', 'Q'), Card('H', 'T'), Card('H', 'J')]
    # probability = montecarlo.evaluate_player_win_probability_after_pre_flop(
    #     player, community_cards, 1)
    # print(probability)
