import pygame
import sys
import random
import time
from dataclasses import dataclass

# --- 定数 ---
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS = 60

BG_COLOR      = (18, 18, 18)
HINT_COLOR    = (80, 80, 80)
PROMPT_COLOR  = (100, 100, 100)
CORRECT_COLOR = (80, 200, 120)
WRONG_COLOR   = (220, 80, 80)
CURSOR_COLOR  = (100, 200, 255)
COMPOSE_COLOR = (255, 200, 80)    # IME 変換中テキストの色
RESULT_COLOR  = (255, 210, 80)

FONT_SIZE = 36
HINT_SIZE = 18

WORD_LIST = [
    # 英語
    "the quick brown fox",
    "practice makes perfect",
    "hello world",
    "keep calm and code on",
    # 日本語
    "すもももももも",
    "たけやぶやけた",
    "にわにはにわにわとりがいる",
    "春はあけぼの",
    "吾輩は猫である",
    "プログラミングは楽しい",
]


# --- ゲーム状態 ---
@dataclass
class GameState:
    prompt: str
    typed: str = ""
    start_time: float | None = None
    end_time: float | None = None
    finished: bool = False

    def record_first_key(self) -> None:
        if self.start_time is None:
            self.start_time = time.time()

    def elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def cpm(self) -> float:
        """1 分あたりの文字数（日英どちらにも適用できる指標）。"""
        secs = self.elapsed()
        if secs == 0:
            return 0.0
        return len(self.prompt) / (secs / 60)

    def accuracy(self) -> float:
        if not self.typed:
            return 0.0
        correct = sum(a == b for a, b in zip(self.typed, self.prompt))
        return correct / len(self.prompt) * 100


def new_game() -> "GameState":
    return GameState(prompt=random.choice(WORD_LIST))


# --- 描画ヘルパー ---
def draw_prompt(screen: pygame.Surface, font: pygame.font.Font, state: GameState) -> None:
    """お題文字列を 1 文字ずつ色付けして中央に描画する。"""
    total_w = sum(font.size(ch)[0] for ch in state.prompt)
    x = WINDOW_WIDTH // 2 - total_w // 2
    y = WINDOW_HEIGHT // 2 - 70

    for i, ch in enumerate(state.prompt):
        if i < len(state.typed):
            color = CORRECT_COLOR if state.typed[i] == ch else WRONG_COLOR
        else:
            color = PROMPT_COLOR
        surf = font.render(ch, True, color)
        screen.blit(surf, (x, y))
        x += surf.get_width()


def draw_input(
    screen: pygame.Surface,
    font: pygame.font.Font,
    state: GameState,
    composing: str,
) -> None:
    """確定済みテキスト + IME 変換中テキスト + カーソルを描画する。"""
    y = WINDOW_HEIGHT // 2

    confirmed_surf = font.render(state.typed, True, (220, 220, 220))
    compose_surf   = font.render(composing,   True, COMPOSE_COLOR)
    cursor_surf    = font.render("_",         True, CURSOR_COLOR)

    total_w = confirmed_surf.get_width() + compose_surf.get_width() + cursor_surf.get_width()
    x = WINDOW_WIDTH // 2 - total_w // 2

    screen.blit(confirmed_surf, (x, y))
    x += confirmed_surf.get_width()

    # 変換中テキストの下線
    if composing:
        screen.blit(compose_surf, (x, y))
        underline_y = y + compose_surf.get_height() - 2
        pygame.draw.line(screen, COMPOSE_COLOR, (x, underline_y),
                         (x + compose_surf.get_width(), underline_y), 2)
        x += compose_surf.get_width()

    screen.blit(cursor_surf, (x, y))


def draw_stats(screen: pygame.Surface, hint_font: pygame.font.Font, state: GameState) -> None:
    """経過時間を右上に表示する。"""
    surf = hint_font.render(f"{state.elapsed():.1f}s", True, HINT_COLOR)
    screen.blit(surf, (WINDOW_WIDTH - surf.get_width() - 20, 20))


def draw_result(screen: pygame.Surface, font: pygame.font.Font,
                hint_font: pygame.font.Font, state: GameState) -> None:
    """完了リザルト画面を描画する。"""
    lines = [
        "Finished!",
        f"Time    : {state.elapsed():.2f} s",
        f"CPM     : {state.cpm():.1f}",
        f"Accuracy: {state.accuracy():.1f}%",
        "",
        "Enter: retry  /  Esc: quit",
    ]
    y = WINDOW_HEIGHT // 2 - len(lines) * 22

    for line in lines:
        color = RESULT_COLOR if line and not line.startswith("Enter") else HINT_COLOR
        surf = font.render(line, True, color) if line else pygame.Surface((0, 0))
        screen.blit(surf, (WINDOW_WIDTH // 2 - surf.get_width() // 2, y))
        y += 44


# --- メインループ ---
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Day 21 - Typing Game")
    clock = pygame.time.Clock()

    # 日英両対応フォント（hiraginosansgb は macOS 標準）
    font      = pygame.font.SysFont("hiraginosansgb", FONT_SIZE)
    hint_font = pygame.font.SysFont("hiraginosansgb", HINT_SIZE)

    # IME イベント（TEXTINPUT / TEXTEDITING）を有効化
    pygame.key.start_text_input()

    state     = new_game()
    composing = ""          # IME 変換中の未確定テキスト

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- 特殊キー（KEYDOWN で処理） ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if state.finished:
                    if event.key == pygame.K_RETURN:
                        state     = new_game()
                        composing = ""
                    continue

                # IME 変換中は Backspace を OS 側に任せる
                if event.key == pygame.K_BACKSPACE and not composing:
                    state = GameState(
                        prompt=state.prompt,
                        typed=state.typed[:-1],
                        start_time=state.start_time,
                    )

            # --- IME 変換中テキスト ---
            elif event.type == pygame.TEXTEDITING:
                composing = event.text

            # --- 確定テキスト（日英どちらもここに来る） ---
            elif event.type == pygame.TEXTINPUT:
                composing = ""
                state.record_first_key()
                new_typed = state.typed + event.text

                if len(new_typed) <= len(state.prompt):
                    finished = new_typed == state.prompt
                    state = GameState(
                        prompt=state.prompt,
                        typed=new_typed,
                        start_time=state.start_time,
                        end_time=time.time() if finished else None,
                        finished=finished,
                    )

        # --- 描画 ---
        screen.fill(BG_COLOR)

        if state.finished:
            draw_result(screen, font, hint_font, state)
        else:
            draw_prompt(screen, font, state)
            draw_input(screen, font, state, composing)
            draw_stats(screen, hint_font, state)

            hint = hint_font.render("Backspace: delete  Esc: quit", True, HINT_COLOR)
            screen.blit(hint, (20, WINDOW_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
