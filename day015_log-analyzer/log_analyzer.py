#!/usr/bin/env python3
"""Access log analyzer CLI."""

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\S+)'
)

TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


@dataclass(frozen=True)
class LogEntry:
    ip: str
    timestamp: datetime
    method: str
    path: str
    protocol: str
    status: int
    size: int | None


@dataclass(frozen=True)
class ParseResult:
    entries: list[LogEntry]
    skipped_lines: list[tuple[int, str]]


@dataclass(frozen=True)
class LogSummary:
    total_requests: int
    status_counts: Counter[int]
    path_counts: Counter[str]
    ip_counts: Counter[str]
    hourly_counts: Counter[str]
    method_counts: Counter[str]
    skipped_count: int


def parse_log_line(line: str) -> LogEntry | None:
    """Parse one Apache/Nginx combined-log-like line."""
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    data = match.groupdict()
    try:
        timestamp = datetime.strptime(data["timestamp"], TIME_FORMAT)
        size = None if data["size"] == "-" else int(data["size"])
        return LogEntry(
            ip=data["ip"],
            timestamp=timestamp,
            method=data["method"],
            path=data["path"],
            protocol=data["protocol"],
            status=int(data["status"]),
            size=size,
        )
    except ValueError:
        return None


def parse_log_text(text: str, status_filter: int | None = None) -> ParseResult:
    entries: list[LogEntry] = []
    skipped_lines: list[tuple[int, str]] = []

    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        entry = parse_log_line(line)
        if entry is None:
            skipped_lines.append((line_no, line))
            continue

        if status_filter is None or entry.status == status_filter:
            entries.append(entry)

    return ParseResult(entries=entries, skipped_lines=skipped_lines)


def summarize(entries: list[LogEntry], skipped_count: int = 0) -> LogSummary:
    return LogSummary(
        total_requests=len(entries),
        status_counts=Counter(entry.status for entry in entries),
        path_counts=Counter(entry.path for entry in entries),
        ip_counts=Counter(entry.ip for entry in entries),
        hourly_counts=Counter(entry.timestamp.strftime("%Y-%m-%d %H:00") for entry in entries),
        method_counts=Counter(entry.method for entry in entries),
        skipped_count=skipped_count,
    )


def format_counter(counter: Counter, limit: int = 5) -> list[str]:
    if not counter:
        return ["  (no data)"]
    return [f"  {key:<24} {count:>5}" for key, count in counter.most_common(limit)]


def render_summary(summary: LogSummary, top: int = 5, status_filter: int | None = None) -> str:
    lines = [
        "Access Log Analyzer",
        "===================",
        "",
    ]

    if status_filter is not None:
        lines.append(f"Filter: status={status_filter}")
        lines.append("")

    lines.extend(
        [
            f"Total requests: {summary.total_requests}",
            f"Skipped lines:   {summary.skipped_count}",
            "",
            "Status codes:",
            *format_counter(summary.status_counts, top),
            "",
            "Methods:",
            *format_counter(summary.method_counts, top),
            "",
            f"Top {top} paths:",
            *format_counter(summary.path_counts, top),
            "",
            f"Top {top} IPs:",
            *format_counter(summary.ip_counts, top),
            "",
            "Requests by hour:",
            *format_counter(summary.hourly_counts, top),
        ]
    )

    return "\n".join(lines)


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be greater than or equal to 1")
    return number


def http_status(value: str) -> int:
    status = int(value)
    if status < 100 or status > 599:
        raise argparse.ArgumentTypeError("must be between 100 and 599")
    return status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Apache/Nginx style access logs.")
    parser.add_argument("logfile", type=Path, help="path to access log file")
    parser.add_argument("--status", type=http_status, help="only include this HTTP status code")
    parser.add_argument("--top", type=positive_int, default=5, help="number of ranking rows to show")
    parser.add_argument(
        "--show-skipped",
        action="store_true",
        help="print skipped invalid log lines to stderr",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = args.logfile.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {args.logfile}: {exc}", file=sys.stderr)
        return 1

    result = parse_log_text(text, status_filter=args.status)
    summary = summarize(result.entries, skipped_count=len(result.skipped_lines))

    print(render_summary(summary, top=args.top, status_filter=args.status))

    if args.show_skipped and result.skipped_lines:
        print("", file=sys.stderr)
        print("Skipped lines:", file=sys.stderr)
        for line_no, line in result.skipped_lines:
            print(f"  line {line_no}: {line}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
