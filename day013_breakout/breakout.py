import math
import os
import random
import sys
from dataclasses import dataclass
from enum import Enum, auto

import pygame

# --- Constants ---
WIN_W, WIN_H = 800, 620
INFO_H = 60
FPS = 60

PADDLE_W, PADDLE_H = 100, 12
PADDLE_Y = WIN_H - 50
PADDLE_SPEED = 7

BALL_R = 8
BALL_SPEED_INIT = 5.0
BALL_SPEED_MAX = 12.0
BALL_SPEED_INC = 0.3

BLOCK_COLS = 10
BLOCK_ROWS = 6
BLOCK_W = 70
BLOCK_H = 22
BLOCK_PAD = 4
BLOCK_TOP = 80

LIVES_INIT = 3
MAX_LEVEL = 3

C_BG = (15, 15, 30)
C_INFO_BG = (25, 25, 50)
C_PADDLE = (100, 200, 255)
C_BALL = (255, 240, 120)
C_TEXT = (220, 220, 220)
C_SHADOW = (0, 0, 0, 120)
C_OVERLAY = (0, 0, 0, 150)

BLOCK_COLORS = {
    1: (100, 220, 120),
    2: (80, 160, 255),
    3: (255, 180, 60),
}


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    CLEAR = auto()


@dataclass(frozen=True)
class Block:
    rect: pygame.Rect
    hp: int
    score: int


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: int = BALL_R

    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, dt_ms):
        scale = dt_ms / (1000 / FPS) if dt_ms > 0 else 1.0
        self.x += self.vx * scale
        self.y += self.vy * scale

        events = []
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = abs(self.vx)
            events.append("wall")
        elif self.x + self.radius >= WIN_W:
            self.x = WIN_W - self.radius
            self.vx = -abs(self.vx)
            events.append("wall")

        if self.y - self.radius <= INFO_H:
            self.y = INFO_H + self.radius
            self.vy = abs(self.vy)
            events.append("ceiling")

        if self.y - self.radius > WIN_H:
            events.append("miss")

        return events

    def draw(self, surface):
        pygame.draw.circle(surface, (80, 70, 20), (int(self.x) + 2, int(self.y) + 2), self.radius)
        pygame.draw.circle(surface, C_BALL, (int(self.x), int(self.y)), self.radius)


@dataclass
class Paddle:
    x: float
    y: float = PADDLE_Y
    width: int = PADDLE_W

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, PADDLE_H)

    @property
    def center_x(self):
        return self.x + self.width / 2

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT]:
            self.x += PADDLE_SPEED

        mx, _ = pygame.mouse.get_pos()
        if pygame.mouse.get_focused():
            target_x = mx - self.width / 2
            self.x += (target_x - self.x) * 0.25

        self.x = max(0, min(WIN_W - self.width, self.x))

    def draw(self, surface):
        shadow_rect = self.rect.move(0, 3)
        pygame.draw.rect(surface, (30, 60, 80), shadow_rect, border_radius=8)
        pygame.draw.rect(surface, C_PADDLE, self.rect, border_radius=8)


def clamp(value, low, high):
    return max(low, min(high, value))


def normalize_velocity(vx, vy, speed):
    mag = math.hypot(vx, vy)
    if mag == 0:
        return 0.0, -speed
    scale = speed / mag
    return vx * scale, vy * scale


def build_blocks(level):
    rng = random.Random(level * 137)
    total_w = BLOCK_COLS * BLOCK_W + (BLOCK_COLS - 1) * BLOCK_PAD
    start_x = (WIN_W - total_w) // 2
    blocks = []

    for row in range(BLOCK_ROWS):
        for col in range(BLOCK_COLS):
            if level >= 3:
                if (row in (1, 4) and col in (2, 7)) or (row == 2 and col in (0, 9)):
                    continue

            if row < 2:
                hp = 1
            elif row < 4:
                hp = 2
            else:
                hp = 3

            if level == 2:
                roll = rng.random()
                if roll > 0.75:
                    hp = 3
                elif roll > 0.35:
                    hp = max(hp, 2)
            elif level >= 3:
                hp = min(3, hp + (1 if (row + col) % 3 == 0 else 0))

            x = start_x + col * (BLOCK_W + BLOCK_PAD)
            y = BLOCK_TOP + row * (BLOCK_H + BLOCK_PAD)
            rect = pygame.Rect(x, y, BLOCK_W, BLOCK_H)
            blocks.append(Block(rect=rect, hp=hp, score=hp * 10))

    return blocks


