from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import os
import random


def initialize_driver(headless=True):
    """Initialize the Selenium WebDriver with an option to toggle headless mode."""
    options = Options()
    
    if headless:
        options.add_argument("--headless")  # Enable headless mode
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(executable_path="chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)


def load_existing_data(file_path):
    """Load existing manga data from JSON file or initialize empty list."""
    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            try:
                return json.load(file)  # Load existing data
            except json.JSONDecodeError:
                return []  # If file is empty or invalid, return empty list
    return []


def save_data_to_file(data, file_path):
    """Save manga data to JSON file."""
    with open(file_path, mode='w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data saved to {file_path}")


def scrape_top_manga_links(driver, num_links):
    """Scrape top manga links from the current page."""
    time.sleep(random.uniform(5, 15))  # Random delay

    # Parse the HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all manga links
    manga_links = [tag['href'] for tag in soup.select('td.title a.hoverinfo_trigger.fl-l.ml12.mr8')]
    
    # Debug print: show extracted links
    print(f"Extracted {len(manga_links)} manga links")
    for i, link in enumerate(manga_links[:num_links], start=1):
        print(i, link)
    
    return manga_links[:num_links]


def click_next_page(driver):
    """Click the 'Next 50' link to navigate to the next page of manga."""
    try:
        next_button = driver.find_element("css selector", 'a.link-blue-box.next')
        next_button.click()
        time.sleep(random.uniform(5, 15))  # Random delay for page load
        return True
    except Exception as e:
        print(f"Error clicking next page: {e}")
        return False


def extract_manga_data(driver, url):
    driver.get(url)
    time.sleep(random.uniform(5, 15))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    def safe_text(selector, default="N/A"):
        el = soup.select_one(selector)
        return el.text.strip() if el else default

    def safe_attr(selector, attr, default="N/A"):
        el = soup.select_one(selector)
        return el.get(attr) or default if el else default

    # NEW: directly extract Themes
    def extract_themes():
        label = soup.find('span', class_='dark_text', string='Themes:')
        if not label:
            return []
        # parent of label contains all the <a> tags for each theme
        container = label.parent
        return [a.text.strip() for a in container.find_all('a')]

    manga_data = {
        "Title": safe_text('span.h1-title span[itemprop="name"]', "Unknown Title"),
        "Type": safe_text('div.spaceit_pad:has(span.dark_text:-soup-contains("Type")) a', "Unknown"),
        "Score": safe_text('div.score-label', "N/A"),
        "Rank": safe_text('span.ranked strong', "N/A"),
        "Popularity": safe_text('span.popularity strong', "N/A"),
        "Members": safe_text('span.members strong', "N/A"),
        "Favourites": safe_text('span:contains("Favorites:")', "N/A"),
        "Authors": [a.text for a in soup.select('span.author a')],
        "Synopsis": safe_text('span[itemprop="description"]', "N/A"),
        "Genres": [g.text.strip() for g in soup.select('div.spaceit_pad span.dark_text:contains("Genres") ~ a')],
        "Themes": extract_themes(),
        "Demographic": safe_text('div.spaceit_pad:has(span:-soup-contains("Demographic")) a', "Unknown"),
        "Recommended": safe_text('div.recommended strong', "N/A"),
        "Mixed Feelings": safe_text('div.mixed-feelings strong', "N/A"),
        "Not Recommended": safe_text('div.not-recommended strong', "N/A"),

        # Bagian yang diubah: mengambil URL gambar dari data-src, fallback ke src
        "Image URL": safe_attr(
            'img[itemprop="image"]', 'data-src',
            safe_attr('img[itemprop="image"]', 'src', "N/A")
        )
    }

    return manga_data



def collect_manga_data(manga_links, data, driver, file_path):
    """Collect manga data for each link and save it to a file."""
    number_processed = 0

    for url in manga_links:
        print(f"Processing: {url}")
        manga_data = extract_manga_data(driver, url)

        # Check if title already exists
        if any(manga['Title'] == manga_data['Title'] for manga in data):
            print(f"{manga_data['Title']} already exists")
        else:
            data.append(manga_data)
            number_processed += 1
            print(f"Added {number_processed}. {manga_data['Title']}")
            save_data_to_file(data, file_path)  # Save data after each addition


def click_next_page(driver):
    """Click the 'Next 50' link to navigate to the next page of manga."""
    try:
        # Wait for the 'Next 50' button to be visible and clickable
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
        next_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.link-blue-box.next'))
        )
        next_button.click()  # Click the 'Next 50' button
        time.sleep(random.uniform(5, 15))  # Random delay for page load
        return True
    except Exception as e:
        print(f"Error clicking next page: {e}")
        return False


def main(num_iterations=10, headless=True):
    """Main function to scrape manga data with URL limit increment."""
    file_path = 'manga_data_new.json'
    base_url = "https://myanimelist.net/topmanga.php?limit="  # Base URL with limit parameter

    # Initialize driver with headless mode control
    driver = initialize_driver(headless)
    data = load_existing_data(file_path)

    try:
        for i in range(num_iterations):
            # Construct URL for the current iteration (increasing limit by 50 each time)
            current_limit = i * 50
            current_url = base_url + str(current_limit)
            print(f"Processing page with limit {current_limit}: {current_url}")

            # Load the current page
            driver.get(current_url)
            time.sleep(random.uniform(5, 15))  # Random delay for page load

            # Scrape manga links (you can set how many you want to collect here)
            manga_links = scrape_top_manga_links(driver, num_links=50)

            # Collect data for each manga link and save it
            collect_manga_data(manga_links, data, driver, file_path)

            print(f"Finished processing page with limit {current_limit}")

    finally:
        driver.quit()  # Make sure to quit the driver after processing
    # Define constants
    file_path = 'manga_data.json'
    top_manga_url = "https://myanimelist.net/topmanga.php?limit=150"

    # Initialize driver with headless mode control
    driver = initialize_driver(headless)
    data = load_existing_data(file_path)

    # Load the first page
    driver.get(top_manga_url)

    try:
        for _ in range(num_iterations):
            # Scrape manga links (you can set how many you want to collect here)
            manga_links = scrape_top_manga_links(driver, num_links=50)

            # Collect data for each manga link and save it
            collect_manga_data(manga_links, data, driver, file_path)

            # Click the next page if available
            if not click_next_page(driver):
                print("No more pages to scrape.")
                break
    finally:
        driver.quit()  # Make sure to quit the driver after processing


# Example usage
if __name__ == "__main__":
    main(num_iterations=5, headless=False)  # You can set headless=False to disable headless mode