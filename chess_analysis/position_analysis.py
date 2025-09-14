from .analysis import Analysis
from .analysis_steps import evaluate_board
import chess
from chess import Board, PieceType, WHITE, BLACK

PIECE_VALUES: dict[PieceType, int] = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def count_material(analysis: Analysis):
    board = analysis.board
    points = [0, 0]
    
    for piece in board.piece_map().values():
        value = PIECE_VALUES[piece.piece_type]
        points[piece.color] += value
    
    analysis['material_points'] = points
    analysis['material'] = points[WHITE] - points[BLACK]
    return points

def measure_development(analysis: Analysis):
    board = analysis.board
    development = [0., 0.]

    starting_board = chess.Board()
    
    # Count how many of each piece type started and how many remain
    for color in [WHITE, BLACK]:
        starting_counts = {}
        current_counts = {}
        
        # Count starting pieces by type
        for square in chess.SQUARES:
            piece = starting_board.piece_at(square)
            if piece and piece.color == color:
                starting_counts[piece.piece_type] = starting_counts.get(piece.piece_type, 0) + 1
        
        # Count current pieces by type
        for piece in board.piece_map().values():
            if piece.color == color:
                current_counts[piece.piece_type] = current_counts.get(piece.piece_type, 0) + 1
        
        # Count moved pieces that haven't been captured
        moved_count = {}
        for square in chess.SQUARES:
            starting_piece = starting_board.piece_at(square)
            current_piece = board.piece_at(square)
            
            if (starting_piece is not None and 
                starting_piece.color == color and 
                starting_piece != current_piece):
                
                piece_type = starting_piece.piece_type
                moved_count[piece_type] = moved_count.get(piece_type, 0) + 1
        
        # Only count development for pieces that moved but weren't captured
        for piece_type, moved in moved_count.items():
            captured = starting_counts.get(piece_type, 0) - current_counts.get(piece_type, 0)
            developed = max(0, moved - captured)
            
            if piece_type in [chess.KNIGHT, chess.BISHOP]:  # Minor pieces
                development[color] += developed * 2
            elif piece_type in [chess.QUEEN, chess.ROOK]:  # Major pieces
                development[color] += developed * 1

    analysis['development'] = development[WHITE] - development[BLACK]
    return development

def evaluate_mobility(analysis: Analysis):
    board = analysis.board
    mobility = [0, 0]
    turn = board.turn

    for color in [WHITE, BLACK]:
        board.turn = color
        # Count the number of legal moves for each piece
        for move in board.legal_moves:
            piece = board.piece_at(move.from_square)
            if piece and piece.color == color:
                mobility[color] += 1

    board.turn = turn

    analysis['mobility'] = mobility[WHITE] - mobility[BLACK]
    return mobility

def check_castled(analysis: Analysis):
    board = analysis.board
    has_castled = [False, False]
    
    temp_board = Board()
    for move in board.move_stack:
        if temp_board.is_castling(move):
            has_castled[temp_board.turn] = True
        temp_board.push(move)
        if has_castled[WHITE] and has_castled[BLACK]:
            break

    analysis['white_has_castled'] = has_castled[WHITE]
    analysis['black_has_castled'] = has_castled[BLACK]
    
    return has_castled

def position_summary(analysis: Analysis):
    summary = {feature: analysis[feature] for feature in [
        'material',
        'development',
        'mobility',
        'white_has_castled',
        'black_has_castled'
    ]}
    
    eval_value = analysis['eval']
    if eval_value >= 20:
        summary['eval'] = 20
    elif eval_value <= -20:
        summary['eval'] = -20
    else:
        summary['eval'] = eval_value
        
    return summary

position_analysis = (Analysis() 
                   | evaluate_board 
                   | count_material 
                   | measure_development 
                   | evaluate_mobility 
                   | check_castled 
                   | position_summary)