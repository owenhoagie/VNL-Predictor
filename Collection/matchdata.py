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
# chrome_options.add_argument("--headless")
service = ChromeService()
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_week_label(driver):
    # Returns the current week label (e.g., "2 AUGUST")
    try:
        week_label_elem = driver.find_element(By.CSS_SELECTOR, ".weekly-nav-text-wrap")
        return week_label_elem.text.strip().upper()
    except Exception:
        return ""

def scrape_match_links(driver):
    # Returns a list of (date, match_url) for all matches on the current week page
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
                    # Find the a tag directly under .vbw-gs2-match-data-card
                    data_card = match.find_element(By.CSS_SELECTOR, ".vbw-gs2-match-data-card")
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
                except Exception:
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

def main():
    all_links = []
    try:
        driver.get(SCHEDULE_URL)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".weekly-nav-text-wrap")))
        time.sleep(2)
        week_label = get_week_label(driver)
        print(f"Starting at week: {week_label}")
        while True:
            # Stop if the current URL is the end week URL
            current_url = driver.current_url
            if current_url == "https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/schedule/#fromDate=2025-05-30&gender=men&undefined=men":
                print(f"Reached end week URL: {current_url}. Stopping.")
                break
            # Scrape all match links for this week
            links = scrape_match_links(driver)
            print(f"Found {len(links)} matches for week {week_label}")
            all_links.extend(links)
            # Otherwise, go to previous week
            clicked = click_prev_week(driver)
            if not clicked:
                print("No more previous week button. Stopping loop.")
                break
            week_label = get_week_label(driver)
            print(f"Switched to week: {week_label}")
        # Save to CSV
        dataset_dir = "Dataset"
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)
        out_path = os.path.join(dataset_dir, "match_links.csv")
        with open(out_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["date", "match_url"])
            writer.writeheader()
            writer.writerows(all_links)
        print(f"Match links saved to {out_path}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()