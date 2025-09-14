import chess
import chess.svg
import chess.pgn
from typing import Optional
from .display import display_svg
from .analysis import Analysis

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

def save_position_history(position_history):
    with open("analysis.txt", "w") as f:
        f.write("=" * 50 + "\n")
        f.write("POSITION ANALYSIS HISTORY\n")
        f.write("=" * 50 + "\n")
        for i, entry in enumerate(position_history):
            f.write(f"\nMove {entry['move_number']}: {entry['last_move'] or 'Starting position'}\n")
            f.write(f"FEN: {entry['fen']}\n")
            analysis = entry['analysis']
            f.write(f"Material: {analysis.get('material', 0):+.1f}\n")
            f.write(f"Development: {analysis.get('development', 0):+.1f}\n")
            f.write(f"Mobility: {analysis.get('mobility', 0):+.1f}\n")
            f.write(f"Evaluation: {analysis.get('eval', 0):+.1f}\n")