#!/usr/bin/env python3
"""Small static file server for local sharing."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import posixpath
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8014
BUFFER_SIZE = 64 * 1024


@dataclass(frozen=True)
class ServerConfig:
    root: Path
    show_hidden: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve a directory over HTTP for quick local file sharing."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to serve. Defaults to the current directory.",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Bind address.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port.")
    parser.add_argument(
        "--show-hidden",
        action="store_true",
        help="Show dotfiles in directory listings.",
    )
    return parser.parse_args()


def normalize_url_path(raw_path: str) -> str:
    parsed = urlparse(raw_path)
    path = posixpath.normpath(unquote(parsed.path))
    if path == ".":
        return "/"
    if not path.startswith("/"):
        path = f"/{path}"
    return path


def path_escapes_root(raw_path: str) -> bool:
    parsed = urlparse(raw_path)
    depth = 0
    for part in unquote(parsed.path).split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if depth == 0:
                return True
            depth -= 1
            continue
        depth += 1
    return False


def resolve_target(root: Path, request_path: str) -> Path | None:
    if path_escapes_root(request_path):
        return None

    normalized = normalize_url_path(request_path)
    relative = normalized.lstrip("/")
    target = (root / relative).resolve()

    try:
        target.relative_to(root)
    except ValueError:
        return None

    return target


def format_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def make_handler(config: ServerConfig) -> type[BaseHTTPRequestHandler]:
    root = config.root
    show_hidden = config.show_hidden

    class ShareRequestHandler(BaseHTTPRequestHandler):
        server_version = "PyShareServer/1.0"

        def do_GET(self) -> None:
            if normalize_url_path(self.path) == "/healthz":
                self.send_json({"status": "ok", "root": str(root)})
                return

            target = resolve_target(root, self.path)
            if target is None:
                self.send_error(403, "Path escapes the shared directory")
                return
            if not target.exists():
                self.send_error(404, "File not found")
                return
            if target.is_dir():
                self.send_directory(target)
                return
            self.send_file(target)

        def do_HEAD(self) -> None:
            target = resolve_target(root, self.path)
            if target is None:
                self.send_error(403, "Path escapes the shared directory")
                return
            if not target.exists() or target.is_dir():
                self.send_error(404, "File not found")
                return
            self.send_file(target, include_body=False)

        def send_json(self, payload: dict[str, str]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_directory(self, directory: Path) -> None:
            body = self.render_directory(directory).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_file(self, file_path: Path, include_body: bool = True) -> None:
            content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            stat = file_path.stat()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(stat.st_size))
            self.send_header("Last-Modified", self.date_time_string(stat.st_mtime))
            self.end_headers()

            if not include_body:
                return
            with file_path.open("rb") as file:
                while chunk := file.read(BUFFER_SIZE):
                    self.wfile.write(chunk)

        def render_directory(self, directory: Path) -> str:
            relative = directory.relative_to(root)
            title = "/" if str(relative) == "." else f"/{relative.as_posix()}/"
            rows = []

            if directory != root:
                parent = posixpath.dirname(title.rstrip("/"))
                parent_href = "/" if parent in ("", "/") else f"{parent}/"
                rows.append(
                    '<tr><td><a href="{0}">../</a></td><td>directory</td><td>-</td></tr>'.format(
                        html.escape(parent_href)
                    )
                )

            for entry in sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                if not show_hidden and entry.name.startswith("."):
                    continue
                suffix = "/" if entry.is_dir() else ""
                href = f"{title.rstrip('/')}/{entry.name}{suffix}" if title != "/" else f"/{entry.name}{suffix}"
                kind = "directory" if entry.is_dir() else "file"
                size = "-" if entry.is_dir() else format_size(entry.stat().st_size)
                rows.append(
                    "<tr><td><a href=\"{href}\">{name}</a></td><td>{kind}</td><td>{size}</td></tr>".format(
                        href=html.escape(href),
                        name=html.escape(f"{entry.name}{suffix}"),
                        kind=kind,
                        size=size,
                    )
                )

            generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Py Share Server {html.escape(title)}</title>
  <style>
    body {{ color: #202124; font-family: system-ui, sans-serif; line-height: 1.5; margin: 2rem auto; max-width: 920px; padding: 0 1rem; }}
    h1 {{ font-size: 1.6rem; margin-bottom: .25rem; }}
    .meta {{ color: #5f6368; margin-bottom: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #dadce0; padding: .65rem .5rem; text-align: left; }}
    th {{ background: #f8fafd; font-weight: 700; }}
    a {{ color: #0b57d0; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Index of {html.escape(title)}</h1>
  <div class="meta">Serving {html.escape(str(root))} · generated {generated}</div>
  <table>
    <thead><tr><th>Name</th><th>Type</th><th>Size</th></tr></thead>
    <tbody>{''.join(rows) or '<tr><td colspan="3">No files</td></tr>'}</tbody>
  </table>
</body>
</html>"""

        def log_message(self, fmt: str, *args: object) -> None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = fmt % args
            print(f"[{timestamp}] {self.client_address[0]} {message}")

    return ShareRequestHandler


def main() -> None:
    args = parse_args()
    root = Path(args.directory).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Directory does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")

    config = ServerConfig(root=root, show_hidden=args.show_hidden)
    handler = make_handler(config)

    try:
        server = ThreadingHTTPServer((args.host, args.port), handler)
    except OSError as exc:
        raise SystemExit(f"Failed to bind {args.host}:{args.port}: {exc}") from exc

    host = args.host if args.host != "0.0.0.0" else socket.gethostbyname(socket.gethostname())
    print(f"Serving {root}")
    print(f"Open http://{host}:{args.port}/")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
