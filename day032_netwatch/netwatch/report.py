from __future__ import annotations
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def print_hosts(hosts: list[dict]) -> None:
    if not hosts:
        console.print("[yellow]登録されたホストはありません[/yellow]")
        return
    t = Table(title="監視ホスト一覧", box=box.ROUNDED)
    t.add_column("ID", style="dim", width=4)
    t.add_column("アドレス", style="cyan")
    t.add_column("名前")
    t.add_column("登録日時", style="dim")
    for h in hosts:
        t.add_row(str(h["id"]), h["address"], h["name"] or "-", str(h["created_at"]))
    console.print(t)


def print_ping_result(address: str, success: bool, rtt_ms: Optional[float]) -> None:
    status = "[green]OK[/green]" if success else "[red]FAIL[/red]"
    rtt_str = f"{rtt_ms:.2f} ms" if rtt_ms is not None else "—"
    console.print(f"  {address}  {status}  RTT: {rtt_str}")


def print_ping_stats(host: dict, stats: list[dict]) -> None:
    if not stats:
        console.print("[yellow]記録がありません[/yellow]")
        return

    success_count = sum(1 for s in stats if s["success"])
    total = len(stats)
    availability = success_count / total * 100
    rtts = [s["rtt_ms"] for s in stats if s["rtt_ms"] is not None]
    avg_rtt = sum(rtts) / len(rtts) if rtts else None
    min_rtt = min(rtts) if rtts else None
    max_rtt = max(rtts) if rtts else None

    color = "green" if availability >= 99 else "yellow" if availability >= 90 else "red"
    console.print(
        f"\n[bold]{host['name']} ({host['address']})[/bold]  "
        f"可用性: [{color}]{availability:.1f}%[/{color}]  "
        f"({success_count}/{total})"
    )

    if avg_rtt is not None:
        console.print(
            f"  RTT — avg: {avg_rtt:.2f} ms  "
            f"min: {min_rtt:.2f} ms  max: {max_rtt:.2f} ms"
        )

    t = Table(box=box.SIMPLE, show_header=True)
    t.add_column("日時", style="dim")
    t.add_column("結果", width=6)
    t.add_column("RTT")
    for s in stats:
        ok = "[green]OK[/green]" if s["success"] else "[red]FAIL[/red]"
        rtt = f"{s['rtt_ms']:.2f} ms" if s["rtt_ms"] is not None else "—"
        t.add_row(str(s["checked_at"]), ok, rtt)
    console.print(t)


def print_traceroute(host: dict, hops: list[dict]) -> None:
    if not hops:
        console.print("[yellow]traceroute 結果がありません[/yellow]")
        return
    t = Table(title=f"traceroute: {host['address']}", box=box.ROUNDED)
    t.add_column("Hop", width=4, style="dim")
    t.add_column("アドレス", style="cyan")
    t.add_column("RTT")
    for h in hops:
        addr = h["hop_address"] or "*"
        rtt = f"{h['rtt_ms']:.2f} ms" if h["rtt_ms"] is not None else "—"
        t.add_row(str(h["hop_num"]), addr, rtt)
    console.print(t)
    if hops:
        console.print(f"[dim]記録日時: {hops[0]['traced_at']}[/dim]")
