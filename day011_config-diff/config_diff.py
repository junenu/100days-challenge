#!/usr/bin/env python3
"""ネットワーク設定差分可視化ツール — Cisco/Juniper 設定ファイルをセクション単位で比較する。"""

import difflib
import json
import sys
import textwrap
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Literal

# ANSI カラー
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

Status = Literal["added", "removed", "changed", "unchanged"]

_STATUS_COLOR = {"added": GREEN, "removed": RED, "changed": YELLOW, "unchanged": DIM}
_STATUS_LABEL = {"added": "[+]", "removed": "[-]", "changed": "[~]", "unchanged": "[ ]"}


# ---------------------------------------------------------------------------
# データ型
# ---------------------------------------------------------------------------

@dataclass
class Section:
    name: str
    lines: list[str] = field(default_factory=list)


@dataclass
class SectionDiff:
    name: str
    status: Status
    before_lines: list[str]
    after_lines: list[str]
    unified_diff: list[str]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "before_lines": self.before_lines,
            "after_lines": self.after_lines,
            "unified_diff": self.unified_diff,
        }


# ---------------------------------------------------------------------------
# パーサー
# ---------------------------------------------------------------------------

def parse_sections(text: str) -> dict[str, Section]:
    """設定テキストをセクション単位（行頭が空白でない行をヘッダーとして）に分割する。"""
    sections: dict[str, Section] = {}
    current: Section | None = None

    for raw in text.splitlines():
        line = raw.rstrip()

        # 空行・コメント行は現在のセクションに付属させる
        if not line or line.startswith("!") or line.startswith("#"):
            if current is not None:
                current.lines.append(line)
            continue

        if not line[0].isspace():
            # 新しいセクションヘッダー
            current = Section(name=line)
            sections[line] = current
        elif current is not None:
            current.lines.append(line)

    return sections


# ---------------------------------------------------------------------------
# 差分計算
# ---------------------------------------------------------------------------

def diff_sections(
    before: dict[str, Section],
    after: dict[str, Section],
    filter_keyword: str | None = None,
) -> list[SectionDiff]:
    """2 つのセクション辞書を比較してセクション差分リストを返す。"""
    all_names = sorted(set(before) | set(after))
    results: list[SectionDiff] = []

    for name in all_names:
        if filter_keyword and filter_keyword.lower() not in name.lower():
            continue

        b_lines = [name] + (before[name].lines if name in before else [])
        a_lines = [name] + (after[name].lines if name in after else [])

        if name not in before:
            status: Status = "added"
        elif name not in after:
            status = "removed"
        elif b_lines == a_lines:
            status = "unchanged"
        else:
            status = "changed"

        unified = (
            list(difflib.unified_diff(b_lines, a_lines, fromfile="before", tofile="after", lineterm=""))
            if status != "unchanged"
            else []
        )

        results.append(SectionDiff(
            name=name,
            status=status,
            before_lines=b_lines,
            after_lines=a_lines,
            unified_diff=unified,
        ))

    return results


# ---------------------------------------------------------------------------
# CLI 出力
# ---------------------------------------------------------------------------

def print_cli(diffs: list[SectionDiff], show_unchanged: bool = False) -> None:
    print(f"{BOLD}{CYAN}")
    print("╔══════════════════════════════════════════╗")
    print("║      Config Diff Visualizer              ║")
    print("╚══════════════════════════════════════════╝")
    print(RESET)

    summary: dict[str, int] = {"added": 0, "removed": 0, "changed": 0, "unchanged": 0}
    for d in diffs:
        summary[d.status] += 1

    print(f"  {GREEN}+ 追加{RESET}  {RED}- 削除{RESET}  {YELLOW}~ 変更{RESET}  {DIM}= 変更なし{RESET}\n")
    print(
        f"  セクション数: 全 {len(diffs)} 件  "
        f"{GREEN}追加:{summary['added']}{RESET}  "
        f"{RED}削除:{summary['removed']}{RESET}  "
        f"{YELLOW}変更:{summary['changed']}{RESET}  "
        f"{DIM}変更なし:{summary['unchanged']}{RESET}\n"
    )
    print("─" * 60)

    target = diffs if show_unchanged else [d for d in diffs if d.status != "unchanged"]

    if not target:
        print(f"\n{GREEN}{BOLD}✓ 差分なし — 設定は完全に一致しています。{RESET}")
        return

    for diff in target:
        color = _STATUS_COLOR[diff.status]
        label = _STATUS_LABEL[diff.status]
        print(f"\n{color}{BOLD}{label} {diff.name}{RESET}")

        for line in diff.unified_diff[2:]:  # --- +++ ヘッダーをスキップ
            if line.startswith("+"):
                print(f"    {GREEN}{line}{RESET}")
            elif line.startswith("-"):
                print(f"    {RED}{line}{RESET}")
            elif line.startswith("@@"):
                print(f"    {CYAN}{line}{RESET}")
            else:
                print(f"    {DIM}{line}{RESET}")


