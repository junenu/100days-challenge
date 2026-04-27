# app.py / index.html コード解説

初心者向けに一行ずつ解説したドキュメントです。

---

## ブロック 1：ライブラリの読み込み（1〜14行目）

```python
import re           # 正規表現（入力値の検証に使う）
import socket       # DNS 解決・UDP ソケット（ネットワーク情報の取得）
import subprocess   # OS のコマンド（ping）を Python から呼び出す
import platform     # Windows か macOS/Linux かを判別する
import ipaddress    # "192.168.1.10/255.255.255.0" をサブネット形式に変換する
import time         # 処理の実行時間を計測する

from flask import Flask, render_template, request, jsonify
# Flask  … Web フレームワーク本体
# render_template … HTML ファイルを返す
# request         … ブラウザから送られたデータを受け取る
# jsonify         … Python の辞書を JSON レスポンスに変換する

import requests as http_requests
# requests … 外部 URL に HTTP リクエストを送るライブラリ
# as http_requests と別名にするのは、Flask の request と混同しないため
```

```python
try:
    import netifaces
    HAS_NETIFACES = True
except ImportError:
    HAS_NETIFACES = False
```

`netifaces` はインストール状況によって存在しないこともあるため `try/except` で囲んでいます。
存在しない場合は `HAS_NETIFACES = False` が立ち、後のコードでフォールバック処理が動きます。

---

## ブロック 2：入力バリデーション（18〜22行目）

```python
_SAFE_HOST_RE = re.compile(r'^[a-zA-Z0-9.\-_]+$')

def _safe_host(value: str) -> bool:
    return bool(_SAFE_HOST_RE.match(value)) and len(value) <= 253
```

**なぜバリデーションが必要なのか？**

`ping` コマンドは `subprocess` 経由でシェルに渡されます。入力値に `; rm -rf /` のような文字が含まれると、意図しないコマンドが実行される「コマンドインジェクション」攻撃に悪用される可能性があります。

正規表現 `^[a-zA-Z0-9.\-_]+$` が許可するのは次の文字だけです：

| 文字 | 用途 |
|------|------|
| `a-z A-Z` | ホスト名の英字 |
| `0-9` | IP アドレスや番号 |
| `.` | ドットの区切り（`192.168.1.1` や `google.com`） |
| `-` `_` | ホスト名のハイフン・アンダースコア |

`; & | < > $ ( )` などは全て弾かれます。
また DNS の仕様上ホスト名の最大長は 253 文字なので `len(value) <= 253` も確認しています。

---

## ブロック 3：ネットワーク情報取得（25〜72行目）

```python
def get_network_info() -> dict:
```

この関数は「IP アドレス・サブネット・デフォルト GW・インターフェース名」を返します。

### 方法 ① netifaces を使う（推奨）

```python
    if HAS_NETIFACES:
        gateways = netifaces.gateways()
        # すべてのルーティング情報を辞書で取得
        # {'default': {AF_INET: ('192.168.10.1', 'en0')}, ...}

        default_gw = gateways.get('default', {})
        if netifaces.AF_INET in default_gw:
            gateway_ip, interface = default_gw[netifaces.AF_INET]
            # AF_INET = IPv4。タプルを分解して GW の IP とインターフェース名を取り出す
```

```python
            iface_addrs = netifaces.ifaddresses(interface)
            # 例: {'en0' の情報} → {AF_INET: [{'addr': '192.168.10.222', 'netmask': '255.255.254.0'}], ...}

            addr = iface_addrs[netifaces.AF_INET][0]
            ip      = addr.get('addr', 'N/A')
            netmask = addr.get('netmask', 'N/A')
```

```python
            net    = ipaddress.IPv4Network(f'{ip}/{netmask}', strict=False)
            subnet = str(net)   # '192.168.10.0/23' のような CIDR 表記に変換
            # strict=False … IP アドレスがネットワークアドレスと一致しなくてもエラーにしない
```

### 方法 ② UDP ソケットのトリック（フォールバック）

```python
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        # 実際にはパケットを送らない。接続先 IP を指定するだけで
        # OS がルーティング情報をもとに「使うべき送信元 IP」をソケットにセットする
        ip = s.getsockname()[0]   # その送信元 IP を取り出す
```

