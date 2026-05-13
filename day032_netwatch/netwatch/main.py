#!/usr/bin/env python3
"""netwatch — ネットワーク監視 CLI"""
from __future__ import annotations
import sys
import time
import uuid
import argparse

from .db import init_db
from . import models, monitor, report


def cmd_add(args: argparse.Namespace) -> None:
    try:
        host = models.add_host(args.address, args.name)
        report.console.print(f"[green]追加:[/green] {host['name']} ({host['address']})")
    except ValueError as e:
        report.console.print(f"[yellow]{e}[/yellow]")


def cmd_remove(args: argparse.Namespace) -> None:
    if models.remove_host(args.address):
        report.console.print(f"[green]削除:[/green] {args.address}")
    else:
        report.console.print(f"[red]見つかりません:[/red] {args.address}")


def cmd_list(_: argparse.Namespace) -> None:
    report.print_hosts(models.get_hosts())


def cmd_ping(args: argparse.Namespace) -> None:
    hosts = _resolve_hosts(args.target)
    if not hosts:
        return
    for h in hosts:
        success, rtt_ms = monitor.ping_host(h["address"], count=args.count)
        models.save_ping(h["id"], success, rtt_ms)
        report.print_ping_result(h["address"], success, rtt_ms)


def cmd_watch(args: argparse.Namespace) -> None:
    report.console.print(
        f"[bold]定期監視開始[/bold]  間隔: {args.interval} 秒  Ctrl+C で停止"
    )
    try:
        while True:
            hosts = models.get_hosts()
            if not hosts:
                report.console.print("[yellow]監視ホストがありません[/yellow]")
            else:
                report.console.rule(style="dim")
                for h in hosts:
                    success, rtt_ms = monitor.ping_host(h["address"])
                    models.save_ping(h["id"], success, rtt_ms)
                    report.print_ping_result(h["address"], success, rtt_ms)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        report.console.print("\n[dim]監視を停止しました[/dim]")


def cmd_report(args: argparse.Namespace) -> None:
    hosts = _resolve_hosts(args.target) if args.target else models.get_hosts()
    if not hosts:
        return
    for h in hosts:
        stats = models.get_ping_stats(h["id"], limit=args.limit)
        report.print_ping_stats(h, stats)


def cmd_trace(args: argparse.Namespace) -> None:
    hosts = _resolve_hosts(args.target)
    if not hosts:
        return
    for h in hosts:
        report.console.print(f"[bold]traceroute:[/bold] {h['address']} ...")
        hops = monitor.traceroute_host(h["address"], max_hops=args.max_hops)
        if hops:
            trace_id = str(uuid.uuid4())
            models.save_traceroute_hops(h["id"], trace_id, hops)
        saved = models.get_latest_traceroute(h["id"])
        report.print_traceroute(h, saved)


def _resolve_hosts(target: str) -> list[dict]:
    if target == "all":
        hosts = models.get_hosts()
        if not hosts:
            report.console.print("[yellow]監視ホストがありません[/yellow]")
        return hosts
    host = models.get_host_by_address(target)
    if not host:
        report.console.print(
            f"[red]未登録:[/red] {target}  先に `netwatch add {target}` を実行してください"
        )
        return []
    return [host]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netwatch",
        description="ネットワーク監視 CLI — ping/traceroute 結果を PostgreSQL に記録",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # add
    p_add = sub.add_parser("add", help="監視ホストを追加")
    p_add.add_argument("address", help="ホストアドレス (IP or ドメイン)")
    p_add.add_argument("--name", "-n", help="表示名 (省略時はアドレスを使用)")
    p_add.set_defaults(func=cmd_add)

    # remove
    p_rm = sub.add_parser("remove", help="監視ホストを削除")
    p_rm.add_argument("address", help="削除するホストアドレス")
    p_rm.set_defaults(func=cmd_remove)

    # list
    p_ls = sub.add_parser("list", help="監視ホスト一覧を表示")
    p_ls.set_defaults(func=cmd_list)

    # ping
    p_ping = sub.add_parser("ping", help="ping を実行して DB に記録")
    p_ping.add_argument("target", help="ホストアドレス または 'all'")
    p_ping.add_argument("--count", "-c", type=int, default=3, help="ping 回数 (デフォルト: 3)")
    p_ping.set_defaults(func=cmd_ping)

    # watch
    p_watch = sub.add_parser("watch", help="全ホストを定期的に監視")
    p_watch.add_argument(
        "--interval", "-i", type=int, default=60, help="監視間隔 秒 (デフォルト: 60)"
    )
    p_watch.set_defaults(func=cmd_watch)

    # report
    p_rep = sub.add_parser("report", help="ping 統計レポートを表示")
    p_rep.add_argument("target", nargs="?", default=None, help="ホストアドレス (省略時: 全ホスト)")
    p_rep.add_argument("--limit", "-l", type=int, default=20, help="表示件数 (デフォルト: 20)")
    p_rep.set_defaults(func=cmd_report)

    # trace
    p_trace = sub.add_parser("trace", help="traceroute を実行して DB に記録")
    p_trace.add_argument("target", help="ホストアドレス または 'all'")
    p_trace.add_argument(
        "--max-hops", type=int, default=30, help="最大ホップ数 (デフォルト: 30)"
    )
    p_trace.set_defaults(func=cmd_trace)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        init_db()
        args.func(args)
    except Exception as e:
        report.console.print(f"[red]エラー:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
