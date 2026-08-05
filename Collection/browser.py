"""Shared Selenium browser construction for collection scripts."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_chrome_driver(options: Options) -> webdriver.Chrome:
    """Start Chrome through Selenium Manager, bypassing stale PATH drivers."""
    driver_path = shutil.which("chromedriver")
    original_path = os.environ.get("PATH", "")
    if driver_path:
        resolved_driver = Path(driver_path).resolve()
        path_entries = [
            entry
            for entry in original_path.split(os.pathsep)
            if not (
                entry
                and (Path(entry) / "chromedriver").resolve()
                == resolved_driver
            )
        ]
        os.environ["PATH"] = os.pathsep.join(path_entries)
    try:
        return webdriver.Chrome(options=options)
    finally:
        os.environ["PATH"] = original_path
