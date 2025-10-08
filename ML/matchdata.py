#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os
from datetime import datetime

# Config
SCHEDULE_URL = "https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/schedule/#fromDate=2025-08-02&gender=men&undefined=men"
START_WEEK_LABEL = "1 AUGUST"
END_WEEK_LABEL = "30 MAY"

chrome_options = Options()
# Commenting out headless mode for debugging
# chrome_options.add_argument("--headless")

# Add debugging output to ensure the browser opens
print("Initializing Selenium...")
service = ChromeService()
driver = webdriver.Chrome(service=service, options=chrome_options)
print("Selenium initialized successfully.")

# Mapping table for converting table row names to human-readable names
STAT_NAME_MAPPING = {
    "attack": "Kills",
    "block": "Blocks",
    "serve": "Aces",
    "opponent-error": "Opponents Errors",
    "total": "Total Points",
    "dig": "Digs",
    "reception": "Receptions",
    "set": "Sets"
    # Add more mappings here as needed
}

def get_week_label(driver):
    # Returns the current week label (e.g., "2 AUGUST")
    try:
        week_label_elem = driver.find_element(By.CSS_SELECTOR, ".weekly-nav-text-wrap")
        return week_label_elem.text.strip().upper()
    except Exception:
        return ""

def scrape_match_links(driver):
    # Returns a list of (date, match_url) for all matches on the current week page, only for 'Men' (case-insensitive)
    links = []
    seen = set()
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".vbw-gs2-matches-container")))
    date_rows = driver.find_elements(By.CSS_SELECTOR, ".vbw-gs2-date-row")
    for date_row in date_rows:
        try:
            date_str = date_row.get_attribute("data-date") or ""
            match_items = date_row.find_elements(By.CSS_SELECTOR, ".vbw-gs2-match-item")
            for match in match_items:
                try:
                    data_card = match.find_element(By.CSS_SELECTOR, ".vbw-gs2-match-data-card")
                    # Check gender (look for p tag with class containing 'vbw-gs2-match-gender')
                    gender = ""
                    try:
                        gender_elem = data_card.find_element(By.CSS_SELECTOR, "p.vbw-gs2-match-gender")
                        gender = gender_elem.text.strip()
                    except Exception as e:
                        print(f"No gender found for match card, skipping. Error: {e}")
                        continue
                    if gender.strip().lower() != "men":
                        # print(f"Skipping non-Men match: gender found was '{gender}'")
                        continue
                    link_elem = data_card.find_element(By.TAG_NAME, "a")
                    match_url = link_elem.get_attribute("href")
                    if match_url and not match_url.endswith("/#"):
                        # If the link is relative, prepend the base URL
                        if match_url.startswith("/"):
                            match_url = "https://en.volleyballworld.com" + match_url
                        if match_url not in seen:
                            print(f"Found match link: {match_url}")
                            links.append({"date": date_str, "match_url": match_url})
                            seen.add(match_url)
                except Exception as e:
                    print(f"Error processing match item: {e}")
                    continue
        except Exception:
            continue
    return links

def click_prev_week(driver):
    # Only check for the bottom nav previous week button with the exact class
    try:
        wait = WebDriverWait(driver, 10)
        # Look for the bottom nav previous button with the exact class
        prev_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".vbw-gs2-weekly-nav-prev.vbw-gs2-comp-weekly-nav")))
        if prev_btn.is_displayed() and 'disabled' not in prev_btn.get_attribute('class'):
            driver.execute_script("arguments[0].click();", prev_btn)
            time.sleep(2)
            return True
        else:
            print("Previous week button is not visible or is disabled. Stopping.")
            return False
    except Exception as e:
        print("Could not click previous week button (bottom only):", e)
        return False

def parse_week_label(week_label):
    # Example week_label: '26 Jul - 1 Aug' or '31 May - 6 Jun'
    # Returns (start_date, end_date) as datetime.date
    try:
        # Remove any extra text, keep only the date range
        week_label = week_label.strip()
        # Find the part like '31 May - 6 Jun'
        if '-' in week_label:
            parts = week_label.split('-')
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            # Add year if not present
            year = datetime.now().year
            # Try to parse both dates
            try:
                start_date = datetime.strptime(f"{start_str} {year}", "%d %b %Y").date()
                end_date = datetime.strptime(f"{end_str} {year}", "%d %b %Y").date()
            except Exception:
                # Try with full month name
                start_date = datetime.strptime(f"{start_str} {year}", "%d %B %Y").date()
                end_date = datetime.strptime(f"{end_str} {year}", "%d %B %Y").date()
            return start_date, end_date
    except Exception:
        pass
    return None, None

