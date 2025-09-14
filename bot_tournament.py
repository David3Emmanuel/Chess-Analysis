from chess_analysis.player import engine_player, random_player
from chess_analysis.auto import run_auto_game

import pandas as pd
import os

from chess_analysis.util import random_first_moves

def setup_tournament(players, n_rounds, games_per_round, csv_filename):
    # Initialize CSV file (remove if exists to start fresh)
    if os.path.exists(csv_filename):
        os.remove(csv_filename)
        print(f"Removed existing {csv_filename} to start fresh")
    
    # Generate all player combinations (each player vs each other player, including self)
    player_combinations = []
    for white_player in players:
        for black_player in players:
            player_combinations.append((white_player, black_player))
    
    # Calculate and display tournament estimates
    total_combinations = len(player_combinations)
    total_games = total_combinations * n_rounds * games_per_round
    
    print(f"Tournament Setup:")
    print(f"  Players: {[p['name'] for p in players]}")
    print(f"  Player combinations: {total_combinations}")
    print(f"  Rounds: {n_rounds}")
    print(f"  Games per combination per round: {games_per_round}")
    print(f"  Estimated total games: {total_games}")
    print(f"  Starting tournament...")
    print("=" * 50)

    return player_combinations

def run_tournament(players, n_rounds=1, games_per_round=1, csv_filename='tournament_results.csv'):
    """
    Run a tournament with multiple rounds and games per round.
    
    Args:
        players (list): List of player objects to compete in the tournament
        n_rounds (int): Number of rounds to play
        games_per_round (int): Number of games to play for each player combination per round
        csv_filename (str): Filename for CSV output (saves after each game)
    
    Returns:
        pd.DataFrame: Combined position analysis data from all games
    """
    
    player_combinations = setup_tournament(players, n_rounds, games_per_round, csv_filename)

    all_position_data = []
    game_counter = 0
    
    for round_num in range(n_rounds):
        print(f"Round {round_num + 1}/{n_rounds}")
        
        for white_player, black_player in player_combinations:
            print(f"  {white_player['name']} (White) vs {black_player['name']} (Black)")
            
            for game_num in range(games_per_round):
                game_counter += 1
                print(f"    Game {game_num + 1}/{games_per_round} (Total: {game_counter})")

                initial_moves = random_first_moves(white_player, black_player, random_player)
                print(f"      Starting game with initial moves: {initial_moves}")

                _, position_history = run_auto_game(
                    (white_player, black_player),
                    initial_moves=initial_moves,
                    bare=True
                )
                                
                game_positions = []
                for position in position_history:                
                    position_data = position['analysis']
                    game_positions.append(position_data)
                all_position_data += game_positions

                game_df = pd.DataFrame(game_positions)
                write_header = not os.path.exists(csv_filename)
                game_df.to_csv(csv_filename, mode='a', header=write_header, index=False)
                
                print(f"      Game {game_counter} data saved to {csv_filename} ({len(game_positions)} positions)")
    
    df = pd.DataFrame(all_position_data)
    
    print(f"\nTournament completed!")
    print(f"Total games played: {game_counter}")
    print(f"Total positions analyzed: {len(df)}")
    print(f"Data shape: {df.shape}")
    print(f"Saved to: {csv_filename}")
    
    return df

tournament_players = [engine_player, random_player]
n_rounds = 10
csv_file = 'tournament_results.csv'
tournament_df = run_tournament(tournament_players, n_rounds=n_rounds, games_per_round=4, csv_filename=csv_file)

print(f"Final results available in: {csv_file}")

print("\nTournament Summary:")
print("=" * 50)

# Game results by player combination
game_results = tournament_df.groupby(['white_player', 'black_player', 'tournament_game'])['game_result'].first().reset_index()
result_summary = game_results.groupby(['white_player', 'black_player'])['game_result'].value_counts().unstack(fill_value=0)
print("Game Results by Player Combination:")
print(result_summary)
