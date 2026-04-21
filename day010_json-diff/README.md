# day010 — JSON Diff Comparator

2 つの JSON を比較して差分を色付きで表示する CLI ツール。

## 機能

- ネストされたオブジェクト・配列を再帰的に比較
- 追加 (緑)・削除 (赤)・変更 (黄) を色分け表示
- ドット記法でパスを表示（例: `user.address.city`）
- ファイルパスとインライン JSON 文字列の両方に対応

## 使い方

```bash
# ファイル比較
python json_diff.py a.json b.json

# インライン JSON 比較
python json_diff.py '{"a":1}' '{"a":2}'
```

## 実行例

```
╔══════════════════════════════╗
║   JSON Diff Comparator 🔍    ║
╚══════════════════════════════╝

  + 追加   - 削除   ~ 変更

差分 (7 件):

  ~ active  - true  →  + false
  ~ address.city  - "Tokyo"  →  + "Osaka"
  + address.country: "Japan"
  ~ age  - 30  →  + 31
  - email: "alice@example.com"
  ~ hobbies[1]  - "coding"  →  + "gaming"
  + nickname: "Ali"

合計: 7 件の差分
```

## テスト

```bash
python -m pytest test_json_diff.py -v
```

18 テスト / 標準ライブラリのみ（追加インストール不要）
