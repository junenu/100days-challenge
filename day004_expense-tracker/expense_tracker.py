#!/usr/bin/env python3
"""CLI Expense Tracker — day004 of 100 Days Challenge."""

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

DATA_FILE = Path(__file__).parent / "expenses.csv"
CSV_FIELDS = ["id", "date", "amount", "category", "description"]

CATEGORIES = [
    "food",
    "transport",
    "housing",
    "health",
    "entertainment",
    "shopping",
    "utilities",
    "other",
]

COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "white": "\033[97m",
    "gray": "\033[90m",
}

CATEGORY_COLORS = {
    "food": "green",
    "transport": "cyan",
    "housing": "blue",
    "health": "magenta",
    "entertainment": "yellow",
    "shopping": "red",
    "utilities": "white",
    "other": "gray",
}

BAR_CHAR = "█"
BAR_MAX_WIDTH = 30


# ──────────────────────────────────────────────
# Color helpers
# ──────────────────────────────────────────────


def c(color: str, text: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{COLORS[color]}{text}{COLORS['reset']}"


def bold(text: str) -> str:
    return f"{COLORS['bold']}{text}{COLORS['reset']}"


# ──────────────────────────────────────────────
# Data access (immutable load / pure write)
# ──────────────────────────────────────────────


def load_expenses() -> list[dict]:
    """Load all expenses from CSV and return as a list of dicts."""
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            {
                "id": int(row["id"]),
                "date": row["date"],
                "amount": float(row["amount"]),
                "category": row["category"],
                "description": row["description"],
            }
            for row in reader
        ]


def save_expenses(expenses: list[dict]) -> None:
    """Write the full list of expenses to CSV (pure overwrite)."""
    with DATA_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(expenses)


def next_id(expenses: list[dict]) -> int:
    """Return the next available ID."""
    return max((e["id"] for e in expenses), default=0) + 1


# ──────────────────────────────────────────────
# Core operations (return new list, never mutate)
# ──────────────────────────────────────────────


def add_expense(
    expenses: list[dict],
    amount: float,
    category: str,
    description: str,
    expense_date: str,
) -> list[dict]:
    """Return a new list with the expense appended."""
    new_expense = {
        "id": next_id(expenses),
        "date": expense_date,
        "amount": round(amount, 2),
        "category": category,
        "description": description,
    }
    return expenses + [new_expense]


def delete_expense(expenses: list[dict], expense_id: int) -> tuple[list[dict], bool]:
    """Return (new_list, was_deleted)."""
    new_list = [e for e in expenses if e["id"] != expense_id]
    return new_list, len(new_list) < len(expenses)


def filter_by_month(expenses: list[dict], year: int, month: int) -> list[dict]:
    """Return expenses that match year/month."""
    prefix = f"{year:04d}-{month:02d}"
    return [e for e in expenses if e["date"].startswith(prefix)]


def filter_by_category(expenses: list[dict], category: str) -> list[dict]:
    return [e for e in expenses if e["category"] == category]


# ──────────────────────────────────────────────
# Display helpers
# ──────────────────────────────────────────────


def format_amount(amount: float) -> str:
    return f"¥{amount:,.0f}"


def category_bar(category: str, amount: float, max_amount: float) -> str:
    width = int(BAR_MAX_WIDTH * amount / max_amount) if max_amount > 0 else 0
    bar = BAR_CHAR * width
    color = CATEGORY_COLORS.get(category, "white")
    return c(color, bar)


def print_expense_table(expenses: list[dict]) -> None:
    if not expenses:
        print(c("gray", "  (no expenses)"))
        return

    header = f"  {'ID':>4}  {'Date':<12}  {'Amount':>10}  {'Category':<14}  Description"
    print(c("bold", header))
    print(c("gray", "  " + "─" * 64))

    for e in sorted(expenses, key=lambda x: x["date"]):
        color = CATEGORY_COLORS.get(e["category"], "white")
        cat_str = c(color, f"{e['category']:<14}")
        amount_str = c("green", f"{format_amount(e['amount']):>10}")
        print(f"  {e['id']:>4}  {e['date']:<12}  {amount_str}  {cat_str}  {e['description']}")


