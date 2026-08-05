"""Run the Vercel-compatible prediction handler for local development."""

from __future__ import annotations

import os
import sys
from http.server import HTTPServer
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "vnl-visualizer" / "api"))

from predict import handler


def main() -> None:
    host = os.environ.get("VNL_API_HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("VNL_API_PORT", "5050"))
    except ValueError as error:
        raise SystemExit("VNL_API_PORT must be a valid integer.") from error

    server = HTTPServer((host, port), handler)
    print(f"Prediction API running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
