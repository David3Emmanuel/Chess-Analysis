import random
from typing import Optional, TYPE_CHECKING
import chess
if TYPE_CHECKING:
    from .analysis import Analysis

def evaluate_board(analysis: 'Analysis') -> tuple[float, Optional[chess.Move], Optional[int]]:
    board = analysis.board
    engine = analysis.engine
    
    move = None
    mate_in = None

    if board.is_game_over():
        result = board.result()
        if result == "1-0":
            eval = float('inf')
        elif result == "0-1":
            eval = float('-inf')
        else:
            eval = 0
    
    else:
        engine.set_fen_position(board.fen())
        raw_eval = engine.get_evaluation()
        best_move_uci = engine.get_best_move()

        if raw_eval['type'] == 'cp':
            eval = raw_eval['value'] / 100.0
        else:
            mate_in = abs(raw_eval['value'])
            eval = float('inf') if raw_eval['value'] > 0 else float('-inf')

        if best_move_uci:
            move = board.parse_uci(best_move_uci)
    
    analysis['eval'] = eval
    analysis['best_move'] = move
    analysis['mate_in'] = mate_in

    return eval, move, mate_in

def process_eval(analysis: 'Analysis'):
    eval = analysis['eval']
    move = analysis['best_move']
    mate_in = analysis['mate_in']
    
    if mate_in is not None:
        winner = "White" if eval > 0 else "Black"
        eval = f"{winner} M{mate_in}"
    if move:
        result = f"{analysis.board.san(move)} ({eval})"
    else:
        result = f"Evaluation: {eval}"

    analysis['move'] = move
    analysis['result'] = result
    return move, result

def random_move(analysis: 'Analysis') -> Optional[chess.Move]:
    board = analysis.board
    
    legal_moves = list(board.legal_moves)
    move = random.choice(legal_moves) if legal_moves else None
    
    analysis['move'] = move
    return move

def extract_move(analysis: 'Analysis') -> Optional[chess.Move]:
    return analysis['move']

def human_move(analysis: 'Analysis') -> Optional[chess.Move]:
    board = analysis.board
    
    print(board)
    print(*board.generate_legal_moves())
    move = None
    
    while not move:
        move_san = input(":: ")
        try:
            move = board.parse_san(move_san)
        except ValueError:
            print('Invalid Move')
    
    analysis['move'] = move
    return move