これは「ルーターに向かうパケットがどのインターフェースから出るか」を OS に聞く裏技です。
実際に `8.8.8.8` にはつながらず、サーバーへのアクセスも発生しません。

---

## ブロック 4：Flask アプリの初期化とルート（75〜82行目）

```python
app = Flask(__name__)
# Flask アプリのインスタンスを作成
# __name__ = このファイルのモジュール名（'app'）。テンプレートや静的ファイルの場所の基準になる

@app.route('/')
def index():
    return render_template('index.html')
# ブラウザで http://localhost:5016/ にアクセスすると
# templates/index.html の内容を HTML として返す

@app.route('/api/network-info')
def network_info():
    return jsonify(get_network_info())
# /api/network-info へのアクセスで get_network_info() の結果を JSON で返す
```

---

## ブロック 5：Ping API（85〜108行目）

```python
@app.route('/api/ping', methods=['POST'])
def ping():
    target = (request.json or {}).get('target', '').strip()
    # ブラウザから送られてきた JSON の 'target' キーを取り出す
    # request.json が None（JSON 以外のリクエスト）でも {} で安全にフォールバック
```

```python
    count_flag = '-n' if platform.system() == 'Windows' else '-c'
    cmd = ['ping', count_flag, '4', target]
    # Windows では ping -n 4、macOS/Linux では ping -c 4 になる
    # コマンドをリストで渡すと shell=True 不要 → インジェクションのリスクがさらに下がる
```

```python
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    # capture_output=True … 標準出力・標準エラーをキャプチャ（ターミナルに表示しない）
    # text=True          … bytes ではなく str として受け取る
    # timeout=15         … 15 秒以上かかったら TimeoutExpired 例外を送出
```

```python
    return jsonify({
        'output': result.stdout + result.stderr,  # ping の生テキスト出力
        'returncode': result.returncode,           # 0 = 成功、それ以外 = 失敗
        'success': result.returncode == 0,         # True/False に変換
        'elapsed': round(time.time() - start, 2),  # 全体の実行時間（秒）
    })
```

---

## ブロック 6：DNS API（111〜140行目）

```python
@app.route('/api/dns', methods=['POST'])
def dns():
    domain = (request.json or {}).get('domain', '').strip()
```

```python
    results = socket.getaddrinfo(domain, None)
    # getaddrinfo は DNS 解決 + ソケット情報を返す
    # None はポート番号を指定しないという意味
    # 返り値: [(AF_INET, SOCK_STREAM, 6, '', ('142.251.24.100', 0)), ...]
    #          [0]アドレスファミリ  [4][0] に IP アドレスが入っている
```

```python
    seen: set = set()
    addresses = []
    for r in results:
        addr   = r[4][0]
        family = 'IPv4' if r[0] == socket.AF_INET else 'IPv6'
        if (addr, family) not in seen:
            seen.add((addr, family))
            addresses.append({'address': addr, 'family': family})
    # getaddrinfo は同じアドレスを複数返すことがある（ソケットタイプ違い）
    # set() を使って重複を排除してから結果リストに追加する
```

```python
    return jsonify({
        'domain': domain,
        'addresses': addresses,     # [{address: '...', family: 'IPv4'}, ...]
        'success': True,
        'elapsed_ms': elapsed_ms,   # 応答時間をミリ秒で返す（0.025s → 25ms）
    })
```

例外処理：

```python
    except socket.gaierror as e:
        return jsonify({'error': f'DNS 解決失敗: {e}', 'success': False})
        # gaierror は "getaddrinfo error" の略。存在しないドメインなどで発生する
```

---

## ブロック 7：HTTP チェック API（143〜176行目）

```python
@app.route('/api/http', methods=['POST'])
def http_check():
    url = (request.json or {}).get('url', '').strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    # 'google.com' と入力しても https://google.com として扱う
```

```python
    resp = http_requests.get(
        url,
        timeout=10,
        allow_redirects=True,          # リダイレクト（301/302）を自動で追う
        headers={'User-Agent': 'NetworkDiag/1.0'},
        # User-Agent を設定しないと一部サーバーが接続を拒否することがある
    )
```

