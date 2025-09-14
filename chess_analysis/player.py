from .analysis import Analysis
from .analysis_steps import evaluate_board, process_eval, random_move, extract_move, human_move

use_engine = Analysis() | evaluate_board | process_eval
use_random = Analysis() | random_move
use_human = Analysis() | human_move

def player(name: str, pipeline: Analysis):
    pipeline |= extract_move
    pipeline.persist['name'] = name
    return pipeline

engine_player = player('Engine', use_engine)
random_player = player('Random', use_random)
human_player = player('Human', use_human)