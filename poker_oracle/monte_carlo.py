from game_manager.deck_manager import Card, DeckManager
from game_manager.pivotal_parameters import PivotalParameters as piv

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
        # Sorts all cards by suit and value
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
        """
        Converts a hole pair string (C2C3) to two Card objects
        """
        card_string_1 = hole_pair_string[:2]
        card_string_2 = hole_pair_string[2:]

        card_1 = Card(card_string_1[0], card_string_1[1])
        card_2 = Card(card_string_2[0], card_string_2[1])
        return [card_1, card_2]

    def write_probability_dictionary_to_file(self, win_probabilites, filename='hole_pair_win_probability', is_class_probability = True):
        """
        Writes the poker cheat sheet to file
        """
        with open(f'{filename}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            for key, probability in win_probabilites.items():
                if is_class_probability:
                    value_1, value_2, card_class = key
                    writer.writerow([value_1, value_2, card_class, probability])
                else:
                    writer.writerow([key, probability])

    def evaluate_all_hole_pair_win_probabilities(self, all_hole_pairs, n_opponents=1, community_cards=[], num_rollouts=piv.number_of_pure_rollout_resolver_rollouts):
        """
        For all hole pairs this function finds the win probability for the hole pair given public cards (community cards)
        """
        win_probabilities = {}
        for hole_pair in all_hole_pairs:
            win_probability = self.evaluate_hole_pair_win_probability(
                hole_pair, n_opponents, community_cards, num_rollouts)
            win_probabilities[hole_pair] = win_probability
        return win_probabilities

    def hole_pair_to_class(self, hole_pair):
        """
        Function maps every hole pair (C2C3)
        """
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
        """
        Finds a hole pair representative hand per hole pair class, i.e maps a list of 1329 hole pair to 169 hole pairs (1 per class).
        """
        all_hole_pairs = self.get_all_possible_hole_pairs()
        found_hole_pair_classes = {}
        hole_pair_representatives = []
        for hole_pair in all_hole_pairs:
            hole_pair_class = self.hole_pair_to_class(hole_pair)
            if not found_hole_pair_classes.get(hole_pair_class, False):
                found_hole_pair_classes[hole_pair_class] = True
                hole_pair_representatives.append(hole_pair)
        return hole_pair_representatives

    def evaluate_all_hole_pair_win_probabilities_classes(self, num_rollouts = piv.number_of_pure_rollout_resolver_rollouts):
        """
        This generates the poker cheat cheet found in "hole_pair_win_probabilities.csv"
        """
        all_class_representative_hole_pairs = self.get_all_hole_pair_classes()
        win_probabilites_for_hole_pair_representing_classes = self.evaluate_all_hole_pair_win_probabilities(
            all_class_representative_hole_pairs, num_rollouts=num_rollouts)
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

    def evaluate_hole_pair_win_probability(self, hole_pair, n_opponents, community_cards, n_rollouts=piv.number_of_pure_rollout_resolver_rollouts):
        """
        Evaluates the hole pair win probability based on simulating n_rollouts with randomly chosen opponent cards and public cards
        """
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

        # Deal number of cards corresponding to the stage
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

            # Use the Hands Evaluator module to find correct winner
            winner = hands_evaluator.get_winner(
                [player_1] + opponents, public_cards + community_cards)

            if player_1 in winner:
                num_player_1_wins += 1/(len(winner))

            self.opponents_hand_over_cards(deck_manager, opponents)
            deck_manager.receive_cards(public_cards)
        return num_player_1_wins / n_rollouts


if __name__ == '__main__':
    print("Generate poker cheat sheet for each class...")
    filename_class = 'hole_pair_win_probability_class'
    montecarlo = MonteCarlo()
    win_probabilites_for_classes = montecarlo.evaluate_all_hole_pair_win_probabilities_classes(num_rollouts=100)
    montecarlo.write_probability_dictionary_to_file(
        win_probabilites_for_classes, filename_class)
    print(f"Cheat sheet written to file: {filename_class}")

    print(f"Generate hole pair win probability individual holepair...")
    filename_individual = 'hole_pair_win_probability_individual'
    all_hole_pairs = montecarlo.get_all_possible_hole_pairs()
    win_probabilities_for_cards = montecarlo.evaluate_all_hole_pair_win_probabilities(all_hole_pairs, num_rollouts=100)
    montecarlo.write_probability_dictionary_to_file(
        win_probabilities_for_cards, filename_individual, is_class_probability=False)
    print(f"Hole pair win probability individual holepair written to file: {filename_individual}")

