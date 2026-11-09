import os
import io
import math
import webbrowser
import threading
import importlib
import importlib.util
import requests
import tkinter as tk
from tkinter import messagebox, filedialog
import chess
import chess.pgn
import chess.engine
import pandas as pd
import joblib
from datetime import datetime, timedelta, timezone


HAS_PIL = importlib.util.find_spec("PIL") is not None
if HAS_PIL:
    PIL_Image = importlib.import_module("PIL.Image")
    PIL_ImageTk = importlib.import_module("PIL.ImageTk")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USERNAME = ""
TARGET_USERNAME = ""
STOCKFISH_PATH = os.path.join(BASE_DIR, "stockfish", "stockfish-windows-x86-64-universal.exe")
MODEL_PATH = os.path.join(BASE_DIR, "models", "chess_error_model.joblib")
AVATAR_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "images.jpg")
USER_AGENT = "ML-Chess-Analyzer/2.4 (user: )"

ENGINE_DEPTH = 12
CP_LOSS_THRESHOLD = 50


THEME = {
    "bg_root": "#161513",          
    "bg_panel": "#211F1C",         
    "bg_panel_elev": "#2B2824",    
    "bg_bubble": "#2A2723",        
    "bg_bubble_active": "#38322A", 
    "bg_bubble_hover": "#312D28",  
    "border_subtle": "#38342E",    
    "border_active": "#C08E3A",    
    "text_primary": "#E8DCC7",     
    "text_secondary": "#B08B6E",   
    "text_muted": "#8B8072",       
    "accent_sage": "#8B9D83",      
    "accent_ochre": "#C08E3A",     
    "accent_terra": "#C66B3D",     
    "accent_moss": "#606C38",     
    
    "sq_light": "#EDD6B0",         
    "sq_dark": "#B58863",          
    "sq_last_light": "#F3E07B",    
    "sq_last_dark": "#CFA840",     
    "sq_selected": "#8B9D83",      
    "sq_check": "#C66B3D",         
    
    "eval_white": "#E8DCC7",       
    "eval_black": "#26231F",       
}


BADGE_STYLE = {
    "brilliant": {"color": "#26C2A3"},
    "great":     {"color": "#749BBF"},
    "book":      {"color": "#D5A47D"},
    "best":      {"color": "#81B64C"},
    "excellent": {"color": "#81B64C"},
    "good":      {"color": "#95B776"},
    "inaccuracy":{"color": "#F7C045"},
    "mistake":   {"color": "#E58F3A"},
    "miss":      {"color": "#EE6B5E"},
    "blunder":   {"color": "#FA412D"},
}

PIECE_VALUES = {
    chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
    chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
}


TRANSLATIONS = {
    "ru": {
        "white_default": "Белые",
        "black_default": "Чёрные",
        "role_me": "Я",
        "role_opp": "Соперник",
        "side_white": "Белые",
        "side_black": "Чёрные",
        "analyzing_short": "Анализ партии...",
        "your_turn": "Ваш ход",
        "opp_turn": "Ход соперника",
        "move_of": "Ход {cur} из {total}",
        "detecting": "Определяется...",
        "unknown_op": "Не определён",
        "btn_prev": "◀ Назад",
        "btn_next": "Вперёд ▶",
        "btn_flip": "⇅ Перевернуть",
        "btn_best": "Лучший ход",
        "btn_combo": "Показать комбинацию",
        "btn_combo_stop": "Вернуться к позиции",
        "btn_return_live": "К ходу {move} ▶",
        "chat_analyzing": "Анализирует вашу партию...",
        "chat_found": "Найдено ошибок в партии: {count}",
        "unlock_all": "Показать все ошибки",
        "typing_wait": "Mistakes следит за ходами партии...",
        "card_header": "Mistakes  •  Ход {move}",
        "card_moves": "Сыграно: {played}   →   Лучше было: {best}",
        "card_btn_best": "Показать лучший ход",
        "card_btn_combo": "Комбинация",
        "history_title": "История ходов",
        "history_empty": "Сделайте ход (Вперёд ▶)",
        "graph_title": "График преимущества",
        "acc_label": "Точность: {acc:.1f}%",
        "acc_short": "Точн: Б {w:.1f}% • Ч {b:.1f}%",
        "err_titles": {
            "blunder": "Грубый зевок",
            "hanging_piece": "Фигура под боем",
            "tactical_error": "Упущенная тактика",
            "positional": "Позиционная ошибка",
            "inaccuracy": "Неточность",
        },
        "piece_names": {
            chess.PAWN: "Пешка", chess.KNIGHT: "Конь",
            chess.BISHOP: "Слон", chess.ROOK: "Ладья",
            chess.QUEEN: "Ферзь", chess.KING: "Король",
        },
        "on_sq": "на",
        "lang_label": "Язык:",
    },
    "en": {
        "white_default": "White",
        "black_default": "Black",
        "role_me": "You",
        "role_opp": "Opponent",
        "side_white": "White",
        "side_black": "Black",
        "analyzing_short": "Analyzing game...",
        "your_turn": "Your turn",
        "opp_turn": "Opponent's turn",
        "move_of": "Move {cur} of {total}",
        "detecting": "Detecting...",
        "unknown_op": "Unknown",
        "btn_prev": "◀ Back",
        "btn_next": "Next ▶",
        "btn_flip": "⇅ Flip Board",
        "btn_best": "Best Move",
        "btn_combo": "Show Combination",
        "btn_combo_stop": "Back to Position",
        "btn_return_live": "To Move {move} ▶",
        "chat_analyzing": "Analyzing your game...",
        "chat_found": "Mistakes found in game: {count}",
        "unlock_all": "Show all mistakes",
        "typing_wait": "Mistakes is watching the game...",
        "card_header": "Mistakes  •  Move {move}",
        "card_moves": "Played: {played}   →   Best was: {best}",
        "card_btn_best": "Show Best Move",
        "card_btn_combo": "Combination",
        "history_title": "Move History",
        "history_empty": "Make a move (Next ▶)",
        "graph_title": "Advantage Graph",
        "acc_label": "Accuracy: {acc:.1f}%",
        "acc_short": "Acc: W {w:.1f}% • B {b:.1f}%",
        "err_titles": {
            "blunder": "Blunder",
            "hanging_piece": "Hanging Piece",
            "tactical_error": "Missed Tactic",
            "positional": "Positional Mistake",
            "inaccuracy": "Inaccuracy",
        },
        "piece_names": {
            chess.PAWN: "Pawn", chess.KNIGHT: "Knight",
            chess.BISHOP: "Bishop", chess.ROOK: "Rook",
            chess.QUEEN: "Queen", chess.KING: "King",
        },
        "on_sq": "on",
        "lang_label": "Lang:",
    }
}

ERROR_COLORS = {
    "blunder": "#C66B3D",
    "hanging_piece": "#C66B3D",
    "tactical_error": "#C08E3A",
    "positional": "#8B9D83",
    "inaccuracy": "#B08B6E"
}


WHITE_OPENINGS_BOOK = [
    (["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"], "Испанская партия (Руй Лопес)", "Ruy Lopez"),
    (["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "b2b4"], "Гамбит Эванса", "Evans Gambit"),
    (["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"], "Итальянская партия", "Italian Game"),
    (["e2e4", "e7e5", "g1f3", "b8c6", "d2d4"], "Шотландская партия", "Scotch Game"),
    (["e2e4", "e7e5", "d2d4", "e5d4", "c2c3"], "Северный гамбит", "Danish Gambit"),
    (["e2e4", "e7e5", "f2f4"], "Королевский гамбит", "King's Gambit"),
    (["e2e4", "e7e5", "b1c3"], "Венская партия", "Vienna Game"),
    (["e2e4", "e7e5", "f1c4"], "Дебют слона", "Bishop's Opening"),
    (["e2e4", "c7c5", "d2d4", "c5d4", "c2c3"], "Гамбит Морра", "Smith-Morra Gambit"),
    (["e2e4", "c7c5", "g1f3"], "Открытая сицилианская", "Open Sicilian"),
    (["e2e4", "c7c5", "b1c3"], "Закрытая сицилианская", "Closed Sicilian"),
    (["d2d4", "d7d5", "c2c4"], "Ферзевый гамбит", "Queen's Gambit"),
    (["d2d4", "d7d5", "f1f4"], "Лондонская система", "London System"),
    (["d2d4", "g8f6", "f1f4"], "Лондонская система", "London System"),
    (["d2d4", "g8f6", "c2c4", "g7g6", "g2g3"], "Каталонское начало", "Catalan Opening"),
    (["d2d4", "f7f5", "e2e4"], "Гамбит Стаунтона", "Staunton Gambit"),
    (["c2c4"], "Английское начало", "English Opening"),
    (["g1f3"], "Дебют Рети", "Reti Opening"),
    (["f2f4"], "Дебют Бёрда", "Bird's Opening"),
    (["b2b3"], "Дебют Ларсена", "Larsen's Opening"),
    (["e2e4"], "Дебют королевской пешки", "King's Pawn Game"),
    (["d2d4"], "Дебют ферзевой пешки", "Queen's Pawn Game"),
]

BLACK_OPENINGS_BOOK = [
    (["e2e4", "c7c5"], "Сицилианская защита", "Sicilian Defense"),
    (["e2e4", "e7e6"], "Французская защита", "French Defense"),
    (["e2e4", "c7c6"], "Защита Каро-Канн", "Caro-Kann Defense"),
    (["e2e4", "d7d5"], "Скандинавская защита", "Scandinavian Defense"),
    (["e2e4", "d7d6", "d2d4", "g8f6"], "Защита Пирца-Уфимцева", "Pirc Defense"),
    (["e2e4", "g8f6"], "Защита Алехина", "Alekhine's Defense"),
    (["e2e4", "e7e5", "g1f3", "g8f6", "f3e5", "b8c6"], "Гамбит Стаффорда", "Stafford Gambit"),
    (["e2e4", "e7e5", "g1f3", "g8f6"], "Русская партия (Защита Петрова)", "Petrov's Defense"),
    (["e2e4", "e7e5", "g1f3", "d7d6"], "Защита Филидора", "Philidor Defense"),
    (["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6"], "Защита двух коней", "Two Knights Defense"),
    (["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"], "Итальянская (Giuoco Piano)", "Giuoco Piano"),
    (["e2e4", "e7e5", "g1f3", "f7f5"], "Латышский гамбит", "Latvian Gambit"),
    (["e2e4", "e7e5", "g1f3", "b8c6"], "Классическая защита (2...Nc6)", "Classical Defense (2...Nc6)"),
    (["e2e4", "e7e5"], "Симметричный ответ (1...e5)", "Symmetrical Response (1...e5)"),
    (["d2d4", "e7e5"], "Гамбит Энглунда", "Englund Gambit"),
    (["d2d4", "d7d5", "c2c4", "d5c4"], "Принятый ферзевый гамбит", "Queen's Gambit Accepted"),
    (["d2d4", "d7d5", "c2c4", "e7e6"], "Отказанный ферзевый гамбит", "Queen's Gambit Declined"),
    (["d2d4", "d7d5", "c2c4", "c7c6"], "Славянская защита", "Slav Defense"),
    (["d2d4", "d7d5", "c2c4", "e7e5"], "Контргамбит Альбина", "Albin Countergambit"),
    (["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "d7d5"], "Защита Грюнфельда", "Gruenfeld Defense"),
    (["d2d4", "g8f6", "c2c4", "g7g6"], "Староиндийская защита", "King's Indian Defense"),
    (["d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4"], "Защита Нимцовича", "Nimzo-Indian Defense"),
    (["d2d4", "g8f6", "c2c4", "c7c5", "d4d5", "b7b5"], "Волжский гамбит", "Benko Gambit"),
    (["d2d4", "g8f6", "c2c4", "e7e5"], "Будапештский гамбит", "Budapest Gambit"),
    (["d2d4", "f7f5"], "Голландская защита", "Dutch Defense"),
    (["d2d4", "g8f6"], "Индийская защита", "Indian Defense"),
    (["d2d4", "d7d5"], "Закрытая защита (1...d5)", "Closed Defense (1...d5)"),
]


def is_book_ply(moves_uci: list) -> bool:
    """Проверяет, входит ли текущая последовательность ходов в дебютную книгу."""
    if not moves_uci or len(moves_uci) > 10:
        return False
    for book in (WHITE_OPENINGS_BOOK, BLACK_OPENINGS_BOOK):
        for item in book:
            pattern = item[0]
            if len(moves_uci) <= len(pattern) and moves_uci == pattern[:len(moves_uci)]:
                return True
    return False


def compute_move_accuracy(cp_loss: float) -> float:
    """Переводит потерю сантипешек (cp_loss) на ходе в процент точности (0..100%)."""
    loss = max(0.0, float(cp_loss))
    acc = 100.0 * math.exp(-0.0038 * loss)
    return max(0.0, min(100.0, acc))


def detect_openings_at_ply(moves_uci: list, pgn_opening_name: str = "", lang: str = "en"):
    """Определяет дебют или гамбит отдельно для Белых и Чёрных на выбранном языке (ru/en)."""
    tr = TRANSLATIONS[lang]
    detecting_str = tr["detecting"]
    unknown_str = tr["unknown_op"]

    if len(moves_uci) == 0:
        return detecting_str, detecting_str

    white_op = detecting_str
    black_op = detecting_str
    idx = 1 if lang == "ru" else 2

    for item in WHITE_OPENINGS_BOOK:
        pattern = item[0]
        if len(moves_uci) >= len(pattern) and moves_uci[:len(pattern)] == pattern:
            white_op = item[idx]
            break

    if len(moves_uci) >= 2:
        for item in BLACK_OPENINGS_BOOK:
            pattern = item[0]
            if len(moves_uci) >= len(pattern) and moves_uci[:len(pattern)] == pattern:
                black_op = item[idx]
                break
        if black_op == detecting_str:
            black_op = pgn_opening_name if pgn_opening_name else unknown_str

    generic_white = (
        "Дебют королевской пешки", "Дебют ферзевой пешки",
        "King's Pawn Game", "Queen's Pawn Game", detecting_str
    )
    generic_black = (
        "Симметричный ответ (1...e5)", "Закрытая защита (1...d5)",
        "Symmetrical Response (1...e5)", "Closed Defense (1...d5)", unknown_str
    )

    if len(moves_uci) >= 6 and pgn_opening_name:
        if white_op in generic_white:
            white_op = pgn_opening_name
        if black_op in generic_black:
            black_op = pgn_opening_name

    return white_op, black_op


def build_localized_error_texts(err: dict, lang: str) -> tuple:
    """Динамически формирует (ai_text, combo_title) на выбранном языке (ru/en)."""
    pred = err["prediction"]
    played_san = err["played_san"]
    best_san = err["best_san"]
    punish_line = err["punish_line_san"]
    best_line = err["best_line_san"]
    attacked_names = err["attacked_names"]

    tr = TRANSLATIONS[lang]
    piece_names = tr["piece_names"]
    on_word = tr["on_sq"]
    hanging_Str = ", ".join(
        f"{piece_names[p_type]} {on_word} {chess.square_name(sq)}"
        for p_type, sq in err["hanging_pieces_raw"]
    )

    if lang == "ru":
        if pred == "blunder":
            ai_text = (
                f"Позиция резко ухудшается после {played_san}. "
                f"Соперник перехватывает инициативу серией: {punish_line}."
            )
            combo_title = "Опровержение соперника"
        elif pred == "hanging_piece":
            if hanging_Str:
                ai_text = f"Без надёжной защиты осталась фигура: {hanging_Str}. Противник использует это: {punish_line}."
            else:
                ai_text = f"Ход {played_san} приводит к неизбежным материальным потерям в варианте: {punish_line}."
            combo_title = "Атака на незащищённую фигуру"
        elif pred == "tactical_error":
            ai_text = (
                f"Упущена тактика! Ход {best_san} начинал сильную комбинацию: {best_line}. "
                f"Фигура брала под бой поля: {attacked_names}."
            )
            combo_title = "Ваша упущенная комбинация"
        elif pred == "inaccuracy":
            ai_text = (
                f"Небольшая неточность. Ход {best_san} точнее сохранял темп и контролировал поля: {attacked_names}."
            )
            combo_title = "Точное продолжение"
        else:
            ai_text = (
                f"Позиционная уступка. Стоило сыграть {best_san} для активного контроля полей ({attacked_names})."
            )
            combo_title = "Позиционный план"
    else:
        if pred == "blunder":
            ai_text = (
                f"The position collapses after {played_san}. "
                f"Your opponent seizes the initiative with: {punish_line}."
            )
            combo_title = "Opponent's Refutation"
        elif pred == "hanging_piece":
            if hanging_Str:
                ai_text = f"Left undefended: {hanging_Str}. Your opponent can punish this via: {punish_line}."
            else:
                ai_text = f"Move {played_san} leads to unavoidable material loss in the line: {punish_line}."
            combo_title = "Attack on Hanging Piece"
        elif pred == "tactical_error":
            ai_text = (
                f"Missed tactic! Playing {best_san} launched a strong combination: {best_line}. "
                f"It targeted squares: {attacked_names}."
            )
            combo_title = "Your Missed Combination"
        elif pred == "inaccuracy":
            ai_text = (
                f"Slight inaccuracy. Playing {best_san} kept better tempo and controlled squares: {attacked_names}."
            )
            combo_title = "Accurate Continuation"
        else:
            ai_text = (
                f"Positional concession. Playing {best_san} offered active control over key squares ({attacked_names})."
            )
            combo_title = "Positional Plan"

    return ai_text, combo_title


def hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(rgb[0]))),
        max(0, min(255, int(rgb[1]))),
        max(0, min(255, int(rgb[2])))
    )


def blend_colors(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t))


