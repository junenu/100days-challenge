# Crystal Shards

Pygame だけで描画するトップダウン型アクション RPG です。村から 3 つのダンジョンへ向かい、各ボスを倒してクリスタルの欠片を集めるとクリアです。

## 起動

```bash
python3 main.py
```

`pygame` が未導入の場合:

```bash
python3 -m pip install pygame
```

## 操作

- `Enter`: タイトル開始 / 会話 / ポータル起動
- `WASD`: 移動
- `Space`: 近接攻撃
- `E`: ポーション使用
- `Esc`: タイトルへ戻る
- `R`: ゲームオーバー・勝利画面からリスタート

## 進行

- 村のポータルから `Forest` → `Cave` → `Tower` の順に攻略します。
- ボスが落とす `Crystal Shard` を取ると村へ戻ります。
- 3 個すべて集めると `VICTORY` です。
