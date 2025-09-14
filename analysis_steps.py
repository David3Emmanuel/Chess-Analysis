import random
from typing import Optional
from analysis import Analysis
import chess

def evaluate_board(analysis: Analysis) -> tuple[float, Optional[chess.Move], Optional[int]]:
    board = analysis.board
    engine = analysis.engine

    engine.set_fen_position(board.fen())
    raw_eval = engine.get_evaluation()
    best_move_uci = engine.get_best_move()
    mate_in = None

    if raw_eval['type'] == 'cp':
        eval = raw_eval['value'] / 100.0
    else:
        mate_in = abs(raw_eval['value'])
        eval = float('inf') if raw_eval['value'] > 0 else float('-inf')

    if best_move_uci:
        move = board.parse_uci(best_move_uci)
    else:
        move = None
    
    analysis['eval'] = eval
    analysis['best_move'] = move
    analysis['mate_in'] = mate_in

    return eval, move, mate_in

def process_eval(analysis: Analysis):
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

def random_move(analysis: Analysis) -> Optional[chess.Move]:
    board = analysis.board
    
    legal_moves = list(board.legal_moves)
    move = random.choice(legal_moves) if legal_moves else None
    
    analysis['move'] = move
    return move

def extract_move(analysis: Analysis) -> Optional[chess.Move]:
    return analysis['move']

def human_move(analysis: Analysis) -> Optional[chess.Move]:
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