from .player import Player
from .deck_manager import Card
from .rules_manager.rules_manager import RuleManager
from .unicode import deck_matrix, chips, hidden_card


class UserInterface():

    WHITESPACE = ' ' * 4

    def print_player_row(self, players):
        row_string = ''

        for player in players:
            player_string = ''
            for card in player.hand:
                player_string = player_string + \
                    deck_matrix[(card.suit, card.value)] + ' '
            player_string = player_string + ' ' + str(player.chips) + chips
            row_string = row_string + player_string + self.WHITESPACE

        print(row_string)
        return len(row_string)

    def print_community_row(self, community_cards, row_length):
        estimated_community_cards_length = 14
        base = ' ' * (row_length // 2 - estimated_community_cards_length // 2)

        for card in community_cards:
            base += deck_matrix[(card.suit, card.value)] + ' '

        print(base)

    def print_pot(self, players, row_length):
        estimated_pot_length = 10
        base = ' ' * (row_length // 2 - estimated_pot_length // 2)
        pot = 0
        for player in players:
            pot += player.betted_chips
        base += str(pot) + chips
        print(base)

    def display_state(self, players, community_cards):
        players_in_upper_row = players[:len(players)//2 + 1]
        players_in_lower_row = reversed(players[len(players)//2 + 1:])

        print("\033c")

        first_row_length = self.print_player_row(players_in_upper_row)
        print('\n')

        self.print_pot(players, first_row_length)
        print('\n')

        self.print_community_row(community_cards, first_row_length)
        print('\n')

        self.print_player_row(players_in_lower_row)
        print('\n')


if __name__ == '__main__':
    # torstein = Player()
    # torstein.recieve_cards([Card('S', '3'), Card('S', '8')])
    # paal = Player()
    # paal.recieve_cards([Card('S', '2'), Card('S', '3')])

    # card1 = Card('S', '4')

    # card2 = Card('S', '5')
    # card3 = Card('S', '6')
    # card4 = Card('S', '7')

    # card5 = Card('S', '9')

    # community_cards = [card1, card2, card3, card4, card5]

    # rule_manager = RuleManager()
    # print(rule_manager.get_winner([torstein, paal], community_cards))
    # rule_manager.player_has_4oak([1, 2, 3, 4, 5, 6, 7])
    pass
