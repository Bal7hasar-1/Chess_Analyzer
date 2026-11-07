import os
import glob
import time
import chess.pgn
import chess.engine
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


USERNAME = ""



ANALYZE_ALL_PLAYERS = True

PGN_DIR = os.path.join(BASE_DIR, "data", "raw_pgn")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "chess_errors_dataset.csv")
STOCKFISH_PATH = STOCKFISH_PATH = os.path.join(BASE_DIR, "stockfish", "stockfish-windows-x86-64-universal.exe")

ENGINE_DEPTH = 12
CP_LOSS_THRESHOLD = 50  


def extract_errors():
    pgn_files = glob.glob(os.path.join(PGN_DIR, "*.pgn"))
    if not pgn_files:
        print(f"Ошибка: В папке {PGN_DIR} не найдено ни одного файла .pgn")
        return pd.DataFrame()

    print(f"Найдено PGN-файлов: {len(pgn_files)}")
    for f in pgn_files:
        print(f" - {os.path.basename(f)}")
    print(f"\nЗапуск Stockfish: {STOCKFISH_PATH}")
    print("Для досрочной остановки и сохранения собранных данных нажмите Ctrl+C.\n")

    dataset = []
    games_processed = 0
    start_time = time.time()

    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            for pgn_path in pgn_files:
                with open(pgn_path, "r", encoding="utf-8", errors="ignore") as pgn_file:
                    while True:
                        game = chess.pgn.read_game(pgn_file)
                        if game is None:
                            break

                        white_player = game.headers.get("White", "")
                        black_player = game.headers.get("Black", "")

                        my_color = None
                        if white_player.lower() == USERNAME.lower():
                            my_color = chess.WHITE
                        elif black_player.lower() == USERNAME.lower():
                            my_color = chess.BLACK

                        
                        if not ANALYZE_ALL_PLAYERS and my_color is None:
                            continue

                        games_processed += 1
                        print(f"Партия {games_processed}: {white_player} vs {black_player} | Собрано ошибок: {len(dataset)}")

                        board = game.board()
                        
                        prev_info = engine.analyse(board, chess.engine.Limit(depth=ENGINE_DEPTH))

                        for move in game.mainline_moves():
                            player_color = board.turn
                            fen_before_move = board.fen()

                            
                            score_before = prev_info["score"].pov(player_color).score(mate_score=2000)
                            best_move_engine = prev_info.get("pv", [None])[0]

                           
                            board.push(move)

                            
                            curr_info = engine.analyse(board, chess.engine.Limit(depth=ENGINE_DEPTH))
                            score_after = curr_info["score"].pov(player_color).score(mate_score=2000)

                            
                            if ANALYZE_ALL_PLAYERS or (player_color == my_color):
                                if score_before is not None and score_after is not None:
                                    cp_loss = score_before - score_after

                                    if cp_loss >= CP_LOSS_THRESHOLD:
                                        dataset.append({
                                            "fen_before": fen_before_move,
                                            "move_number": board.fullmove_number,
                                            "played_move": move.uci(),
                                            "best_move": best_move_engine.uci() if best_move_engine else None,
                                            "cp_loss": cp_loss,
                                            "eval_before": score_before,
                                            "eval_after": score_after
                                        })

                            prev_info = curr_info

    except KeyboardInterrupt:
        print("\n[!] Анализ остановлен пользователем (Ctrl+C). Сохраняем собранные данные...")
    except FileNotFoundError as e:
        print(f"\nОшибка: Не найден файл движка или PGN.\n{e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"\nПроизошла ошибка при анализе: {e}. Сохраняем то, что успели собрать...")

    elapsed_time = round(time.time() - start_time, 1)
    print(f"\n=== ГОТОВО ===")
    print(f"Проанализировано партий: {games_processed} за {elapsed_time} сек.")
    print(f"Найдено ошибок (cp_loss >= {CP_LOSS_THRESHOLD}): {len(dataset)}")

    return pd.DataFrame(dataset)


if __name__ == "__main__":
    df_errors = extract_errors()

    if not df_errors.empty:
        df_errors.to_csv(OUTPUT_CSV, index=False)
        print(f"Датасет успешно сохранен в: {OUTPUT_CSV}")