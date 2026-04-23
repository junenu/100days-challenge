import pygame
import sys

# --- Constants ---
BOARD_SIZE = 8
CELL_SIZE = 70
MARGIN = 40
INFO_HEIGHT = 100

WIDTH = BOARD_SIZE * CELL_SIZE + MARGIN * 2
HEIGHT = BOARD_SIZE * CELL_SIZE + MARGIN * 2 + INFO_HEIGHT

FPS = 60

# Colors
C_BG = (34, 34, 34)
C_BOARD = (0, 120, 60)
C_GRID = (0, 90, 45)
C_BLACK = (20, 20, 20)
C_WHITE = (240, 240, 240)
C_HINT = (100, 200, 120, 120)
C_TEXT = (220, 220, 220)
C_HIGHLIGHT = (255, 220, 50)
C_BUTTON = (60, 60, 60)
C_BUTTON_HOVER = (90, 90, 90)

EMPTY, BLACK, WHITE = 0, 1, 2

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]


# --- Board logic ---
def make_board():
    board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    mid = BOARD_SIZE // 2
    board[mid - 1][mid - 1] = WHITE
    board[mid - 1][mid] = BLACK
    board[mid][mid - 1] = BLACK
    board[mid][mid] = WHITE
    return board


def opponent(player):
    return WHITE if player == BLACK else BLACK


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def flips_for_move(board, r, c, player):
    if board[r][c] != EMPTY:
        return []
    opp = opponent(player)
    all_flips = []
    for dr, dc in DIRECTIONS:
        line = []
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc) and board[nr][nc] == opp:
            line.append((nr, nc))
            nr += dr
            nc += dc
        if line and in_bounds(nr, nc) and board[nr][nc] == player:
            all_flips.extend(line)
    return all_flips


def valid_moves(board, player):
    return [(r, c) for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if flips_for_move(board, r, c, player)]


def apply_move(board, r, c, player):
    new_board = [row[:] for row in board]
    flips = flips_for_move(new_board, r, c, player)
    new_board[r][c] = player
    for fr, fc in flips:
        new_board[fr][fc] = player
    return new_board


def count(board):
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    return black, white


def board_pos(r, c):
    x = MARGIN + c * CELL_SIZE + CELL_SIZE // 2
    y = MARGIN + r * CELL_SIZE + CELL_SIZE // 2
    return x, y