def print_summary_chart(expenses: list[dict], label: str) -> None:
    if not expenses:
        print(c("gray", "  データがありません"))
        return

    totals: dict[str, float] = defaultdict(float)
    for e in expenses:
        totals[e["category"]] += e["amount"]

    total_all = sum(totals.values())
    max_amount = max(totals.values())

    print(bold(f"\n  {label} — 合計: {c('green', format_amount(total_all))}"))
    print(c("gray", "  " + "─" * 55))

    for cat in sorted(totals, key=lambda k: totals[k], reverse=True):
        amt = totals[cat]
        pct = 100 * amt / total_all if total_all else 0
        bar = category_bar(cat, amt, max_amount)
        color = CATEGORY_COLORS.get(cat, "white")
        print(
            f"  {c(color, f'{cat:<14}')}  {bar:<{BAR_MAX_WIDTH}}  "
            f"{c('green', format_amount(amt)):>12}  {c('gray', f'{pct:5.1f}%')}"
        )


# ──────────────────────────────────────────────
# Input helpers
# ──────────────────────────────────────────────


def prompt(text: str, default: str = "") -> str:
    """Read user input, returning default if blank."""
    display = f"  {text}"
    if default:
        display += f" [{default}]"
    display += ": "
    value = input(display).strip()
    return value if value else default


def prompt_amount() -> float:
    """Prompt for a valid positive amount."""
    while True:
        raw = prompt("金額 (例: 1200)")
        try:
            amount = float(raw.replace(",", "").replace("¥", ""))
            if amount <= 0:
                raise ValueError
            return amount
        except ValueError:
            print(c("red", "  有効な正の数値を入力してください"))


def prompt_category() -> str:
    """Prompt for a valid category."""
    cats = "  " + "  ".join(
        c(CATEGORY_COLORS.get(cat, "white"), f"{i+1}.{cat}")
        for i, cat in enumerate(CATEGORIES)
    )
    print(cats)
    while True:
        raw = prompt("カテゴリ (番号 or 名前)", default="other")
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(CATEGORIES):
                return CATEGORIES[idx]
        if raw.lower() in CATEGORIES:
            return raw.lower()
        print(c("red", f"  無効なカテゴリです。1〜{len(CATEGORIES)} または名前を入力してください"))


def prompt_date() -> str:
    """Prompt for a date, defaulting to today."""
    today = date.today().isoformat()
    while True:
        raw = prompt("日付 (YYYY-MM-DD)", default=today)
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print(c("red", "  YYYY-MM-DD 形式で入力してください"))


# ──────────────────────────────────────────────
# Commands
# ──────────────────────────────────────────────


def cmd_add() -> None:
    print(bold("\n  ── 支出を追加 ──"))
    amount = prompt_amount()
    print(c("gray", "  カテゴリを選択:"))
    category = prompt_category()
    description = prompt("説明 (任意)", default="")
    expense_date = prompt_date()

    expenses = load_expenses()
    updated = add_expense(expenses, amount, category, description, expense_date)
    save_expenses(updated)

    new_id = updated[-1]["id"]
    print(
        c("green", f"\n  追加しました → ID:{new_id}  {format_amount(amount)}  "
          f"[{category}]  {expense_date}")
    )


