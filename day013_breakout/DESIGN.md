# Day013 ブロック崩し — 基本設計

## 概要

Python + pygame 製のブロック崩し（Breakout）。
day012（オセロ）と同じ単一ファイル構成。

## 技術スタック

- Python 3.11+
- pygame 2.x
- 外部依存なし（pygame のみ）

## ファイル構成

```
day013_breakout/
├── breakout.py       # ゲーム本体（単一ファイル）
├── requirements.txt
└── README.md
```

## ウィンドウ仕様

| 項目 | 値 |
|------|----|
| 解像度 | 800 × 620 px |
| FPS | 60 |
| フォント | pygame デフォルト（pygame.font.SysFont） |

## ゲームフロー

```
MENU → PLAYING → (PAUSED) → GAME_OVER / CLEAR
                   ↑___↓ (P キー)
CLEAR / GAME_OVER → MENU (R キー)
```

## 定数（Constants）

```python
WIN_W, WIN_H = 800, 620
INFO_H = 60          # 上部スコアバー高さ
FPS = 60

# パドル
PADDLE_W, PADDLE_H = 100, 12
PADDLE_Y = WIN_H - 50
PADDLE_SPEED = 7

# ボール
BALL_R = 8
BALL_SPEED_INIT = 5.0
BALL_SPEED_MAX  = 12.0
BALL_SPEED_INC  = 0.3   # ブロック破壊ごとに加速

# ブロックグリッド
BLOCK_COLS  = 10
BLOCK_ROWS  = 6
BLOCK_W     = 70
BLOCK_H     = 22
BLOCK_PAD   = 4
BLOCK_TOP   = 80        # グリッド開始 Y（INFO_H 以降）

# ライフ
LIVES_INIT = 3
```

## カラーパレット

```python
C_BG       = (15, 15, 30)
C_INFO_BG  = (25, 25, 50)
C_PADDLE   = (100, 200, 255)
C_BALL     = (255, 240, 120)
C_TEXT     = (220, 220, 220)
C_SHADOW   = (0, 0, 0, 120)

# ブロック行ごとの色（HP 兼用）
BLOCK_COLORS = {
    1: (100, 220, 120),   # 緑  1hit
    2: (80, 160, 255),    # 青  2hit
    3: (255, 180, 60),    # 橙  3hit（ヒットで色変化）
}
```

## データ構造

### Block（dataclass frozen）

```python
@dataclass(frozen=True)
class Block:
    rect: pygame.Rect   # 位置・サイズ
    hp: int             # 残 HP（1〜3）
    score: int          # 破壊時スコア（hp × 10）
```

Block は immutable。ヒット時は新しい Block(hp=old.hp-1) に置き換え。

### Ball（dataclass）

```python
@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: int = BALL_R
```

メソッド:
- `update(dt_ms) -> list[str]`  壁・天井バウンス、落下検出 → イベント文字列を返す
- `draw(surface)`

### Paddle（dataclass）

```python
@dataclass
class Paddle:
    x: float
    y: float = PADDLE_Y
    width: int = PADDLE_W
```

メソッド:
- `update(keys)` — 左右キー / マウス X で移動（画面端クランプ）
- `draw(surface)`

### GameScene

```python
@dataclass
class GameScene:
    blocks: list[Block]
    ball: Ball
    paddle: Paddle
    score: int = 0
    lives: int = LIVES_INIT
    level: int = 1
```

メソッド:
- `update(keys, dt_ms) -> GameState`
- `draw(surface)`
- `reset()`

## 衝突検出

### ボール ↔ パドル

```
if ball.rect.colliderect(paddle.rect):
    vy = -abs(vy)   # 常に上向きに反射
    # パドル中心からの距離で vx を調整（角度コントロール）
    offset = (ball.x - paddle.cx) / (paddle.width / 2)  # -1.0 〜 1.0
    vx = offset * BALL_SPEED * 1.2
    # 速度大きさを正規化して speed を維持
```

### ボール ↔ ブロック

各ブロックの上下左右どの辺から衝突したかを判定し vy / vx を反転。
同フレームに複数ブロック衝突した場合は全て処理（重複反転防止フラグ `bounced_x`, `bounced_y`）。

## スコア設計

| イベント | 点数 |
|---------|-----|
| HP1 ブロック破壊 | 10 |
| HP2 ブロック破壊 | 20 |
| HP3 ブロック破壊 | 30 |
| 全ブロック破壊（クリア） | +500 |

## レベル設計

レベル定義は `build_blocks(level: int) -> list[Block]` で生成。

```
level 1: 上 2 行 HP1、中 2 行 HP2、下 2 行 HP3
level 2: ランダムに HP2/HP3 が増える
level 3+: ギャップ（空きセル）を含む配置
```

## 入力

| キー / 操作 | 効果 |
|------------|------|
| ← / → | パドル移動 |
| マウス移動 | パドル移動（オプション） |
| SPACE | ボール発射（PLAYING 開始前） |
| P | PLAYING ↔ PAUSED |
| R | GAME_OVER / CLEAR → MENU |
| ESC | 終了 |

## メインループ構造

```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()
    state = GameState.MENU
    scene = GameScene.new(level=1)

    while True:
        dt = clock.tick(FPS)
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for e in events:
            if e.type == pygame.QUIT: sys.exit()
            state = handle_event(e, state, scene)

        if state == GameState.PLAYING:
            state = scene.update(keys, dt)

        screen.fill(C_BG)
        scene.draw(screen)
        draw_hud(screen, scene, state)
        if state != GameState.PLAYING:
            draw_overlay(screen, state)
        pygame.display.flip()
```

## 実装上の注意

1. Ball・Block は immutable dataclass → ヒット時に新インスタンスを作成
2. `list[Block]` は内包表記でフィルタ（hp==0 を除外）
3. 壁・天井は `WIN_W`, `INFO_H` を境界に使う
4. パドルは左端 `0`・右端 `WIN_W - PADDLE_W` でクランプ
5. ボールが `WIN_H` を超えたら lives -= 1、リセット
6. lives == 0 で GAME_OVER
7. blocks が空になったら次レベル or CLEAR（level >= 3）

## requirements.txt

```
pygame>=2.0
```
