# day011 — Config Diff Visualizer

Cisco / Juniper などのネットワーク設定ファイルを **セクション単位** で比較・可視化するツール。  
CLI と Web UI の両方に対応。

## 機能

- **セクション単位の差分**: 行単位ではなく、`interface`・`router ospf`・`ip access-list` などのブロック単位で比較
- **ステータス分類**: 追加 (green) / 削除 (red) / 変更 (yellow) / 変更なし (gray)
- **セクションフィルター**: `--filter acl` など特定のセクションだけ抽出して比較
- **CLI 出力**: ANSI カラーつきの unified diff 表示
- **Web UI**: ブラウザで side-by-side / unified diff をインタラクティブに確認

## 使い方

### CLI

```bash
# 基本比較
python config_diff.py before.cfg after.cfg

# セクションフィルター（route-map だけ表示）
python config_diff.py before.cfg after.cfg --filter route-map

# 変更なしセクションも含めて表示
python config_diff.py before.cfg after.cfg --all
```

### Web UI

```bash
python config_diff.py --web           # http://127.0.0.1:8011
python config_diff.py --web --port 9000  # ポート指定
```

ブラウザで「サンプルを読み込む」ボタンを押すとデモデータが入力されます。

## サンプル実行

```bash
python config_diff.py sample_before.cfg sample_after.cfg
python config_diff.py sample_before.cfg sample_after.cfg --filter interface
```

## テスト

```bash
python -m pytest test_config_diff.py -v
```

## 技術スタック

- Python 3.12（標準ライブラリのみ）
  - `difflib` — unified diff 生成
  - `http.server` — 組み込み Web サーバー
- HTML / CSS / Vanilla JS — Web UI（外部依存なし）
