# othello.py コード解説

初心者向けに一行ずつ解説したドキュメントです。

---

## ブロック 1：ライブラリの読み込み（1〜2行目）

```python
import pygame   # ゲーム画面の描画・マウス・キーボード入力を扱うライブラリ
import sys      # プログラムを終了する sys.exit() のために必要
```

`import` は「外部の道具箱を借りてくる」命令です。pygame がないと画面が表示できません。

---

## ブロック 2：定数の定義（5〜31行目）

```python
BOARD_SIZE = 8          # ボードは 8×8 マス
CELL_SIZE = 70          # 1マスのピクセルサイズ（70px × 70px）
MARGIN = 40             # 盤の外側の余白（px）
INFO_HEIGHT = 100       # 盤の下にあるスコア表示エリアの高さ

WIDTH  = BOARD_SIZE * CELL_SIZE + MARGIN * 2   # ウィンドウ幅 = 8×70 + 40×2 = 640px
HEIGHT = BOARD_SIZE * CELL_SIZE + MARGIN * 2 + INFO_HEIGHT  # ウィンドウ高さ = 660px

FPS = 60   # 1秒間に画面を60回描き直す（アニメーションを滑らかにする）
```

```python
# 色は (赤, 緑, 青) の 0〜255 の数字で表す（RGB）
C_BG        = (34, 34, 34)      # 背景色：ほぼ黒
C_BOARD     = (0, 120, 60)      # 盤面：緑
C_GRID      = (0, 90, 45)       # グリッド線：暗い緑
C_BLACK     = (20, 20, 20)      # 黒石の色
C_WHITE     = (240, 240, 240)   # 白石の色
C_HINT      = (100, 200, 120, 120)  # ヒントの色（4番目の120は透明度）
C_TEXT      = (220, 220, 220)   # テキストの色：明るいグレー
C_HIGHLIGHT = (255, 220, 50)    # 強調色：黄色
C_BUTTON    = (60, 60, 60)      # ボタンの色
C_BUTTON_HOVER = (90, 90, 90)   # マウスを乗せたときのボタンの色
```

```python
EMPTY, BLACK, WHITE = 0, 1, 2   # マスの状態を数字で表す（空=0, 黒=1, 白=2）
```

これで `board[r][c] == BLACK` のように判定できます。

```python
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),   # 左上, 上, 右上
              (0,  -1),          (0,  1),    # 左,       右
              (1,  -1),  (1, 0), (1,  1)]   # 左下, 下, 右下
```

石をひっくり返せるか調べるとき、**8方向すべて**を調べます。このリストがその8方向を表しています。

---

## ブロック 3：盤面の初期化（35〜42行目）

```python
def make_board():
    board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    # EMPTY（=0）が8個並んだリストを、8行分作る → 8×8の二重リスト
```

イメージ：
```
board[0] = [0, 0, 0, 0, 0, 0, 0, 0]  ← 1行目
board[1] = [0, 0, 0, 0, 0, 0, 0, 0]  ← 2行目
...（8行）
```

```python
    mid = BOARD_SIZE // 2   # 8 ÷ 2 = 4（盤面の中央付近のインデックス）

    board[mid - 1][mid - 1] = WHITE  # (3,3) に白
    board[mid - 1][mid]     = BLACK  # (3,4) に黒
    board[mid][mid - 1]     = BLACK  # (4,3) に黒
    board[mid][mid]         = WHITE  # (4,4) に白
    return board
```

オセロは最初から中央に4つの石が置かれた状態でスタートします。

---

## ブロック 4：ユーティリティ関数（45〜94行目）

```python
def opponent(player):
    return WHITE if player == BLACK else BLACK
    # 黒が来たら白を返す、白が来たら黒を返す（相手の色を得る）
```

```python
def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE
    # 行r・列cがボード内（0〜7）に収まっているか確認する
    # はみ出た場所を参照するとエラーになるため、必ずチェックする
```

