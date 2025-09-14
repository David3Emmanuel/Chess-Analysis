import chess

from util import display_board, export_game
from player import engine_player, random_player
from display import is_closed, finish_display
from position_analysis import position_analysis

board = chess.Board()
for move in "".split():
    board.push_san(move)

players = [engine_player, random_player]

while not (board.is_game_over() or is_closed()):
    player = players[1 - board.turn]
    move = player(board)
    print(f'{player['name']} - {board.san(move)}')
    board.push(move)
    display_board(board, move, pov=chess.WHITE)
    
    position = position_analysis(board)
    print(position)

finish_display()
export_game(board, players)