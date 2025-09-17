from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Setup Chrome options for headless mode (Optional: comment out if you want to see the browser)
chrome_options = Options()
# chrome_options.add_argument("--headless")

# Setup Selenium WebDriver (ensure chromedriver is installed and in PATH)
service = ChromeService()
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-blockers/"
    driver.get(url)

    wait = WebDriverWait(driver, 60)
    # Wait until the specific stats table loads
    table = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table.vbw-o-table.vbw-tournament-player-statistic-table.vbw-stats-scorers")
    ))

    # Optional, give time to load fully
    time.sleep(2)

    # Extract headers
    headers = [header.text for header in table.find_elements(By.TAG_NAME, "th")]

    # Extract rows
    rows = []
    for row_elem in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
        cells = row_elem.find_elements(By.TAG_NAME, "td")
        row = [cell.text for cell in cells]
        rows.append(row)

    # Save to CSV file
    with open("best_blockers_stats.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    print("Data saved successfully to best_blockers_stats.csv")

finally:
    driver.quit()
