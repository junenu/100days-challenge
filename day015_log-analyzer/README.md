# Day015 — log-analyzer

Apache/Nginx 風のアクセスログを読み込み、ステータスコード・URL・IP・時間帯別に集計する CLI ツールです。
不正なログ行はクラッシュせずスキップし、必要に応じて詳細を表示できます。

## 技術スタック

- Language: Python 3.12
- Framework/Library: 標準ライブラリのみ
- その他: `argparse`, `re`, `collections.Counter`, `unittest`

## 起動方法

```bash
# サンプルログを解析
python3 log_analyzer.py sample.log

# 404 だけに絞り込み
python3 log_analyzer.py sample.log --status 404

# ランキング件数を変更
python3 log_analyzer.py sample.log --top 3

# スキップした不正行を stderr に表示
python3 log_analyzer.py sample.log --show-skipped
```

## 機能一覧

### 実装済み

- [x] Apache/Nginx 風アクセスログのパース
- [x] 総リクエスト数の表示
- [x] HTTP ステータスコード別集計
- [x] HTTP メソッド別集計
- [x] URL パス別ランキング
- [x] アクセス元 IP 別ランキング
- [x] 時間帯別アクセス数の表示
- [x] `--status` によるステータスコード絞り込み
- [x] `--top` によるランキング件数変更
- [x] 不正なログ行のスキップと `--show-skipped` 表示
- [x] `unittest` によるパース・集計テスト

### 今後の改善候補

- [ ] JSON/CSV 出力
- [ ] User-Agent 別集計
- [ ] 複数ログファイルの一括集計
- [ ] 日付範囲による絞り込み

## 動作確認

```bash
python3 -m unittest -v test_log_analyzer.py
python3 log_analyzer.py sample.log
python3 log_analyzer.py sample.log --status 404 --show-skipped
```

### サンプル実行結果

```bash
$ python3 log_analyzer.py sample.log
Access Log Analyzer
===================

Total requests: 12
Skipped lines:   1

Status codes:
  200                          7
  404                          2
  302                          1
  403                          1
  500                          1

Methods:
  GET                         11
  POST                         1

Top 5 paths:
  /docs                        4
  /api/status                  2
  /                            1
  /assets/app.css              1
  /favicon.ico                 1

Top 5 IPs:
  192.168.10.11                3
  192.168.10.12                3
  192.168.10.13                1
  192.168.10.14                1
  192.168.10.15                1

Requests by hour:
  2026-04-26 09:00             5
  2026-04-26 10:00             4
  2026-04-26 11:00             3
```

```bash
$ python3 log_analyzer.py sample.log --status 404
Access Log Analyzer
===================

Filter: status=404

Total requests: 2
Skipped lines:   1

Status codes:
  404                          2

Methods:
  GET                          2

Top 5 paths:
  /favicon.ico                 1
  /missing                     1

Top 5 IPs:
  192.168.10.13                1
  192.168.10.12                1

Requests by hour:
  2026-04-26 09:00             1
  2026-04-26 10:00             1
```

## 開発ログ

### 学んだこと

- 正規表現でログ形式を厳密に切り出し、日時変換や数値変換は別途 `try` で守ると異常入力に強くなる
- `collections.Counter` を使うとランキング形式の集計を短く実装できる

### 詰まったこと・解決方法

- ログのサイズ欄は `-` になる場合があるため、整数にできない値として落とさず `None` として扱った
- 絞り込み後の件数と不正行の件数は意味が違うため、パース結果とサマリーを分けて保持した

### 次回やってみたいこと

- Day14 のファイル共有サーバーにアクセスログ出力形式を寄せて、このツールで解析できるようにする
