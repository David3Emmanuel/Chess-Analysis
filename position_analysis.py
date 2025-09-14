from analysis import Analysis
import chess
from chess import PieceType, WHITE, BLACK

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

def position_summary(analysis: Analysis):
    return {feature: analysis[feature] for feature in [
        'material'
    ]}

position_analysis = Analysis() | count_material | position_summary