def scrape_match_sets(driver, match_url):
    # Visit the match page and extract set scores (up to 5 sets), home/away team names, and winner/loser
    driver.get(match_url)
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".vbw-mu__sets--result, .vbw-mu_sets--result")))
    except Exception:
        print(f"No set data found for {match_url}")
        return ["", "", "", "", "", "", "", "", "", "", "", "", "", ""]

    # Get home and away team abbreviations and full names
    def get_team_info(team_block):
        abbr = name = ""
        try:
            abbr = team_block.find_element(By.CSS_SELECTOR, ".vbw-mu__team__name--abbr, .vbw-mu_team_name--abbr").text.strip()
        except Exception:
            pass
        try:
            name = team_block.find_element(By.CSS_SELECTOR, ".vbw-mu__team__name:not(.vbw-mu__team__name--abbr), .vbw-mu_team_name:not(.vbw-mu_team_name--abbr)").text.strip()
        except Exception:
            pass
        return abbr if abbr else name

    try:
        home_team_block = driver.find_element(By.CSS_SELECTOR, ".vbw-mu__team--home, .vbw-mu_team--home")
        home = get_team_info(home_team_block)
    except Exception as e:
        print(f"Could not find home team: {e}")
        home = ""
    try:
        away_team_block = driver.find_element(By.CSS_SELECTOR, ".vbw-mu__team--away, .vbw-mu_team--away")
        away = get_team_info(away_team_block)
    except Exception as e:
        print(f"Could not find away team: {e}")
        away = ""

    print(f"Home: {home}, Away: {away}, URL: {match_url}")

    # Determine winner and loser
    winner = loser = ""
    try:
        home_score_div = driver.find_element(By.CSS_SELECTOR, ".vbw-mu__score--home, .vbw-mu_score--home")
        away_score_div = driver.find_element(By.CSS_SELECTOR, ".vbw-mu__score--away, .vbw-mu_score--away")
        if 'winner' in home_score_div.get_attribute('class'):
            winner = home
            loser = away
        elif 'winner' in away_score_div.get_attribute('class'):
            winner = away
            loser = home
    except Exception:
        pass

    set_data = []
    for set_no in range(1, 6):
        try:
            set_div = driver.find_element(By.CSS_SELECTOR, f'.vbw-mu__sets--result[data-set-no="{set_no}"], .vbw-mu_sets--result[data-set-no="{set_no}"]')
            points_home = ""
            points_away = ""
            # Home points
            try:
                points_home = set_div.find_element(By.CSS_SELECTOR, ".vbw-mu__pointA, .vbw-mu_pointA").text.strip()
            except Exception:
                pass
            # Away points
            try:
                points_away = set_div.find_element(By.CSS_SELECTOR, ".vbw-mu__pointB, .vbw-mu_pointB").text.strip()
            except Exception:
                pass
            set_data.extend([points_home, points_away])
        except Exception:
            set_data.extend(["", ""])

    team_stats = scrape_team_stats(driver)

    return [home, away, winner, loser] + set_data + team_stats

def scrape_stat(driver, stat_key):
    try:
        # Wait for the stat row to load
        stat_row = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"tr.vbw-o-table__row.{stat_key}"))
        )
        # print(f"{stat_key.capitalize()} row found.")

        team_a_stat = stat_row.find_element(
            By.CSS_SELECTOR, "td.vbw-o-table__cell.-td-teamA span"
        )
        team_b_stat = stat_row.find_element(
            By.CSS_SELECTOR, "td.vbw-o-table__cell.-td-teamB span"
        )

        team_a_stat = team_a_stat.text.strip()
        team_b_stat = team_b_stat.text.strip()

        # print(f"Team A {stat_key.capitalize()}: {team_a_stat}, Team B {stat_key.capitalize()}: {team_b_stat}")
        return [team_a_stat, team_b_stat]
    except Exception as e:
        print(f"Error grabbing {stat_key} stat: {e}")
        return [None, None]

def scrape_team_stats(driver):
    team_stats = []
    for stat_key in STAT_NAME_MAPPING.keys():
        team_stats.extend(scrape_stat(driver, stat_key))
    return team_stats

def main():
    all_rows = []
    try:
        driver.get(SCHEDULE_URL)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".weekly-nav-text-wrap")))
        time.sleep(2)
        week_label = get_week_label(driver)
        print(f"Starting at week: {week_label}")
        match_links = []
        while True:
            current_url = driver.current_url
            if current_url == "https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/schedule/#fromDate=2025-05-30&gender=men&undefined=men":
                print(f"Reached end week URL: {current_url}. Stopping.")
                break
            links = scrape_match_links(driver)
            print(f"Found {len(links)} matches for week {week_label}")
            match_links.extend(links)
            clicked = click_prev_week(driver)
            if not clicked:
                print("No more previous week button. Stopping loop.")
                break
            week_label = get_week_label(driver)
            print(f"Switched to week: {week_label}")
        # For each match, scrape set data
        for idx, match in enumerate(match_links):  # Process all games
            # Convert date to number format (YYYY-MM-DD)
            date_str = match["date"]
            try:
                # Try to parse the date string and format as YYYY-MM-DD
                date_obj = datetime.strptime(date_str.split(" ")[1] + " " + date_str.split(" ")[2] + " " + date_str.split(" ")[3], "%b %d %Y")
                date = date_obj.strftime("%Y-%m-%d")
            except Exception:
                date = date_str
            match_data = scrape_match_sets(driver, match["match_url"])
            home, away, winner, loser = match_data[0], match_data[1], match_data[2], match_data[3]
            set_scores = match_data[4:14]
            team_stats = match_data[14:]
            # Interleave set scores as Set1 Home, Set1 Away, Set2 Home, Set2 Away, ...
            interleaved = []
            for i in range(0, 10, 2):
                interleaved.append(set_scores[i])
                interleaved.append(set_scores[i+1])
            row = [date, home, away, winner, loser] + team_stats + interleaved
            all_rows.append(row)
            print(f"Scraped sets for match {idx+1}/{len(match_links)}: {match['match_url']}")
        # Save to CSV
        dataset_dir = "ML"
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)
        out_path = os.path.join(dataset_dir, "match_set_stats.csv")
        with open(out_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Dynamically generate headers based on the mapping table
            stat_headers = []
            for stat_key, stat_name in STAT_NAME_MAPPING.items():
                stat_headers.extend([f"{stat_name} Home", f"{stat_name} Away"])

            header = [
                "Date", "Home Team", "Away Team", "Winner", "Loser"
            ] + stat_headers + [
                f"Set{i} {team}" for i in range(1, 6) for team in ("Home", "Away")
            ]
            writer.writerow(header)
            writer.writerows(all_rows)
        print(f"Match set stats saved to {out_path}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()