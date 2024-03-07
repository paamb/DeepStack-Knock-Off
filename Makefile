default: run

# Target for running the game manager
run:
	@echo "Running game manager..."
	python3 -m game_manager.game_manager

# Target for testing the rules manager
test:
	@echo "Testing rules manager..."
	python3 -m game_manager.rules_manager.tests.test_rules_manager

# Helper target for cleaning up any generated files, if necessary
clean:
	@echo "Cleaning up..."
	# Add commands to clean up generated files, if any
