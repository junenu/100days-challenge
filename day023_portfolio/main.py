"""Entry point: generate the portfolio and optionally serve it locally."""

import argparse
import http.server
import os
import webbrowser
from pathlib import Path

from data import PERSON
from generator import generate

OUTPUT = Path(__file__).parent / "output" / "index.html"


def serve(port: int) -> None:
    os.chdir(OUTPUT.parent)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *_: None  # suppress request logs
    with http.server.HTTPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"Serving at {url}  (Ctrl+C to stop)")
        webbrowser.open(url)
        httpd.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Portfolio static site generator")
    parser.add_argument("--serve", action="store_true", help="Serve generated site locally")
    parser.add_argument("--port", type=int, default=8080, help="Port for local server (default: 8080)")
    args = parser.parse_args()

    generate(PERSON, OUTPUT)

    if args.serve:
        serve(args.port)


if __name__ == "__main__":
    main()
