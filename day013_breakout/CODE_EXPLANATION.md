# breakout.py コード解説

初心者向けに一行ずつ解説したドキュメントです。

---

## ブロック 1：ライブラリの読み込み（1〜8行目）

```python
import math       # sqrt（平方根）や hypot（2点間の距離）などの数学関数
import os         # ファイルパスの存在確認（フォント探索に使用）
import random     # ボール発射角度のランダム化
import sys        # プログラム終了の sys.exit() に必要
from dataclasses import dataclass  # データを持つクラスを簡単に作るデコレータ
from enum import Enum, auto        # ゲーム状態を名前で管理する列挙型

import pygame     # ゲーム画面の描画・キーボード・マウス入力を扱うライブラリ
```

`dataclass` を使うと `__init__` を自動生成してくれるので、座標や速度を持つゲームオブジェクトの定義がシンプルになります。

---

## ブロック 2：定数の定義（10〜46行目）

```python
WIN_W, WIN_H = 800, 620   # ウィンドウの幅・高さ（ピクセル）
INFO_H = 60               # 上部 HUD（スコア表示バー）の高さ
FPS = 60                  # 1秒間に画面を60回描き直す
```

```python
PADDLE_W, PADDLE_H = 100, 12   # パドルの幅・高さ
PADDLE_Y = WIN_H - 50          # パドルの Y 座標（下から50px）
PADDLE_SPEED = 7               # 1フレームで動くピクセル数
```

```python
BALL_R = 8              # ボールの半径（px）
BALL_SPEED_INIT = 5.0   # 初期速度（px/フレーム）
BALL_SPEED_MAX  = 12.0  # 上限速度
BALL_SPEED_INC  = 0.3   # ブロックを壊すたびに増加する速度
```

```python
BLOCK_COLS = 10    # ブロックの列数
BLOCK_ROWS = 6     # ブロックの行数
BLOCK_W = 70       # 1ブロックの幅
BLOCK_H = 22       # 1ブロックの高さ
BLOCK_PAD = 4      # ブロック間の隙間
BLOCK_TOP = 80     # ブロックグリッドの開始 Y 座標
```

```python
# 色は (赤, 緑, 青) の 0〜255 で表す（RGB）
C_BG      = (15, 15, 30)      # 背景：深い紺色
C_INFO_BG = (25, 25, 50)      # HUD 背景：やや明るい紺色
C_PADDLE  = (100, 200, 255)   # パドル：水色
C_BALL    = (255, 240, 120)   # ボール：黄色
C_TEXT    = (220, 220, 220)   # テキスト：明るいグレー
```

```python
BLOCK_COLORS = {
    1: (100, 220, 120),   # HP1 → 緑（1発で壊れる）
    2: (80,  160, 255),   # HP2 → 青（2発で壊れる）
    3: (255, 180,  60),   # HP3 → 橙（3発で壊れる）
}
```

HP が高いほどブロックの色が変わるので、プレイヤーが「あと何回当てれば壊れるか」を一目でわかります。

---

## ブロック 3：ゲーム状態の定義（49〜54行目）

```python
class GameState(Enum):
    MENU      = auto()   # タイトル画面
    PLAYING   = auto()   # プレイ中
    PAUSED    = auto()   # 一時停止中
    GAME_OVER = auto()   # ゲームオーバー
    CLEAR     = auto()   # 全レベルクリア
```

`Enum`（列挙型）を使うと、状態を数字ではなく名前で管理できます。`auto()` は自動で連番の値を割り当てます。

遷移図：
```
MENU ──SPACE──▶ PLAYING ──P──▶ PAUSED
                   │               │
                 ミス3回          P
                   │               │
                   ▼               ▼
               GAME_OVER      PLAYING
                   │
               全ブロック破壊
                   │
                 CLEAR（level 3 完了時）
```

---

## ブロック 4：Block クラス（57〜61行目）

```python
@dataclass(frozen=True)   # frozen=True → 作成後に変更できない（immutable）
class Block:
    rect: pygame.Rect   # 位置とサイズ（pygame の矩形オブジェクト）
    hp: int             # 残り耐久値（1〜3）
    score: int          # 破壊したときに加算する点数
```

`frozen=True` にすることで、ボールが当たって HP を減らすときは**元のオブジェクトを変えず、新しい Block を作る**設計になっています。

```python
# HP を1減らしたブロックに置き換える（実際の処理）
new_blocks[idx] = Block(rect=block.rect, hp=block.hp - 1, score=block.score)
```

