from .analysis_steps import evaluate_board
import chess
from chess import Board, PieceType, WHITE, BLACK
from typing import TYPE_CHECKING
from .analysis import Analysis

if TYPE_CHECKING:
    from .engine import Engine

PIECE_VALUES: dict[PieceType, int] = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def count_material(analysis: 'Analysis'):
    board = analysis.board
    points = [0, 0]
    
    for piece in board.piece_map().values():
        value = PIECE_VALUES[piece.piece_type]
        points[piece.color] += value
    
    analysis['material_points'] = points
    analysis['material'] = points[WHITE] - points[BLACK]
    analysis['white_material'] = points[WHITE]
    analysis['black_material'] = points[BLACK]
    return points

def measure_development(analysis: 'Analysis'):
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
    analysis['white_development'] = development[WHITE]
    analysis['black_development'] = development[BLACK]
    return development

def evaluate_mobility(analysis: 'Analysis'):
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
    analysis['white_mobility'] = mobility[WHITE]
    analysis['black_mobility'] = mobility[BLACK]
    return mobility

def check_castled(analysis: 'Analysis'):
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

def position_summary(analysis: 'Analysis'):
    summary = {feature: analysis[feature] for feature in [
        'material',
        'white_material',
        'black_material',
        'development',
        'white_development',
        'black_development',
        'mobility',
        'white_mobility',
        'black_mobility',
        'white_has_castled',
        'black_has_castled',
        'fullmove_number',
        'halfmove_clock',
        'furthest_rank',
        'white_furthest_rank',
        'black_furthest_rank',
        'white_king_file',
        'white_king_rank',
        'black_king_file',
        'black_king_rank'
    ]}
    
    eval_value = analysis['eval']
    if not eval_value: return summary
    
    if eval_value >= 20:
        summary['eval'] = 20
    elif eval_value <= -20:
        summary['eval'] = -20
    else:
        summary['eval'] = eval_value
        
    return summary

def count_moves(analysis: 'Analysis'):
    board = analysis.board
    analysis['fullmove_number'] = board.fullmove_number
    analysis['halfmove_clock'] = board.halfmove_clock
    return board.fullmove_number, board.halfmove_clock

def get_furthest_rank(analysis: 'Analysis'):
    board = analysis.board
    furthest_rank = [0, 0]

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            color = piece.color
            rank = chess.square_rank(square)
            if color == BLACK: rank = 7 - rank
            if rank > furthest_rank[color]:
                furthest_rank[color] = rank

    analysis['furthest_rank'] = furthest_rank[WHITE] - furthest_rank[BLACK]
    analysis['white_furthest_rank'] = furthest_rank[WHITE]
    analysis['black_furthest_rank'] = furthest_rank[BLACK]
    return furthest_rank

def get_king_positions(analysis: 'Analysis'):
    board = analysis.board
    for square, piece in board.piece_map().items():
        if piece.piece_type == chess.KING:
            rank = chess.square_rank(square)
            if piece.color == BLACK: rank = 7 - rank
            file = chess.square_file(square)
            if piece.color == WHITE:
                analysis['white_king_file'] = file
                analysis['white_king_rank'] = rank
            else:
                analysis['black_king_file'] = file
                analysis['black_king_rank'] = rank

raw_eval = (Analysis()
            | count_material 
            | measure_development 
            | evaluate_mobility 
            | check_castled
            | count_moves
            | get_furthest_rank
            | get_king_positions)
position_analysis = raw_eval.copy() | evaluate_board | position_summary
position_analysis_without_eval = raw_eval.copy() | position_summary

def custom_position_analysis(engine: 'Engine'):
    return position_analysis.copy_with_engine(engine)