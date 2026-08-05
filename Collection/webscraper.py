
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from pathlib import Path
from Collection.browser import create_chrome_driver
from Collection.config import website_configs

DATASET_DIR = Path(__file__).resolve().parents[1] / "Dataset"

def scrape_table(driver, url, header_map, columns_to_keep):
    driver.get(url)
    wait = WebDriverWait(driver, 60)
    table = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table.vbw-o-table.vbw-tournament-player-statistic-table.vbw-stats-scorers")
    ))
    wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "table.vbw-o-table.vbw-tournament-player-statistic-table"
                ".vbw-stats-scorers tbody tr",
            )
        )
    )

    # Read the table in one browser call instead of thousands of Selenium
    # element round-trips.
    table_rows = driver.execute_script(
        """
        return Array.from(arguments[0].querySelectorAll('tbody tr')).map(
          (row) => Array.from(row.querySelectorAll('td')).map((cell) => ({
            classes: Array.from(cell.classList),
            text: cell.innerText.trim(),
          }))
        );
        """,
        table,
    )

    data = {}
    for cells in table_rows:
        row_dict = {col: "0" for col in columns_to_keep}  # Default all to 0
        for cell in cells:
            for cls in cell["classes"]:
                if cls in header_map:
                    mapped = header_map[cls]
                    row_dict[mapped] = cell["text"] or "0"
        key = (row_dict.get("Player Name", ""), row_dict.get("Team", ""))
        if key[0] and key[1]:
            data[key] = row_dict
    return data

def main():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = create_chrome_driver(chrome_options)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    try:
        for config in website_configs:
            stats = scrape_table(driver, config["url"], config["header_map"], config["columns_to_keep"])
            # Write each website's data to its own CSV file in Dataset folder
            filename = DATASET_DIR / f"{config['name']}_stats.csv"
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
