
class PivotalParameters:
    # If total number of players are 2. 
    # Then we use the deepstack resolver in river stage
    number_of_human_players = 1
    number_of_AI_players = 1

    # Only texas holdem for now
    game = "texasHoldem"

    # Changing this will also change the calculations in the resolvers
    starting_chips_per_player = 100.0
    small_blind = 5.0


    #### Values for the resolver ####

    # Restricts the tree in getting bigger
    number_of_allowed_bets_resolver = 2

    number_of_chance_node_children = 5

    # Rollouts
    number_of_deep_stack_rollouts = 100
    number_of_pure_rollout_resolver_rollouts = 10000

    # Used when calculating the 
    average_pot_size = 30
    verbose = False


pivotal_parameters = PivotalParameters()
