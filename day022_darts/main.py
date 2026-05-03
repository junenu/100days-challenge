"""
Darts Game — 501 ルール 2 プレイヤー（vs CPU）
"""
import pygame
import math
import random
import sys

# ---- 定数 ----
SCREEN_W, SCREEN_H = 1000, 720
FPS = 60

BG_COLOR      = (20, 20, 30)
TEXT_COLOR    = (230, 230, 230)
PANEL_COLOR   = (30, 30, 45)
HIGHLIGHT     = (255, 220, 50)
RED           = (220, 50, 50)
GREEN         = (50, 200, 80)
DART_COLOR    = (180, 180, 60)
SHADOW_COLOR  = (0, 0, 0, 120)

BOARD_CX = 480
BOARD_CY = 360
BOARD_R  = 260   # ボード全体半径（px）

# 実際のダーツボード比率に基づく各ゾーン半径
_SCALE = BOARD_R / 170.0
DBULL_R  = 6.35  * _SCALE   # ダブルブル（50 点）
SBULL_R  = 15.9  * _SCALE   # シングルブル（25 点）
TRI_IN   = 99.0  * _SCALE   # トリプルリング 内側
TRI_OUT  = 107.0 * _SCALE   # トリプルリング 外側
DBL_IN   = 162.0 * _SCALE   # ダブルリング 内側
DBL_OUT  = 170.0 * _SCALE   # ダブルリング 外側

# セグメント順（12 時から時計回り）
SEGMENTS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
NUM_SEG  = 20
SEG_ANG  = 2 * math.pi / NUM_SEG           # 1 セグメント角度
HALF_SEG = SEG_ANG / 2                      # 半セグメント
OFFSET   = -math.pi / 2 - HALF_SEG         # 12 時位置補正

# ダーツボード配色
COLORS_DARK  = {"base": (20, 20, 20),  "red": (180, 30, 30),  "green": (20, 100, 40)}
COLORS_LIGHT = {"base": (220, 200, 170), "red": (220, 80, 80), "green": (60, 160, 80)}

STARTING_SCORE = 501
DARTS_PER_TURN = 3
CPU_SKILL = 0.82   # CPU 命中精度（0〜1）


def angle_of_segment(seg_idx: int) -> float:
    """セグメントインデックスの中心角（ラジアン）を返す"""
    return OFFSET + seg_idx * SEG_ANG + HALF_SEG


def score_at(dx: float, dy: float) -> tuple[int, str]:
    """
    ボード中心からの相対座標 (dx, dy) を受け取り
    (得点, ゾーン名) を返す。ボード外は (0, "Miss")。
    """
    r = math.hypot(dx, dy)
    if r > DBL_OUT:
        return 0, "Miss"
    if r <= DBULL_R:
        return 50, "Double Bull"
    if r <= SBULL_R:
        return 25, "Bull"

    # セグメント判定（atan2 で角度→インデックス）
    angle = math.atan2(dy, dx) - OFFSET
    angle %= (2 * math.pi)
    seg_idx = int(angle / SEG_ANG)
    seg_idx = max(0, min(NUM_SEG - 1, seg_idx))
    number = SEGMENTS[seg_idx]

    if TRI_IN <= r <= TRI_OUT:
        return number * 3, f"Triple {number}"
    if DBL_IN <= r <= DBL_OUT:
        return number * 2, f"Double {number}"
    return number, str(number)


