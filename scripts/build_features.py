import os
import time
import pandas as pd
import chess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_CSV = os.path.join(BASE_DIR, "data", "chess_errors_dataset.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "chess_features_dataset.csv")

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}


def get_material_balance(board: chess.Board, player_color: chess.Color) -> int:
    score = 0
    for square, piece in board.piece_map().items():
        val = PIECE_VALUES[piece.piece_type]
        score += val if piece.color == player_color else -val
    return score


def count_hanging_pieces(board: chess.Board, color: chess.Color) -> int:
    opponent = not color
    hanging = 0
    for square, piece in board.piece_map().items():
        if piece.color == color and piece.piece_type != chess.KING:
            if board.is_attacked_by(opponent, square) and not board.is_attacked_by(color, square):
                hanging += 1
    return hanging


def calculate_features(row):
    board_before = chess.Board(row["fen_before"])
    player_color = board_before.turn

    board_played = board_before.copy()
    try:
        board_played.push_uci(str(row["played_move"]))
    except Exception:
        pass

    board_best = board_before.copy()
    has_best_move = False
    if pd.notna(row["best_move"]):
        try:
            board_best.push_uci(str(row["best_move"]))
            has_best_move = True
        except Exception:
            pass

    if not has_best_move:
        return pd.Series({
            "mat_diff": pd.NA,
            "hanging_diff": pd.NA,
            "mobility_diff": pd.NA,
            "best_gives_check": pd.NA,
            "error_class": pd.NA
        })

    mat_diff = get_material_balance(board_best, player_color) - get_material_balance(board_played, player_color)
    hanging_diff = count_hanging_pieces(board_played, player_color) - count_hanging_pieces(board_best, player_color)
    mobility_diff = board_best.legal_moves.count() - board_played.legal_moves.count()
    best_gives_check = int(board_best.is_check())

    if mat_diff >= 3 or row["cp_loss"] > 400:
        error_class = "blunder"          
    elif hanging_diff > 0:
        error_class = "hanging_piece"    
    elif row["cp_loss"] >= 200:
        error_class = "tactical_error"   
    elif row["cp_loss"] < 100:
        error_class = "inaccuracy"       
    else:
        error_class = "positional"       

    return pd.Series({
        "mat_diff": mat_diff,
        "hanging_diff": hanging_diff,
        "mobility_diff": mobility_diff,
        "best_gives_check": best_gives_check,
        "error_class": error_class
    })


if __name__ == "__main__":
    if not os.path.exists(INPUT_CSV):
        print(f"Error: File {INPUT_CSV}  not found. Please run extract_errors.py first.")
        exit()

    print(f"Reading raw errors from: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)

    start_time = time.time()
    print(f"Generating features for {len(df)} positions...")

    features_df = df.apply(calculate_features, axis=1)
    df_final = pd.concat([df, features_df], axis=1)
    df_final = df_final.dropna(subset=["error_class"])

    df_final.to_csv(OUTPUT_CSV, index=False)
    print(f"\n=== DONE in {round(time.time() - start_time, 1)} sec. ===")
    print(f"Dataset saved to: {OUTPUT_CSV}")
    print("\nError type distribution:")
    print(df_final["error_class"].value_counts())