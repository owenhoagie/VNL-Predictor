"""Run the Vercel-compatible prediction handler for local development."""

from __future__ import annotations

import sys
from http.server import HTTPServer
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "vnl-visualizer" / "api"))

from predict import handler


def main() -> None:
    server = HTTPServer(("127.0.0.1", 5000), handler)
    print("Prediction API running at http://127.0.0.1:5000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