def create_rounded_rect(canvas: tk.Canvas, x1, y1, x2, y2, r=16, **kwargs):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def draw_move_classification_badge(canvas: tk.Canvas, cx: float, cy: float, radius: float, badge_type: str):
    """
    Отрисовывает САМ ЗНАЧОК оценки хода (!!, !, ?!, ?, ??, ★, 📖, ✔, 👍, ✖)
    соответствующего яркого цвета БЕЗ фонового кружка, с тёмным микро-контуром для читаемости.
    """
    if not badge_type or badge_type not in BADGE_STYLE:
        return
    col = BADGE_STYLE[badge_type]["color"]
    shadow = "#161513"

    def draw_outlined_text(txt: str, f_size: int):
        fnt = ("Segoe UI", f_size, "bold")
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, 1.5)):
            canvas.create_text(cx + dx, cy + dy, text=txt, fill=shadow, font=fnt)
        canvas.create_text(cx, cy, text=txt, fill=col, font=fnt)

    if badge_type == "brilliant":
        draw_outlined_text("!!", max(9, int(radius * 1.45)))
    elif badge_type == "great":
        draw_outlined_text("!", max(9, int(radius * 1.50)))
    elif badge_type == "inaccuracy":
        draw_outlined_text("?!", max(8, int(radius * 1.35)))
    elif badge_type == "mistake":
        draw_outlined_text("?", max(9, int(radius * 1.50)))
    elif badge_type == "blunder":
        draw_outlined_text("??", max(8, int(radius * 1.35)))
    elif badge_type == "best":
        
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            r = radius * 0.92 if i % 2 == 0 else radius * 0.40
            pts.extend([cx + r * math.cos(ang), cy + r * math.sin(ang)])
        canvas.create_polygon(pts, fill=col, outline=shadow, width=max(1.2, radius * 0.14), joinstyle=tk.ROUND)
    elif badge_type == "good":
        
        lw = max(2.2, radius * 0.34)
        pts = [
            cx - radius * 0.65, cy + radius * 0.04,
            cx - radius * 0.15, cy + radius * 0.55,
            cx + radius * 0.70, cy - radius * 0.50
        ]
        canvas.create_line(pts, fill=shadow, width=lw + 2.2, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        canvas.create_line(pts, fill=col, width=lw, capstyle=tk.ROUND, joinstyle=tk.ROUND)
    elif badge_type == "miss":
        
        lw = max(2.2, radius * 0.34)
        d = radius * 0.55
        canvas.create_line(cx - d, cy - d, cx + d, cy + d, fill=shadow, width=lw + 2.2, capstyle=tk.ROUND)
        canvas.create_line(cx - d, cy + d, cx + d, cy - d, fill=shadow, width=lw + 2.2, capstyle=tk.ROUND)
        canvas.create_line(cx - d, cy - d, cx + d, cy + d, fill=col, width=lw, capstyle=tk.ROUND)
        canvas.create_line(cx - d, cy + d, cx + d, cy - d, fill=col, width=lw, capstyle=tk.ROUND)
    elif badge_type == "book":
        
        w = radius * 0.78
        h = radius * 0.58
        canvas.create_polygon(
            [cx, cy - h * 0.7, cx - w, cy - h, cx - w, cy + h * 0.85, cx, cy + h],
            fill=col, outline=shadow, width=1.4
        )
        canvas.create_polygon(
            [cx, cy - h * 0.7, cx + w, cy - h, cx + w, cy + h * 0.85, cx, cy + h],
            fill=col, outline=shadow, width=1.4
        )
        canvas.create_line(cx, cy - h * 0.7, cx, cy + h, fill=shadow, width=max(1.2, radius * 0.16))
    elif badge_type == "excellent":
        
        r = radius * 1.25
        canvas.create_rectangle(
            cx - r * 0.52, cy - r * 0.05, cx - r * 0.22, cy + r * 0.46,
            fill=col, outline=shadow, width=1.2
        )
        pts = [
            cx - r * 0.16, cy - r * 0.05,
            cx - r * 0.02, cy - r * 0.54,
            cx + r * 0.18, cy - r * 0.48,
            cx + r * 0.12, cy - r * 0.10,
            cx + r * 0.50, cy - r * 0.10,
            cx + r * 0.40, cy + r * 0.46,
            cx - r * 0.16, cy + r * 0.46,
        ]
        canvas.create_polygon(pts, fill=col, outline=shadow, width=1.2, joinstyle=tk.ROUND)


def draw_mistakes_knight_avatar(canvas: tk.Canvas, cx: float, cy: float, size: float, photo_cache=None):
    """Отрисовывает аватарку Mistakes (контур коня на светлом бейдже)."""
    r = size / 2
    create_rounded_rect(
        canvas, cx - r, cy - r, cx + r, cy + r,
        r=size * 0.34, fill="#E8DCC7", outline=THEME["border_subtle"], width=1.5
    )

    if HAS_PIL and photo_cache is not None and os.path.exists(AVATAR_IMAGE_PATH):
        try:
            key = f"avatar_{int(size)}"
            if key not in photo_cache:
                img = PIL_Image.open(AVATAR_IMAGE_PATH).convert("RGBA")
                inner = max(14, int(size * 0.72))
                img = img.resize((inner, inner), PIL_Image.Resampling.LANCZOS)
                photo_cache[key] = PIL_ImageTk.PhotoImage(img)
            canvas.create_image(cx, cy, image=photo_cache[key])
            return
        except Exception:
            pass

    s = size * 0.38
    lw = max(2.0, size * 0.068)

    outer_pts = [
        cx - 0.16 * s, cy - 0.56 * s,
        cx - 0.52 * s, cy - 0.25 * s,
        cx - 0.66 * s, cy + 0.12 * s,
        cx - 0.85 * s, cy + 0.34 * s,
        cx - 0.78 * s, cy + 0.52 * s,
        cx - 0.58 * s, cy + 0.45 * s,
        cx - 0.64 * s, cy + 0.58 * s,
        cx - 0.45 * s, cy + 0.52 * s,
        cx - 0.25 * s, cy + 0.24 * s,
        cx + 0.08 * s, cy + 0.02 * s,
    ]
    canvas.create_line(outer_pts, fill="#161513", width=lw, capstyle=tk.ROUND, joinstyle=tk.ROUND, smooth=True)

    ears_pts = [
        cx - 0.38 * s, cy - 0.44 * s,
        cx - 0.42 * s, cy - 0.84 * s,
        cx - 0.16 * s, cy - 0.64 * s,
        cx + 0.04 * s, cy - 0.86 * s,
        cx + 0.18 * s, cy - 0.56 * s,
    ]
    canvas.create_line(ears_pts, fill="#161513", width=lw, capstyle=tk.ROUND, joinstyle=tk.ROUND)

    mane_base_pts = [
        cx + 0.18 * s, cy - 0.56 * s,
        cx + 0.65 * s, cy - 0.42 * s,
        cx + 0.86 * s, cy + 0.18 * s,
        cx + 0.90 * s, cy + 0.82 * s,
        cx - 0.36 * s, cy + 0.82 * s,
        cx - 0.32 * s, cy + 0.55 * s,
        cx - 0.04 * s, cy + 0.12 * s,
    ]
    canvas.create_line(mane_base_pts, fill="#161513", width=lw, capstyle=tk.ROUND, joinstyle=tk.ROUND)

    canvas.create_line(
        cx - 0.44 * s, cy - 0.18 * s, cx - 0.30 * s, cy - 0.28 * s,
        fill="#161513", width=lw * 0.95, capstyle=tk.ROUND
    )
    canvas.create_oval(
        cx - 0.72 * s, cy + 0.26 * s, cx - 0.62 * s, cy + 0.36 * s,
        fill="#161513", outline="#161513"
    )


def draw_classic_merida_piece(canvas: tk.Canvas, cx: float, cy: float, sq_size: float, piece_type: int, is_white: bool):
    """Классический векторный рендерер фигур Merida."""
    r = sq_size * 0.415
    fill_col = "#FFFFFF" if is_white else "#0C0C0C"
    stroke_col = "#0C0C0C"
    inner_col = "#0C0C0C" if is_white else "#FFFFFF"
    lw = max(1.4, sq_size * 0.038)
    ilw = max(1.1, sq_size * 0.028)

    if piece_type == chess.PAWN:
        body_pts = [
            cx - 0.62 * r, cy + 0.82 * r,
            cx + 0.62 * r, cy + 0.82 * r,
            cx + 0.58 * r, cy + 0.64 * r,
            cx + 0.44 * r, cy + 0.50 * r,
            cx + 0.24 * r, cy + 0.20 * r,
            cx + 0.36 * r, cy - 0.04 * r,
            cx - 0.36 * r, cy - 0.04 * r,
            cx - 0.24 * r, cy + 0.20 * r,
            cx - 0.44 * r, cy + 0.50 * r,
            cx - 0.58 * r, cy + 0.64 * r,
        ]
        canvas.create_polygon(body_pts, fill=fill_col, outline=stroke_col, width=lw, joinstyle=tk.ROUND)
        canvas.create_oval(
            cx - 0.35 * r, cy - 0.70 * r, cx + 0.35 * r, cy - 0.02 * r,
            fill=fill_col, outline=stroke_col, width=lw
        )
        if is_white:
            canvas.create_line(cx - 0.48 * r, cy + 0.64 * r, cx + 0.48 * r, cy + 0.64 * r, fill=inner_col, width=ilw)
            canvas.create_line(cx - 0.32 * r, cy - 0.04 * r, cx + 0.32 * r, cy - 0.04 * r, fill=inner_col, width=ilw)
        else:
            canvas.create_line(cx - 0.44 * r, cy + 0.68 * r, cx + 0.44 * r, cy + 0.68 * r, fill=inner_col, width=ilw * 0.9)

    elif piece_type == chess.ROOK:
        pts = [
            cx - 0.70 * r, cy + 0.82 * r,
            cx + 0.70 * r, cy + 0.82 * r,
            cx + 0.64 * r, cy + 0.64 * r,
            cx + 0.52 * r, cy + 0.50 * r,
            cx + 0.44 * r, cy + 0.36 * r,
            cx + 0.44 * r, cy - 0.24 * r,
            cx + 0.58 * r, cy - 0.38 * r,
            cx + 0.58 * r, cy - 0.74 * r,
            cx + 0.34 * r, cy - 0.74 * r,
            cx + 0.34 * r, cy - 0.54 * r,
            cx + 0.14 * r, cy - 0.54 * r,
            cx + 0.14 * r, cy - 0.74 * r,
            cx - 0.14 * r, cy - 0.74 * r,
            cx - 0.14 * r, cy - 0.54 * r,
            cx - 0.34 * r, cy - 0.54 * r,
            cx - 0.34 * r, cy - 0.74 * r,
            cx - 0.58 * r, cy - 0.74 * r,
            cx - 0.58 * r, cy - 0.38 * r,
            cx - 0.44 * r, cy - 0.24 * r,
            cx - 0.44 * r, cy + 0.36 * r,
            cx - 0.52 * r, cy + 0.50 * r,
            cx - 0.64 * r, cy + 0.64 * r,
        ]
        canvas.create_polygon(pts, fill=fill_col, outline=stroke_col, width=lw, joinstyle=tk.ROUND)
        canvas.create_line(cx - 0.54 * r, cy + 0.64 * r, cx + 0.54 * r, cy + 0.64 * r, fill=inner_col, width=ilw)
        canvas.create_line(cx - 0.44 * r, cy + 0.48 * r, cx + 0.44 * r, cy + 0.48 * r, fill=inner_col, width=ilw)
        canvas.create_line(cx - 0.42 * r, cy - 0.24 * r, cx + 0.42 * r, cy - 0.24 * r, fill=inner_col, width=ilw)
        canvas.create_line(cx - 0.48 * r, cy - 0.38 * r, cx + 0.48 * r, cy - 0.38 * r, fill=inner_col, width=ilw)

    elif piece_type == chess.KNIGHT:
        pts = [
            cx - 0.62 * r, cy + 0.82 * r,
            cx + 0.68 * r, cy + 0.82 * r,
            cx + 0.66 * r, cy + 0.34 * r,
            cx + 0.56 * r, cy - 0.16 * r,
            cx + 0.34 * r, cy - 0.54 * r,
            cx + 0.04 * r, cy - 0.68 * r,
            cx - 0.06 * r, cy - 0.86 * r,
            cx - 0.20 * r, cy - 0.66 * r,
            cx - 0.36 * r, cy - 0.82 * r,
            cx - 0.40 * r, cy - 0.52 * r,
            cx - 0.68 * r, cy - 0.14 * r,
            cx - 0.78 * r, cy + 0.12 * r,
            cx - 0.68 * r, cy + 0.26 * r,
            cx - 0.46 * r, cy + 0.18 * r,
            cx - 0.54 * r, cy + 0.30 * r,
            cx - 0.36 * r, cy + 0.28 * r,
            cx - 0.14 * r, cy + 0.02 * r,
            cx - 0.28 * r, cy + 0.42 * r,
            cx - 0.56 * r, cy + 0.64 * r,
        ]
        canvas.create_polygon(pts, fill=fill_col, outline=stroke_col, width=lw, joinstyle=tk.ROUND)
        canvas.create_line(
            cx - 0.42 * r, cy - 0.30 * r, cx - 0.28 * r, cy - 0.38 * r,
            fill=inner_col, width=ilw * 1.25, capstyle=tk.ROUND
        )
        canvas.create_oval(
            cx - 0.66 * r, cy + 0.04 * r, cx - 0.56 * r, cy + 0.14 * r,
            fill=inner_col, outline=""
        )
        canvas.create_line(
            cx + 0.04 * r, cy - 0.54 * r,
            cx + 0.38 * r, cy - 0.32 * r,
            cx + 0.52 * r, cy + 0.16 * r,
            cx + 0.54 * r, cy + 0.66 * r,
            fill=inner_col, width=ilw * 1.15, smooth=True, capstyle=tk.ROUND
        )
        canvas.create_line(cx - 0.50 * r, cy + 0.68 * r, cx + 0.52 * r, cy + 0.68 * r, fill=inner_col, width=ilw)

    elif piece_type == chess.BISHOP:
        lappet_left = [
            cx - 0.76 * r, cy + 0.82 * r,
            cx - 0.22 * r, cy + 0.72 * r,
            cx - 0.14 * r, cy + 0.58 * r,
            cx - 0.62 * r, cy + 0.66 * r,
        ]
        lappet_right = [
            cx + 0.76 * r, cy + 0.82 * r,
            cx + 0.22 * r, cy + 0.72 * r,
            cx + 0.14 * r, cy + 0.58 * r,
            cx + 0.62 * r, cy + 0.66 * r,
        ]
        canvas.create_polygon(lappet_left, fill=fill_col, outline=stroke_col, width=lw, joinstyle=tk.ROUND)
        canvas.create_polygon(lappet_right, fill=fill_col, outline=stroke_col, width=lw, joinstyle=tk.ROUND)

        dome_pts = [
            cx - 0.46 * r, cy + 0.58 * r,
            cx + 0.46 * r, cy + 0.58 * r,
            cx + 0.38 * r, cy + 0.36 * r,
            cx + 0.48 * r, cy - 0.06 * r,
            cx + 0.32 * r, cy - 0.48 * r,
            cx, cy - 0.70 * r,
            cx - 0.32 * r, cy - 0.48 * r,
            cx - 0.48 * r, cy - 0.06 * r,
            cx - 0.38 * r, cy + 0.36 * r,
        ]
        canvas.create_polygon(dome_pts, fill=fill_col, outline=stroke_col, width=lw, joinstyle=tk.ROUND)

        canvas.create_oval(
            cx - 0.12 * r, cy - 0.90 * r, cx + 0.12 * r, cy - 0.68 * r,
            fill=fill_col, outline=stroke_col, width=lw
        )
        canvas.create_line(cx, cy - 0.34 * r, cx, cy - 0.06 * r, fill=inner_col, width=ilw * 1.25)
        canvas.create_line(cx - 0.14 * r, cy - 0.20 * r, cx + 0.14 * r, cy - 0.20 * r, fill=inner_col, width=ilw * 1.25)
        canvas.create_line(cx - 0.38 * r, cy + 0.38 * r, cx + 0.38 * r, cy + 0.38 * r, fill=inner_col, width=ilw)
        canvas.create_line(cx - 0.42 * r, cy + 0.50 * r, cx + 0.42 * r, cy + 0.50 * r, fill=inner_col, width=ilw)

    elif piece_type == chess.QUEEN:
        pts = [
            cx - 0.60 * r, cy + 0.80 * r,
            cx + 0.60 * r, cy + 0.80 * r,
            cx + 0.54 * r, cy + 0.44 * r,
            cx + 0.78 * r, cy - 0.38 * r,
            cx + 0.38 * r, cy + 0.08 * r,
            cx + 0.42 * r, cy - 0.56 * r,
            cx + 0.14 * r, cy + 0.04 * r,
            cx, cy - 0.64 * r,
            cx - 0.14 * r, cy + 0.04 * r,
            cx - 0.42 * r, cy - 0.56 * r,
            cx - 0.38 * r, cy + 0.08 * r,
            cx - 0.78 * r, cy - 0.38 * r,
            cx - 0.54 * r, cy + 0.44 * r,
        ]
        canvas.create_polygon(pts, fill=fill_col, outline=stroke_col, width=lw, joinstyle=tk.ROUND)
        for px, py in [(-0.78, -0.45), (-0.42, -0.64), (0.0, -0.72), (0.42, -0.64), (0.78, -0.45)]:
            canvas.create_oval(
                cx + (px - 0.095) * r, cy + (py - 0.095) * r,
                cx + (px + 0.095) * r, cy + (py + 0.095) * r,
                fill=fill_col, outline=stroke_col, width=lw * 0.9
            )
        canvas.create_line(
            cx - 0.48 * r, cy + 0.34 * r,
            cx - 0.26 * r, cy + 0.22 * r,
            cx, cy + 0.32 * r,
            cx + 0.26 * r, cy + 0.22 * r,
            cx + 0.48 * r, cy + 0.34 * r,
            fill=inner_col, width=ilw, smooth=True
        )
        canvas.create_line(cx - 0.50 * r, cy + 0.50 * r, cx + 0.50 * r, cy + 0.50 * r, fill=inner_col, width=ilw)
        canvas.create_line(cx - 0.54 * r, cy + 0.66 * r, cx + 0.54 * r, cy + 0.66 * r, fill=inner_col, width=ilw)

    elif piece_type == chess.KING:
        canvas.create_line(cx, cy - 0.96 * r, cx, cy - 0.58 * r, fill=stroke_col, width=lw * 1.25)
        canvas.create_line(cx - 0.18 * r, cy - 0.80 * r, cx + 0.18 * r, cy - 0.80 * r, fill=stroke_col, width=lw * 1.25)
        canvas.create_oval(
            cx - 0.15 * r, cy - 0.66 * r, cx + 0.15 * r, cy - 0.46 * r,
            fill=fill_col, outline=stroke_col, width=lw * 0.9
        )
        pts = [
            cx - 0.58 * r, cy + 0.80 * r,
            cx + 0.58 * r, cy + 0.80 * r,
            cx + 0.54 * r, cy + 0.44 * r,
            cx + 0.74 * r, cy - 0.08 * r,
            cx + 0.56 * r, cy - 0.42 * r,
            cx + 0.22 * r, cy - 0.44 * r,
            cx, cy - 0.32 * r,
            cx - 0.22 * r, cy - 0.44 * r,
            cx - 0.56 * r, cy - 0.42 * r,
            cx - 0.74 * r, cy - 0.08 * r,
            cx - 0.54 * r, cy + 0.44 * r,
        ]
        canvas.create_polygon(pts, fill=fill_col, outline=stroke_col, width=lw, joinstyle=tk.ROUND)
        canvas.create_line(
            cx - 0.46 * r, cy + 0.26 * r,
            cx - 0.54 * r, cy - 0.08 * r,
            cx - 0.34 * r, cy - 0.28 * r,
            cx - 0.04 * r, cy - 0.12 * r,
            cx - 0.04 * r, cy + 0.28 * r,
            fill=inner_col, width=ilw, smooth=True
        )
        canvas.create_line(
            cx + 0.46 * r, cy + 0.26 * r,
            cx + 0.54 * r, cy - 0.08 * r,
            cx + 0.34 * r, cy - 0.28 * r,
            cx + 0.04 * r, cy - 0.12 * r,
            cx + 0.04 * r, cy + 0.28 * r,
            fill=inner_col, width=ilw, smooth=True
        )
        canvas.create_line(cx - 0.48 * r, cy + 0.48 * r, cx + 0.48 * r, cy + 0.48 * r, fill=inner_col, width=ilw)
        canvas.create_line(cx - 0.52 * r, cy + 0.64 * r, cx + 0.52 * r, cy + 0.64 * r, fill=inner_col, width=ilw)


class RoundedButton(tk.Canvas):
    def __init__(
        self, parent, text: str, command=None,
        bg_color="#2B2824", hover_color="#38342E",
        fg_color="#E8DCC7", width=136, height=44, radius=14
    ):
        super().__init__(
            parent, width=width, height=height,
            bg=parent["bg"], highlightthickness=0, cursor="hand2"
        )
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.radius = radius
        self.enabled = True
        self._hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)
        self.bind("<Configure>", lambda e: self._draw())
        self._draw()

    def set_state(self, enabled: bool):
        self.enabled = enabled
        self.config(cursor="hand2" if enabled else "arrow")
        self._draw()

    def set_text_and_color(self, text: str, bg_color: str = None):
        self.text = text
        if bg_color:
            self.bg_color = bg_color
        self._draw()

    def _on_enter(self, _):
        if self.enabled:
            self._hovered = True
            self._draw()

    def _on_leave(self, _):
        self._hovered = False
        self._draw()

    def _on_click(self, _):
        if self.enabled and self.command:
            self.command()

    def _draw(self):
        self.delete("all")
        w = max(self.winfo_width(), int(self["width"]))
        h = max(self.winfo_height(), int(self["height"]))
        if not self.enabled:
            fill = "#1D1B18"
            fg = THEME["text_muted"]
            border = "#2A2723"
        else:
            fill = self.hover_color if self._hovered else self.bg_color
            fg = self.fg_color
            border = THEME["border_active"] if self._hovered else THEME["border_subtle"]

        create_rounded_rect(self, 2, 2, w - 2, h - 2, r=self.radius, fill=fill, outline=border, width=1.2)
        self.create_text(w / 2, h / 2, text=self.text, fill=fg, font=("Segoe UI", 9, "bold"))