```python
    final_url = str(resp.url)   # リダイレクト後の最終 URL
    return jsonify({
        'url': final_url,
        'status_code': resp.status_code,    # 200, 301, 404 など
        'status_text': resp.reason,         # 'OK', 'Not Found' など
        'elapsed_ms': elapsed_ms,           # ミリ秒
        'content_type': resp.headers.get('Content-Type', ''),  # 'text/html; charset=...'
        'server': resp.headers.get('Server', ''),               # 'nginx', 'gws' など
        'redirected': final_url != url,     # リダイレクトが発生したか
        'success': resp.status_code < 400,  # 4xx/5xx はエラー扱い
    })
```

ステータスコードの目安：

| コード | 意味 |
|--------|------|
| 200 | 正常 |
| 301 / 302 | リダイレクト（自動的に追う） |
| 403 | アクセス拒否 |
| 404 | ページが見つからない |
| 5xx | サーバーエラー |

---

## ブロック 8：フロントエンド（JavaScript）の仕組み

`templates/index.html` の JavaScript を解説します。

### ネットワーク情報の自動取得

```javascript
async function loadNetworkInfo() {
    const res = await fetch('/api/network-info');
    // fetch は非同期 HTTP リクエストを送る Web API
    // await を使うことで「レスポンスが来るまで待つ」処理になる

    const d = await res.json();
    // レスポンスボディを JSON として解析し JavaScript オブジェクトに変換

    grid.innerHTML = items.map(item => `<div class="info-card">...</div>`).join('');
    // map でカード HTML の配列を作り、join で1つの文字列に結合して DOM に挿入
}
```

ページ読み込み時に `loadNetworkInfo()` が呼ばれ、サーバーサイドの情報をリアルタイムで表示します。

### 送信処理（Ping を例に）

```javascript
async function runPing() {
    const target = document.getElementById('ping-input').value.trim();
    setLoading('ping-btn', 'ping-result', true);
    // ボタンを無効化してスピナーを表示（二重送信防止）

    const res = await fetch('/api/ping', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ target }),
        // JSON.stringify … { target: '8.8.8.8' } → '{"target":"8.8.8.8"}'
    });

    const d = await res.json();
    if (d.error) {
        el.innerHTML = `<span class="err">エラー: ${escHtml(d.error)}</span>`;
    } else {
        el.innerHTML = `<span class="ok">[成功]</span> ...` + escHtml(d.output);
    }

    setLoading('ping-btn', 'ping-result', false);
    // 完了後にボタンを再び有効化
}
```

### XSS 対策

```javascript
function escHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}
// サーバーから返ってきたテキストをそのまま innerHTML に入れると
// <script>alert('XSS')</script> などが実行されてしまう。
// < > を HTML エンティティに変換することで「テキストとして」表示させる。
```

### Enter キー対応

```javascript
function onEnter(inputId, fn) {
    document.getElementById(inputId).addEventListener('keydown', e => {
        if (e.key === 'Enter') fn();
    });
}
onEnter('ping-input', runPing);
// 入力欄で Enter を押すと runPing() が呼ばれるように登録する
```

---

## 全体の構成まとめ

```
day016_netdiag-web/
├── app.py              ← Flask サーバー（API + ルーティング）
├── requirements.txt    ← 依存パッケージ一覧
└── templates/
    └── index.html      ← HTML + CSS + JavaScript（UI 全体）
```

```
リクエストの流れ

ブラウザ
  │
  ├─ GET /                → render_template('index.html')  HTML を返す
  │
  ├─ GET /api/network-info → get_network_info()  IP/サブネット/GW を返す
  │
  ├─ POST /api/ping        → subprocess.run(['ping', ...])  ping 結果を返す
  │
  ├─ POST /api/dns         → socket.getaddrinfo(...)  アドレス一覧を返す
  │
  └─ POST /api/http        → requests.get(...)  ステータスコード等を返す
```

```
セキュリティの多層防御

ブラウザ入力
  ↓
_safe_host() で正規表現チェック（英数字・ドット・ハイフン以外を弾く）
  ↓
subprocess.run にリスト形式でコマンドを渡す（shell=False → シェル経由しない）
  ↓
escHtml() でレスポンスを HTML エンティティ化（XSS 防止）
```