# ---------------------------------------------------------------------------
# Web UI (組み込み HTTP サーバー)
# ---------------------------------------------------------------------------

_HTML = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Config Diff Visualizer</title>
<style>
  :root {
    --bg: #1e1e2e;
    --surface: #181825;
    --surface2: #313244;
    --text: #cdd6f4;
    --subtext: #a6adc8;
    --green: #a6e3a1;
    --red: #f38ba8;
    --yellow: #f9e2af;
    --blue: #89b4fa;
    --cyan: #89dceb;
    --gray: #6c7086;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Consolas', 'Menlo', monospace; font-size: 13px; min-height: 100vh; }

  header { background: var(--surface); border-bottom: 1px solid var(--surface2); padding: 14px 24px; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 16px; font-weight: 700; color: var(--blue); }
  header span { color: var(--subtext); font-size: 12px; }

  .container { padding: 20px 24px; max-width: 1400px; margin: 0 auto; }

  /* Input area */
  .input-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .input-box label { display: block; margin-bottom: 6px; color: var(--subtext); font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; }
  .input-box textarea {
    width: 100%; height: 200px; background: var(--surface); border: 1px solid var(--surface2);
    border-radius: 6px; color: var(--text); padding: 10px; font-family: inherit; font-size: 12px;
    resize: vertical; outline: none; transition: border-color 0.2s;
  }
  .input-box textarea:focus { border-color: var(--blue); }

  .controls { display: flex; gap: 10px; margin-bottom: 20px; align-items: center; }
  .controls input {
    flex: 1; background: var(--surface); border: 1px solid var(--surface2); border-radius: 6px;
    color: var(--text); padding: 8px 12px; font-family: inherit; font-size: 12px; outline: none;
  }
  .controls input:focus { border-color: var(--blue); }
  .controls input::placeholder { color: var(--gray); }
  .btn { background: var(--blue); color: var(--bg); border: none; border-radius: 6px; padding: 8px 20px; font-weight: 700; cursor: pointer; font-size: 13px; }
  .btn:hover { opacity: 0.85; }
  .btn-ghost { background: var(--surface2); color: var(--text); }

  /* Summary */
  .summary { display: flex; gap: 16px; margin-bottom: 16px; padding: 12px 16px; background: var(--surface); border-radius: 8px; border: 1px solid var(--surface2); }
  .summary-item { display: flex; align-items: center; gap: 6px; font-size: 12px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; }
  .badge-added { background: rgba(166,227,161,0.15); color: var(--green); }
  .badge-removed { background: rgba(243,139,168,0.15); color: var(--red); }
  .badge-changed { background: rgba(249,226,175,0.15); color: var(--yellow); }
  .badge-unchanged { background: rgba(108,112,134,0.15); color: var(--gray); }

  /* Results layout */
  .results-grid { display: grid; grid-template-columns: 260px 1fr; gap: 16px; }

  /* Section list */
  .section-list { background: var(--surface); border: 1px solid var(--surface2); border-radius: 8px; overflow: hidden; }
  .section-list-header { padding: 10px 14px; background: var(--surface2); font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--subtext); }
  .section-item { padding: 8px 14px; cursor: pointer; border-bottom: 1px solid var(--surface2); display: flex; align-items: center; gap: 8px; transition: background 0.15s; }
  .section-item:last-child { border-bottom: none; }
  .section-item:hover { background: var(--surface2); }
  .section-item.active { background: rgba(137,180,250,0.1); border-left: 3px solid var(--blue); }
  .section-name { flex: 1; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .dot-added { background: var(--green); }
  .dot-removed { background: var(--red); }
  .dot-changed { background: var(--yellow); }
  .dot-unchanged { background: var(--gray); }

  /* Diff view */
  .diff-panel { background: var(--surface); border: 1px solid var(--surface2); border-radius: 8px; overflow: hidden; }
  .diff-panel-header { padding: 10px 16px; background: var(--surface2); display: flex; align-items: center; gap: 10px; }
  .diff-panel-title { font-size: 12px; font-weight: 700; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .diff-mode-btns { display: flex; gap: 4px; }
  .mode-btn { background: var(--surface); border: 1px solid var(--surface2); color: var(--subtext); padding: 3px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; font-family: inherit; }
  .mode-btn.active { background: var(--blue); color: var(--bg); border-color: var(--blue); font-weight: 700; }

  .diff-content { padding: 0; overflow-x: auto; }
  .diff-table { width: 100%; border-collapse: collapse; font-size: 12px; }
  .diff-table td { padding: 2px 12px; white-space: pre; vertical-align: top; }
  .diff-table .ln { color: var(--gray); user-select: none; width: 40px; text-align: right; padding-right: 8px; border-right: 1px solid var(--surface2); }
  .line-added { background: rgba(166,227,161,0.1); color: var(--green); }
  .line-removed { background: rgba(243,139,168,0.1); color: var(--red); }
  .line-hunk { background: rgba(137,222,235,0.08); color: var(--cyan); font-style: italic; }
  .line-context { color: var(--subtext); }

  /* Side-by-side */
  .side-by-side { display: grid; grid-template-columns: 1fr 1fr; }
  .side-panel { overflow-x: auto; }
  .side-panel + .side-panel { border-left: 1px solid var(--surface2); }
  .side-label { padding: 6px 12px; background: var(--surface2); font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--subtext); }

  .empty-state { padding: 40px; text-align: center; color: var(--gray); font-size: 13px; }
  #results { display: none; }
</style>
</head>
<body>
<header>
  <h1>⚙ Config Diff Visualizer</h1>
  <span>Cisco / Juniper ネットワーク設定 差分ビューワー</span>
</header>

<div class="container">
  <div class="input-grid">
    <div class="input-box">
      <label>Before（変更前の設定）</label>
      <textarea id="before" placeholder="変更前の設定ファイルを貼り付け..."></textarea>
    </div>
    <div class="input-box">
      <label>After（変更後の設定）</label>
      <textarea id="after" placeholder="変更後の設定ファイルを貼り付け..."></textarea>
    </div>
  </div>

  <div class="controls">
    <input id="filter" placeholder="セクションフィルター（例: acl, route-map, interface, ospf）">
    <button class="btn" onclick="compare()">比較する</button>
    <button class="btn btn-ghost" onclick="loadSample()">サンプルを読み込む</button>
  </div>

  <div id="results">
    <div class="summary" id="summary"></div>
    <div class="results-grid">
      <div>
        <div class="section-list" id="section-list"></div>
      </div>
      <div class="diff-panel" id="diff-panel">
        <div class="diff-panel-header">
          <span class="diff-panel-title" id="diff-title">セクションを選択してください</span>
          <div class="diff-mode-btns">
            <button class="mode-btn active" id="btn-unified" onclick="setMode('unified')">unified</button>
            <button class="mode-btn" id="btn-side" onclick="setMode('side')">side-by-side</button>
          </div>
        </div>
        <div class="diff-content" id="diff-content">
          <div class="empty-state">← 左のセクションリストからセクションを選択</div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
let _diffs = [];
let _activeIdx = -1;
let _mode = 'unified';

async function compare() {
  const before = document.getElementById('before').value.trim();
  const after = document.getElementById('after').value.trim();
  const filter = document.getElementById('filter').value.trim();

  if (!before && !after) {
    alert('設定テキストを入力してください。');
    return;
  }

  const res = await fetch('/api/diff', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ before, after, filter }),
  });

  const data = await res.json();
  _diffs = data.diffs;
  _activeIdx = -1;
  renderResults();
}

