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

    def test_flush(self):
        # Reset community cards for a flush scenario
        self.community_cards = [
            Card('S', '2'), Card('S', '4'), Card('S', '7'),
            Card('S', '8'), Card('S', 'J')
        ]
        # Player 1 has two spades, contributing to a flush but with a lower high card within the flush
        self.player1.receive_cards([Card('S', '3'), Card('H', '5')])
        # Player 2 has one spade, contributing to a flush with a higher high card in the community cards
        self.player2.receive_cards([Card('S', 'K'), Card('H', '3')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Player 2 should be winning with a flush that uses the high card 'J' from the community cards
        self.assertIn(self.player2, winners)
        self.assertNotIn(self.player1, winners)

    def test_straight(self):
        # Reset community cards for a straight scenario
        self.community_cards = [
            Card('S', '5'), Card('H', '6'), Card('D', '7'),
            Card('C', '8'), Card('S', '9')
        ]
        # Player 1 has cards that do not contribute to a straight
        self.player1.receive_cards([Card('S', '2'), Card('H', '3')])
        # Player 2 has cards that also do not contribute to the straight
        self.player2.receive_cards([Card('C', '2'), Card('D', '4')])

        winners = self.rule_manager.get_winner(
            [self.player1, self.player2], self.community_cards)
        # Both players should tie with the straight on the board
        self.assertIn(self.player1, winners)
        self.assertIn(self.player2, winners)

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


if __name__ == '__main__':
    unittest.main()
