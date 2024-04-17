from .player import Player
from .deck_manager import Card
from .unicode import deck_matrix, chips, hidden_card


class UserInterface():

    WHITESPACE = ' ' * 4

    def print_player_row(self, players, current_player, winners):
        row_string = ''
        invisible_characters = 0

        for player in players:
            player_string = ''
            if len(player.hand) == 0:
                player_string = "BUSTED"
            else:
                for card in player.hand:
                    card_to_add = deck_matrix[(card.suit, card.value)] if not (player.hide_cards and not winners) else hidden_card
                    player_string = player_string + \
                        card_to_add + ' '
                player_string = player_string + ' ' + str(player.chips) + chips

            player_string = f"{player_string:20}"
            if (not current_player == None and player == current_player) and not player in winners:
                player_string = '\033[1;32m' + player_string + '\033[0m'
                invisible_characters = invisible_characters + 11
            elif player in winners:
                player_string = '\033[1;33m' + player_string + '\033[0m'
                invisible_characters = invisible_characters + 11
            elif player.is_folded:
                player_string = '\033[90m' + player_string + '\033[0m'
                invisible_characters = invisible_characters + 9

            row_string = row_string + player_string

        print(row_string)
        return len(row_string) - invisible_characters

    def print_community_row(self, community_cards, row_length):
        estimated_community_cards_length = 14
        base = ' ' * (row_length // 2 - estimated_community_cards_length // 2)

        for card in community_cards:
            base += deck_matrix[(card.suit, card.value)] + ' '

        print(base)

    def round_over(self, players, community_cards, winners):
        self.display_state(players, community_cards, winners=winners)
        input("ROUND OVER (PRESS ENTER TO CONTINUE)")

    def print_pot(self, players, row_length):
        estimated_pot_length = 10
        base = ' ' * (row_length // 2 - estimated_pot_length // 2)
        pot = 0
        for player in players:
            pot += player.betted_chips
        base += str(pot) + chips
        print(base)

    def display_state(self, players, community_cards, current_player_index=None, winners=[]):
        players_in_upper_row = players[:len(players)//2]
        players_in_lower_row = reversed(players[len(players)//2:])
        if not current_player_index == None:
            current_player = players[current_player_index]
        else:
            current_player = None

        print("\033c")

        first_row_length = self.print_player_row(
            players_in_upper_row, current_player, winners)
        print('\n')

        self.print_pot(players, first_row_length)
        print('\n')

        self.print_community_row(community_cards, first_row_length)
        print('\n')

        self.print_player_row(players_in_lower_row, current_player, winners)
        print('\n')

    def display_possible_actions(self, player, possible_actions, current_bet, raise_amount):
        ACTION_TO_PRETTY = {
            'C': f'CHECK/CALL ({current_bet - player.betted_chips}) [C]',
            'B': f'BET/RAISE ({current_bet + raise_amount - player.betted_chips}) [B]',
            'F': 'FOLD [F]',
            'A': 'ALL-IN [A]',
        }

        for action in possible_actions:
            print(ACTION_TO_PRETTY[action])
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

    # hands_evaluator = HandsEvaluator()
    # print(hands_evaluator.get_winner([torstein, paal], community_cards))
    # hands_evaluator.player_has_4oak([1, 2, 3, 4, 5, 6, 7])
    pass