```python
def flips_for_move(board, r, c, player):
    # 「(r,c) に player が石を置いたとき、ひっくり返せる石のリスト」を返す
    if board[r][c] != EMPTY:
        return []   # すでに石がある場所には置けない → 空リストを返す

    opp = opponent(player)   # 相手の色を取得
    all_flips = []           # ひっくり返せる石を入れるリスト

    for dr, dc in DIRECTIONS:   # 8方向それぞれについて調べる
        line = []               # この方向で挟める石を一時的に保存
        nr, nc = r + dr, c + dc # 1つ隣のマスの座標

        while in_bounds(nr, nc) and board[nr][nc] == opp:
            # 隣が相手の石である限り、その方向へ進み続ける
            line.append((nr, nc))   # 相手の石の座標を記録
            nr += dr                # さらに1つ先へ進む
            nc += dc

        if line and in_bounds(nr, nc) and board[nr][nc] == player:
            # 条件：相手の石が1個以上あって、その先に自分の石がある
            # → この方向の相手石はすべてひっくり返せる
            all_flips.extend(line)  # ひっくり返せる石をまとめて追加

    return all_flips   # すべての方向の結果を返す
```

具体例：
```
. . B . .
. . W . .    ← B=黒, W=白, .=空
. . * . .    ← *に黒を置こうとしている
```
`*` から上方向に進むと白があり、その先に黒がある → 白をひっくり返せる！

```python
def valid_moves(board, player):
    return [(r, c) for r in range(BOARD_SIZE)
                   for c in range(BOARD_SIZE)
                   if flips_for_move(board, r, c, player)]
    # 全64マスを調べ、1枚以上ひっくり返せるマスだけをリストにして返す
    # これが「有効手」＝石を置けるマスの一覧
```

```python
def apply_move(board, r, c, player):
    new_board = [row[:] for row in board]
    # row[:] は行のコピーを作る。元の board を壊さないために新しい盤面を作る

    flips = flips_for_move(new_board, r, c, player)  # ひっくり返す石を取得
    new_board[r][c] = player                          # 指定マスに石を置く
    for fr, fc in flips:
        new_board[fr][fc] = player   # 挟んだ相手の石を自分の色に変える
    return new_board   # 新しい盤面を返す（元の盤面は変更されない）
```

```python
def count(board):
    black = sum(row.count(BLACK) for row in board)  # 全行の黒石数を合計
    white = sum(row.count(WHITE) for row in board)  # 全行の白石数を合計
    return black, white   # 2つの値を同時に返す
```

```python
def board_pos(r, c):
    x = MARGIN + c * CELL_SIZE + CELL_SIZE // 2   # マスの中央のX座標（ピクセル）
    y = MARGIN + r * CELL_SIZE + CELL_SIZE // 2   # マスの中央のY座標（ピクセル）
    return x, y   # 石を描くときの中心座標として使う
```

---

## ブロック 5：AI の評価マップ（98〜107行目）

```python
WEIGHT_MAP = [
    [100, -20, 10,  5,  5, 10, -20, 100],   # 行0（上端）
    [-20, -50, -2, -2, -2, -2, -50, -20],   # 行1
    [ 10,  -2,  1,  1,  1,  1,  -2,  10],   # 行2
    ...
]
```

各マスに「価値の点数」を割り当てたテーブルです。

| 値 | 場所 | 理由 |
|----|------|------|
| **+100** | 四隅 | 一度取れば絶対返されない最強マス |
| **-50** | 隅の隣の隅隣 | 相手に隅を渡しやすい危険地帯 |
| **-20** | 端の隅隣 | 同じく相手に隅を取られやすい |
| **+10** | 端の中央付近 | やや有利 |
| **+1** | 中央付近 | 普通 |

---

## ブロック 6：AI のスコア計算（110〜119行目）

```python
def ai_score(board, player):
    opp = opponent(player)
    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == player:
                score += WEIGHT_MAP[r][c]   # 自分の石 → プラス
            elif board[r][c] == opp:
                score -= WEIGHT_MAP[r][c]   # 相手の石 → マイナス
    return score   # スコアが高いほど白（AI）に有利な盤面
```

---

## ブロック 7：Minimax アルゴリズム（122〜154行目）

```python
def minimax(board, player, depth, alpha, beta, maximizing):
    moves = valid_moves(board, player)

    if depth == 0 or not moves:
        return ai_score(board, WHITE), None
        # 探索を止める条件：depth=0（4手先まで読み終えた）か、打てる手がない
        # → 今の盤面を評価してスコアを返す
```

```python
    best_move = None
    if maximizing:   # 白（AI）の手番 → スコアを最大にしたい
        best_val = -10**9   # 最初は「最悪の値」をセット（-10億）

        for r, c in moves:   # 打てる手を1つずつ試す
            nb = apply_move(board, r, c, player)   # 仮に石を置いた盤面を作る
            val, _ = minimax(nb, opponent(player), depth - 1, alpha, beta, False)
            # 相手がその後最善を尽くしたときのスコアを再帰で計算

            if val > best_val:
                best_val, best_move = val, (r, c)   # より良い手が見つかったら更新

            alpha = max(alpha, val)   # alpha = 白が確実に確保できる最低スコア
            if beta <= alpha:
                break   # α-β 枝刈り：これ以上調べても意味がないのでスキップ
```