function renderResults() {
  const results = document.getElementById('results');
  results.style.display = 'block';

  // Summary
  const cnt = { added: 0, removed: 0, changed: 0, unchanged: 0 };
  for (const d of _diffs) cnt[d.status]++;

  document.getElementById('summary').innerHTML = `
    <div class="summary-item">セクション合計: <strong>${_diffs.length}</strong></div>
    <div class="summary-item"><span class="badge badge-added">+ 追加</span> <strong>${cnt.added}</strong></div>
    <div class="summary-item"><span class="badge badge-removed">- 削除</span> <strong>${cnt.removed}</strong></div>
    <div class="summary-item"><span class="badge badge-changed">~ 変更</span> <strong>${cnt.changed}</strong></div>
    <div class="summary-item"><span class="badge badge-unchanged">= 変更なし</span> <strong>${cnt.unchanged}</strong></div>
  `;

  // Section list
  const list = document.getElementById('section-list');
  if (_diffs.length === 0) {
    list.innerHTML = '<div class="empty-state">セクションなし</div>';
    return;
  }

  list.innerHTML = '<div class="section-list-header">セクション一覧</div>' +
    _diffs.map((d, i) => `
      <div class="section-item ${i === _activeIdx ? 'active' : ''}" onclick="selectSection(${i})">
        <div class="dot dot-${d.status}"></div>
        <span class="section-name" title="${esc(d.name)}">${esc(d.name)}</span>
      </div>
    `).join('');

  // 最初の差分があるセクションを自動選択
  const firstChanged = _diffs.findIndex(d => d.status !== 'unchanged');
  if (firstChanged >= 0) selectSection(firstChanged);
}