def cmd_list(args: list[str]) -> None:
    expenses = load_expenses()

    # Optional filter: --month YYYY-MM or --cat CATEGORY
    if "--month" in args:
        idx = args.index("--month")
        if idx + 1 < len(args):
            try:
                y, m = map(int, args[idx + 1].split("-"))
                expenses = filter_by_month(expenses, y, m)
                print(bold(f"\n  ── {y:04d}-{m:02d} の支出一覧 ──"))
            except ValueError:
                print(c("red", "  --month には YYYY-MM 形式を指定してください"))
                return
    elif "--cat" in args:
        idx = args.index("--cat")
        if idx + 1 < len(args):
            cat = args[idx + 1].lower()
            if cat not in CATEGORIES:
                print(c("red", f"  未知のカテゴリ: {cat}"))
                return
            expenses = filter_by_category(expenses, cat)
            print(bold(f"\n  ── [{cat}] の支出一覧 ──"))
    else:
        print(bold("\n  ── 全支出一覧 ──"))

    print_expense_table(expenses)

    if expenses:
        total = sum(e["amount"] for e in expenses)
        print(c("gray", "  " + "─" * 64))
        print(f"  {'合計':>40}  {c('green', format_amount(total)):>10}")


def cmd_delete(args: list[str]) -> None:
    if not args:
        print(c("red", "  使い方: delete <ID>"))
        return
    try:
        expense_id = int(args[0])
    except ValueError:
        print(c("red", "  ID は整数で指定してください"))
        return

    expenses = load_expenses()
    updated, deleted = delete_expense(expenses, expense_id)
    if deleted:
        save_expenses(updated)
        print(c("green", f"  ID:{expense_id} を削除しました"))
    else:
        print(c("red", f"  ID:{expense_id} が見つかりません"))


def cmd_summary(args: list[str]) -> None:
    expenses = load_expenses()
    today = date.today()

    if "--month" in args:
        idx = args.index("--month")
        if idx + 1 < len(args):
            try:
                y, m = map(int, args[idx + 1].split("-"))
                target = filter_by_month(expenses, y, m)
                print_summary_chart(target, f"{y:04d}-{m:02d} 月次サマリー")
                return
            except ValueError:
                print(c("red", "  --month には YYYY-MM 形式を指定してください"))
                return

    # Default: current month
    this_month = filter_by_month(expenses, today.year, today.month)
    print_summary_chart(this_month, f"{today.year:04d}-{today.month:02d} 今月のサマリー")

    # Year-to-date
    ytd = [e for e in expenses if e["date"].startswith(str(today.year))]
    print_summary_chart(ytd, f"{today.year:04d} 年間サマリー")


def cmd_help() -> None:
    print(bold("\n  ── Expense Tracker ──"))
    print(c("gray", "  毎日の支出を記録・集計する CLI 家計簿\n"))
    print(bold("  コマンド:"))
    cmds = [
        ("add", "支出を追加（対話式）"),
        ("list", "支出一覧を表示"),
        ("list --month YYYY-MM", "特定月の支出を表示"),
        ("list --cat CATEGORY", "カテゴリ別に絞り込み"),
        ("delete <ID>", "指定 ID の支出を削除"),
        ("summary", "今月 / 年間のカテゴリ別グラフ"),
        ("summary --month YYYY-MM", "特定月のサマリーを表示"),
        ("help", "このヘルプを表示"),
    ]
    for cmd, desc in cmds:
        print(f"  {c('cyan', f'python expense_tracker.py {cmd}'):<55}  {desc}")

    print(bold("\n  カテゴリ:"))
    for cat in CATEGORIES:
        color = CATEGORY_COLORS.get(cat, "white")
        print(f"    {c(color, cat)}")
    print()


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────


def main() -> None:
    args = sys.argv[1:]
    command = args[0].lower() if args else "help"
    rest = args[1:]

    dispatch = {
        "add": lambda: cmd_add(),
        "list": lambda: cmd_list(rest),
        "delete": lambda: cmd_delete(rest),
        "summary": lambda: cmd_summary(rest),
        "help": lambda: cmd_help(),
    }

    if command in dispatch:
        dispatch[command]()
    else:
        print(c("red", f"  未知のコマンド: {command}"))
        cmd_help()


if __name__ == "__main__":
    main()