@dataclass
class GameScene:
    blocks: list[Block]
    ball: Ball
    paddle: Paddle
    score: int = 0
    lives: int = LIVES_INIT
    level: int = 1
    launched: bool = False
    clear_bonus_awarded: bool = False

    @classmethod
    def new(cls, level=1):
        paddle = Paddle(x=(WIN_W - PADDLE_W) / 2)
        ball = Ball(x=paddle.center_x, y=paddle.y - BALL_R - 2, vx=0.0, vy=-BALL_SPEED_INIT)
        return cls(blocks=build_blocks(level), ball=ball, paddle=paddle, level=level)

    def reset_ball(self):
        self.ball.x = self.paddle.center_x
        self.ball.y = self.paddle.y - self.ball.radius - 2
        self.ball.vx = 0.0
        self.ball.vy = -BALL_SPEED_INIT
        self.launched = False

    def reset(self):
        self.blocks = build_blocks(1)
        self.paddle = Paddle(x=(WIN_W - PADDLE_W) / 2)
        self.ball = Ball(x=self.paddle.center_x, y=self.paddle.y - BALL_R - 2, vx=0.0, vy=-BALL_SPEED_INIT)
        self.score = 0
        self.lives = LIVES_INIT
        self.level = 1
        self.launched = False
        self.clear_bonus_awarded = False

    def launch_ball(self):
        if not self.launched:
            self.launched = True
            self.ball.vx = random.choice((-1, 1)) * (BALL_SPEED_INIT * 0.45)
            self.ball.vy = -math.sqrt(max(BALL_SPEED_INIT ** 2 - self.ball.vx ** 2, 1.0))

    def current_ball_speed(self):
        speed = math.hypot(self.ball.vx, self.ball.vy)
        if speed <= 0:
            return BALL_SPEED_INIT
        return min(speed, BALL_SPEED_MAX)

    def handle_paddle_collision(self):
        if self.ball.vy <= 0:
            return
        if not self.ball.rect().colliderect(self.paddle.rect):
            return

        self.ball.y = self.paddle.y - self.ball.radius - 1
        speed = self.current_ball_speed()
        offset = (self.ball.x - self.paddle.center_x) / (self.paddle.width / 2)
        offset = clamp(offset, -1.0, 1.0)
        new_vx = offset * speed * 1.2
        new_vy = -abs(speed)
        self.ball.vx, self.ball.vy = normalize_velocity(new_vx, new_vy, speed)

    def handle_block_collisions(self):
        ball_rect = self.ball.rect()
        hit_indices = [i for i, block in enumerate(self.blocks) if ball_rect.colliderect(block.rect)]
        if not hit_indices:
            return

        prev_x = self.ball.x - self.ball.vx
        prev_y = self.ball.y - self.ball.vy
        prev_rect = pygame.Rect(
            int(prev_x - self.ball.radius),
            int(prev_y - self.ball.radius),
            self.ball.radius * 2,
            self.ball.radius * 2,
        )

        bounced_x = False
        bounced_y = False
        new_blocks = self.blocks[:]
        removed = 0

        for idx in hit_indices:
            block = self.blocks[idx]
            curr_idx = idx - removed
            prev_overlap_x = prev_rect.right > block.rect.left and prev_rect.left < block.rect.right
            prev_overlap_y = prev_rect.bottom > block.rect.top and prev_rect.top < block.rect.bottom

            hit_left = prev_rect.right <= block.rect.left and prev_overlap_y
            hit_right = prev_rect.left >= block.rect.right and prev_overlap_y
            hit_top = prev_rect.bottom <= block.rect.top and prev_overlap_x
            hit_bottom = prev_rect.top >= block.rect.bottom and prev_overlap_x

            if (hit_left or hit_right) and not bounced_x:
                self.ball.vx *= -1
                bounced_x = True
            if (hit_top or hit_bottom) and not bounced_y:
                self.ball.vy *= -1
                bounced_y = True

            if not (hit_left or hit_right or hit_top or hit_bottom):
                if not bounced_y:
                    self.ball.vy *= -1
                    bounced_y = True
                elif not bounced_x:
                    self.ball.vx *= -1
                    bounced_x = True

            if block.hp <= 1:
                self.score += block.score
                new_blocks.pop(curr_idx)
                removed += 1
            else:
                new_blocks[curr_idx] = Block(rect=block.rect, hp=block.hp - 1, score=block.score)

            speed = min(BALL_SPEED_MAX, self.current_ball_speed() + BALL_SPEED_INC)
            self.ball.vx, self.ball.vy = normalize_velocity(self.ball.vx, self.ball.vy, speed)

        self.blocks = new_blocks

    def update(self, keys, dt_ms):
        self.paddle.update(keys)

        if not self.launched:
            self.ball.x = self.paddle.center_x
            self.ball.y = self.paddle.y - self.ball.radius - 2
            return GameState.PLAYING

        events = self.ball.update(dt_ms)
        self.handle_paddle_collision()
        self.handle_block_collisions()

        if "miss" in events:
            self.lives -= 1
            if self.lives <= 0:
                return GameState.GAME_OVER
            self.reset_ball()
            return GameState.PLAYING

        if not self.blocks:
            if not self.clear_bonus_awarded:
                self.score += 500
                self.clear_bonus_awarded = True
            if self.level >= MAX_LEVEL:
                return GameState.CLEAR
            self.level += 1
            self.blocks = build_blocks(self.level)
            self.clear_bonus_awarded = False
            self.reset_ball()

        return GameState.PLAYING

    def draw(self, surface, font_small):
        self.paddle.draw(surface)
        self.ball.draw(surface)

        for block in self.blocks:
            color = BLOCK_COLORS[block.hp]
            shadow = block.rect.move(2, 2)
            pygame.draw.rect(surface, (20, 20, 20), shadow, border_radius=5)
            pygame.draw.rect(surface, color, block.rect, border_radius=5)
            pygame.draw.rect(surface, (245, 245, 245), block.rect, 1, border_radius=5)
            hp_text = font_small.render(str(block.hp), True, C_BG)
            surface.blit(
                hp_text,
                (
                    block.rect.centerx - hp_text.get_width() // 2,
                    block.rect.centery - hp_text.get_height() // 2,
                ),
            )


