#!/usr/bin/env python3
"""JSON差分比較ツール — 2つのJSONファイルを比較して差分を色付きで表示する。"""

import json
import sys
from pathlib import Path
from typing import Any

# ANSI カラーコード
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def _fmt_value(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _diff(
    left: Any,
    right: Any,
    path: str = "",
    lines: list[str] | None = None,
) -> list[str]:
    if lines is None:
        lines = []

    label = f"{DIM}{path}{RESET}" if path else "(root)"

    if type(left) != type(right) and not (
        isinstance(left, (int, float)) and isinstance(right, (int, float))
    ):
        lines.append(
            f"{YELLOW}~ {label}{RESET}  "
            f"{RED}- {_fmt_value(left)}{RESET}  →  "
            f"{GREEN}+ {_fmt_value(right)}{RESET}"
        )
        return lines

    if isinstance(left, dict) and isinstance(right, dict):
        all_keys = sorted(set(left) | set(right))
        for key in all_keys:
            child_path = f"{path}.{key}" if path else key
            if key not in left:
                lines.append(f"{GREEN}+ {child_path}: {_fmt_value(right[key])}{RESET}")
            elif key not in right:
                lines.append(f"{RED}- {child_path}: {_fmt_value(left[key])}{RESET}")
            else:
                _diff(left[key], right[key], child_path, lines)

    elif isinstance(left, list) and isinstance(right, list):
        max_len = max(len(left), len(right))
        for i in range(max_len):
            child_path = f"{path}[{i}]"
            if i >= len(left):
                lines.append(f"{GREEN}+ {child_path}: {_fmt_value(right[i])}{RESET}")
            elif i >= len(right):
                lines.append(f"{RED}- {child_path}: {_fmt_value(left[i])}{RESET}")
            else:
                _diff(left[i], right[i], child_path, lines)

    else:
        if left != right:
            lines.append(
                f"{YELLOW}~ {label}{RESET}  "
                f"{RED}- {_fmt_value(left)}{RESET}  →  "
                f"{GREEN}+ {_fmt_value(right)}{RESET}"
            )

    return lines


def _load(path_or_text: str) -> Any:
    p = Path(path_or_text)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(path_or_text)


def _print_banner() -> None:
    print(f"{BOLD}{CYAN}")
    print("╔══════════════════════════════╗")
    print("║   JSON Diff Comparator 🔍    ║")
    print("╚══════════════════════════════╝")
    print(RESET)


def _print_legend() -> None:
    print(
        f"  {GREEN}+{RESET} 追加   {RED}-{RESET} 削除   {YELLOW}~{RESET} 変更\n"
    )


def compare(left_src: str, right_src: str) -> None:
    try:
        left = _load(left_src)
        right = _load(right_src)
    except json.JSONDecodeError as e:
        print(f"{RED}JSON parse error: {e}{RESET}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"{RED}File not found: {e}{RESET}", file=sys.stderr)
        sys.exit(1)

    _print_banner()
    _print_legend()

    diffs = _diff(left, right)

    if not diffs:
        print(f"{GREEN}{BOLD}✓ 差分なし — 2つの JSON は完全に一致しています。{RESET}")
    else:
        print(f"{BOLD}差分 ({len(diffs)} 件):{RESET}")
        print()
        for line in diffs:
            print(f"  {line}")
        print()
        print(f"{BOLD}合計: {len(diffs)} 件の差分{RESET}")


def _usage() -> None:
    print(
        f"{BOLD}使い方:{RESET}\n"
        "  python json_diff.py <file1.json> <file2.json>\n"
        "  python json_diff.py '<json1>' '<json2>'\n\n"
        f"{BOLD}例:{RESET}\n"
        "  python json_diff.py a.json b.json\n"
        '  python json_diff.py \'{"a":1}\' \'{"a":2}\''
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        _usage()
        sys.exit(1)

    compare(sys.argv[1], sys.argv[2])
