import unittest
from ..rules_manager import RuleManager, Player, Card


class TestRulesManager(unittest.TestCase):
    def setUp(self):
        # This runs before each test method
        self.rule_manager = RuleManager()
        self.community_cards = [
            Card('S', 'T'), Card('S', 'J'), Card('S', 'Q'),
            # Community cards for Royal Flush test
            Card('S', 'K'), Card('S', '2')
        ]
        self.player1 = Player()
        self.player2 = Player()

    def test_royal_flush(self):
        self.player1.receive_cards([Card('S', '3'), Card('S', '8')])
        # Assuring a Royal Flush with community cards
        self.player2.receive_cards([Card('S', 'A'), Card('S', 'K')])
        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Player 1 should be winning with royal flush
        self.assertIn(self.player2, winners)
        self.assertNotIn(self.player1, winners)

        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        royal_flush = self.rule_manager.get_players_with_royal_flush(
            player_cards)

        self.assertEqual(winners, royal_flush)

    def test_straight_flush(self):
        # Reset community cards for a straight flush scenario
        self.community_cards = [
            Card('S', '3'), Card('S', '4'),
            Card('S', '5'), Card('S', '6'), Card('S', '7')
        ]
        # Assuring a Straight Flush
        self.player1.receive_cards([Card('S', '7'), Card('S', '8')])
        self.player2.receive_cards([Card('S', '8'), Card('S', '9')])
        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Player 2 should be winning with higher straight flush
        self.assertNotIn(self.player1, winners)
        self.assertIn(self.player2, winners)

        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_straight_flush = self.rule_manager.get_players_with_best_straight_flush(
            player_cards)

        self.assertEqual(winners, best_straight_flush)

    def test_four_of_a_kind(self):
        # Reset community cards for a 4oak scenario
        self.community_cards = [
            Card('S', '9'), Card('H', '9'), Card('D', '9'),
            Card('C', '9'), Card('S', '5')
        ]
        self.player1.receive_cards([Card('S', '2'), Card('S', '3')])
        # Assuring a win with higher kicker
        self.player2.receive_cards([Card('S', '4'), Card('S', '8')])
        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Player 2 should be winning with higher kicker
        self.assertIn(self.player2, winners)
        self.assertNotIn(self.player1, winners)

        # Checking if the players actually win on 4oak
        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_4oak = self.rule_manager.get_players_with_best_4oak_hand(
            player_cards)

        self.assertEqual(winners, best_4oak)

    def test_full_house(self):
        # Reset community cards for a full house scenario
        self.community_cards = [
            Card('S', '9'), Card('H', '9'), Card('D', '2'),
            Card('C', '2'), Card('S', '5')
        ]
        # Player 1 receives cards that give them a full house, 9s over 2s
        self.player1.receive_cards([Card('S', '9'), Card('H', '2')])
        # Player 2 also receives a full house, but lower, 2s over 5s
        self.player2.receive_cards([Card('S', '2'), Card('S', '5')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)

        # Player 1 should be winning with a higher full house (9s over 2s)
        self.assertIn(self.player1, winners)
        # Ensure player 2 is not in the winners as their full house is lower
        self.assertNotIn(self.player2, winners)

        # Checking if the players actually win on full_house
        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_full_house = self.rule_manager.get_players_with_best_full_house(
            player_cards)

        self.assertEqual(winners, best_full_house)

    def test_flush(self):
        # Reset community cards for a flush scenario
        self.community_cards = [
            Card('S', '2'), Card('S', '4'), Card('S', 'K'),
            Card('S', '8'), Card('S', 'J')
        ]
        # Player 1 has two spades, contributing to a flush but with a lower high card within the flush
        self.player1.receive_cards([Card('S', '3'), Card('H', '5')])
        # Player 2 has one spade, contributing to a flush with a higher high card in the community cards
        self.player2.receive_cards([Card('S', 'Q'), Card('H', '3')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Player 2 should be winning with a flush that uses the high card 'J' from the community cards
        self.assertIn(self.player2, winners)
        self.assertNotIn(self.player1, winners)

        # Checking if the players actually win on flush
        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_flush = self.rule_manager.get_players_with_best_flush(
            player_cards)

        self.assertEqual(winners, best_flush)

    def test_straight(self):
        # Reset community cards for a straight scenario
        self.community_cards = [
            Card('S', '5'), Card('H', '4'), Card('D', '3'),
            Card('C', '2'), Card('S', 'K')
        ]
        # Player 1 has cards that do not contribute to a straight
        self.player1.receive_cards([Card('S', '4'), Card('H', '6')])
        # Player 2 has cards that also do not contribute to the straight
        self.player2.receive_cards([Card('C', 'Q'), Card('D', 'Q')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)

        # Both players should tie with the straight on the board
        self.assertIn(self.player1, winners)
        self.assertNotIn(self.player2, winners)

        # Checking if the players actually win on flush
        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_straight = self.rule_manager.get_players_with_best_straight(
            player_cards)

        self.assertEqual(winners, best_straight)

    def test_three_of_a_kind(self):
        # Reset community cards for a 3oak scenario
        self.community_cards = [
            Card('S', '7'), Card('H', '7'), Card('D', '5'),
            Card('C', '2'), Card('S', '9')
        ]
        # Player 1 has a card that makes 3oak with the community cards
        self.player1.receive_cards([Card('D', '7'), Card('H', '3')])
        # Player 2 has unrelated high cards that do not contribute to a 3oak
        self.player2.receive_cards([Card('C', 'K'), Card('D', 'Q')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Player 1 should be the winner with 3oak
        self.assertIn(self.player1, winners)
        self.assertNotIn(self.player2, winners)
        # Checking if the players actually win on 3oak
        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_3oak = self.rule_manager.get_players_with_best_3oak(
            player_cards)

        self.assertEqual(winners, best_3oak)

    def test_two_pair(self):
        # Reset community cards for a Two Pair scenario
        self.community_cards = [
            Card('S', '7'), Card('H', '7'), Card('D', '5'),
            Card('C', '5'), Card('S', '9')
        ]
        # Player 1 has a card that contributes to a Two Pair with the community cards
        self.player1.receive_cards([Card('D', '8'), Card('H', '3')])
        # Player 2 has a better Two Pair using one hole card and the community cards
        self.player2.receive_cards([Card('C', '9'), Card('D', 'Q')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Player 2 should be the winner with a better Two Pair
        self.assertIn(self.player2, winners)
        self.assertNotIn(self.player1, winners)
        # Checking if the players actually win based on the Two Pair rule
        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_two_pair = self.rule_manager.get_players_with_best_two_pairs(
            player_cards)

        self.assertEqual(winners, best_two_pair)

    def test_one_pair(self):
        # Reset community cards for a One Pair scenario
        self.community_cards = [
            Card('S', 'K'), Card('H', 'Q'), Card('D', '9'),
            Card('C', 'Q'), Card('S', '2')
        ]
        # Player 1 has a card that contributes to a Two Pair with the community cards
        self.player1.receive_cards([Card('D', '5'), Card('H', 'T')])
        # Player 2 has a better Two Pair using one hole card and the community cards
        self.player2.receive_cards([Card('C', '7'), Card('D', 'J')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)

        # Player 2 should be the winner with a higher One Pair
        self.assertIn(self.player2, winners)
        self.assertNotIn(self.player1, winners)
        # Checking if the players actually win based on the One Pair rule
        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_one_pair = self.rule_manager.get_players_with_best_one_pair(
            player_cards)

        self.assertEqual(winners, best_one_pair)

    def test_high_card(self):
        # Reset community cards for a High Card scenario
        self.community_cards = [
            Card('S', '7'), Card('H', '5'), Card('D', '4'),
            Card('C', '2'), Card('S', '9')
        ]
        # Player 1 has high cards that do not form a pair or better with the community cards
        self.player1.receive_cards([Card('D', 'J'), Card('H', '3')])
        # Player 2 has a slightly higher card than Player 1, also not forming a pair or better
        self.player2.receive_cards([Card('C', 'Q'), Card('D', '6')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Player 2 should be the winner with a higher card (Queen > Jack)
        self.assertIn(self.player2, winners)
        self.assertNotIn(self.player1, winners)
        # Checking if the players actually win based on the High Card rule
        player_cards = self.rule_manager.create_player_card_dictionary(
            [self.player1, self.player2], self.community_cards)

        best_high_card = self.rule_manager.get_players_with_best_high_card(
            player_cards)

        self.assertEqual(winners, best_high_card)


if __name__ == '__main__':
    unittest.main()
    # unittest.TestCase("test_straight")
