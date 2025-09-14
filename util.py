import chess
import chess.svg
import chess.pgn
from typing import Optional
from display import display_svg
from analysis import Analysis

def display_board(board: chess.Board, move: Optional[chess.Move] = None, pov: Optional[chess.Color] = None) -> None:
    svg = chess.svg.board(
        board, size=400,
        lastmove=move,
        orientation=board.turn if pov is None else pov
    )
    display_svg(svg)

def export_game(board: chess.Board, players: list[Analysis]) -> None:
    game = chess.pgn.Game.from_board(board)
    game.headers['White'] = players[0]['name']
    game.headers['Black'] = players[1]['name']
    
    with open("game.pgn", "w") as f:
        exporter = chess.pgn.FileExporter(f)
        game.accept(exporter)