これにより「途中の状態を誤って変えてしまう」バグが起きにくくなります。

---

## ブロック 5：Ball クラス（64〜107行目）

```python
@dataclass
class Ball:
    x: float    # 中心 X 座標
    y: float    # 中心 Y 座標
    vx: float   # X 方向の速度（正 = 右、負 = 左）
    vy: float   # Y 方向の速度（正 = 下、負 = 上）
    radius: int = BALL_R   # 半径（デフォルトは定数 BALL_R）
```

### rect() メソッド

```python
def rect(self):
    return pygame.Rect(
        int(self.x - self.radius),   # 左端の X
        int(self.y - self.radius),   # 上端の Y
        self.radius * 2,             # 幅（直径）
        self.radius * 2,             # 高さ（直径）
    )
```

衝突判定に使う矩形を返します。ボールは円ですが、pygame の衝突判定は矩形ベースなので、円の周囲を囲む正方形（バウンディングボックス）に変換しています。

### update() メソッド

```python
def update(self, dt_ms):
    scale = dt_ms / (1000 / FPS) if dt_ms > 0 else 1.0
    # dt_ms = 前フレームからの経過ミリ秒
    # FPS=60 なら 1フレーム≒16.7ms → scale≒1.0
    # 処理落ちで1フレームが長くなっても、移動量を補正できる
    self.x += self.vx * scale
    self.y += self.vy * scale
```

```python
    if self.x - self.radius <= 0:       # 左壁に当たった
        self.x = self.radius            # めり込まないよう補正
        self.vx = abs(self.vx)          # 右方向に反転（必ず正）
    elif self.x + self.radius >= WIN_W: # 右壁に当たった
        self.x = WIN_W - self.radius
        self.vx = -abs(self.vx)         # 左方向に反転（必ず負）

    if self.y - self.radius <= INFO_H:  # 天井（HUD の下端）に当たった
        self.y = INFO_H + self.radius
        self.vy = abs(self.vy)          # 下方向に反転

    if self.y - self.radius > WIN_H:    # 画面下端を超えた → ミス
        events.append("miss")
```

`abs()` を使って「必ず正（または負）の向きにする」ことで、壁にめり込んだときに逆向きで反射し続けるバグを防いでいます。

### draw() メソッド

```python
def draw(self, surface):
    # 右下にずらした暗い円を先に描く → 影に見える
    pygame.draw.circle(surface, (80, 70, 20), (int(self.x) + 2, int(self.y) + 2), self.radius)
    # 本体の黄色い円を描く
    pygame.draw.circle(surface, C_BALL, (int(self.x), int(self.y)), self.radius)
```

影を2px ずらして描くだけで、立体感が生まれます。

---

## ブロック 6：Paddle クラス（110〜140行目）

```python
@dataclass
class Paddle:
    x: float
    y: float = PADDLE_Y   # Y 座標（デフォルトは定数）
    width: int = PADDLE_W
```

```python
    @property         # メソッドなのに「変数」のように呼べる（self.rect で取得）
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, PADDLE_H)

    @property
    def center_x(self):
        return self.x + self.width / 2   # パドルの中心 X（反射角計算に使用）
```

### update() メソッド

```python
    def update(self, keys):
        if keys[pygame.K_LEFT]:     # ← キーが押されている
            self.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT]:    # → キーが押されている
            self.x += PADDLE_SPEED

        mx, _ = pygame.mouse.get_pos()          # マウスの X 座標を取得
        if pygame.mouse.get_focused():           # ウィンドウにフォーカスがある場合のみ
            target_x = mx - self.width / 2      # マウス位置がパドルの中心になる X
            self.x += (target_x - self.x) * 0.25  # 目標位置の 1/4 だけ近づく（なめらか移動）

        self.x = max(0, min(WIN_W - self.width, self.x))  # 画面外に出ないよう制限
```

`self.x += (target_x - self.x) * 0.25` は「線形補間（Lerp）」と呼ばれるテクニックで、パドルがマウスにゆっくり追いつくようになります。係数を大きくするほど俊敏になります。

---

## ブロック 7：ユーティリティ関数（143〜152行目）

```python
def clamp(value, low, high):
    return max(low, min(high, value))
    # value を low〜high の範囲に収める
    # 例: clamp(1.5, -1.0, 1.0) → 1.0
```

