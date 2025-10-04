
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os

url = "https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/standings/men/#advanced"
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = ChromeService()
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get(url)
    wait = WebDriverWait(driver, 60)
    # Wait for the Advanced tab and click it if needed (robust for both direct and tab navigation)
    try:
        # Use the correct selector for the Advanced tab
        advanced_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.advanced-mode[href='#advanced']")))
        advanced_tab.click()
        print("Clicked Advanced tab.")
    except Exception:
        print("Advanced tab not found or already selected. Proceeding...")

    # Wait for the advanced table to load
    try:
        table = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table.vbw-o-table.vbw-ranking-table.advanced")
        ))
    except Exception as e:
        print("Could not find the advanced team ranking table. Check selector and page load.")
        driver.quit()
        raise e
    time.sleep(2)

    # Get headers
    header_row = table.find_element(By.TAG_NAME, "thead")
    headers = [th.text for th in header_row.find_elements(By.TAG_NAME, "th")]

    # Get team rows
    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.CSS_SELECTOR, "tr.vbw-o-table__row")

    data = []
    for idx, row in enumerate(rows):
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.text for cell in cells]
        data.append(row_data)
        # Print log after each row
        if row_data:
            print(f"{row_data[0]} ({idx+1}/{len(rows)})")

    # Save to CSV in Dataset directory
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../team_stats.csv")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"Team stats saved to {out_path}")
finally:
    driver.quit()