function selectSection(idx) {
  _activeIdx = idx;

  // section-list のアクティブ更新
  document.querySelectorAll('.section-item').forEach((el, i) => {
    el.classList.toggle('active', i === idx);
  });

  const diff = _diffs[idx];
  document.getElementById('diff-title').textContent = diff.name;
  renderDiff(diff);
}

function setMode(mode) {
  _mode = mode;
  document.getElementById('btn-unified').classList.toggle('active', mode === 'unified');
  document.getElementById('btn-side').classList.toggle('active', mode === 'side');
  if (_activeIdx >= 0) renderDiff(_diffs[_activeIdx]);
}

function renderDiff(diff) {
  const content = document.getElementById('diff-content');

  if (diff.status === 'unchanged') {
    content.innerHTML = `<div class="empty-state" style="color:var(--gray)">✓ このセクションに変更はありません</div>`;
    return;
  }

  if (_mode === 'unified') {
    content.innerHTML = renderUnified(diff);
  } else {
    content.innerHTML = renderSideBySide(diff);
  }
}

function renderUnified(diff) {
  if (diff.unified_diff.length === 0) return '<div class="empty-state">差分データなし</div>';

  const rows = diff.unified_diff.slice(2).map((line, i) => {
    let cls = 'line-context';
    if (line.startsWith('+')) cls = 'line-added';
    else if (line.startsWith('-')) cls = 'line-removed';
    else if (line.startsWith('@@')) cls = 'line-hunk';
    return `<tr class="${cls}"><td class="ln">${i + 1}</td><td>${esc(line)}</td></tr>`;
  }).join('');

  return `<table class="diff-table"><tbody>${rows}</tbody></table>`;
}