```python
def normalize_velocity(vx, vy, speed):
    mag = math.hypot(vx, vy)   # ベクトルの長さ = sqrt(vx² + vy²)
    if mag == 0:
        return 0.0, -speed     # 長さ0なら真上に飛ぶ
    scale = speed / mag        # 目標の速さ / 現在の長さ
    return vx * scale, vy * scale
    # vx, vy の「向き」は保ちながら「速さ」だけを speed に合わせる
```

ボールがパドルやブロックに当たると反射して速度ベクトルが変わりますが、`normalize_velocity` でスケーリングし直すことで速さが一定に保たれます。

---

## ブロック 8：レベルのブロック配置（155〜188行目）

```python
def build_blocks(level):
    rng = random.Random(level * 137)
    # シード（seed）を level に固定した乱数生成器
    # 同じ level なら毎回同じ配置になる（再現性を持たせる）
```

```python
    total_w = BLOCK_COLS * BLOCK_W + (BLOCK_COLS - 1) * BLOCK_PAD
    start_x = (WIN_W - total_w) // 2   # グリッドを画面中央に揃える X 座標
    blocks = []
```

```python
    for row in range(BLOCK_ROWS):
        for col in range(BLOCK_COLS):

            # レベル3：特定のマスを空白にしてパターンを作る
            if level >= 3:
                if (row in (1, 4) and col in (2, 7)) or (row == 2 and col in (0, 9)):
                    continue   # このマスはブロックを置かずスキップ

            # 行によって基本 HP を決める
            if row < 2:
                hp = 1   # 上 2 行：HP1（緑）
            elif row < 4:
                hp = 2   # 中 2 行：HP2（青）
            else:
                hp = 3   # 下 2 行：HP3（橙）

            # レベル2：ランダムに強いブロックを増やす
            if level == 2:
                roll = rng.random()        # 0.0〜1.0 の乱数
                if roll > 0.75:
                    hp = 3                 # 25% の確率で HP3 に
                elif roll > 0.35:
                    hp = max(hp, 2)        # 40% の確率で最低でも HP2 に

            x = start_x + col * (BLOCK_W + BLOCK_PAD)   # ブロックの X 座標
            y = BLOCK_TOP + row * (BLOCK_H + BLOCK_PAD)  # ブロックの Y 座標
            rect = pygame.Rect(x, y, BLOCK_W, BLOCK_H)
            blocks.append(Block(rect=rect, hp=hp, score=hp * 10))
            # 点数は HP × 10（HP3 なら 30 点）

    return blocks
```

---

## ブロック 9：GameScene クラス（191〜358行目）

ゲームの全状態（ブロック一覧・ボール・パドル・スコア・ライフ）をまとめて持つクラスです。

### new() クラスメソッド

```python
    @classmethod
    def new(cls, level=1):
        paddle = Paddle(x=(WIN_W - PADDLE_W) / 2)   # 画面中央にパドルを配置
        ball = Ball(x=paddle.center_x, y=paddle.y - BALL_R - 2, vx=0.0, vy=-BALL_SPEED_INIT)
        # ボールをパドルの中央上に置く。vy がマイナス＝上向き
        return cls(blocks=build_blocks(level), ball=ball, paddle=paddle, level=level)
```

`@classmethod` は「インスタンスではなくクラス自体を引数に取るメソッド」です。`GameScene.new()` のように呼び、初期化のロジックをここにまとめています。

### launch_ball() メソッド

```python
    def launch_ball(self):
        if not self.launched:
            self.launched = True
            self.ball.vx = random.choice((-1, 1)) * (BALL_SPEED_INIT * 0.45)
            # ランダムに左右どちらかへ斜めに飛ばす
            self.ball.vy = -math.sqrt(max(BALL_SPEED_INIT ** 2 - self.ball.vx ** 2, 1.0))
            # vy² + vx² = BALL_SPEED_INIT² になるよう計算（ピタゴラスの定理）
```

`vx² + vy² = speed²` という式から `vy = -√(speed² - vx²)` を計算することで、合成速度を初期速度に固定しています。

### handle_paddle_collision() メソッド

```python
    def handle_paddle_collision(self):
        if self.ball.vy <= 0:   # ボールが上向きなら当たらない（すり抜け防止）
            return
        if not self.ball.rect().colliderect(self.paddle.rect):
            return   # 衝突していなければ何もしない

        self.ball.y = self.paddle.y - self.ball.radius - 1   # めり込み補正

        speed = self.current_ball_speed()
        offset = (self.ball.x - self.paddle.center_x) / (self.paddle.width / 2)
        # offset = -1.0（左端）〜 0.0（中央）〜 +1.0（右端）
        offset = clamp(offset, -1.0, 1.0)

        new_vx = offset * speed * 1.2   # 端に当たるほど横方向が強くなる
        new_vy = -abs(speed)            # 必ず上向きに反射
        self.ball.vx, self.ball.vy = normalize_velocity(new_vx, new_vy, speed)
```