```python
    else:   # 黒（プレイヤー）の手番 → スコアを最小にしようとする（AI視点）
        best_val = 10**9   # 最初は「最高の値」をセット（+10億）

        for r, c in moves:
            nb = apply_move(board, r, c, player)
            val, _ = minimax(nb, opponent(player), depth - 1, alpha, beta, True)

            if val < best_val:
                best_val, best_move = val, (r, c)

            beta = min(beta, val)   # beta = 黒が確実に抑えられる最高スコア
            if beta <= alpha:
                break   # α-β 枝刈り
```

**α-β 枝刈りのイメージ：**
```
白がある手を考えている（スコア 50 確定）
→ 別の手を調べ始めたら、黒が「スコア30にできる」とわかった
→ 白にとってこの手は50より悪い → 調べる意味なし → スキップ（枝刈り）
```

```python
def ai_move(board):
    _, move = minimax(board, WHITE, depth=4, alpha=-10**9, beta=10**9, maximizing=True)
    return move   # 4手先まで読んで最善手を返す
```

---

## ブロック 8：盤面の描画（158〜204行目）

```python
def draw_board(surface, board, hints, selected, font_small):
    pygame.draw.rect(surface, C_BOARD,
                     (MARGIN, MARGIN, BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE))
    # 緑色の盤面背景を四角形で描く（x, y, 幅, 高さ）
```

```python
    for i in range(BOARD_SIZE + 1):   # 0〜8 の9本の線を描く
        x = MARGIN + i * CELL_SIZE
        y = MARGIN + i * CELL_SIZE
        pygame.draw.line(surface, C_GRID, (x, MARGIN), (x, MARGIN + BOARD_SIZE * CELL_SIZE), 1)
        # 縦線：(x, 上端) から (x, 下端) まで
        pygame.draw.line(surface, C_GRID, (MARGIN, y), (MARGIN + BOARD_SIZE * CELL_SIZE, y), 1)
        # 横線：(左端, y) から (右端, y) まで
```

```python
    hint_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    # SRCALPHA = 透明度（アルファ値）を扱える Surface を作成
    hint_surf.fill((100, 200, 120, 80))
    # 半透明の緑色で塗りつぶす（80 = やや透明）

    for (r, c) in hints:   # 有効手のマス全部に対して
        x = MARGIN + c * CELL_SIZE
        y = MARGIN + r * CELL_SIZE
        surface.blit(hint_surf, (x, y))   # 半透明の緑を重ねて貼り付ける
        cx, cy = board_pos(r, c)
        pygame.draw.circle(surface, (80, 200, 100), (cx, cy), 8)   # 中央に緑の点
```

```python
    radius = CELL_SIZE // 2 - 5   # 石の半径（マスの半分より少し小さく）
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == EMPTY:
                continue   # 空マスはスキップ
            cx, cy = board_pos(r, c)
            color = C_BLACK if board[r][c] == BLACK else C_WHITE

            pygame.draw.circle(surface, (10, 10, 10), (cx + 2, cy + 2), radius)
            # 右下にずらした黒い円 → 影に見える
            pygame.draw.circle(surface, color, (cx, cy), radius)
            # 本体の石を描く

            if board[r][c] == WHITE:
                pygame.draw.circle(surface, (255, 255, 255),
                                   (cx - radius // 4, cy - radius // 4), radius // 5)
                # 白石の左上に小さな白丸 → ツヤに見える
```

---

## ブロック 9：情報エリアの描画（207〜248行目）

```python
def draw_info(surface, board, current_player, game_over, passed, font, font_small, buttons):
    info_y = MARGIN + BOARD_SIZE * CELL_SIZE + 10   # 盤面の下側の Y 座標

    black_cnt, white_cnt = count(board)   # 現在のスコアを取得

    for col, (player_color, piece_color, label, score) in enumerate([...]):
        # 黒・白の2つ分、石のアイコンとスコアを横に並べて描く
        pygame.draw.circle(surface, C_HIGHLIGHT, (x + 15, info_y + 20), 14, 2)
        # 現在の手番の石に黄色の枠を描いて「あなたのターン」を示す
```

```python
    if game_over:
        # 勝敗メッセージを中央に表示
    elif passed:
        # パスメッセージを表示
```

