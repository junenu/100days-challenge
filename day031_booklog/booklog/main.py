#!/usr/bin/env python3
"""booklog — PostgreSQL backed reading tracker CLI."""

import argparse
import sys

from .db import connect, migrate
from .commands import cmd_add, cmd_list, cmd_review, cmd_show, cmd_delete, cmd_stats

VALID_STATUSES = ("want", "reading", "read")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="booklog",
        description="PostgreSQL で本を管理する読書ログ CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="本を追加する")
    p_add.add_argument("title", help="タイトル")
    p_add.add_argument("author", help="著者名")
    p_add.add_argument("--genre", "-g", help="ジャンル")
    p_add.add_argument("--pages", "-p", type=int, help="ページ数")
    p_add.add_argument(
        "--status", "-s", choices=VALID_STATUSES, default="want", help="読書状態 (デフォルト: want)"
    )

    # list
    p_list = sub.add_parser("list", help="本一覧を表示する")
    p_list.add_argument("--status", "-s", choices=VALID_STATUSES, help="絞り込み: 読書状態")
    p_list.add_argument("--genre", "-g", help="絞り込み: ジャンル（部分一致）")

    # show
    p_show = sub.add_parser("show", help="本の詳細を表示する")
    p_show.add_argument("id", type=int, help="本の ID")

    # review
    p_review = sub.add_parser("review", help="評価・メモ・状態を更新する")
    p_review.add_argument("id", type=int, help="本の ID")
    p_review.add_argument("--rating", "-r", type=int, choices=range(1, 6), metavar="1-5", help="評価")
    p_review.add_argument("--notes", "-n", help="メモ")
    p_review.add_argument("--status", "-s", choices=VALID_STATUSES, help="読書状態")

    # delete
    p_delete = sub.add_parser("delete", help="本を削除する")
    p_delete.add_argument("id", type=int, help="本の ID")

    # stats
    sub.add_parser("stats", help="読書統計を表示する")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    conn = connect()
    migrate(conn)

    try:
        if args.command == "add":
            cmd_add(conn, args.title, args.author, args.genre, args.pages, args.status)
        elif args.command == "list":
            cmd_list(conn, args.status, args.genre)
        elif args.command == "show":
            cmd_show(conn, args.id)
        elif args.command == "review":
            cmd_review(conn, args.id, args.rating, args.notes, args.status)
        elif args.command == "delete":
            cmd_delete(conn, args.id)
        elif args.command == "stats":
            cmd_stats(conn)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
