# day016 — ネットワーク診断 Web サービス

PC のネットワーク設定画面のように、クライアントの情報表示と疎通確認ができる Web アプリ。

## 機能

| 項目 | 内容 |
|------|------|
| ネットワーク情報 | IP アドレス・サブネット・デフォルト GW・インターフェース名を自動取得して表示 |
| Ping | IP アドレスまたはホスト名への ICMP 疎通確認（4 パケット） |
| DNS | ドメイン名の名前解決（IPv4/IPv6 アドレス一覧・応答時間） |
| HTTP | URL への HTTP/HTTPS 接続確認（ステータスコード・応答時間・リダイレクト有無） |

## 起動方法

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5016
```

## 技術スタック

- Backend: Python / Flask
- ネットワーク情報取得: `netifaces` + `ipaddress`
- DNS 解決: `socket.getaddrinfo`
- HTTP チェック: `requests`
- Ping: `subprocess` (OS の `ping` コマンドを実行)
- Frontend: Vanilla HTML/CSS/JS（ダークテーマ）