def draw_board(surf: pygame.Surface, alpha_overlay: pygame.Surface) -> None:
    """ダーツボードを描画する"""
    cx, cy = BOARD_CX, BOARD_CY

    # 外枠
    pygame.draw.circle(surf, (60, 40, 20), (cx, cy), int(DBL_OUT) + 10)
    pygame.draw.circle(surf, (10, 10, 10),  (cx, cy), int(DBL_OUT) + 3)

    # 各セグメントを描画
    for i, number in enumerate(SEGMENTS):
        start_a = OFFSET + i * SEG_ANG
        end_a   = start_a + SEG_ANG
        dark  = (i % 2 == 0)
        cols = COLORS_DARK if dark else COLORS_LIGHT

        # シングルアウター（TRI_OUT 〜 DBL_IN）
        _draw_sector(surf, cx, cy, TRI_OUT, DBL_IN,  start_a, end_a, cols["base"])
        # ダブルリング（DBL_IN 〜 DBL_OUT）
        _draw_sector(surf, cx, cy, DBL_IN,  DBL_OUT, start_a, end_a,
                     cols["red"] if i % 2 == 0 else cols["green"])
        # シングルインナー（SBULL_R 〜 TRI_IN）
        _draw_sector(surf, cx, cy, SBULL_R, TRI_IN,  start_a, end_a, cols["base"])
        # トリプルリング（TRI_IN 〜 TRI_OUT）
        _draw_sector(surf, cx, cy, TRI_IN,  TRI_OUT, start_a, end_a,
                     cols["red"] if i % 2 == 0 else cols["green"])

    # ブル
    pygame.draw.circle(surf, (20, 120, 50), (cx, cy), int(SBULL_R))
    pygame.draw.circle(surf, (200, 40, 40),  (cx, cy), int(DBULL_R))

    # セグメント番号
    font_s = pygame.font.SysFont("Arial", 18, bold=True)
    for i, number in enumerate(SEGMENTS):
        a  = OFFSET + i * SEG_ANG + HALF_SEG
        nr = DBL_OUT + 20
        tx = cx + nr * math.cos(a)
        ty = cy + nr * math.sin(a)
        txt = font_s.render(str(number), True, TEXT_COLOR)
        surf.blit(txt, txt.get_rect(center=(int(tx), int(ty))))

    # ワイヤー（境界線）
    pygame.draw.circle(surf, (80, 80, 80), (cx, cy), int(DBL_OUT), 2)
    pygame.draw.circle(surf, (80, 80, 80), (cx, cy), int(DBL_IN),  1)
    pygame.draw.circle(surf, (80, 80, 80), (cx, cy), int(TRI_OUT), 1)
    pygame.draw.circle(surf, (80, 80, 80), (cx, cy), int(TRI_IN),  1)
    pygame.draw.circle(surf, (80, 80, 80), (cx, cy), int(SBULL_R), 1)


def _draw_sector(surf: pygame.Surface,
                 cx: float, cy: float,
                 r_inner: float, r_outer: float,
                 a_start: float, a_end: float,
                 color: tuple) -> None:
    """扇形ドーナツ（ウェッジ）を描画する"""
    steps = max(4, int((a_end - a_start) * r_outer / 4))
    pts = []
    angles = [a_start + (a_end - a_start) * t / steps for t in range(steps + 1)]
    for a in angles:
        pts.append((cx + r_outer * math.cos(a), cy + r_outer * math.sin(a)))
    for a in reversed(angles):
        pts.append((cx + r_inner * math.cos(a), cy + r_inner * math.sin(a)))
    if len(pts) >= 3:
        pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def draw_dart(surf: pygame.Surface, x: int, y: int, color: tuple = DART_COLOR) -> None:
    """ダーツの刺さったマークを描画"""
    pygame.draw.circle(surf, (0, 0, 0), (x + 2, y + 2), 5)  # 影
    pygame.draw.circle(surf, color, (x, y), 5)
    pygame.draw.circle(surf, (255, 255, 255), (x, y), 2)


class Player:
    def __init__(self, name: str, is_cpu: bool = False) -> None:
        self.name    = name
        self.is_cpu  = is_cpu
        self.score   = STARTING_SCORE
        self.history: list[list[tuple[int, str, int, int]]] = []  # per-turn list of (pts, zone, x, y)
        self.current_turn: list[tuple[int, str, int, int]] = []

    def throw(self, tx: int, ty: int) -> tuple[int, str]:
        """座標 (tx, ty) に投げる。得点と結果を返す"""
        dx = tx - BOARD_CX
        dy = ty - BOARD_CY
        pts, zone = score_at(dx, dy)
        # バスト判定
        if self.score - pts < 0:
            pts, zone = 0, "Bust"
        elif self.score - pts == 1:
            pts, zone = 0, "Bust"  # 1 残りはダブルフィニッシュ不能→バスト
        self.score -= pts
        self.current_turn.append((pts, zone, tx, ty))
        return pts, zone

    def end_turn(self) -> None:
        self.history.append(list(self.current_turn))
        self.current_turn = []

    def won(self) -> bool:
        return self.score == 0


