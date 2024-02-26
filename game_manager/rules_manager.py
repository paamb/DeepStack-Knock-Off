class RuleManager():
    card_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, '10': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}

    def sort_on_value(self, cards):
        return sorted(cards, key=lambda card: self.card_values[card.value])

    def get_winner(self, players, community_cards = []):

        player_cards = { player: self.sort_on_value(player.cards + community_cards) for player in players }


        # check if someone or multiple people have royal flush
        players_with_royal_flush = self.get_players_with_royal_flush(player_cards)
        if len(players_with_royal_flush) > 0:
            return players_with_royal_flush

        # check if someone or multiple people have straight flush
        players_with_straight_flush = self.get_players_with_best_straight_flush(player_cards)
        if len(players_with_straight_flush) > 0:
            return players_with_straight_flush

        # check if someone or multiple people have 4 of a kind
        players_with_4oak = self.get_players_with_best_4oak(players)
        if len(players_with_4oak > 0):
            return players_with_4oak

        # check if someone or multiple people have full house
        players_with_full_house = self.get_players_with_best_full_house(players)
        if len(players_with_full_house) > 0:
            return players_with_full_house


        # check if someone or multiple people have flush
        players_with_flush = self.get_players_with_best_flush(players)
        if len(players_with_flush) > 0:
            return players_with_flush


        # check if someone or multiple people have straight
        players_with_straight = self.get_players_with_best_straight(players)
        if len(players_with_straight) > 0:
            return players_with_straight


        # check if someone or multiple people have 3 of a kind
        players_with_3oak = self.get_players_with_best_3oak(players)
        if len(players_with_3oak) > 0:
            return players_with_3oak


        # check if someone or multiple people have 2 pairs
        players_with_two_pairs = self.get_players_with_best_two_pairs(players)
        if len(players_with_two_pairs) > 0:
            return players_with_two_pairs


        # check if someone or multiple people have one pair
        players_with_one_pair = self.get_players_with_best_one_pair(players)
        if len(players_with_one_pair) > 0:
            return players_with_one_pair


        # check if someone or multiple people have high card
        players_with_high_card = self.get_players_with_best_high_card(players)
        if len(players_with_high_card) > 0:
            return players_with_high_card



    ### EVALUATION FUNCTIONS ### metode: returner nøkkelverdier for hvevr hånd for senere sammenligning
    def get_players_with_royal_flush(self, player_cards):

        for (player, cards) in player_cards.items():
            previous_value = 14
            for card in reversed(cards):
                if self.card_values[card.value] >= previous_value - 1:
                    


        pass

    def get_players_with_best_straight_flush(self, player_cards):
        pass

    def get_players_with_best_4oak(self, player_cards):
        pass

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