```python
    mouse_pos = pygame.mouse.get_pos()   # マウスカーソルの現在位置を取得
    for btn in buttons:
        color = C_BUTTON_HOVER if btn["rect"].collidepoint(mouse_pos) else C_BUTTON
        # マウスがボタンの上にあれば明るい色、そうでなければ暗い色
        pygame.draw.rect(surface, color, btn["rect"], border_radius=6)
        # 角丸四角形でボタンを描く
```

---

## ブロック 10：マウス座標 → マス変換（251〜256行目）

```python
def cell_from_mouse(mx, my):
    c = (mx - MARGIN) // CELL_SIZE   # X座標から列番号を計算
    r = (my - MARGIN) // CELL_SIZE   # Y座標から行番号を計算
    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        return r, c   # ボード内なら (行, 列) を返す
    return None       # ボード外ならNone（クリック無効）
```

例：`mx=180, MARGIN=40, CELL_SIZE=70` の場合
`(180 - 40) // 70 = 140 // 70 = 2` → 2列目

---

## ブロック 11：メインループ（260〜370行目）

```python
def main():
    pygame.init()   # pygame の全機能を起動（呼ばないと動かない）
    screen = pygame.display.set_mode((WIDTH, HEIGHT))   # ウィンドウを作成
    pygame.display.set_caption("Othello — Day 012")     # ウィンドウのタイトルを設定
    clock = pygame.time.Clock()   # FPS制御用のタイマー
```

```python
    board = make_board()       # 初期盤面を作成
    current_player = BLACK     # 黒（プレイヤー）が先手
    game_over = False          # ゲーム終了フラグ
    passed = False             # パスフラグ
    show_hints = True          # ヒント表示フラグ
    ai_delay = 0               # AI が即座に打つと不自然なので、遅延用カウンタ
```

```python
    while True:   # ←「ゲームループ」：プログラムが終わるまでずっと繰り返す
        clock.tick(FPS)   # 1ループを 1/60秒 に制限（60FPS）
```

ゲームループの中身は3つに分かれています：

### ① AI の処理

```python
        if current_player == WHITE and not game_over:
            ai_delay += 1   # フレームごとにカウンタを増やす
            if ai_delay >= FPS // 2:   # 30フレーム（0.5秒）たったら打つ
                ai_delay = 0
                moves = valid_moves(board, WHITE)
                if moves:
                    move = ai_move(board)   # AI が最善手を計算
                    board = apply_move(board, move[0], move[1], WHITE)
                passed = not bool(moves)   # 打てる手がなければパス
                current_player = BLACK     # 黒の番に交代
```

### ② イベント処理（キー・マウス）

```python
        for event in pygame.event.get():   # 発生したイベントを全部取得
            if event.type == pygame.QUIT:  # ×ボタンが押された
                pygame.quit()
                sys.exit()   # プログラム終了

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:   # R キーが押された
                    board = make_board()       # ゲームリセット

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 左クリックされた
                mx, my = event.pos   # クリックした座標を取得

                if btn_reset["rect"].collidepoint(mx, my):   # Reset ボタン上
                    board = make_board()   # リセット
                    continue

                if current_player == BLACK and not game_over:
                    cell = cell_from_mouse(mx, my)   # どのマスか判定
                    if cell:
                        r, c = cell
                        if flips_for_move(board, r, c, BLACK):   # 有効手か確認
                            board = apply_move(board, r, c, BLACK)   # 石を置く
                            current_player = WHITE   # AI の番に交代
```

### ③ 描画

```python
        screen.fill(C_BG)   # 毎フレーム背景を塗りつぶして前のフレームを消す
        draw_board(screen, board, hints, None, font_small)   # 盤面を描く
        draw_info(screen, board, ...)   # スコア・ボタンを描く
        pygame.display.flip()   # 描いた内容を画面に反映（これを忘れると何も表示されない）
```

```python
if __name__ == "__main__":
    main()
    # このファイルを直接実行したとき（python othello.py）だけ main() を呼ぶ
    # 他のファイルから import されたときは呼ばない
```

---

## 全体の流れまとめ

```
起動
 └─ main()
     ├─ 盤面・変数の初期化
     └─ ゲームループ（60回/秒）
          ├─【AI処理】白の番 → 0.5秒後に Minimax で最善手を計算して打つ
          ├─【入力処理】クリック/キー入力 → 黒石を置く・リセットなど
          └─【描画】背景 → 盤面 → 石 → ヒント → スコア → 画面反映
```