function renderSideBySide(diff) {
  const before = diff.before_lines;
  const after = diff.after_lines;

  const bRows = before.map((line, i) => {
    const inAfter = after.includes(line);
    const cls = inAfter ? 'line-context' : 'line-removed';
    return `<tr class="${cls}"><td class="ln">${i + 1}</td><td>${esc(line)}</td></tr>`;
  }).join('');

  const aRows = after.map((line, i) => {
    const inBefore = before.includes(line);
    const cls = inBefore ? 'line-context' : 'line-added';
    return `<tr class="${cls}"><td class="ln">${i + 1}</td><td>${esc(line)}</td></tr>`;
  }).join('');

  return `
    <div class="side-by-side">
      <div class="side-panel">
        <div class="side-label">Before</div>
        <table class="diff-table"><tbody>${bRows}</tbody></table>
      </div>
      <div class="side-panel">
        <div class="side-label">After</div>
        <table class="diff-table"><tbody>${aRows}</tbody></table>
      </div>
    </div>
  `;
}

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function loadSample() {
  document.getElementById('before').value = SAMPLE_BEFORE;
  document.getElementById('after').value = SAMPLE_AFTER;
}

const SAMPLE_BEFORE = `!
hostname Router-A
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.252
 no shutdown
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
!
ip access-list extended PERMIT-WEB
 permit tcp any any eq 80
 permit tcp any any eq 443
!
route-map POLICY permit 10
 match ip address PERMIT-WEB
 set local-preference 100
!`;

const SAMPLE_AFTER = `!
hostname Router-A
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 ip helper-address 10.0.0.10
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.252
 no shutdown
!
interface Loopback0
 ip address 172.16.0.1 255.255.255.255
!
router ospf 1
 router-id 172.16.0.1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
 network 172.16.0.1 0.0.0.0 area 0
!
ip access-list extended PERMIT-WEB
 permit tcp any any eq 80
 permit tcp any any eq 443
 permit tcp any any eq 8080
!
route-map POLICY permit 10
 match ip address PERMIT-WEB
 set local-preference 150
!`;
</script>
</body>
</html>
"""


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 標準ログを抑制

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = _HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/api/diff":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        before_text: str = body.get("before", "")
        after_text: str = body.get("after", "")
        filter_kw: str | None = body.get("filter") or None

        before_secs = parse_sections(before_text)
        after_secs = parse_sections(after_text)
        diffs = diff_sections(before_secs, after_secs, filter_kw)

        resp = json.dumps({"diffs": [d.to_dict() for d in diffs]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)


def serve(port: int = 8011) -> None:
    server = HTTPServer(("127.0.0.1", port), _Handler)
    print(f"{BOLD}{CYAN}Config Diff Visualizer{RESET} — http://127.0.0.1:{port}/")
    print("終了: Ctrl+C\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{DIM}サーバーを停止しました。{RESET}")


# ---------------------------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------------------------

def _usage() -> None:
    print(textwrap.dedent(f"""\
        {BOLD}使い方:{RESET}
          python config_diff.py <before.cfg> <after.cfg>          # CLI 差分表示
          python config_diff.py <before.cfg> <after.cfg> --filter acl   # セクションフィルター
          python config_diff.py <before.cfg> <after.cfg> --all    # 変更なしセクションも表示
          python config_diff.py --web                             # Web UI (ポート 8011)
          python config_diff.py --web --port 9000                 # ポート指定

        {BOLD}例:{RESET}
          python config_diff.py before.cfg after.cfg
          python config_diff.py before.cfg after.cfg --filter route-map
          python config_diff.py --web
    """))


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--web" in args:
        port_idx = args.index("--port") + 1 if "--port" in args else -1
        port = int(args[port_idx]) if port_idx > 0 else 8011
        serve(port)
        sys.exit(0)

    if len(args) < 2:
        _usage()
        sys.exit(1)

    before_path = Path(args[0])
    after_path = Path(args[1])

    for p in (before_path, after_path):
        if not p.exists():
            print(f"{RED}ファイルが見つかりません: {p}{RESET}", file=sys.stderr)
            sys.exit(1)

    filter_kw: str | None = None
    if "--filter" in args:
        idx = args.index("--filter") + 1
        if idx < len(args):
            filter_kw = args[idx]

    show_unchanged = "--all" in args

    before_secs = parse_sections(before_path.read_text(encoding="utf-8"))
    after_secs = parse_sections(after_path.read_text(encoding="utf-8"))
    diffs = diff_sections(before_secs, after_secs, filter_kw)
    print_cli(diffs, show_unchanged)
