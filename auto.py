import chess

from util import display_board, export_game, save_position_history
from player import engine_player, random_player
from display import is_closed, finish_display, plot_position_history
from position_analysis import position_analysis

board = chess.Board()
for move in "".split():
    board.push_san(move)

players = [engine_player, random_player]
position_history = []

initial_position = position_analysis(board)
position_history.append({
    'move_number': 0,
    'fen': board.fen(),
    'last_move': None,
    'analysis': initial_position.copy()
})

while not (board.is_game_over() or is_closed()):
    player = players[1 - board.turn]
    move = player(board)
    move_san = board.san(move)
    print(f'{player['name']} - {move_san}')
    board.push(move)
    display_board(board, move, pov=chess.WHITE)
    
    position = position_analysis(board)
    position_history.append({
        'move_number': len(position_history),
        'fen': board.fen(),
        'last_move': move_san,
        'analysis': position.copy()
    })

finish_display()
save_position_history(position_history)
plot_position_history(position_history)
export_game(board, players)