class Game:
    STATE_PLAYER   = "player"
    STATE_CPU      = "cpu"
    STATE_GAMEOVER = "gameover"

    def __init__(self) -> None:
        self.players = [Player("YOU"), Player("CPU", is_cpu=True)]
        self.turn_idx   = 0          # 0 = player, 1 = CPU
        self.dart_count = 0          # 現在のターンで投げた本数
        self.state      = self.STATE_PLAYER
        self.message    = ""
        self.winner     = None
        self.cpu_timer  = 0          # CPU の思考演出タイマー
        self.aim_x      = BOARD_CX
        self.aim_y      = BOARD_CY
        self.flash_pts: list[tuple[int, str, int, int, int]] = []  # (pts, zone, x, y, alpha)

    @property
    def current_player(self) -> Player:
        return self.players[self.turn_idx]

    def _apply_throw(self, tx: int, ty: int) -> None:
        pts, zone = self.current_player.throw(tx, ty)
        self.message = f"{zone}  {'+' if pts else ''}{pts if pts else 'BUST' if zone == 'Bust' else '0'}"
        self.flash_pts.append((pts, zone, tx, ty, 255))
        self.dart_count += 1

        if self.current_player.won():
            self.state  = self.STATE_GAMEOVER
            self.winner = self.current_player
            return

        if zone == "Bust":
            # バストなら残り本数スキップ
            self.current_player.end_turn()
            self._next_turn()
            return

        if self.dart_count >= DARTS_PER_TURN:
            self.current_player.end_turn()
            self._next_turn()

    def _next_turn(self) -> None:
        self.dart_count = 0
        self.turn_idx   = 1 - self.turn_idx
        self.state = self.STATE_CPU if self.current_player.is_cpu else self.STATE_PLAYER
        if self.state == self.STATE_CPU:
            self.cpu_timer = FPS // 2   # 0.5 秒後に投げる

    def player_throw(self, mx: int, my: int) -> None:
        if self.state != self.STATE_PLAYER:
            return
        # マウス位置に微小なブレを加える
        sx = random.gauss(0, 8)
        sy = random.gauss(0, 8)
        self._apply_throw(int(mx + sx), int(my + sy))

    def cpu_step(self) -> None:
        if self.state != self.STATE_CPU:
            return
        self.cpu_timer -= 1
        if self.cpu_timer > 0:
            return
        self.cpu_timer = int(FPS * 0.6)

        # CPU: スコアに応じて狙いを変える
        score = self.current_player.score
        if score <= 40 and score % 2 == 0:
            # ダブルフィニッシュを狙う
            target_seg = score // 2
            self._cpu_aim_segment(target_seg, ring="double")
        elif score == 50:
            self._cpu_aim_bull(double=True)
        elif score == 25:
            self._cpu_aim_bull(double=False)
        else:
            # トリプル 20 を基本に狙う
            self._cpu_aim_segment(20, ring="triple")

    def _cpu_aim_segment(self, number: int, ring: str = "single") -> None:
        try:
            seg_idx = SEGMENTS.index(number)
        except ValueError:
            seg_idx = 0
        a = OFFSET + seg_idx * SEG_ANG + HALF_SEG
        if ring == "triple":
            r = (TRI_IN + TRI_OUT) / 2
        elif ring == "double":
            r = (DBL_IN + DBL_OUT) / 2
        else:
            r = (SBULL_R + TRI_IN) / 2
        tx = BOARD_CX + r * math.cos(a)
        ty = BOARD_CY + r * math.sin(a)
        spread = 18 * (1 - CPU_SKILL)
        tx += random.gauss(0, spread)
        ty += random.gauss(0, spread)
        self._apply_throw(int(tx), int(ty))

    def _cpu_aim_bull(self, double: bool) -> None:
        r = DBULL_R / 2 if double else (DBULL_R + SBULL_R) / 2
        a = random.uniform(0, 2 * math.pi)
        spread = 10 * (1 - CPU_SKILL)
        tx = BOARD_CX + r * math.cos(a) + random.gauss(0, spread)
        ty = BOARD_CY + r * math.sin(a) + random.gauss(0, spread)
        self._apply_throw(int(tx), int(ty))

    def update(self) -> None:
        self.cpu_step()
        # フラッシュのアルファを減らす
        self.flash_pts = [(p, z, x, y, max(0, a - 3))
                          for p, z, x, y, a in self.flash_pts if a > 0]


