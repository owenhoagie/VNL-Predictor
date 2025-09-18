from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os

# Config: specify which fields to extract from player profile
PROFILE_FIELDS = ["Position", "Age", "Height"]

url = "https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/statistics/men/best-scorers/"
chrome_options = Options()
# chrome_options.add_argument("--headless")
service = ChromeService()
driver = webdriver.Chrome(service=service, options=chrome_options)

def scrape_player_profile(driver, profile_url, fields):
    driver.get(profile_url)
    # Wait until at least one bio col is present
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "vbw-player-bio-col")))
    bio_cols = driver.find_elements(By.CLASS_NAME, "vbw-player-bio-col")
    data = {field: "" for field in fields}
    for col in bio_cols:
        try:
            head = col.find_element(By.CLASS_NAME, "vbw-player-bio-head").text.strip()
            value = col.find_element(By.CLASS_NAME, "vbw-player-bio-text").text.strip()
            if head in data:
                data[head] = value
        except Exception:
            continue
    return data

try:
    driver.get(url)
    wait = WebDriverWait(driver, 60)
    table = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table.vbw-o-table.vbw-tournament-player-statistic-table.vbw-stats-scorers")
    ))
    time.sleep(2)

    # Step 1: Collect all player info from main table
    player_infos = []
    for row_elem in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
        cells = row_elem.find_elements(By.TAG_NAME, "td")
        # Find player name cell and extract link
        player_cell = None
        for cell in cells:
            if "playername" in cell.get_attribute("class"):
                player_cell = cell
                break
        if player_cell:
            player_name = player_cell.text
            link_elem = player_cell.find_element(By.TAG_NAME, "a")
            profile_link = link_elem.get_attribute("href") if link_elem else ""
        else:
            player_name = ""
            profile_link = ""
        # Find team cell
        team = ""
        for cell in cells:
            if "federation" in cell.get_attribute("class"):
                team = cell.text
                break
        player_infos.append({"Player Name": player_name, "Team": team, "Profile Link": profile_link})

    # Step 2: For each player, visit their profile and scrape details
    rows = []
    total_players = len(player_infos)
    for idx, info in enumerate(player_infos):
        try:
            if info["Profile Link"]:
                profile_data = scrape_player_profile(driver, info["Profile Link"], PROFILE_FIELDS)
            else:
                profile_data = {field: "" for field in PROFILE_FIELDS}
        except Exception as e:
            print(f"Error scraping {info['Player Name']} ({info['Profile Link']}): {e}")
            profile_data = {field: "" for field in PROFILE_FIELDS}
        row = [info["Player Name"], info["Team"]] + [profile_data[field] for field in PROFILE_FIELDS]
        rows.append(row)
        # Print log after each successful scrape
        name = info["Player Name"]
        age = profile_data.get("Age", "")
        height = profile_data.get("Height", "")
        position = profile_data.get("Position", "")
        print(f"{name} - {age} - {height} - {position} ({idx+1}/{total_players})")
        # No sleep needed, we wait for elements instead

    # Save to CSV
    dataset_dir = "Dataset"
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    with open(os.path.join(dataset_dir, "player_profiles.csv"), mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        header = ["Player Name", "Team"] + PROFILE_FIELDS
        writer.writerow(header)
        writer.writerows(rows)

    print(f"Player profile data saved to {os.path.join(dataset_dir, 'player_profiles.csv')}")

finally:
    driver.quit()