パドルのどこに当てるかで反射角が変わります。中央に当てれば真上に、端に当てれば斜めに飛びます。これがブロック崩しの駆け引きの核心です。

### handle_block_collisions() メソッド

```python
    def handle_block_collisions(self):
        ball_rect = self.ball.rect()
        # 現在ボールと重なっているブロックのインデックスを全部集める
        hit_indices = [i for i, block in enumerate(self.blocks)
                       if ball_rect.colliderect(block.rect)]
        if not hit_indices:
            return
```

```python
        # 1フレーム前のボール位置を計算（どの辺から当たったか判定するため）
        prev_x = self.ball.x - self.ball.vx
        prev_y = self.ball.y - self.ball.vy
        prev_rect = pygame.Rect(...)
```

「前フレームの位置」を使う理由：ボールが高速だと1フレームでブロックを通り過ぎてしまうため、「どちら側から入ってきたか」を前フレームの位置で判定します。

```python
        bounced_x = False   # この フレームで既に X 方向を反転したか
        bounced_y = False   # この フレームで既に Y 方向を反転したか

        for idx in hit_indices:
            block = self.blocks[idx]

            # 前フレームでブロックと重なっていた軸を調べる
            prev_overlap_x = prev_rect.right > block.rect.left and prev_rect.left < block.rect.right
            prev_overlap_y = prev_rect.bottom > block.rect.top and prev_rect.top < block.rect.bottom

            # 前フレームで X 方向に重なっていた → 左右からの衝突
            hit_left  = prev_rect.right <= block.rect.left  and prev_overlap_y
            hit_right = prev_rect.left  >= block.rect.right and prev_overlap_y
            # 前フレームで Y 方向に重なっていた → 上下からの衝突
            hit_top    = prev_rect.bottom <= block.rect.top    and prev_overlap_x
            hit_bottom = prev_rect.top    >= block.rect.bottom and prev_overlap_x
```

```python
            if (hit_left or hit_right) and not bounced_x:
                self.ball.vx *= -1   # 左右から → X 速度を反転
                bounced_x = True

            if (hit_top or hit_bottom) and not bounced_y:
                self.ball.vy *= -1   # 上下から → Y 速度を反転
                bounced_y = True
```

`bounced_x / bounced_y` フラグにより、同フレームに複数ブロックに当たっても二重反転しないようにしています。

```python
            if block.hp <= 1:
                self.score += block.score   # 得点加算
                new_blocks.pop(curr_idx)    # ブロックを消去
                removed += 1
            else:
                # HP を1減らした新しい Block インスタンスに置き換える
                new_blocks[curr_idx] = Block(rect=block.rect, hp=block.hp - 1, score=block.score)

            # ブロックを壊すたびにボールを少し加速
            speed = min(BALL_SPEED_MAX, self.current_ball_speed() + BALL_SPEED_INC)
            self.ball.vx, self.ball.vy = normalize_velocity(self.ball.vx, self.ball.vy, speed)
```

### update() メソッド

```python
    def update(self, keys, dt_ms):
        self.paddle.update(keys)

        if not self.launched:           # 未発射：ボールをパドルに追従させるだけ
            self.ball.x = self.paddle.center_x
            self.ball.y = self.paddle.y - self.ball.radius - 2
            return GameState.PLAYING

        events = self.ball.update(dt_ms)   # ボール移動・壁・天井の判定
        self.handle_paddle_collision()      # パドルとの衝突
        self.handle_block_collisions()      # ブロックとの衝突

        if "miss" in events:               # ボールが画面下に落ちた
            self.lives -= 1
            if self.lives <= 0:
                return GameState.GAME_OVER  # ライフがなくなった
            self.reset_ball()              # ボールをパドルに戻す
            return GameState.PLAYING

        if not self.blocks:                # 全ブロックを破壊した
            self.score += 500              # クリアボーナス
            if self.level >= MAX_LEVEL:
                return GameState.CLEAR     # 最終レベルなら全クリア
            self.level += 1               # 次のレベルへ
            self.blocks = build_blocks(self.level)
            self.reset_ball()

        return GameState.PLAYING
```

### draw() メソッド

