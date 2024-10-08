default: run

# Target for running the game manager
run:
	@echo "Running game manager..."
	python3 -m game_manager.game_manager

expected:
	python3 -m resolvers.resolvers

hole:
	python3 -m poker_oracle.monte_carlo

# Target for testing the rules manager
# 
utility_matrix:
	python3 -m poker_oracle.utility_matrix


test:
	@echo "Testing rules manager..."
	python3 -m poker_oracle.hands_evaluator.tests.test_hands_evaluator
	python3 -m game_manager.test_game_manager

# Helper target for cleaning up any generated files, if necessary
clean:
	@echo "Cleaning up..."
	# Add commands to clean up generated files, if any
