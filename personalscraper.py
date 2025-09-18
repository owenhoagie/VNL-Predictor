from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

url = "https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/statistics/men/best-scorers/"
chrome_options = Options()
# chrome_options.add_argument("--headless")
service = ChromeService()
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get(url)
    wait = WebDriverWait(driver, 60)
    table = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table.vbw-o-table.vbw-tournament-player-statistic-table.vbw-stats-scorers")
    ))
    time.sleep(2)

    rows = []
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
        rows.append([player_name, team, profile_link])

    # Save to CSV
    with open("Dataset/player_profiles.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Player Name", "Team", "Profile Link"])
        writer.writerows(rows)

    print("Player profile data saved to Dataset/player_profiles.csv")

finally:
    driver.quit()