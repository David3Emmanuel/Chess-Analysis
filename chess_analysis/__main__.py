from .auto import run_auto_game
from .player import engine_player, random_player, custom_player

if __name__ == "__main__":
    run_auto_game((custom_player('final_model.joblib'), random_player))