"""Scrape VNL men's advanced team standings."""

from __future__ import annotations

import csv
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Collection.browser import create_chrome_driver

STANDINGS_URL = (
    "https://en.volleyballworld.com/volleyball/competitions/"
    "volleyball-nations-league/standings/men/#advanced"
)
OUTPUT_FILE = Path(__file__).resolve().with_name("team_stats.csv")
HEADERS = [
    "Rank",
    "Team",
    "Total",
    "Won",
    "Lost",
    "3-0",
    "3-1",
    "3-2",
    "2-3",
    "1-3",
    "0-3",
    "Points",
    "Sets Won",
    "Sets Lost",
    "Set Ratio",
    "Points Won",
    "Points Lost",
    "Point Ratio",
]


def scrape_team_stats(driver: webdriver.Chrome) -> list[list[str]]:
    driver.get(STANDINGS_URL)
    wait = WebDriverWait(driver, 60)
    try:
        advanced_tab = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.advanced-mode[href='#advanced']")
            )
        )
        advanced_tab.click()
        print("Clicked Advanced tab.")
    except Exception:
        print("Advanced tab not found or already selected. Proceeding...")

    table = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table.vbw-o-table.vbw-ranking-table.advanced")
        )
    )
    rows = table.find_element(By.TAG_NAME, "tbody").find_elements(
        By.CSS_SELECTOR,
        "tr.vbw-o-table__row",
    )
    data: list[list[str]] = []
    for index, row in enumerate(rows, start=1):
        values = [cell.text for cell in row.find_elements(By.TAG_NAME, "td")]
        if not values:
            continue
        if len(values) != len(HEADERS):
            raise ValueError(
                f"Expected {len(HEADERS)} team columns, found {len(values)} "
                f"for row {index}."
            )
        data.append(values)
        print(f"{values[1]} ({index}/{len(rows)})")
    return data


def main() -> None:
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = create_chrome_driver(options)
    try:
        rows = scrape_team_stats(driver)
        with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS)
            writer.writerows(rows)
        print(f"Team stats saved to {OUTPUT_FILE}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
