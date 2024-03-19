import unittest
from game_manager.game_manager import PotManager
from game_manager.player import Player


class TestRulesManager(unittest.TestCase):
    def setUp(self):
        self.player1 = Player(chips=0)
        self.player2 = Player(chips=0)
        self.player3 = Player(chips=0)
        self.player4 = Player(chips=0)
        self.player5 = Player(chips=0)
        self.potmanager = PotManager()
    
    def test1(self):
        self.player1.betted_chips = 30
        self.player2.betted_chips = 50
        self.player3.betted_chips = 50
        self.player4.betted_chips = 30

        all_players = [self.player1, self.player2, self.player3, self.player4]
        winners = [self.player3, self.player4]

        self.potmanager.distribute_pot(all_players, winners)

        self.assertEqual(self.player1.chips, 0)
        self.assertEqual(self.player2.chips, 0)
        self.assertEqual(self.player3.chips, 100)
        self.assertEqual(self.player4.chips, 60)

    def test2(self):
        self.player1.betted_chips = 100
        self.player2.betted_chips = 100
        self.player3.betted_chips = 20

        all_players = [self.player1, self.player2, self.player3]
        winners = [self.player3]

        self.potmanager.distribute_pot(all_players, winners)

        self.assertEqual(self.player1.chips, 80)
        self.assertEqual(self.player2.chips, 80)
        self.assertEqual(self.player3.chips, 60)

    def test3(self):
        self.player1.betted_chips = 20
        self.player2.betted_chips = 80
        self.player3.betted_chips = 40
        self.player4.betted_chips = 100
        self.player5.betted_chips = 80

        all_players = [self.player1, self.player2, self.player3, self.player4, self.player5]
        winners = [self.player3, self.player4, self.player5]

        self.potmanager.distribute_pot(all_players, winners)

        self.assertEqual(self.player1.chips, 0)
        self.assertEqual(self.player2.chips, 0)
        self.assertEqual(self.player3.chips, 60)
        self.assertEqual(self.player4.chips, 140)
        self.assertEqual(self.player5.chips, 120)

if __name__ == '__main__':
    unittest.main()

