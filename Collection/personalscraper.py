"""Scrape player profile attributes from Volleyball World."""

from __future__ import annotations

import csv
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Collection.browser import create_chrome_driver

PROFILE_FIELDS = ["Position", "Age", "Height"]
PLAYER_STATS_URL = (
    "https://en.volleyballworld.com/volleyball/competitions/"
    "volleyball-nations-league/statistics/men/best-scorers/"
)
OUTPUT_FILE = (
    Path(__file__).resolve().parents[1] / "Dataset" / "player_profiles.csv"
)


def scrape_player_profile(
    driver: webdriver.Chrome,
    profile_url: str,
    fields: list[str],
) -> dict[str, str]:
    driver.get(profile_url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "vbw-player-bio-col"))
    )
    data = {field: "" for field in fields}
    for column in driver.find_elements(By.CLASS_NAME, "vbw-player-bio-col"):
        try:
            heading = column.find_element(
                By.CLASS_NAME,
                "vbw-player-bio-head",
            ).text.strip()
            value = column.find_element(
                By.CLASS_NAME,
                "vbw-player-bio-text",
            ).text.strip()
            if heading in data:
                data[heading] = value
        except Exception:
            continue
    return data


def collect_player_links(driver: webdriver.Chrome) -> list[dict[str, str]]:
    driver.get(PLAYER_STATS_URL)
    table = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "table.vbw-o-table.vbw-tournament-player-statistic-table"
                ".vbw-stats-scorers",
            )
        )
    )
    return driver.execute_script(
        """
        return Array.from(arguments[0].querySelectorAll('tbody tr'))
          .map((row) => {
            const player = row.querySelector('td.playername');
            const team = row.querySelector('td.federation');
            const link = player?.querySelector('a');
            return {
              'Player Name': player?.innerText.trim() ?? '',
              'Team': team?.innerText.trim() ?? '',
              'Profile Link': link?.href ?? '',
            };
          })
          .filter((player) => player['Player Name']);
        """,
        table,
    )


def main() -> None:
    driver = create_chrome_driver(Options())
    try:
        players = collect_player_links(driver)
        rows: list[list[str]] = []
        for index, player in enumerate(players, start=1):
            try:
                profile = (
                    scrape_player_profile(
                        driver,
                        player["Profile Link"],
                        PROFILE_FIELDS,
                    )
                    if player["Profile Link"]
                    else {field: "" for field in PROFILE_FIELDS}
                )
            except Exception as error:
                print(
                    f"Error scraping {player['Player Name']} "
                    f"({player['Profile Link']}): {error}"
                )
                profile = {field: "" for field in PROFILE_FIELDS}
            rows.append(
                [player["Player Name"], player["Team"]]
                + [profile[field] for field in PROFILE_FIELDS]
            )
            print(
                f"{player['Player Name']} - {profile['Age']} - "
                f"{profile['Height']} - {profile['Position']} "
                f"({index}/{len(players)})"
            )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Player Name", "Team", *PROFILE_FIELDS])
            writer.writerows(rows)
        print(f"Player profile data saved to {OUTPUT_FILE}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
