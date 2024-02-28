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


if __name__ == '__main__':
    unittest.main()
