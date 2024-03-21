from typing import List, Tuple, Dict
from game_manager.deck_manager import Card
from game_manager.player import Player
card_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
               '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
length_of_player_hand = 5


def find_highest_card_from_player_card_tuples(player_and_highest_card_tuples: List[Tuple[Player, int]]) -> int:
    # Expects list [(player, card_value (e.g 12) )]
    # Returns the highest card among all the players
    return max(player_and_highest_card_tuples, key=lambda x: x[1])[1]


def find_best_card_from_list(cards: List[Card]):
    return max(cards, key=lambda card: get_card_int_value(card))


def find_player_and_highest_card_for_each_player(player_cards: Dict[Player, List[Card]]) -> List[Tuple[Player, int]]:
    return [(player, get_card_int_value(
            find_best_card_from_list(cards))) for player, cards in player_cards.items()]


def get_card_int_value(card: Card):
    return card_values[card.value]


def get_list_of_card_values(cards: List[Card]):
    return [get_card_int_value(card) for card in cards]


def get_players_with_best_high_card_from_tuple(player_cards_tuples):
    sorted_players_by_highest_hand = sorted(
        player_cards_tuples, key=lambda x: (x[1][0], x[1][1], x[1][2], x[1][3], x[1][4]), reverse=True)

    # # Best pair with 3 kickers
    best_pair_hand = sorted_players_by_highest_hand[0][1]

    # Find best player with best hand
    best_players = [player_cards_tuple[0] for player_cards_tuple in player_cards_tuples if (
        player_cards_tuple[1]) == best_pair_hand]

    return best_players


def find_players_with_highest_card_from_single_card(player_and_highest_card_tuples: List[Tuple[Player, int]]) -> Tuple[List[Player], int]:
    # Returns all the players that have the highest card
    highest_value_card = find_highest_card_from_player_card_tuples(
        player_and_highest_card_tuples)
    players = [player for player,
               card_value in player_and_highest_card_tuples if card_value == highest_value_card]
    return (players, highest_value_card)


def get_players_with_best_high_card(player_cards: Dict[Player, List[Card]]):
    # Find highest card for each player
    player_and_highest_card = find_player_and_highest_card_for_each_player(
        player_cards)

    # Find players with the highest card
    players_with_highest_card = find_players_with_highest_card_from_single_card(
        player_and_highest_card)

    return players_with_highest_card


def get_cards_excluding_value(cards: List[Card], value: str) -> List[Card]:
    return [card for card in cards if card_values[card.value] != value]


def create_player_hands_excluding_value(player_cards: Dict[Player, List[Card]], value_to_exclude: int) -> Dict[Player, List[Card]]:
    player_cards_excluding_value = {}
    for player, cards in player_cards.items():
        cards_excluding_value = get_cards_excluding_value(
            cards, value_to_exclude)
        player_cards_excluding_value[player] = cards_excluding_value
    return player_cards_excluding_value


def find_players_with_highest_card_from_set_of_cards(self, player_and_set_of_cards_tuples):
    pass


def find_players_with_highest_kicker(players_with_4oak):
    pass


# def find_highest_card_from_player_card_tuples(cards, )


def find_highest_card_from_player_card_tuples_excluding_value(cards, cards_to_exclude):
    pass


def find_players_with_highest_card_from_card_collection(hand):
    pass