# --- Simple AI ---
WEIGHT_MAP = [
    [100, -20, 10,  5,  5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [ 10,  -2,  1,  1,  1,  1,  -2,  10],
    [  5,  -2,  1,  1,  1,  1,  -2,   5],
    [  5,  -2,  1,  1,  1,  1,  -2,   5],
    [ 10,  -2,  1,  1,  1,  1,  -2,  10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10,  5,  5, 10, -20, 100],
]


def ai_score(board, player):
    opp = opponent(player)
    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == player:
                score += WEIGHT_MAP[r][c]
            elif board[r][c] == opp:
                score -= WEIGHT_MAP[r][c]
    return score


def minimax(board, player, depth, alpha, beta, maximizing):
    moves = valid_moves(board, player)
    if depth == 0 or not moves:
        return ai_score(board, WHITE), None

    best_move = None
    if maximizing:
        best_val = -10**9
        for r, c in moves:
            nb = apply_move(board, r, c, player)
            val, _ = minimax(nb, opponent(player), depth - 1, alpha, beta, False)
            if val > best_val:
                best_val, best_move = val, (r, c)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best_val, best_move
    else:
        best_val = 10**9
        for r, c in moves:
            nb = apply_move(board, r, c, player)
            val, _ = minimax(nb, opponent(player), depth - 1, alpha, beta, True)
            if val < best_val:
                best_val, best_move = val, (r, c)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best_val, best_move


def ai_move(board):
    _, move = minimax(board, WHITE, depth=4, alpha=-10**9, beta=10**9, maximizing=True)
    return move


# --- Drawing ---
def draw_board(surface, board, hints, selected, font_small):
    # Board background
    pygame.draw.rect(surface, C_BOARD,
                     (MARGIN, MARGIN, BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE))

    # Grid lines
    for i in range(BOARD_SIZE + 1):
        x = MARGIN + i * CELL_SIZE
        y = MARGIN + i * CELL_SIZE
        pygame.draw.line(surface, C_GRID, (x, MARGIN), (x, MARGIN + BOARD_SIZE * CELL_SIZE), 1)
        pygame.draw.line(surface, C_GRID, (MARGIN, y), (MARGIN + BOARD_SIZE * CELL_SIZE, y), 1)

    # Hint overlay
    hint_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    hint_surf.fill((100, 200, 120, 80))

    for (r, c) in hints:
        x = MARGIN + c * CELL_SIZE
        y = MARGIN + r * CELL_SIZE
        surface.blit(hint_surf, (x, y))
        # Dot in center
        cx, cy = board_pos(r, c)
        pygame.draw.circle(surface, (80, 200, 100), (cx, cy), 8)

    # Pieces
    radius = CELL_SIZE // 2 - 5
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == EMPTY:
                continue
            cx, cy = board_pos(r, c)
            color = C_BLACK if board[r][c] == BLACK else C_WHITE
            shadow_color = (0, 0, 0, 100)
            pygame.draw.circle(surface, (10, 10, 10), (cx + 2, cy + 2), radius)
            pygame.draw.circle(surface, color, (cx, cy), radius)
            # Highlight on white piece
            if board[r][c] == WHITE:
                pygame.draw.circle(surface, (255, 255, 255), (cx - radius // 4, cy - radius // 4), radius // 5)

    # Column/Row labels
    for i in range(BOARD_SIZE):
        label = font_small.render(chr(ord('A') + i), True, C_TEXT)
        surface.blit(label, (MARGIN + i * CELL_SIZE + CELL_SIZE // 2 - label.get_width() // 2,
                              MARGIN - 22))
        label = font_small.render(str(i + 1), True, C_TEXT)
        surface.blit(label, (MARGIN - 20 - label.get_width() // 2,
                              MARGIN + i * CELL_SIZE + CELL_SIZE // 2 - label.get_height() // 2))


def draw_info(surface, board, current_player, game_over, passed, font, font_small, buttons):
    info_y = MARGIN + BOARD_SIZE * CELL_SIZE + 10

    black_cnt, white_cnt = count(board)

    # Player indicators
    for col, (player_color, piece_color, label, score) in enumerate([
        (C_TEXT, C_BLACK, "Black (You)", black_cnt),
        (C_TEXT, C_WHITE, "White (AI)", white_cnt),
    ]):
        x = MARGIN + col * (WIDTH // 2 - MARGIN)
        pygame.draw.circle(surface, piece_color, (x + 15, info_y + 20), 12)
        if col == 0 and current_player == BLACK and not game_over:
            pygame.draw.circle(surface, C_HIGHLIGHT, (x + 15, info_y + 20), 14, 2)
        elif col == 1 and current_player == WHITE and not game_over:
            pygame.draw.circle(surface, C_HIGHLIGHT, (x + 15, info_y + 20), 14, 2)
        t = font_small.render(f"{label}: {score}", True, C_TEXT)
        surface.blit(t, (x + 32, info_y + 12))

    # Status message
    if game_over:
        b, w = count(board)
        if b > w:
            msg = "Black wins!"
        elif w > b:
            msg = "White (AI) wins!"
        else:
            msg = "Draw!"
        t = font.render(msg, True, C_HIGHLIGHT)
        surface.blit(t, (WIDTH // 2 - t.get_width() // 2, info_y + 40))
    elif passed:
        t = font_small.render("No valid moves — turn passed", True, (200, 100, 100))
        surface.blit(t, (WIDTH // 2 - t.get_width() // 2, info_y + 45))

    # Buttons
    mouse_pos = pygame.mouse.get_pos()
    for btn in buttons:
        color = C_BUTTON_HOVER if btn["rect"].collidepoint(mouse_pos) else C_BUTTON
        pygame.draw.rect(surface, color, btn["rect"], border_radius=6)
        t = font_small.render(btn["label"], True, C_TEXT)
        surface.blit(t, (btn["rect"].centerx - t.get_width() // 2,
                         btn["rect"].centery - t.get_height() // 2))


def cell_from_mouse(mx, my):
    c = (mx - MARGIN) // CELL_SIZE
    r = (my - MARGIN) // CELL_SIZE
    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        return r, c
    return None


# --- Main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Othello — Day 012")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 22, bold=True)
    font_small = pygame.font.SysFont("Arial", 17)

    btn_reset = {
        "label": "Reset",
        "rect": pygame.Rect(WIDTH - MARGIN - 90, MARGIN + BOARD_SIZE * CELL_SIZE + 60, 80, 28),
    }
    btn_hint = {
        "label": "Hints: ON",
        "rect": pygame.Rect(WIDTH - MARGIN - 190, MARGIN + BOARD_SIZE * CELL_SIZE + 60, 90, 28),
    }
    buttons = [btn_hint, btn_reset]

    board = make_board()
    current_player = BLACK
    game_over = False
    passed = False
    show_hints = True
    ai_thinking = False
    ai_delay = 0

    while True:
        clock.tick(FPS)
        hints = valid_moves(board, current_player) if show_hints and not game_over else []

        # AI turn
        if current_player == WHITE and not game_over:
            ai_delay += 1
            if ai_delay >= FPS // 2:  # 0.5 sec delay so it feels natural
                ai_delay = 0
                moves = valid_moves(board, WHITE)
                if moves:
                    move = ai_move(board)
                    if move:
                        board = apply_move(board, move[0], move[1], WHITE)
                passed = not bool(moves)
                current_player = BLACK
                # Check if black also has no moves
                if not valid_moves(board, BLACK):
                    if not valid_moves(board, WHITE):
                        game_over = True
                    else:
                        passed = True
                        current_player = WHITE

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = make_board()
                    current_player = BLACK
                    game_over = False
                    passed = False
                    ai_delay = 0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Button clicks
                if btn_reset["rect"].collidepoint(mx, my):
                    board = make_board()
                    current_player = BLACK
                    game_over = False
                    passed = False
                    ai_delay = 0
                    continue

                if btn_hint["rect"].collidepoint(mx, my):
                    show_hints = not show_hints
                    btn_hint["label"] = f"Hints: {'ON' if show_hints else 'OFF'}"
                    continue

                # Board click — player's turn only
                if current_player == BLACK and not game_over:
                    cell = cell_from_mouse(mx, my)
                    if cell:
                        r, c = cell
                        if flips_for_move(board, r, c, BLACK):
                            board = apply_move(board, r, c, BLACK)
                            passed = False
                            current_player = WHITE
                            ai_delay = 0

                            # Check if white has no moves
                            if not valid_moves(board, WHITE):
                                if not valid_moves(board, BLACK):
                                    game_over = True
                                else:
                                    passed = True
                                    current_player = BLACK

        # --- Draw ---
        screen.fill(C_BG)
        draw_board(screen, board,
                   hints if current_player == BLACK else [],
                   None, font_small)
        draw_info(screen, board, current_player, game_over, passed, font, font_small, buttons)
        pygame.display.flip()


if __name__ == "__main__":
    main()
