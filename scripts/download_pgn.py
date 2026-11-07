import requests
import os
import chess.pgn
import io
import time  

def fetch_chesscom_games(username: str, year: int, month: int) -> list:
    month_str = str(month).zfill(2)
    url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month_str}"
    
    headers = {
        "User-Agent": "ML-Chess-Analyzer/2.2 (user: )"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    
    data = response.json()
    parsed_games = []
    
    for game_data in data.get("games", []):
        pgn_string = game_data["pgn"]
        pgn_io = io.StringIO(pgn_string)
        game = chess.pgn.read_game(pgn_io)
        if game is not None:
            parsed_games.append(game)
            
    return parsed_games




username = ""
year = 2026


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw_pgn")
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_filename = os.path.join(OUTPUT_DIR, f"{username}_games_{year}.pgn")


with open(output_filename, "w", encoding="utf-8") as pgn_file:
    
    
    for month in range(1, 13):
        print(f"Скачиваю партии за {month:02d}.{year}...")
        
        
        games_list = fetch_chesscom_games(username, year, month)
        
        if not games_list:
            print("  -> Партий нет (вы не играли в этом месяце или месяц еще не наступил)")
            continue
            
        print(f"  -> Найдено партий: {len(games_list)}")
        
        
        for game in games_list:
            
            print(game, file=pgn_file, end="\n\n")
            
        time.sleep(0.7)

print(f"\nГотово! Все партии успешно сохранены в локальный файл: {output_filename}")