```python
    def draw(self, surface, font_small):
        self.paddle.draw(surface)
        self.ball.draw(surface)

        for block in self.blocks:
            color = BLOCK_COLORS[block.hp]              # HP に対応した色を取得

            shadow = block.rect.move(2, 2)              # 右下に2px ずらした影
            pygame.draw.rect(surface, (20, 20, 20), shadow, border_radius=5)
            pygame.draw.rect(surface, color, block.rect, border_radius=5)  # 本体
            pygame.draw.rect(surface, (245, 245, 245), block.rect, 1, border_radius=5)
            # 1px の白枠でブロックを縁取る（第4引数 1 = 枠のみ）

            hp_text = font_small.render(str(block.hp), True, C_BG)
            surface.blit(
                hp_text,
                (block.rect.centerx - hp_text.get_width() // 2,
                 block.rect.centery - hp_text.get_height() // 2),
            )
            # ブロックの中央に HP 数字を表示
```

---

## ブロック 10：HUD の描画（361〜374行目）

```python
def draw_hud(surface, scene, state, font, font_small):
    pygame.draw.rect(surface, C_INFO_BG, (0, 0, WIN_W, INFO_H))
    # 上部に帯状の HUD 背景を描く

    texts = [
        font.render(f"SCORE {scene.score}", True, C_TEXT),      # スコア（大）
        font_small.render(f"LIVES {scene.lives}", True, C_TEXT), # ライフ数
        font_small.render(f"LEVEL {scene.level}", True, C_TEXT), # レベル
        font_small.render(f"STATE {state.name}", True, C_TEXT),  # 現在の状態
    ]

    surface.blit(texts[0], (20, 16))                              # 左端にスコア
    surface.blit(texts[1], (WIN_W - 220, 14))                    # 右側にライフ
    surface.blit(texts[2], (WIN_W - 220, 34))                    # ライフの下にレベル
    surface.blit(texts[3], (WIN_W // 2 - texts[3].get_width() // 2, 20))  # 中央に状態
```

`surface.blit(画像, (x, y))` は「画像を指定座標に貼り付ける」命令です。テキストも `font.render()` で Surface（画像）に変換してから `blit` します。

---

## ブロック 11：オーバーレイ画面の描画（377〜408行目）

```python
def draw_overlay(surface, state, font, font_small):
    if state == GameState.PLAYING:
        return   # プレイ中は何も表示しない

    overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    # SRCALPHA = 透明度を扱える Surface を作成
    overlay.fill(C_OVERLAY)   # 半透明の黒で塗る（背景を透かす）
    surface.blit(overlay, (0, 0))
```

```python
    # 状態に応じてタイトルとメッセージを切り替える
    if state == GameState.MENU:
        title = "Breakout"
        lines = ["SPACE で開始", "P で一時停止 / 再開", "R でリセット", "ESC で終了"]
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
    # 横中央揃え：「ウィンドウ中央 - テキスト幅の半分」が左端の座標

    for idx, line in enumerate(lines):
        text = font_small.render(line, True, C_TEXT)
        surface.blit(text, (WIN_W // 2 - text.get_width() // 2, WIN_H // 2 - 20 + idx * 28))
        # 1行28px 間隔で縦に並べる
```

---

## ブロック 12：イベント処理（411〜440行目）

```python
def handle_event(event, state, scene):
    if event.type == pygame.QUIT:   # ×ボタンが押された
        pygame.quit()
        sys.exit()

    if event.type == pygame.KEYDOWN:   # キーが押された瞬間（押しっぱなしではない）
        if event.key == pygame.K_ESCAPE:   # ESC キー
            pygame.quit()
            sys.exit()

        if event.key == pygame.K_r:    # R キー → リセットしてメニューへ
            scene.reset()
            return GameState.MENU

        if event.key == pygame.K_p:    # P キー → ポーズ切り替え
            if state == GameState.PLAYING:
                return GameState.PAUSED
            if state == GameState.PAUSED:
                return GameState.PLAYING

        if event.key == pygame.K_SPACE:   # SPACE キー → ゲーム開始 or ボール発射
            if state == GameState.MENU:
                scene.reset()
                scene.launch_ball()
                return GameState.PLAYING
            if state == GameState.PLAYING and not scene.launched:
                scene.launch_ball()

    return state   # 変化がなければ現在の state をそのまま返す
```

`pygame.KEYDOWN` は「キーを押した瞬間」、`pygame.key.get_pressed()` は「押し続けている間」を検出します。パドルの移動には後者を使い、ゲーム状態の切り替えには前者を使っています。