def draw_score_panel(surf: pygame.Surface, game: Game, font: pygame.font.Font,
                     font_large: pygame.font.Font, font_small: pygame.font.Font) -> None:
    """左側スコアパネルを描画"""
    panel_rect = pygame.Rect(0, 0, 200, SCREEN_H)
    pygame.draw.rect(surf, PANEL_COLOR, panel_rect)
    pygame.draw.line(surf, (60, 60, 80), (200, 0), (200, SCREEN_H), 2)

    y = 20
    for i, p in enumerate(game.players):
        active = (i == game.turn_idx and game.state != game.STATE_GAMEOVER)
        color  = HIGHLIGHT if active else TEXT_COLOR

        # プレイヤー名
        name_surf = font.render(p.name, True, color)
        surf.blit(name_surf, (20, y))
        y += 34

        # スコア（大きく）
        score_surf = font_large.render(str(p.score), True, color)
        surf.blit(score_surf, (20, y))
        y += 58

        # 現在ターンのダーツ
        if active and p.current_turn:
            for pts, zone, *_ in p.current_turn:
                s = f"  {'+' if pts else ''}{pts}"
                c = GREEN if pts > 0 else RED
                surf.blit(font_small.render(s, True, c), (20, y))
                y += 20
        y += 12

        # 区切り線
        pygame.draw.line(surf, (60, 60, 80), (10, y), (190, y), 1)
        y += 12

    # ダーツ残数
    if game.state in (game.STATE_PLAYER, game.STATE_CPU):
        remaining = DARTS_PER_TURN - game.dart_count
        txt = f"Darts: {'●' * remaining}{'○' * (DARTS_PER_TURN - remaining)}"
        surf.blit(font_small.render(txt, True, TEXT_COLOR), (20, y + 10))
        y += 36

    # メッセージ
    if game.message:
        msg_surf = font.render(game.message, True, HIGHLIGHT)
        surf.blit(msg_surf, (10, SCREEN_H - 60))


def draw_aim_crosshair(surf: pygame.Surface, mx: int, my: int) -> None:
    """照準クロスヘアを描画"""
    r = 18
    pygame.draw.circle(surf, (255, 255, 100, 160), (mx, my), r, 2)
    pygame.draw.line(surf,   (255, 255, 100), (mx - r - 4, my), (mx + r + 4, my), 1)
    pygame.draw.line(surf,   (255, 255, 100), (mx, my - r - 4), (mx, my + r + 4), 1)


def draw_gameover(surf: pygame.Surface, winner: Player,
                  font_large: pygame.font.Font, font: pygame.font.Font) -> None:
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surf.blit(overlay, (0, 0))

    msg1 = font_large.render(f"{winner.name} WINS!", True, HIGHLIGHT)
    msg2 = font.render("Press R to restart  /  Q to quit", True, TEXT_COLOR)
    surf.blit(msg1, msg1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))
    surf.blit(msg2, msg2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Darts — 501")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("Arial", 52, bold=True)
    font       = pygame.font.SysFont("Arial", 22, bold=True)
    font_small = pygame.font.SysFont("Arial", 16)

    # ボードをキャッシュ描画
    board_surf   = pygame.Surface((SCREEN_W, SCREEN_H))
    alpha_overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    board_surf.fill(BG_COLOR)
    draw_board(board_surf, alpha_overlay)

    game = Game()
    pygame.mouse.set_visible(False)

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    game = Game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.state == game.STATE_PLAYER:
                    game.player_throw(mx, my)

        game.update()

        # 描画
        screen.blit(board_surf, (0, 0))

        # 刺さったダーツを描画
        for p in game.players:
            color = (100, 200, 255) if not p.is_cpu else (255, 120, 80)
            for turn in p.history[-2:]:
                for _, _, x, y in turn:
                    draw_dart(screen, x, y, color)
            for _, _, x, y in p.current_turn:
                draw_dart(screen, x, y, color)

        # フラッシュメッセージ
        for pts, zone, x, y, a in game.flash_pts:
            alpha_s = pygame.Surface((200, 28), pygame.SRCALPHA)
            alpha_s.fill((0, 0, 0, 0))
            c = (*GREEN, a) if pts > 0 else (*RED, a)
            t_surf = font.render(f"+{pts}  {zone}" if pts else "BUST", True, c[:3])
            screen.blit(t_surf, (x + 10, y - 20))

        # UI パネル
        draw_score_panel(screen, game, font, font_large, font_small)

        if game.state == game.STATE_PLAYER:
            draw_aim_crosshair(screen, mx, my)
        elif game.state == game.STATE_CPU:
            # CPU 思考中インジケータ
            dots = "." * ((pygame.time.get_ticks() // 400) % 4)
            t = font.render(f"CPU thinking{dots}", True, (180, 180, 255))
            screen.blit(t, (220, 20))

        if game.state == game.STATE_GAMEOVER:
            draw_gameover(screen, game.winner, font_large, font)

        pygame.display.flip()


if __name__ == "__main__":
    main()