class StartupOnboardingDialog:
    """Стартовое окно ввода никнеймов Chess.com и проверки наличия Stockfish."""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.completed = False
        self.my_username = ""
        self.target_username = ""
        self.sf_path = self._auto_detect_stockfish()

        self.win = tk.Toplevel(root)
        self.win.title("Chess Studio & Mistakes — Setup")
        self.win.geometry("500x430")
        self.win.configure(bg=THEME["bg_root"])
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._build_ui()

    def _auto_detect_stockfish(self) -> str:
        candidates = [
            STOCKFISH_PATH,
            os.path.join(BASE_DIR, "stockfish.exe"),
            os.path.join(os.getcwd(), "stockfish", "stockfish-windows-x86-64-universal.exe"),
            os.path.join(os.getcwd(), "stockfish.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return ""

    def _build_ui(self):
        container = tk.Frame(self.win, bg=THEME["bg_panel"], padx=24, pady=20)
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        tk.Label(
            container, text="Welcome to Chess Analyzer",
            bg=THEME["bg_panel"], fg=THEME["text_primary"], font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 14))

        tk.Label(
            container, text="1. Enter your Chess.com username:",
            bg=THEME["bg_panel"], fg=THEME["text_secondary"], font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.entry_me = tk.Entry(
            container, bg=THEME["bg_panel_elev"], fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"], relief=tk.FLAT, font=("Segoe UI", 11)
        )
        self.entry_me.pack(fill=tk.X, pady=(4, 14), ipady=6)

        tk.Label(
            container, text="2. Player whose last game to analyze (leave blank for yourself):",
            bg=THEME["bg_panel"], fg=THEME["text_secondary"], font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.entry_target = tk.Entry(
            container, bg=THEME["bg_panel_elev"], fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"], relief=tk.FLAT, font=("Segoe UI", 11)
        )
        self.entry_target.pack(fill=tk.X, pady=(4, 16), ipady=6)

        self.sf_frame = tk.Frame(container, bg=THEME["bg_bubble"], padx=12, pady=10)
        self.sf_frame.pack(fill=tk.X, pady=(0, 18))
        self._update_sf_status_ui()

        btn_row = tk.Frame(container, bg=THEME["bg_panel"])
        btn_row.pack(fill=tk.X, side=tk.BOTTOM)

        self.start_btn = RoundedButton(
            btn_row, text="Start Analysis ▶", command=self._on_start,
            bg_color="#2A3328", hover_color="#364233", width=180, height=42
        )
        self.start_btn.pack(side=tk.RIGHT)

    def _update_sf_status_ui(self):
        for w in self.sf_frame.winfo_children():
            w.destroy()

        if self.sf_path and os.path.exists(self.sf_path):
            tk.Label(
                self.sf_frame, text="✓ Stockfish engine found and ready!",
                bg=THEME["bg_bubble"], fg=THEME["accent_sage"], font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")
            tk.Label(
                self.sf_frame, text=os.path.basename(self.sf_path),
                bg=THEME["bg_bubble"], fg=THEME["text_muted"], font=("Segoe UI", 8)
            ).pack(anchor="w")
        else:
            tk.Label(
                self.sf_frame,
                text="⚠ Stockfish engine not found!\nPlease download Stockfish from the official website, extract it, and select the .exe file:",
                bg=THEME["bg_bubble"], fg=THEME["accent_terra"], font=("Segoe UI", 9, "bold"),
                justify=tk.LEFT
            ).pack(anchor="w", pady=(0, 8))

            actions = tk.Frame(self.sf_frame, bg=THEME["bg_bubble"])
            actions.pack(fill=tk.X)

            dl_btn = tk.Button(
                actions, text="🌐 Download Stockfish",
                command=lambda: webbrowser.open("https://stockfishchess.org/download/"),
                bg=THEME["accent_ochre"], fg="#161513", relief=tk.FLAT,
                font=("Segoe UI", 9, "bold"), padx=10, pady=4, cursor="hand2"
            )
            dl_btn.pack(side=tk.LEFT, padx=(0, 8))

            browse_btn = tk.Button(
                actions, text="📁 Locate stockfish.exe...",
                command=self._browse_sf,
                bg=THEME["bg_panel_elev"], fg=THEME["text_primary"], relief=tk.FLAT,
                font=("Segoe UI", 9), padx=10, pady=4, cursor="hand2"
            )
            browse_btn.pack(side=tk.LEFT)

    def _browse_sf(self):
        path = filedialog.askopenfilename(
            parent=self.win,
            title="Select Stockfish executable (.exe)",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if path and os.path.exists(path):
            self.sf_path = path
            self._update_sf_status_ui()

    def _on_start(self):
        me = self.entry_me.get().strip()
        target = self.entry_target.get().strip()
        if not me:
            messagebox.showwarning("Username required", "Please enter your Chess.com username.", parent=self.win)
            return
        if not self.sf_path or not os.path.exists(self.sf_path):
            messagebox.showwarning(
                "Stockfish required",
                "Stockfish engine was not found.\nClick 'Download Stockfish' to get it from the official site, then select the .exe file.",
                parent=self.win
            )
            return

        self.my_username = me
        self.target_username = target if target else me
        self.completed = True
        self.win.destroy()

    def _on_cancel(self):
        self.completed = False
        self.win.destroy()


def get_last_game_pgn(username: str) -> str:
    now = datetime.now(timezone.utc)

    def fetch_month(year, month):
        url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=12)
        if resp.status_code == 200:
            return resp.json().get("games", [])
        return []

    games = fetch_month(now.year, now.month)
    if not games:
        prev_month = now.replace(day=1) - timedelta(days=1)
        games = fetch_month(prev_month.year, prev_month.month)

    if not games:
        raise ValueError(f"No games found for '{username}' in the last 2 months.")
    return games[-1]["pgn"]


def get_material_balance(board: chess.Board, player_color: chess.Color) -> int:
    return sum(
        PIECE_VALUES[p.piece_type] * (1 if p.color == player_color else -1)
        for p in board.piece_map().values()
    )


def count_hanging_pieces(board: chess.Board, color: chess.Color) -> int:
    opponent = not color
    return sum(
        1 for sq, p in board.piece_map().items()
        if p.color == color and p.piece_type != chess.KING
        and board.is_attacked_by(opponent, sq) and not board.is_attacked_by(color, sq)
    )


def get_hanging_raw(board: chess.Board, color: chess.Color):
    opponent = not color
    raw_items = []
    squares = []
    for sq, p in board.piece_map().items():
        if p.color == color and p.piece_type != chess.KING:
            if board.is_attacked_by(opponent, sq) and not board.is_attacked_by(color, sq):
                raw_items.append((p.piece_type, sq))
                squares.append(sq)
    return raw_items, squares


def format_eval_label(cp_white: int, mate_white: int = None) -> str:
    if mate_white is not None:
        return f"M{abs(mate_white)}"
    pawns = cp_white / 100.0
    if abs(pawns) < 0.05:
        return "0.0"
    return f"{pawns:+.1f}"


def eval_to_white_ratio(cp_white: int, mate_white: int = None) -> float:
    if mate_white is not None:
        return 1.0 if mate_white > 0 else 0.0
    pawns = cp_white / 100.0
    ratio = 1.0 / (1.0 + math.exp(-0.42 * pawns))
    return max(0.04, min(0.96, ratio))


class ChessAnalyzerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.lang = "en"  # Английский язык по умолчанию
        self.root.title(f"Chess Studio & Mistakes — {TARGET_USERNAME}")
        self.root.geometry("1440x880")
        self.root.minsize(1180, 740)
        self.root.configure(bg=THEME["bg_root"])

        self.photo_cache = {}

        self.white_name = ""
        self.black_name = ""
        self.white_elo = ""
        self.black_elo = ""
        self.white_accuracy = None
        self.black_accuracy = None
        self.my_color = chess.WHITE
        self.bottom_color = chess.WHITE

        self.boards_history = []
        self.moves_history = []
        self.uci_history = []
        self.evals_history = []
        self.move_meta_history = [None]
        self.errors_by_ply = {}
        self.pgn_opening_name = ""

        self.current_ply = 0
        self.latest_ply = 0
        self.unlocked_plies = set()
        self.analysis_finished = False

        self.displayed_white_ratio = 0.5
        self.target_white_ratio = 0.5
        self.current_eval_label = "0.0"
        self.current_eval_white_adv = True

        self.selected_square = None
        self.legal_target_squares = []
        self.show_best_move_arrow = True

        self.move_anim_active = False
        self.move_anim_data = None
        self.animating_combo = False
        self.combo_timer = None
        self.combo_board = None
        self.combo_last_move = None

        self.chat_cards = {}
        self.history_Row_bounds = {}
        self.typing_step = 0
        self.sq_size = 64
        self.board_margin = 24
        self.eval_bar_width = 30
        self.eval_bar_gap = 12

        self._build_layout()
        self._start_typing_animation()

        self.root.bind("<Left>", lambda e: self.prev_move())
        self.root.bind("<Right>", lambda e: self.next_move())

        threading.Thread(target=self._run_analysis_background, daemon=True).start()

    def set_language(self, new_lang: str):
        if new_lang not in ("ru", "en") or self.lang == new_lang:
            return
        self.lang = new_lang
        tr = TRANSLATIONS[self.lang]

        self.btn_prev.set_text_and_color(tr["btn_prev"])
        self.btn_next.set_text_and_color(tr["btn_next"])
        self.btn_flip.set_text_and_color(tr["btn_flip"])
        self.btn_best.set_text_and_color(tr["btn_best"])
        if self.animating_combo:
            self.btn_combo.set_text_and_color(tr["btn_combo_stop"], "#6B2D28")
        else:
            self.btn_combo.set_text_and_color(tr["btn_combo"], "#3B2E1E")

        if self.current_ply < self.latest_ply:
            self.btn_return_live.set_text_and_color(
                tr["btn_return_live"].format(move=(self.latest_ply + 1) // 2), "#4A3222"
            )

        self._draw_lang_switcher()
        self._redraw_player_cards()
        self._draw_chat_header()
        self._draw_typing_indicator()
        self._redraw_move_history()
        self._draw_eval_graph()
        for ply in list(self.chat_cards.keys()):
            self._draw_mistake_card(ply)

    def _build_layout(self):
        tr = TRANSLATIONS[self.lang]
        self.main_container = tk.Frame(self.root, bg=THEME["bg_root"])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=18, pady=14)

        self.main_container.columnconfigure(0, weight=7, minsize=780)
        self.main_container.columnconfigure(1, weight=5, minsize=440)
        self.main_container.rowconfigure(0, weight=1)

        
        self.left_col = tk.Frame(self.main_container, bg=THEME["bg_root"])
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.left_col.rowconfigure(1, weight=1)
        self.left_col.columnconfigure(0, weight=1)

        
        self.top_bar_frame = tk.Frame(self.left_col, bg=THEME["bg_root"])
        self.top_bar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.lang_switch_canvas = tk.Canvas(
            self.top_bar_frame, width=108, height=68, bg=THEME["bg_root"], highlightthickness=0, cursor="hand2"
        )
        self.lang_switch_canvas.pack(side=tk.LEFT, padx=(0, 10))
        self.lang_switch_canvas.bind("<Configure>", lambda e: self._draw_lang_switcher())
        self.lang_switch_canvas.bind("<Button-1>", self._on_lang_switcher_click)

        self.top_player_canvas = tk.Canvas(
            self.top_bar_frame, height=68, bg=THEME["bg_root"], highlightthickness=0
        )
        self.top_player_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.top_player_canvas.bind("<Configure>", lambda e: self._redraw_player_cards())

        
        self.center_stage = tk.Frame(self.left_col, bg=THEME["bg_root"])
        self.center_stage.grid(row=1, column=0, sticky="nsew")
        self.center_stage.rowconfigure(0, weight=1)
        self.center_stage.columnconfigure(1, weight=1)

        
        self.history_outer = tk.Frame(self.center_stage, width=200, bg=THEME["bg_panel"])
        self.history_outer.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=2)
        self.history_outer.grid_propagate(False)

        self.history_header_canvas = tk.Canvas(
            self.history_outer, height=48, bg=THEME["bg_panel_elev"], highlightthickness=0
        )
        self.history_header_canvas.pack(fill=tk.X)

        self.history_body = tk.Frame(self.history_outer, bg=THEME["bg_panel"])
        self.history_body.pack(fill=tk.BOTH, expand=True)

        self.history_scroll = tk.Scrollbar(
            self.history_body, orient=tk.VERTICAL,
            bg=THEME["bg_panel"], troughcolor=THEME["bg_panel"], highlightthickness=0, bd=0
        )
        self.history_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_canvas = tk.Canvas(
            self.history_body, bg=THEME["bg_panel"], highlightthickness=0,
            yscrollcommand=self.history_scroll.set, cursor="hand2"
        )
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_scroll.config(command=self.history_canvas.yview)
        self.history_canvas.bind("<Configure>", lambda e: self._redraw_move_history())
        self.history_canvas.bind("<Button-1>", self._on_history_click)

        
        self.board_stage = tk.Frame(self.center_stage, bg=THEME["bg_root"])
        self.board_stage.grid(row=0, column=1, sticky="nsew")
        self.board_stage.bind("<Configure>", self._on_board_stage_resize)

        self.board_canvas = tk.Canvas(
            self.board_stage, bg=THEME["bg_root"], highlightthickness=0, cursor="hand2"
        )
        self.board_canvas.pack(expand=True)
        self.board_canvas.bind("<Button-1>", self._on_board_click)

        
        self.bottom_player_canvas = tk.Canvas(
            self.left_col, height=68, bg=THEME["bg_root"], highlightthickness=0
        )
        self.bottom_player_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 10))
        self.bottom_player_canvas.bind("<Configure>", lambda e: self._redraw_player_cards())

        
        self.controls_frame = tk.Frame(self.left_col, bg=THEME["bg_root"])
        self.controls_frame.grid(row=3, column=0, sticky="ew")

        self.btn_prev = RoundedButton(
            self.controls_frame, text=tr["btn_prev"], command=self.prev_move, width=106, height=44
        )
        self.btn_prev.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_prev.set_state(False)

        self.btn_next = RoundedButton(
            self.controls_frame, text=tr["btn_next"], command=self.next_move, width=106, height=44
        )
        self.btn_next.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_next.set_state(False)

        self.btn_flip = RoundedButton(
            self.controls_frame, text=tr["btn_flip"], command=self.flip_board,
            bg_color="#2B2824", hover_color="#3A352F", width=132, height=44
        )
        self.btn_flip.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_best = RoundedButton(
            self.controls_frame, text=tr["btn_best"], command=self.toggle_best_move_arrow,
            bg_color="#2A3328", hover_color="#364233", width=124, height=44
        )
        self.btn_best.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_best.set_state(False)

        self.btn_combo = RoundedButton(
            self.controls_frame, text=tr["btn_combo"], command=self.play_combination,
            bg_color="#3B2E1E", hover_color="#4D3C27", width=174, height=44
        )
        self.btn_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_combo.set_state(False)

        self.btn_return_live = RoundedButton(
            self.controls_frame, text=tr["btn_return_live"].format(move=1), command=self.return_to_latest_ply,
            bg_color="#4A3222", hover_color="#5E3F2B", width=156, height=44
        )

        
        self.right_col = tk.Canvas(
            self.main_container, bg=THEME["bg_root"], highlightthickness=0
        )
        self.right_col.grid(row=0, column=1, sticky="nsew")
        self.right_col.bind("<Configure>", self._on_right_col_configure)

        self.chat_wrapper = tk.Frame(self.right_col, bg=THEME["bg_panel"])

        self.chat_header = tk.Canvas(
            self.chat_wrapper, height=76, bg=THEME["bg_panel_elev"], highlightthickness=0
        )
        self.chat_header.pack(fill=tk.X, side=tk.TOP)
        self.chat_header.bind("<Configure>", lambda e: self._draw_chat_header())

        tk.Frame(self.chat_wrapper, height=1, bg=THEME["border_subtle"]).pack(fill=tk.X)

        
        self.graph_frame = tk.Frame(self.chat_wrapper, height=185, bg=THEME["bg_panel_elev"])
        self.graph_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.graph_frame.pack_propagate(False)

        tk.Frame(self.chat_wrapper, height=1, bg=THEME["border_subtle"]).pack(fill=tk.X, side=tk.BOTTOM)

        self.graph_canvas = tk.Canvas(
            self.graph_frame, bg=THEME["bg_panel_elev"], highlightthickness=0, cursor="hand2"
        )
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", lambda e: self._draw_eval_graph())
        self.graph_canvas.bind("<Button-1>", self._on_graph_click)

        
        self.chat_body_frame = tk.Frame(self.chat_wrapper, bg=THEME["bg_panel"])
        self.chat_body_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_scrollbar = tk.Scrollbar(
            self.chat_body_frame, orient=tk.VERTICAL,
            bg=THEME["bg_panel"], troughcolor=THEME["bg_panel"], highlightthickness=0, bd=0
        )
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 4), pady=8)

        self.chat_stream_canvas = tk.Canvas(
            self.chat_body_frame, bg=THEME["bg_panel"], highlightthickness=0,
            yscrollcommand=self.chat_scrollbar.set
        )
        self.chat_stream_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 4), pady=8)
        self.chat_scrollbar.config(command=self.chat_stream_canvas.yview)

        self.messages_container = tk.Frame(self.chat_stream_canvas, bg=THEME["bg_panel"])
        self.messages_window_id = self.chat_stream_canvas.create_window(
            (0, 0), window=self.messages_container, anchor="nw"
        )

        self.messages_container.bind("<Configure>", self._on_messages_container_configure)
        self.chat_stream_canvas.bind("<Configure>", self._on_stream_canvas_configure)
        self.chat_stream_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.cards_list_frame = tk.Frame(self.messages_container, bg=THEME["bg_panel"])
        self.cards_list_frame.pack(fill=tk.X, expand=True)

        self.typing_bubble_canvas = tk.Canvas(
            self.messages_container, height=58, bg=THEME["bg_panel"], highlightthickness=0
        )
        self.typing_bubble_canvas.pack(fill=tk.X, pady=(6, 12), padx=4)

    
    def _redraw_move_history(self):
        hc = self.history_header_canvas
        hc.delete("all")
        hw = max(165, hc.winfo_width())
        tr = TRANSLATIONS[self.lang]

        if self.white_accuracy is not None and self.black_accuracy is not None:
            hc.create_text(
                hw / 2, 15, text=tr["history_title"],
                fill=THEME["text_primary"], font=("Segoe UI", 10, "bold")
            )
            hc.create_text(
                hw / 2, 34,
                text=tr["acc_short"].format(w=self.white_accuracy, b=self.black_accuracy),
                fill=THEME["accent_sage"], font=("Segoe UI", 8, "bold")
            )
        else:
            hc.create_text(
                hw / 2, 24, text=tr["history_title"],
                fill=THEME["text_primary"], font=("Segoe UI", 10, "bold")
            )

        c = self.history_canvas
        c.delete("all")
        self.history_Row_bounds.clear()

        w = max(175, c.winfo_width())
        total_plies_available = len(self.move_meta_history) - 1

        if total_plies_available <= 0:
            c.create_text(
                w / 2, 40, text=tr["analyzing_short"],
                fill=THEME["text_muted"], font=("Segoe UI", 9, "italic")
            )
            c.configure(scrollregion=(0, 0, w, 100))
            return

        
        shown_plies = min(self.current_ply, total_plies_available)
        if shown_plies <= 0:
            c.create_text(
                w / 2, 40, text=tr["history_empty"],
                fill=THEME["text_muted"], font=("Segoe UI", 8, "italic")
            )
            c.configure(scrollregion=(0, 0, w, 100))
            return

        row_h = 30
        num_col_w = 28
        col_w = (w - num_col_w - 6) / 2
        shown_rows = (shown_plies + 1) // 2

        for row_idx in range(shown_rows):
            y1 = 6 + row_idx * row_h
            y2 = y1 + row_h - 2
            cy = (y1 + y2) / 2

            if row_idx % 2 == 1:
                c.create_rectangle(2, y1, w - 2, y2, fill="#1C1A17", outline="")

            c.create_text(
                14, cy, text=f"{row_idx + 1}.",
                fill=THEME["text_muted"], font=("Segoe UI", 8, "bold")
            )

            for side_i, ply in enumerate((row_idx * 2 + 1, row_idx * 2 + 2)):
                if ply > shown_plies:
                    continue
                meta = self.move_meta_history[ply]
                if not meta:
                    continue

                x1 = num_col_w + side_i * col_w
                x2 = x1 + col_w - 2
                self.history_Row_bounds[ply] = (x1, y1, x2, y2)

                if ply == self.current_ply:
                    create_rounded_rect(
                        c, x1, y1 + 1, x2, y2 - 1, r=6,
                        fill=THEME["bg_bubble_active"], outline=THEME["accent_ochre"], width=1.2
                    )

                
                draw_classic_merida_piece(
                    c, x1 + 11, cy, 18,
                    meta["piece_type"], meta["is_white"]
                )

                
                c.create_text(
                    x1 + 22, cy, text=meta["san"], anchor="w",
                    fill=THEME["text_primary"] if ply == self.current_ply else THEME["text_secondary"],
                    font=("Segoe UI", 8, "bold" if ply == self.current_ply else "normal")
                )

                
                draw_move_classification_badge(
                    c, x2 - 9, cy, 7.5, meta["badge"]
                )

        total_h = max(120, 12 + shown_rows * row_h)
        c.configure(scrollregion=(0, 0, w, total_h))

        
        if shown_rows > 8:
            c.yview_moveto(1.0)

    def _on_history_click(self, event):
        if not self.boards_history:
            return
        cx = self.history_canvas.canvasx(event.x)
        cy = self.history_canvas.canvasy(event.y)
        for ply, (x1, y1, x2, y2) in self.history_Row_bounds.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                self.stop_combo_animation()
                self.selected_square = None
                self.legal_target_squares = []
                prev_board = self.boards_history[self.current_ply]
                self.current_ply = ply
                if self.current_ply > self.latest_ply:
                    self.latest_ply = self.current_ply
                self.update_view(animate_from_board=prev_board)
                break

    
    def _draw_eval_graph(self):
        c = self.graph_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 80 or h < 60:
            return

        tr = TRANSLATIONS[self.lang]
        pad_l, pad_r, pad_t, pad_b = 16, 16, 28, 16
        gw = max(40, w - pad_l - pad_r)
        gh = max(30, h - pad_t - pad_b)
        mid_y = pad_t + gh / 2.0

        c.create_text(
            pad_l, 14, text=tr["graph_title"], anchor="w",
            fill=THEME["text_secondary"], font=("Segoe UI", 9, "bold")
        )

        create_rounded_rect(
            c, pad_l, pad_t, pad_l + gw, pad_t + gh, r=10,
            fill="#1A1816", outline=THEME["border_subtle"], width=1.2
        )

        c.create_line(
            pad_l + 2, mid_y, pad_l + gw - 2, mid_y,
            fill=THEME["border_subtle"], width=1.2, dash=(4, 3)
        )

        if not self.evals_history:
            c.create_oval(
                pad_l - 3.5, mid_y - 3.5, pad_l + 3.5, mid_y + 3.5,
                fill=THEME["accent_ochre"], outline="#161513"
            )
            return

        max_ply = max(1, len(self.evals_history) - 1)
        shown_ply = min(self.current_ply, len(self.evals_history) - 1)

        pts = []
        for p in range(shown_ply + 1):
            x = pad_l + (p / max_ply) * gw
            if p == 0:
                y = mid_y
            else:
                ev = self.evals_history[p]
                ratio = eval_to_white_ratio(ev["cp_white"], ev["mate_white"])
                y = pad_t + gh * (1.0 - ratio)
            pts.append((p, x, y))

        if len(pts) >= 2:
            poly = [pts[0][1], mid_y]
            for _, px, py in pts:
                poly.extend([px, py])
            poly.extend([pts[-1][1], mid_y])
            c.create_polygon(poly, fill="#38322A", outline="")

            line_coords = []
            for _, px, py in pts:
                line_coords.extend([px, py])
            c.create_line(line_coords, fill=THEME["text_primary"], width=2.0, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        for p, px, py in pts:
            meta = self.move_meta_history[p] if p < len(self.move_meta_history) else None
            badge = meta["badge"] if meta else None
            dot_col = BADGE_STYLE[badge]["color"] if badge in BADGE_STYLE else THEME["accent_ochre"]
            r = 4.2 if p == self.current_ply else 2.6
            c.create_oval(px - r, py - r, px + r, py + r, fill=dot_col, outline="#161513", width=1)

    def _on_graph_click(self, event):
        if not self.evals_history or len(self.evals_history) <= 1:
            return
        w = self.graph_canvas.winfo_width()
        pad_l, pad_r = 16, 16
        gw = max(40, w - pad_l - pad_r)
        rel_x = max(0.0, min(1.0, (event.x - pad_l) / gw))
        target_ply = int(round(rel_x * (len(self.evals_history) - 1)))

        self.stop_combo_animation()
        self.selected_square = None
        self.legal_target_squares = []
        prev_board = self.boards_history[self.current_ply]
        self.current_ply = target_ply
        if self.current_ply > self.latest_ply:
            self.latest_ply = self.current_ply
        self.update_view(animate_from_board=prev_board)

    def _draw_lang_switcher(self):
        c = self.lang_switch_canvas
        c.delete("all")
        w = max(108, c.winfo_width())
        h = max(68, c.winfo_height())

        create_rounded_rect(
            c, 2, 2, w - 2, h - 2, r=16,
            fill=THEME["bg_panel"], outline=THEME["border_subtle"], width=1.2
        )

        tr = TRANSLATIONS[self.lang]
        c.create_text(
            w / 2, 16, text=tr["lang_label"],
            fill=THEME["text_muted"], font=("Segoe UI", 8, "bold")
        )

        mid_x = w / 2
        btn_y1, btn_y2 = 28, h - 8

        ru_active = (self.lang == "ru")
        ru_fill = THEME["accent_ochre"] if ru_active else THEME["bg_panel_elev"]
        ru_fg = "#161513" if ru_active else THEME["text_primary"]
        create_rounded_rect(
            c, 8, btn_y1, mid_x - 2, btn_y2, r=10,
            fill=ru_fill, outline=THEME["border_active"] if ru_active else THEME["border_subtle"]
        )
        c.create_text((8 + mid_x - 2) / 2, (btn_y1 + btn_y2) / 2, text="RU", fill=ru_fg, font=("Segoe UI", 9, "bold"))

        en_active = (self.lang == "en")
        en_fill = THEME["accent_ochre"] if en_active else THEME["bg_panel_elev"]
        en_fg = "#161513" if en_active else THEME["text_primary"]
        create_rounded_rect(
            c, mid_x + 2, btn_y1, w - 8, btn_y2, r=10,
            fill=en_fill, outline=THEME["border_active"] if en_active else THEME["border_subtle"]
        )
        c.create_text((mid_x + 2 + w - 8) / 2, (btn_y1 + btn_y2) / 2, text="EN", fill=en_fg, font=("Segoe UI", 9, "bold"))

    def _on_lang_switcher_click(self, event):
        w = max(108, self.lang_switch_canvas.winfo_width())
        if event.x < w / 2:
            self.set_language("ru")
        else:
            self.set_language("en")

    def _redraw_player_cards(self):
        top_color = not self.bottom_color
        self._draw_single_player_card(self.top_player_canvas, top_color, is_top=True)
        self._draw_single_player_card(self.bottom_player_canvas, self.bottom_color, is_top=False)

    def _draw_single_player_card(self, canvas: tk.Canvas, color: chess.Color, is_top: bool):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 80:
            return

        tr = TRANSLATIONS[self.lang]
        board = self.boards_history[self.current_ply] if self.boards_history else chess.Board()
        is_turn = (board.turn == color) and bool(self.boards_history)

        border_col = THEME["accent_ochre"] if is_turn else THEME["border_subtle"]
        create_rounded_rect(
            canvas, 2, 2, w - 2, h - 2, r=16,
            fill=THEME["bg_panel"], outline=border_col, width=1.6 if is_turn else 1.2
        )

        badge_cx, badge_cy = 34, h / 2
        create_rounded_rect(
            canvas, badge_cx - 20, badge_cy - 20, badge_cx + 20, badge_cy + 20,
            r=11, fill=THEME["sq_light"] if color == chess.WHITE else THEME["sq_dark"], outline=""
        )
        draw_classic_merida_piece(canvas, badge_cx, badge_cy + 1, 34, chess.KING, color == chess.WHITE)

        is_me = (color == self.my_color)
        role_prefix = tr["role_me"] if is_me else tr["role_opp"]
        default_name = tr["white_default"] if color == chess.WHITE else tr["black_default"]
        raw_name = self.white_name if color == chess.WHITE else self.black_name
        player_name = raw_name if raw_name else default_name

        player_elo = self.white_elo if color == chess.WHITE else self.black_elo
        elo_str = f" ({player_elo})" if player_elo else ""
        side_str = tr["side_white"] if color == chess.WHITE else tr["side_black"]

        mat_diff = get_material_balance(board, color)
        mat_str = f"   +{mat_diff}" if mat_diff > 0 else ""

        # Общая точность ходов игрока (Accuracy %)
        player_acc = self.white_accuracy if color == chess.WHITE else self.black_accuracy
        acc_str = f"   •   {tr['acc_label'].format(acc=player_acc)}" if player_acc is not None else ""

        canvas.create_text(
            66, h / 2 - 11,
            text=f"{player_name}{elo_str}  •  {side_str}{mat_str}{acc_str}",
            anchor="w", fill=THEME["text_primary"], font=("Segoe UI", 11, "bold")
        )

        white_op, black_op = detect_openings_at_ply(
            self.uci_history[:self.current_ply], self.pgn_opening_name, self.lang
        )
        op_name = white_op if color == chess.WHITE else black_op
        op_label_color = THEME["accent_sage"] if is_me else THEME["text_secondary"]

        canvas.create_text(
            66, h / 2 + 12,
            text=f"{role_prefix}: {op_name}",
            anchor="w", fill=op_label_color, font=("Segoe UI", 9, "bold")
        )

        if not self.boards_history:
            canvas.create_text(
                w - 18, h / 2, text=tr["analyzing_short"],
                anchor="e", fill=THEME["text_muted"], font=("Segoe UI", 9, "italic")
            )
        else:
            if is_turn:
                pill_x1, pill_y1, pill_x2, pill_y2 = w - 142, h / 2 - 14, w - 16, h / 2 + 14
                create_rounded_rect(
                    canvas, pill_x1, pill_y1, pill_x2, pill_y2, r=10,
                    fill=THEME["bg_panel_elev"], outline=THEME["accent_ochre"], width=1.2
                )
                turn_txt = tr["your_turn"] if is_me else tr["opp_turn"]
                canvas.create_text(
                    (pill_x1 + pill_x2) / 2, h / 2, text=turn_txt,
                    fill=THEME["accent_ochre"], font=("Segoe UI", 9, "bold")
                )
            elif not is_top:
                move_num = (self.current_ply + 1) // 2
                total_moves = len(self.boards_history) // 2
                canvas.create_text(
                    w - 18, h / 2,
                    text=tr["move_of"].format(cur=move_num, total=total_moves),
                    anchor="e", fill=THEME["text_muted"], font=("Segoe UI", 9)
                )

    def flip_board(self):
        self.bottom_color = not self.bottom_color
        self._redraw_player_cards()
        if self.boards_history:
            active_board = self.combo_board if self.animating_combo else self.boards_history[self.current_ply]
            self.draw_board(
                active_board,
                error_info=None if self.animating_combo else self.errors_by_ply.get(self.current_ply),
                combo_move=self.combo_last_move
            )

    def _on_right_col_configure(self, event):
        self.right_col.delete("bg_card")
        w, h = event.width, event.height
        create_rounded_rect(
            self.right_col, 2, 2, w - 2, h - 2,
            r=22, fill=THEME["bg_panel"], outline=THEME["border_subtle"], width=1.5, tags="bg_card"
        )
        self.right_col.create_window(
            10, 10, width=max(100, w - 20), height=max(100, h - 20),
            anchor="nw", window=self.chat_wrapper, tags="bg_card"
        )

    def _draw_chat_header(self):
        c = self.chat_header
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 50:
            return

        tr = TRANSLATIONS[self.lang]
        create_rounded_rect(c, 0, 0, w, h, r=16, fill=THEME["bg_panel_elev"], outline="")
        draw_mistakes_knight_avatar(c, 38, h / 2, 48, self.photo_cache)
        c.create_oval(52, h / 2 + 10, 64, h / 2 + 22, fill=THEME["accent_sage"], outline=THEME["bg_panel_elev"], width=2)

        c.create_text(
            76, h / 2 - 10, text="Mistakes", anchor="w",
            fill=THEME["text_primary"], font=("Segoe UI", 14, "bold")
        )
        status_sub = (
            tr["chat_analyzing"]
            if not self.analysis_finished
            else tr["chat_found"].format(count=len(self.errors_by_ply))
        )
        c.create_text(
            76, h / 2 + 12, text=status_sub, anchor="w",
            fill=THEME["accent_sage"], font=("Segoe UI", 9)
        )

        if self.analysis_finished and len(self.unlocked_plies) < len(self.errors_by_ply):
            btn_x1, btn_y1, btn_x2, btn_y2 = w - 158, h / 2 - 16, w - 14, h / 2 + 16
            create_rounded_rect(
                c, btn_x1, btn_y1, btn_x2, btn_y2, r=10,
                fill=THEME["bg_bubble"], outline=THEME["border_subtle"], tags="unlock_all_btn"
            )
            c.create_text(
                (btn_x1 + btn_x2) / 2, h / 2, text=tr["unlock_all"],
                fill=THEME["text_primary"], font=("Segoe UI", 9, "bold"), tags="unlock_all_btn"
            )
            c.tag_bind("unlock_all_btn", "<Button-1>", lambda e: self.unlock_all_mistakes())

    def _start_typing_animation(self):
        self._draw_typing_indicator()
        self.typing_step = (self.typing_step + 1) % 24
        self.root.after(75, self._start_typing_animation)

    def _draw_typing_indicator(self):
        c = self.typing_bubble_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 50:
            return

        tr = TRANSLATIONS[self.lang]
        draw_mistakes_knight_avatar(c, 24, 28, 34, self.photo_cache)

        bx1, by1, bx2, by2 = 50, 8, 138, 48
        create_rounded_rect(
            c, bx1, by1, bx2, by2, r=16,
            fill=THEME["bg_bubble"], outline=THEME["border_subtle"], width=1.2
        )

        phase = (self.typing_step / 24.0) * (2 * math.pi)
        for i in range(3):
            wave = 0.5 + 0.5 * math.sin(phase - i * 1.15)
            dot_r = 3.2 + 2.0 * wave
            dot_col = blend_colors(THEME["text_muted"], THEME["text_primary"], wave)
            cx = bx1 + 24 + i * 20
            cy = (by1 + by2) / 2 - 1.5 * wave
            c.create_oval(cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r, fill=dot_col, outline="")

        c.create_text(
            bx2 + 12, (by1 + by2) / 2, text=tr["typing_wait"], anchor="w",
            fill=THEME["text_muted"], font=("Segoe UI", 9, "italic")
        )

    def _ensure_mistake_message_in_chat(self, ply: int):
        if ply in self.chat_cards or ply not in self.errors_by_ply:
            return

        self.unlocked_plies.add(ply)
        row_frame = tk.Frame(self.cards_list_frame, bg=THEME["bg_panel"])
        row_frame.pack(fill=tk.X, pady=6, padx=4)

        card_canvas = tk.Canvas(
            row_frame, height=148, bg=THEME["bg_panel"], highlightthickness=0, cursor="hand2"
        )
        card_canvas.pack(fill=tk.X, expand=True)

        self.chat_cards[ply] = {
            "ply": ply,
            "frame": row_frame,
            "canvas": card_canvas,
            "fade": 0.0,
            "hovered": False,
        }

        card_canvas.bind("<Configure>", lambda e, p=ply: self._draw_mistake_card(p))
        card_canvas.bind("<Enter>", lambda e, p=ply: self._on_card_hover(p, True))
        card_canvas.bind("<Leave>", lambda e, p=ply: self._on_card_hover(p, False))
        card_canvas.bind("<Button-1>", lambda e, p=ply: self._on_mistake_card_clicked(p, e))

        self._animate_card_fade_in(ply)
        self.root.after(60, lambda: self.chat_stream_canvas.yview_moveto(1.0))
        self._draw_chat_header()

    def _animate_card_fade_in(self, ply: int):
        card = self.chat_cards.get(ply)
        if not card:
            return
        card["fade"] = min(1.0, card["fade"] + 0.14)
        self._draw_mistake_card(ply)
        if card["fade"] < 1.0:
            self.root.after(28, lambda: self._animate_card_fade_in(ply))

    def _on_card_hover(self, ply: int, is_hover: bool):
        if ply in self.chat_cards:
            self.chat_cards[ply]["hovered"] = is_hover
            self._draw_mistake_card(ply)

    def _draw_mistake_card(self, ply: int):
        card = self.chat_cards.get(ply)
        if not card:
            return

        c = card["canvas"]
        c.delete("all")
        w = c.winfo_width()
        if w < 80:
            return

        tr = TRANSLATIONS[self.lang]
        err = self.errors_by_ply[ply]
        ai_text, _ = build_localized_error_texts(err, self.lang)

        t = card["fade"]
        is_active = (self.current_ply == ply)

        target_bg = THEME["bg_bubble_active"] if is_active else (
            THEME["bg_bubble_hover"] if card["hovered"] else THEME["bg_bubble"]
        )
        bg_col = blend_colors(THEME["bg_panel"], target_bg, t)

        err_accent = ERROR_COLORS.get(err["prediction"], THEME["accent_ochre"])
        target_border = err_accent if is_active else THEME["border_subtle"]
        border_col = blend_colors(THEME["bg_panel"], target_border, t)

        text_main = blend_colors(THEME["bg_panel"], THEME["text_primary"], t)
        text_sub = blend_colors(THEME["bg_panel"], THEME["text_secondary"], t)
        badge_col = blend_colors(THEME["bg_panel"], err_accent, t)

        draw_mistakes_knight_avatar(c, 24, 28, 34, self.photo_cache)

        bx1, bx2 = 50, w - 6
        text_width = max(160, bx2 - bx1 - 28)

        temp_txt = c.create_text(
            bx1 + 18, 62, text=ai_text, anchor="nw",
            width=text_width, font=("Segoe UI", 10), fill=text_main
        )
        bbox = c.bbox(temp_txt)
        c.delete(temp_txt)
        text_h = (bbox[3] - bbox[1]) if bbox else 44
        card_h = max(136, 62 + text_h + 48)

        if int(c["height"]) != card_h:
            c.config(height=card_h)

        create_rounded_rect(
            c, bx1, 4, bx2, card_h - 4, r=18,
            fill=bg_col, outline=border_col, width=2.0 if is_active else 1.2
        )

        create_rounded_rect(
            c, bx1 + 6, 16, bx1 + 10, card_h - 16, r=2,
            fill=badge_col, outline=""
        )

        title_loc = tr["err_titles"].get(err["prediction"], "Mistake")
        c.create_text(
            bx1 + 18, 22, text=tr["card_header"].format(move=err["move_number"]),
            anchor="w", fill=text_sub, font=("Segoe UI", 9, "bold")
        )

        c.create_text(
            bx2 - 14, 22, text=f"{title_loc} (−{err['cp_loss'] / 100:.1f})",
            anchor="e", fill=badge_col, font=("Segoe UI", 9, "bold")
        )

        c.create_text(
            bx1 + 18, 42,
            text=tr["card_moves"].format(played=err["played_san"], best=err["best_san"]),
            anchor="w", fill=text_main, font=("Segoe UI", 10, "bold")
        )

        c.create_text(
            bx1 + 18, 62, text=ai_text, anchor="nw",
            width=text_width, fill=text_main, font=("Segoe UI", 10)
        )

        btn_y1, btn_y2 = card_h - 38, card_h - 12
        b1_x1, b1_x2 = bx1 + 18, bx1 + 178
        create_rounded_rect(
            c, b1_x1, btn_y1, b1_x2, btn_y2, r=9,
            fill=blend_colors(THEME["bg_panel"], "#2A3328", t),
            outline=blend_colors(THEME["bg_panel"], THEME["accent_sage"], t),
            tags="btn_best_in_card"
        )
        c.create_text(
            (b1_x1 + b1_x2) / 2, (btn_y1 + btn_y2) / 2,
            text=tr["card_btn_best"],
            fill=blend_colors(THEME["bg_panel"], "#E8DCC7", t),
            font=("Segoe UI", 9, "bold"), tags="btn_best_in_card"
        )

        b2_x1, b2_x2 = b1_x2 + 10, b1_x2 + 160
        if b2_x2 < bx2 - 10:
            create_rounded_rect(
                c, b2_x1, btn_y1, b2_x2, btn_y2, r=9,
                fill=blend_colors(THEME["bg_panel"], "#3B2E1E", t),
                outline=blend_colors(THEME["bg_panel"], THEME["accent_ochre"], t),
                tags="btn_combo_in_card"
            )
            c.create_text(
                (b2_x1 + b2_x2) / 2, (btn_y1 + btn_y2) / 2,
                text=tr["card_btn_combo"],
                fill=blend_colors(THEME["bg_panel"], "#E8DCC7", t),
                font=("Segoe UI", 9, "bold"), tags="btn_combo_in_card"
            )

    def _on_mistake_card_clicked(self, ply: int, _):
        card = self.chat_cards.get(ply)
        clicked_tags = ()
        if card:
            items = card["canvas"].find_withtag("current")
            if items:
                clicked_tags = card["canvas"].gettags(items[0])

        self.stop_combo_animation()
        self.selected_square = None
        self.legal_target_squares = []

        prev_board = self.boards_history[self.current_ply] if self.boards_history else None
        self.current_ply = ply
        if self.current_ply > self.latest_ply:
            self.latest_ply = self.current_ply
        self.show_best_move_arrow = True

        if "btn_combo_in_card" in clicked_tags:
            self.update_view(animate_from_board=None)
            self.play_combination()
        else:
            self.update_view(animate_from_board=prev_board)

    def unlock_all_mistakes(self):
        for ply in sorted(self.errors_by_ply.keys()):
            self._ensure_mistake_message_in_chat(ply)
        self._draw_chat_header()

    def _on_messages_container_configure(self, _):
        self.chat_stream_canvas.configure(scrollregion=self.chat_stream_canvas.bbox("all"))

    def _on_stream_canvas_configure(self, event):
        self.chat_stream_canvas.itemconfig(self.messages_window_id, width=event.width)

    def _on_mousewheel(self, event):
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget is None:
            return
        if str(widget).startswith(str(self.history_outer)):
            self.history_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif str(widget).startswith(str(self.chat_body_frame)):
            self.chat_stream_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _classify_move_badge(
        self, ply: int, move: chess.Move, best_move: chess.Move,
        cp_loss_mover: int, moves_uci_so_far: list, ml_prediction: str = None
    ) -> str:
        """Определяет иконку оценки для каждого полухода по первому референсу."""
        if ml_prediction:
            mapping = {
                "blunder": "blunder",
                "hanging_piece": "blunder",
                "tactical_error": "miss",
                "positional": "mistake",
                "inaccuracy": "inaccuracy",
            }
            return mapping.get(ml_prediction, "mistake")

        if is_book_ply(moves_uci_so_far):
            return "book"
        if best_move and move == best_move:
            return "best"
        if cp_loss_mover <= 12:
            return "excellent"
        if cp_loss_mover <= 35:
            return "good"
        if cp_loss_mover < 90:
            return "inaccuracy"
        if cp_loss_mover < 200:
            return "mistake"
        return "blunder"

    def _run_analysis_background(self):
        try:
            model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
            pgn_string = get_last_game_pgn(TARGET_USERNAME)
            game = chess.pgn.read_game(io.StringIO(pgn_string))

            self.white_name = game.headers.get("White", "")
            self.black_name = game.headers.get("Black", "")
            self.white_elo = game.headers.get("WhiteElo", "")
            self.black_elo = game.headers.get("BlackElo", "")

            if self.white_name.lower() == USERNAME.lower():
                self.my_color = chess.WHITE
            elif self.black_name.lower() == USERNAME.lower():
                self.my_color = chess.BLACK
            elif self.white_name.lower() == TARGET_USERNAME.lower():
                self.my_color = chess.WHITE
            else:
                self.my_color = chess.BLACK

            self.bottom_color = self.my_color

            opening_hdr = game.headers.get("Opening", "")
            eco_url = game.headers.get("ECOUrl", "")
            if not opening_hdr and eco_url:
                opening_hdr = eco_url.split("/")[-1].replace("-", " ")
            self.pgn_opening_name = opening_hdr

            board = game.board()
            self.boards_history = [board.copy()]
            self.moves_history = [None]
            self.uci_history = []
            self.move_meta_history = [None]

            white_acc_scores = []
            black_acc_scores = []

            feature_cols = ["cp_loss", "mat_diff", "hanging_diff", "mobility_diff", "best_gives_check"]
            ply = 0

            with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
                prev_info = engine.analyse(board, chess.engine.Limit(depth=ENGINE_DEPTH))
                w_pov_0 = prev_info["score"].pov(chess.WHITE)
                self.evals_history = [{
                    "cp_white": w_pov_0.score(mate_score=2000) or 0,
                    "mate_white": w_pov_0.mate()
                }]

                for move in game.mainline_moves():
                    ply += 1
                    turn_color = board.turn
                    fen_before = board.fen()
                    board_before = board.copy()

                    moved_piece = board_before.piece_at(move.from_square)
                    piece_type = moved_piece.piece_type if moved_piece else chess.PAWN

                    played_san = board_before.san(move)
                    score_before_my = prev_info["score"].pov(self.my_color).score(mate_score=2000)
                    score_before_mover = prev_info["score"].pov(turn_color).score(mate_score=2000)

                    best_pv = prev_info.get("pv", [])
                    best_move_engine = best_pv[0] if best_pv else None
                    best_san = board_before.san(best_move_engine) if best_move_engine else "—"
                    best_line_san = board_before.variation_san(best_pv[:5]) if best_pv else ""

                    board.push(move)
                    self.boards_history.append(board.copy())
                    self.moves_history.append(move)
                    self.uci_history.append(move.uci())

                    curr_info = engine.analyse(board, chess.engine.Limit(depth=ENGINE_DEPTH))
                    score_after_my = curr_info["score"].pov(self.my_color).score(mate_score=2000)
                    score_after_mover = curr_info["score"].pov(turn_color).score(mate_score=2000)

                    cp_loss_mover = max(0, (score_before_mover or 0) - (score_after_mover or 0))
                    move_acc = compute_move_accuracy(cp_loss_mover)
                    if turn_color == chess.WHITE:
                        white_acc_scores.append(move_acc)
                    else:
                        black_acc_scores.append(move_acc)

                    w_pov = curr_info["score"].pov(chess.WHITE)
                    self.evals_history.append({
                        "cp_white": w_pov.score(mate_score=2000) or 0,
                        "mate_white": w_pov.mate()
                    })

                    punish_pv = curr_info.get("pv", [])
                    punish_line_san = board.variation_san(punish_pv[:5]) if punish_pv else ""

                    ml_prediction_for_ply = None

                    if turn_color == self.my_color and score_before_my is not None and score_after_my is not None:
                        cp_loss = score_before_my - score_after_my
                        if cp_loss >= CP_LOSS_THRESHOLD and best_move_engine and move != best_move_engine:
                            board_best = chess.Board(fen_before)
                            board_best.push(best_move_engine)

                            mat_diff = get_material_balance(board_best, self.my_color) - get_material_balance(board, self.my_color)
                            hanging_diff = count_hanging_pieces(board, self.my_color) - count_hanging_pieces(board_best, self.my_color)
                            mobility_diff = board_best.legal_moves.count() - board.legal_moves.count()
                            best_gives_check = int(board_best.is_check())

                            hanging_pieces_raw, hanging_squares = get_hanging_raw(board, self.my_color)
                            attacked_after_best = list(board_best.attacks(best_move_engine.to_square))
                            attacked_names = ", ".join(chess.square_name(sq) for sq in attacked_after_best[:6])

                            if model is not None:
                                X_input = pd.DataFrame([{
                                    "cp_loss": cp_loss,
                                    "mat_diff": mat_diff,
                                    "hanging_diff": hanging_diff,
                                    "mobility_diff": mobility_diff,
                                    "best_gives_check": best_gives_check
                                }])[feature_cols]
                                prediction = model.predict(X_input)[0]
                            else:
                                prediction = "blunder" if cp_loss >= 200 else ("tactical_error" if cp_loss >= 120 else "inaccuracy")

                            ml_prediction_for_ply = prediction

                            show_captured = prediction not in ("blunder", "hanging_piece")
                            if prediction in ("blunder", "hanging_piece"):
                                combo_board_start = board.copy()
                                combo_moves = punish_pv[:5] if prediction == "blunder" else punish_pv[:4]
                            else:
                                combo_board_start = board_before.copy()
                                combo_moves = best_pv[:5] if prediction == "tactical_error" else best_pv[:4]

                            self.errors_by_ply[ply] = {
                                "move_number": board_before.fullmove_number,
                                "played_move": move,
                                "played_san": played_san,
                                "best_move": best_move_engine,
                                "best_san": best_san,
                                "cp_loss": cp_loss,
                                "prediction": prediction,
                                "punish_line_san": punish_line_san,
                                "best_line_san": best_line_san,
                                "attacked_names": attacked_names,
                                "hanging_pieces_raw": hanging_pieces_raw,
                                "hanging_squares": hanging_squares,
                                "attacked_squares": attacked_after_best if show_captured else [],
                                "combo_board_start": combo_board_start,
                                "combo_moves": combo_moves,
                            }

                    badge_type = self._classify_move_badge(
                        ply, move, best_move_engine, cp_loss_mover,
                        self.uci_history[:ply], ml_prediction_for_ply
                    )

                    self.move_meta_history.append({
                        "ply": ply,
                        "move_number": board_before.fullmove_number,
                        "is_white": (turn_color == chess.WHITE),
                        "piece_type": piece_type,
                        "san": played_san,
                        "badge": badge_type,
                        "to_sq": move.to_square,
                    })

                    prev_info = curr_info

            self.white_accuracy = (sum(white_acc_scores) / len(white_acc_scores)) if white_acc_scores else 100.0
            self.black_accuracy = (sum(black_acc_scores) / len(black_acc_scores)) if black_acc_scores else 100.0

            self.analysis_finished = True
            self.root.after(0, self._on_analysis_complete)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error / Ошибка", str(e)))

    def _on_analysis_complete(self):
        self.btn_prev.set_state(True)
        self.btn_next.set_state(True)
        self.current_ply = 0
        self.latest_ply = 0
        self._draw_chat_header()
        self.update_view()

    def prev_move(self):
        if not self.boards_history or self.current_ply <= 0:
            return
        self.stop_combo_animation()
        self.selected_square = None
        self.legal_target_squares = []
        prev_board = self.boards_history[self.current_ply]
        self.current_ply -= 1
        self.update_view(animate_from_board=prev_board)

    def next_move(self):
        if not self.boards_history or self.current_ply >= len(self.boards_history) - 1:
            return
        self.stop_combo_animation()
        self.selected_square = None
        self.legal_target_squares = []
        prev_board = self.boards_history[self.current_ply]
        self.current_ply += 1
        if self.current_ply > self.latest_ply:
            self.latest_ply = self.current_ply
        self.update_view(animate_from_board=prev_board)

    def return_to_latest_ply(self):
        if not self.boards_history:
            return
        self.stop_combo_animation()
        self.selected_square = None
        self.legal_target_squares = []
        prev_board = self.boards_history[self.current_ply]
        self.current_ply = self.latest_ply
        self.update_view(animate_from_board=prev_board)

    def toggle_best_move_arrow(self):
        self.show_best_move_arrow = not self.show_best_move_arrow
        self.draw_board(self.boards_history[self.current_ply], error_info=self.errors_by_ply.get(self.current_ply))

    def stop_combo_animation(self):
        if self.combo_timer:
            self.root.after_cancel(self.combo_timer)
            self.combo_timer = None
        self.animating_combo = False
        self.combo_board = None
        self.combo_last_move = None
        tr = TRANSLATIONS[self.lang]
        self.btn_combo.set_text_and_color(tr["btn_combo"], "#3B2E1E")

    def play_combination(self):
        if self.animating_combo:
            self.stop_combo_animation()
            self.update_view()
            return

        err = self.errors_by_ply.get(self.current_ply)
        if not err or not err["combo_moves"]:
            return

        tr = TRANSLATIONS[self.lang]
        self.animating_combo = True
        self.btn_combo.set_text_and_color(tr["btn_combo_stop"], "#6B2D28")
        self.combo_board = err["combo_board_start"].copy()
        self._animate_combo_step(list(err["combo_moves"]), 0)

    def _animate_combo_step(self, moves_list, idx):
        if not self.animating_combo or idx >= len(moves_list):
            return

        prev_b = self.combo_board.copy()
        move = moves_list[idx]
        self.combo_last_move = move
        self.combo_board.push(move)

        self._start_smooth_piece_move(prev_b, self.combo_board, move, combo_mode=True)

        if idx + 1 < len(moves_list):
            self.combo_timer = self.root.after(880, self._animate_combo_step, moves_list, idx + 1)

    def _on_board_stage_resize(self, event):
        extra_w = self.eval_bar_width + self.eval_bar_gap + self.board_margin * 2
        extra_h = self.board_margin * 2
        avail_sq_w = (event.width - extra_w) // 8
        avail_sq_h = (event.height - extra_h) // 8
        sq = min(avail_sq_w, avail_sq_h)
        if sq < 38:
            return
        self.sq_size = sq
        canvas_w = self.eval_bar_width + self.eval_bar_gap + self.sq_size * 8 + self.board_margin * 2
        canvas_h = self.sq_size * 8 + self.board_margin * 2
        self.board_canvas.config(width=canvas_w, height=canvas_h)
        if self.boards_history:
            active_board = self.combo_board if self.animating_combo else self.boards_history[self.current_ply]
            self.draw_board(
                active_board,
                error_info=None if self.animating_combo else self.errors_by_ply.get(self.current_ply),
                combo_move=self.combo_last_move
            )

    @property
    def board_origin_x(self) -> int:
        return self.eval_bar_width + self.eval_bar_gap + self.board_margin

    @property
    def board_origin_y(self) -> int:
        return self.board_margin

    def square_to_xy(self, square: chess.Square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        if self.bottom_color == chess.WHITE:
            col, row = file, 7 - rank
        else:
            col, row = 7 - file, rank
        x = self.board_origin_x + col * self.sq_size
        y = self.board_origin_y + row * self.sq_size
        return x, y

    def xy_to_square(self, x: float, y: float):
        col = int((x - self.board_origin_x) // self.sq_size)
        row = int((y - self.board_origin_y) // self.sq_size)
        if not (0 <= col < 8 and 0 <= row < 8):
            return None
        if self.bottom_color == chess.WHITE:
            file, rank = col, 7 - row
        else:
            file, rank = 7 - col, row
        return chess.square(file, rank)

    def _on_board_click(self, event):
        if not self.boards_history or self.animating_combo:
            return
        sq = self.xy_to_square(event.x, event.y)
        if sq is None:
            return

        board = self.boards_history[self.current_ply]
        piece = board.piece_at(sq)

        if self.selected_square == sq:
            self.selected_square = None
            self.legal_target_squares = []
        elif piece is not None:
            self.selected_square = sq
            self.legal_target_squares = [
                m.to_square for m in board.legal_moves if m.from_square == sq
            ]
        else:
            self.selected_square = None
            self.legal_target_squares = []

        self.draw_board(board, error_info=self.errors_by_ply.get(self.current_ply))

    def update_view(self, animate_from_board: chess.Board = None):
        if not self.boards_history:
            return

        tr = TRANSLATIONS[self.lang]
        board = self.boards_history[self.current_ply]
        err = self.errors_by_ply.get(self.current_ply)

        if err:
            self._ensure_mistake_message_in_chat(self.current_ply)

        if self.current_ply < len(self.evals_history):
            ev = self.evals_history[self.current_ply]
            self.target_white_ratio = eval_to_white_ratio(ev["cp_white"], ev["mate_white"])
            self.current_eval_label = format_eval_label(ev["cp_white"], ev["mate_white"])
            self.current_eval_white_adv = (ev["cp_white"] >= 0) if ev["mate_white"] is None else (ev["mate_white"] > 0)
            self._animate_eval_bar()

        self._redraw_player_cards()
        self._redraw_move_history()
        self._draw_eval_graph()

        self.btn_prev.set_state(self.current_ply > 0)
        self.btn_next.set_state(self.current_ply < len(self.boards_history) - 1)
        self.btn_best.set_state(bool(err and err["best_move"]))
        self.btn_combo.set_state(bool(err and err["combo_moves"]))

        if self.current_ply < self.latest_ply:
            self.btn_return_live.set_text_and_color(
                tr["btn_return_live"].format(move=(self.latest_ply + 1) // 2), "#4A3222"
            )
            self.btn_return_live.pack(side=tk.RIGHT, padx=(8, 0))
        else:
            self.btn_return_live.pack_forget()

        for p in self.chat_cards:
            self._draw_mistake_card(p)

        last_move = self.moves_history[self.current_ply] if self.current_ply > 0 else None
        if animate_from_board is not None and last_move is not None:
            self._start_smooth_piece_move(animate_from_board, board, last_move, combo_mode=False)
        else:
            self.draw_board(board, error_info=err)

    def _animate_eval_bar(self):
        diff = self.target_white_ratio - self.displayed_white_ratio
        if abs(diff) > 0.008:
            self.displayed_white_ratio += diff * 0.28
            if not self.move_anim_active and self.boards_history:
                active_b = self.combo_board if self.animating_combo else self.boards_history[self.current_ply]
                self.draw_board(
                    active_b,
                    error_info=None if self.animating_combo else self.errors_by_ply.get(self.current_ply),
                    combo_move=self.combo_last_move
                )
            self.root.after(20, self._animate_eval_bar)
        else:
            self.displayed_white_ratio = self.target_white_ratio

    def _start_smooth_piece_move(self, board_from: chess.Board, board_to: chess.Board, move: chess.Move, combo_mode=False):
        piece = board_to.piece_at(move.to_square)
        if piece is None:
            self.draw_board(
                board_to,
                error_info=None if combo_mode else self.errors_by_ply.get(self.current_ply),
                combo_move=move if combo_mode else None
            )
            return

        x1, y1 = self.square_to_xy(move.from_square)
        x2, y2 = self.square_to_xy(move.to_square)
        self.move_anim_active = True
        self.move_anim_data = {
            "piece": piece,
            "x1": x1 + self.sq_size / 2,
            "y1": y1 + self.sq_size / 2,
            "x2": x2 + self.sq_size / 2,
            "y2": y2 + self.sq_size / 2,
            "hide_sq": move.to_square,
            "step": 0,
            "total_steps": 10,
            "board_to": board_to,
            "combo_move": move if combo_mode else None,
            "error_info": None if combo_mode else self.errors_by_ply.get(self.current_ply)
        }
        self._step_smooth_piece_move()

    def _step_smooth_piece_move(self):
        if not self.move_anim_active or not self.move_anim_data:
            return
        d = self.move_anim_data
        d["step"] += 1
        t = d["step"] / d["total_steps"]
        ease = 1.0 - (1.0 - t) ** 3
        cx = d["x1"] + (d["x2"] - d["x1"]) * ease
        cy = d["y1"] + (d["y2"] - d["y1"]) * ease

        self.draw_board(
            d["board_to"],
            error_info=d["error_info"],
            combo_move=d["combo_move"],
            anim_piece=(d["piece"], cx, cy, d["hide_sq"])
        )

        if d["step"] < d["total_steps"]:
            self.root.after(18, self._step_smooth_piece_move)
        else:
            self.move_anim_active = False
            self.move_anim_data = None
            self.draw_board(d["board_to"], error_info=d["error_info"], combo_move=d["combo_move"])

    def _draw_evaluation_bar(self, c: tk.Canvas, board_px: int):
        bx1 = 4
        bx2 = self.eval_bar_width
        by1 = self.board_origin_y
        by2 = by1 + board_px
        bar_h = by2 - by1

        bottom_ratio = self.displayed_white_ratio if self.bottom_color == chess.WHITE else (1.0 - self.displayed_white_ratio)
        split_y = by2 - bar_h * bottom_ratio

        top_col = THEME["eval_black"] if self.bottom_color == chess.WHITE else THEME["eval_white"]
        bot_col = THEME["eval_white"] if self.bottom_color == chess.WHITE else THEME["eval_black"]

        create_rounded_rect(c, bx1, by1, bx2, by2, r=12, fill=top_col, outline=THEME["border_subtle"], width=1.5)

        if by2 - split_y > 8:
            c.create_rectangle(bx1 + 1, split_y, bx2 - 1, by2 - 10, fill=bot_col, outline="")
            create_rounded_rect(c, bx1 + 1, max(by1 + 2, by2 - 22), bx2 - 1, by2 - 1, r=11, fill=bot_col, outline="")

        mid_y = (by1 + by2) / 2
        c.create_line(bx1 + 4, mid_y, bx2 - 4, mid_y, fill=THEME["accent_ochre"], width=1.5)

        adv_is_bottom = (self.current_eval_white_adv and self.bottom_color == chess.WHITE) or (
            not self.current_eval_white_adv and self.bottom_color == chess.BLACK
        )
        txt_x = (bx1 + bx2) / 2
        if adv_is_bottom:
            txt_y = by2 - 14
            txt_fg = "#161513" if bot_col == THEME["eval_white"] else THEME["text_primary"]
        else:
            txt_y = by1 + 14
            txt_fg = "#161513" if top_col == THEME["eval_white"] else THEME["text_primary"]

        c.create_text(txt_x, txt_y, text=self.current_eval_label, fill=txt_fg, font=("Segoe UI", 8, "bold"))

    def draw_board(
        self, board: chess.Board, error_info: dict = None,
        combo_move: chess.Move = None, anim_piece: tuple = None
    ):
        c = self.board_canvas
        c.delete("all")
        board_px = self.sq_size * 8

        self._draw_evaluation_bar(c, board_px)

        frame_x1 = self.board_origin_x - self.board_margin + 2
        frame_y1 = 2
        frame_x2 = self.board_origin_x + board_px + self.board_margin - 2
        frame_y2 = board_px + self.board_margin * 2 - 2

        create_rounded_rect(
            c, frame_x1, frame_y1, frame_x2, frame_y2,
            r=22, fill=THEME["bg_panel"], outline=THEME["border_subtle"], width=2
        )

        last_move = combo_move if combo_move else (
            self.moves_history[self.current_ply] if self.current_ply > 0 else None
        )
        king_in_check_sq = board.king(board.turn) if board.is_check() else None

        for sq in chess.SQUARES:
            x, y = self.square_to_xy(sq)
            is_light = (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 1
            bg_color = THEME["sq_light"] if is_light else THEME["sq_dark"]

            if last_move and sq in (last_move.from_square, last_move.to_square):
                bg_color = THEME["sq_last_light"] if is_light else THEME["sq_last_dark"]

            if self.selected_square == sq:
                bg_color = THEME["sq_selected"]

            c.create_rectangle(x, y, x + self.sq_size, y + self.sq_size, fill=bg_color, outline="")

            if sq == king_in_check_sq:
                pad = 3
                create_rounded_rect(
                    c, x + pad, y + pad, x + self.sq_size - pad, y + self.sq_size - pad,
                    r=10, fill=THEME["sq_check"], outline="#FFFFFF", width=1.5
                )

            if error_info and not combo_move and sq in error_info["hanging_squares"]:
                pad = 4
                create_rounded_rect(
                    c, x + pad, y + pad, x + self.sq_size - pad, y + self.sq_size - pad,
                    r=10, fill="", outline=THEME["accent_terra"], width=3
                )

            if error_info and not combo_move and self.show_best_move_arrow and sq in error_info["attacked_squares"]:
                pad = 6
                create_rounded_rect(
                    c, x + pad, y + pad, x + self.sq_size - pad, y + self.sq_size - pad,
                    r=8, fill="", outline=THEME["accent_sage"], width=2
                )

            if sq in self.legal_target_squares:
                cx = x + self.sq_size / 2
                cy = y + self.sq_size / 2
                if board.piece_at(sq) is not None:
                    ring_r = self.sq_size * 0.42
                    c.create_oval(
                        cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r,
                        outline="#3E4A3B", width=3.5
                    )
                else:
                    dot_r = self.sq_size * 0.14
                    c.create_oval(
                        cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r,
                        fill="#4A5746", outline=""
                    )

        c.create_rectangle(
            self.board_origin_x, self.board_origin_y,
            self.board_origin_x + board_px, self.board_origin_y + board_px,
            outline="#3B3228", width=1.5
        )

        files = "abcdefgh" if self.bottom_color == chess.WHITE else "hgfedcba"
        ranks = "87654321" if self.bottom_color == chess.WHITE else "12345678"
        for i in range(8):
            fx = self.board_origin_x + i * self.sq_size + self.sq_size / 2
            fy = self.board_origin_y + board_px + self.board_margin * 0.52
            c.create_text(fx, fy, text=files[i], fill=THEME["text_primary"], font=("Segoe UI", 10, "bold"))

            rx = self.board_origin_x + board_px + self.board_margin * 0.52
            ry = self.board_origin_y + i * self.sq_size + self.sq_size / 2
            c.create_text(rx, ry, text=ranks[i], fill=THEME["text_primary"], font=("Segoe UI", 10, "bold"))

        hide_sq = anim_piece[3] if anim_piece else None
        for sq, piece in board.piece_map().items():
            if sq == hide_sq:
                continue
            x, y = self.square_to_xy(sq)
            draw_classic_merida_piece(
                c, x + self.sq_size / 2, y + self.sq_size / 2,
                self.sq_size, piece.piece_type, piece.color == chess.WHITE
            )

        if anim_piece:
            p_obj, acx, acy, _ = anim_piece
            draw_classic_merida_piece(c, acx, acy, self.sq_size, p_obj.piece_type, p_obj.color == chess.WHITE)

        if error_info and not combo_move:
            if error_info["played_move"]:
                self._draw_smooth_arrow(
                    error_info["played_move"].from_square,
                    error_info["played_move"].to_square,
                    THEME["accent_terra"], width=5
                )
            if self.show_best_move_arrow and error_info["best_move"]:
                self._draw_smooth_arrow(
                    error_info["best_move"].from_square,
                    error_info["best_move"].to_square,
                    "#606C38", width=7
                )

        if combo_move:
            self._draw_smooth_arrow(
                combo_move.from_square, combo_move.to_square,
                THEME["accent_ochre"], width=6
            )

        
        if not combo_move and not anim_piece and 0 < self.current_ply < len(self.move_meta_history):
            meta = self.move_meta_history[self.current_ply]
            if meta and meta.get("badge"):
                bx, by = self.square_to_xy(meta["to_sq"])
                badge_r = max(10.0, self.sq_size * 0.19)
                draw_move_classification_badge(
                    c, bx + self.sq_size - badge_r * 0.90, by + badge_r * 0.90,
                    badge_r, meta["badge"]
                )

    def _draw_smooth_arrow(self, from_sq: chess.Square, to_sq: chess.Square, color: str, width: int = 6):
        x1, y1 = self.square_to_xy(from_sq)
        x2, y2 = self.square_to_xy(to_sq)
        cx1, cy1 = x1 + self.sq_size / 2, y1 + self.sq_size / 2
        cx2, cy2 = x2 + self.sq_size / 2, y2 + self.sq_size / 2
        self.board_canvas.create_line(
            cx1, cy1, cx2, cy2,
            fill=color, width=width, arrow=tk.LAST,
            arrowshape=(15, 19, 7), capstyle=tk.ROUND
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    onboarding = StartupOnboardingDialog(root)
    root.wait_window(onboarding.win)

    if not onboarding.completed:
        raise SystemExit()

    USERNAME = onboarding.my_username
    TARGET_USERNAME = onboarding.target_username
    STOCKFISH_PATH = onboarding.sf_path
    USER_AGENT = f"ML-Chess-Analyzer/2.4 (user: {USERNAME})"

    if not os.path.exists(MODEL_PATH):
        alt_model = os.path.join(os.getcwd(), "chess_error_model.joblib")
        if os.path.exists(alt_model):
            MODEL_PATH = alt_model

    root.deiconify()
    app = ChessAnalyzerGUI(root)
    root.mainloop()