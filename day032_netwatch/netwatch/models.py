from __future__ import annotations
from typing import Optional
from .db import connect


def add_host(address: str, name: Optional[str] = None) -> dict:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO hosts (address, name) VALUES (%s, %s)"
                " ON CONFLICT (address) DO NOTHING RETURNING *",
                (address, name or address),
            )
            row = cur.fetchone()
        conn.commit()
    if row is None:
        raise ValueError(f"{address} はすでに登録済みです")
    return dict(row)


def remove_host(address: str) -> bool:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM hosts WHERE address = %s RETURNING id", (address,)
            )
            deleted = cur.fetchone() is not None
        conn.commit()
    return deleted


def get_hosts() -> list[dict]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hosts ORDER BY id")
            return [dict(r) for r in cur.fetchall()]


def get_host_by_address(address: str) -> Optional[dict]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hosts WHERE address = %s", (address,))
            row = cur.fetchone()
    return dict(row) if row else None


def save_ping(host_id: int, success: bool, rtt_ms: Optional[float]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ping_results (host_id, success, rtt_ms) VALUES (%s, %s, %s)",
                (host_id, success, rtt_ms),
            )
        conn.commit()


def save_traceroute_hops(host_id: int, trace_id: str, hops: list[dict]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for hop in hops:
                cur.execute(
                    "INSERT INTO traceroute_hops"
                    " (host_id, trace_id, hop_num, hop_address, rtt_ms)"
                    " VALUES (%s, %s, %s, %s, %s)",
                    (
                        host_id,
                        trace_id,
                        hop["hop_num"],
                        hop.get("address"),
                        hop.get("rtt_ms"),
                    ),
                )
        conn.commit()


def get_ping_stats(host_id: int, limit: int = 50) -> list[dict]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT success, rtt_ms, checked_at FROM ping_results"
                " WHERE host_id = %s ORDER BY checked_at DESC LIMIT %s",
                (host_id, limit),
            )
            return [dict(r) for r in cur.fetchall()]


def get_latest_traceroute(host_id: int) -> list[dict]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT h.hop_num, h.hop_address, h.rtt_ms, h.traced_at
                FROM traceroute_hops h
                WHERE h.host_id = %s
                  AND h.trace_id = (
                      SELECT trace_id FROM traceroute_hops
                      WHERE host_id = %s
                      ORDER BY traced_at DESC LIMIT 1
                  )
                ORDER BY h.hop_num
                """,
                (host_id, host_id),
            )
            return [dict(r) for r in cur.fetchall()]
