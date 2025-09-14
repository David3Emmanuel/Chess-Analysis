import chess
from .analysis import Analysis
from .util import display_board, export_game, save_position_history
from .display import is_closed, finish_display, plot_position_history
from .position_analysis import position_analysis


def setup_game(players: tuple[Analysis, Analysis], initial_moves: list[str]):
    """
    Set up a new chess game with optional initial moves and players.
    
    Args:
        players (list): List of two player functions [white_player, black_player]
        initial_moves (list): List of moves in SAN notation

    Returns:
        tuple: (board, players, position_history)
    """
    
    board = chess.Board()
    for move in initial_moves:
        board.push_san(move)
    
    position_history = []
    initial_position = position_analysis(board)
    position_history.append({
        'move_number': 0,
        'fen': board.fen(),
        'last_move': None,
        'analysis': initial_position.copy()
    })
    
    return board, players, position_history


def play_game(board, players, position_history):
    """
    Play the chess game until completion or display is closed.
    
    Args:
        board (chess.Board): The chess board
        players (list): List of player functions
        position_history (list): List to store position history
    
    Returns:
        None: Modifies board and position_history in place
    """
    while not (board.is_game_over() or is_closed()):
        player = players[1 - board.turn]
        move = player(board)
        move_san = board.san(move)
        print(f'{player["name"]} - {move_san}')
        board.push(move)
        display_board(board, move, pov=chess.WHITE)
        
        position = position_analysis(board)
        position_history.append({
            'move_number': len(position_history),
            'fen': board.fen(),
            'last_move': move_san,
            'analysis': position.copy()
        })


def finalize_game(board, players, position_history):
    """
    Finalize the game by cleaning up display and saving data.
    
    Args:
        board (chess.Board): The chess board
        players (list): List of player functions
        position_history (list): Position history data
    """
    finish_display()
    save_position_history(position_history)
    plot_position_history(position_history)
    export_game(board, players)


def run_auto_game(players: tuple[Analysis, Analysis], initial_moves: list[str] = []):
    """
    Run a complete automated chess game.
    
    Args:
        players (list): List of two player functions [white_player, black_player]
        initial_moves (list): List of moves in SAN notation
    """
    board, players, position_history = setup_game(players, initial_moves)
    play_game(board, players, position_history)
    finalize_game(board, players, position_history)
