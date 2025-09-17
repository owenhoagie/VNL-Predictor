
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from config import website_configs

def scrape_table(driver, url, header_map, columns_to_keep):
    driver.get(url)
    wait = WebDriverWait(driver, 60)
    table = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table.vbw-o-table.vbw-tournament-player-statistic-table.vbw-stats-scorers")
    ))
    time.sleep(2)
    # Get raw headers from th class names
    th_elements = table.find_elements(By.TAG_NAME, "th")
    raw_headers = []
    for th in th_elements:
        # Find the class that matches a key in header_map
        th_classes = th.get_attribute("class").split()
        found = None
        for cls in th_classes:
            if cls in header_map:
                found = cls
                break
        raw_headers.append(found)
    # Build column index mapping using header_map
    col_indices = {}
    for idx, raw in enumerate(raw_headers):
        if raw is not None:
            mapped = header_map.get(raw)
            if mapped:
                col_indices[mapped] = idx
    # Extract rows
    data = {}
    for row_elem in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
        cells = row_elem.find_elements(By.TAG_NAME, "td")
        row_dict = {col: "0" for col in columns_to_keep}  # Default all to 0
        for cell in cells:
            cell_classes = cell.get_attribute("class").split()
            for cls in cell_classes:
                if cls in header_map:
                    mapped = header_map[cls]
                    row_dict[mapped] = cell.text if cell.text.strip() != "" else "0"
        key = (row_dict.get("Player Name", ""), row_dict.get("Team", ""))
        if key[0] and key[1]:
            data[key] = row_dict
    return data
    merged = {}
    for stats in all_stats:
        for key, row in stats.items():
            if key not in merged:
                merged[key] = {}
            merged[key].update(row)
    # Ensure all columns exist
    for row in merged.values():
        for col in columns:
            if col not in row:
                row[col] = ""
    return merged

def main():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    import os
    dataset_dir = "Dataset"
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    try:
        for config in website_configs:
            stats = scrape_table(driver, config["url"], config["header_map"], config["columns_to_keep"])
            # Write each website's data to its own CSV file in Dataset folder
            filename = os.path.join(dataset_dir, f"{config['name']}_stats.csv")
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                header = config["columns_to_keep"]
                writer.writerow(header)
                for row in stats.values():
                    writer.writerow([row.get(col, "0") if not row.get(col) else row.get(col) for col in header])
            print(f"Data saved successfully to {filename}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