def draw_hud(surface, scene, state, font, font_small):
    pygame.draw.rect(surface, C_INFO_BG, (0, 0, WIN_W, INFO_H))

    texts = [
        font.render(f"SCORE {scene.score}", True, C_TEXT),
        font_small.render(f"LIVES {scene.lives}", True, C_TEXT),
        font_small.render(f"LEVEL {scene.level}", True, C_TEXT),
        font_small.render(f"STATE {state.name}", True, C_TEXT),
    ]

    surface.blit(texts[0], (20, 16))
    surface.blit(texts[1], (WIN_W - 220, 14))
    surface.blit(texts[2], (WIN_W - 220, 34))
    surface.blit(texts[3], (WIN_W // 2 - texts[3].get_width() // 2, 20))


def draw_overlay(surface, state, font, font_small):
    if state == GameState.PLAYING:
        return

    overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    overlay.fill(C_OVERLAY)
    surface.blit(overlay, (0, 0))

    if state == GameState.MENU:
        title = "Breakout"
        lines = [
            "SPACE で開始",
            "P で一時停止 / 再開",
            "R でリセット",
            "ESC で終了",
        ]
    elif state == GameState.PAUSED:
        title = "Paused"
        lines = ["P で再開", "R でメニューに戻る"]
    elif state == GameState.GAME_OVER:
        title = "Game Over"
        lines = ["R でメニューに戻る", "ESC で終了"]
    else:
        title = "Clear!"
        lines = ["全レベルクリア", "R でメニューに戻る"]

    title_surf = font.render(title, True, C_TEXT)
    surface.blit(title_surf, (WIN_W // 2 - title_surf.get_width() // 2, WIN_H // 2 - 80))

    for idx, line in enumerate(lines):
        text = font_small.render(line, True, C_TEXT)
        surface.blit(text, (WIN_W // 2 - text.get_width() // 2, WIN_H // 2 - 20 + idx * 28))


def handle_event(event, state, scene):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if event.key == pygame.K_r:
            scene.reset()
            return GameState.MENU

        if event.key == pygame.K_p:
            if state == GameState.PLAYING:
                return GameState.PAUSED
            if state == GameState.PAUSED:
                return GameState.PLAYING

        if event.key == pygame.K_SPACE:
            if state == GameState.MENU:
                scene.reset()
                scene.launch_ball()
                return GameState.PLAYING
            if state == GameState.PLAYING and not scene.launched:
                scene.launch_ball()
                return GameState.PLAYING

    return state


_JP_FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
]


def _make_font(size: int, bold: bool = False) -> pygame.font.Font:
    for path in _JP_FONT_CANDIDATES:
        if os.path.exists(path):
            return pygame.font.Font(path, size)
    return pygame.font.SysFont("notosanscjk,applegothic,arial", size, bold=bold)


def run_check():
    scene = GameScene.new(level=1)
    assert len(build_blocks(1)) > 0
    assert len(build_blocks(2)) > 0
    assert len(build_blocks(3)) > 0
    assert isinstance(scene.blocks[0], Block)
    print("check OK")


def main():
    if "--check" in sys.argv:
        run_check()
        return

    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Breakout - Day 013")
    clock = pygame.time.Clock()

    font = _make_font(28, bold=True)
    font_small = _make_font(18)

    state = GameState.MENU
    scene = GameScene.new(level=1)

    while True:
        dt_ms = clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            state = handle_event(event, state, scene)

        if state == GameState.PLAYING:
            state = scene.update(keys, dt_ms)
        elif state in (GameState.MENU, GameState.PAUSED, GameState.GAME_OVER, GameState.CLEAR):
            scene.paddle.update(keys)
            if not scene.launched:
                scene.ball.x = scene.paddle.center_x
                scene.ball.y = scene.paddle.y - scene.ball.radius - 2

        screen.fill(C_BG)
        scene.draw(screen, font_small)
        draw_hud(screen, scene, state, font, font_small)
        draw_overlay(screen, state, font, font_small)
        pygame.display.flip()


if __name__ == "__main__":
    main()