---

## ブロック 13：フォント読み込み（443〜455行目）

```python
_JP_FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    # macOS に標準搭載されている日本語フォントのパス候補
    ...
]

def _make_font(size: int, bold: bool = False) -> pygame.font.Font:
    for path in _JP_FONT_CANDIDATES:
        if os.path.exists(path):          # ファイルが存在するか確認
            return pygame.font.Font(path, size)   # 見つかったフォントを使う
    return pygame.font.SysFont("notosanscjk,applegothic,arial", size, bold=bold)
    # 見つからなければシステムフォントでフォールバック
```

`pygame.font.SysFont("Arial", ...)` だけでは日本語グリフ（字形）が含まれないため文字化けします。日本語フォントファイルを直接指定することで正しく表示されます。

---

## ブロック 14：メインループ（467〜506行目）

```python
def main():
    pygame.init()   # pygame の全機能を初期化（必ず最初に呼ぶ）
    screen = pygame.display.set_mode((WIN_W, WIN_H))   # ウィンドウを作成
    pygame.display.set_caption("Breakout - Day 013")   # タイトルバーの文字
    clock = pygame.time.Clock()   # FPS 制御用タイマー

    font       = _make_font(28, bold=True)   # HUD 用の大きいフォント
    font_small = _make_font(18)              # ブロック HP 表示・メニュー用

    state = GameState.MENU       # 最初はメニュー画面から
    scene = GameScene.new(level=1)
```

```python
    while True:   # ゲームループ（ESC か ×ボタンで sys.exit() されるまで続く）
        dt_ms = clock.tick(FPS)          # 1フレームを 1/60 秒に制限し、経過 ms を返す
        keys = pygame.key.get_pressed()  # 現在押されているキーを全て取得

        for event in pygame.event.get():          # 今フレームのイベントを処理
            state = handle_event(event, state, scene)

        if state == GameState.PLAYING:
            state = scene.update(keys, dt_ms)     # ゲームロジック更新
        elif state in (GameState.MENU, GameState.PAUSED, GameState.GAME_OVER, GameState.CLEAR):
            scene.paddle.update(keys)             # メニュー中もパドルは動かせる
            if not scene.launched:
                scene.ball.x = scene.paddle.center_x   # 未発射ならボールをパドルに追従
                scene.ball.y = scene.paddle.y - scene.ball.radius - 2
```

```python
        # 描画（毎フレーム全て描き直す）
        screen.fill(C_BG)                               # 背景を塗りつぶして前フレームを消す
        scene.draw(screen, font_small)                  # ブロック・ボール・パドルを描く
        draw_hud(screen, scene, state, font, font_small)  # HUD を描く
        draw_overlay(screen, state, font, font_small)   # オーバーレイ画面を描く
        pygame.display.flip()                           # 描いた内容を画面に表示
```

```python
if __name__ == "__main__":
    main()
    # このファイルを直接実行した場合のみ main() を呼ぶ
    # import breakout として読み込まれた場合は呼ばない
```

---

## 全体の流れまとめ

```
起動
 └─ main()
     ├─ pygame 初期化・ウィンドウ作成
     ├─ state = MENU、scene を初期化
     └─ ゲームループ（60回/秒）
          ├─【入力処理】handle_event() で SPACE/P/R/ESC を処理 → state 更新
          ├─【ゲーム更新】state == PLAYING のとき scene.update() を呼ぶ
          │    ├─ パドル移動
          │    ├─ ボール移動 + 壁・天井反射
          │    ├─ パドル衝突判定（反射角を計算）
          │    ├─ ブロック衝突判定（HP 減算・得点・加速）
          │    └─ ミス / レベルクリア / ゲームオーバー判定
          └─【描画】背景 → ブロック → ボール → パドル → HUD → オーバーレイ → 画面反映
```

### 衝突判定のポイント

```
前フレームの位置と現フレームの位置を比べて
「どの辺から衝突したか」を判定する

  前フレーム     現フレーム
  ┌──┐           ┌──┐
  │  │   →→→    │  │
  └──┘           └──┘
           ┌────────┐
           │ Block  │  ← 左辺から衝突 → vx を反転
           └────────┘
```

### 反射角のポイント

```
パドルの端に当てるほど横方向が強くなる

      左端        中央        右端
   ↗ 急角度    ↑ 真上    ↗ 急角度
  パドル左       中央       パドル右
  ←←←←←       ↑       →→→→→
  offset=-1.0  0.0  +1.0
```
