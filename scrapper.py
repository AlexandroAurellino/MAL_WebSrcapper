from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
import os  # To check if the file exists
import random

# Initialize Selenium with headless options and user-agent
options = Options()
options.add_argument("--headless")  # Uncomment this line to run in headless mode
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Set your user-agent string

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# Path to the JSON file
file_path = 'manga_data.json'

# Load existing data if file exists, otherwise create an empty list
if os.path.exists(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        try:
            data = json.load(file)  # Load existing data
        except json.JSONDecodeError:
            data = []  # If file is empty or has invalid format, initialize an empty list
else:
    data = []

# Step 1: Scrape the top 50 manga links from the Top Manga page
top_manga_url = "https://myanimelist.net/topmanga.php"
driver.get(top_manga_url)
time.sleep(random.uniform(5, 15))  # Random delay between 5 and 15 seconds

# Get page source and parse with BeautifulSoup
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Find all links to individual manga pages
manga_links = []
for tag in soup.select('td.title a.hoverinfo_trigger.fl-l.ml12.mr8'):
    manga_links.append(tag['href'])  # Extract the 'href' attribute (manga link)

# Debug print: Print all extracted manga links
print(f"Extracted {len(manga_links)} manga links:")

number_links = 1
for link in manga_links:
    print(number_links, " ", link)
    number_links += 1

# Step 2: Loop through each manga link and scrape the data
for url in manga_links:
    print(f"Processing: {url}")  # Debug print to show the current link being processed

    try:
        # Open the MyAnimeList manga page
        driver.get(url)
        time.sleep(random.uniform(5, 15))  # Random delay for page load

        # Get page source
        html = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Extracting the data from the page
        # Extract the manga title (Japanese) if available, ignore the English title
        title_element = soup.select_one('span.h1-title span[itemprop="name"]')
        if title_element:
            title = title_element.contents[0].strip()
        else:
            title = "Unknown Title"
            print(f"Title not found for {url}")

        # Extract other data safely with error handling
        try:
            score = soup.find('div', class_='score-label').text.strip()  # Score/Rating
        except AttributeError:
            score = "N/A"

        try:
            rank = soup.select_one('span.ranked strong').text.strip()  # Rank
        except AttributeError:
            rank = "N/A"

        try:
            popularity = soup.select_one('span.popularity strong').text.strip()  # Popularity rank
        except AttributeError:
            popularity = "N/A"

        try:
            members = soup.select_one('span.members strong').text.strip()  # Members count
        except AttributeError:
            members = "N/A"

        try:
            favourites = soup.find('span', string='Favorites:').next_sibling.strip()  # Favorites count
        except AttributeError:
            favourites = "N/A"

        # Extract the type of manga
        try:
            type_element = soup.select_one('div.spaceit_pad:has(span.dark_text:-soup-contains("Type")) a')
            manga_type = type_element.text.strip() if type_element else "Unknown"  # Fallback to "Unknown" if not found
        except Exception as e:
            manga_type = "Unknown"
            print(f"Error extracting type for {url}: {e}")

        # Extract author information as a list
        try:
            author_info = soup.select('span.author a')
            authors = [a.text for a in author_info]  # Store multiple authors as a list
        except Exception as e:
            authors = []
            print(f"Error extracting authors for {url}: {e}")

        # Extract synopsis
        try:
            synopsis = soup.find('span', {'itemprop': 'description'}).text.strip()
        except AttributeError:
            synopsis = "N/A"

        # Extract genres as a list
        try:
            genres = [genre.text.strip() for genre in soup.select('div.spaceit_pad a[href*="/manga/genre"]')]
        except Exception as e:
            genres = []
            print(f"Error extracting genres for {url}: {e}")

        # Function to handle singular and plural cases for themes and similar elements
        def extract_singular_plural(soup, singular, plural):
            section = soup.find('span', string=f'{singular}:') or soup.find('span', string=f'{plural}:')
            if section:
                return [item.text.strip() for item in section.parent.find_all('a')]
            return []

        # Extract themes using the helper function for singular/plural cases
        themes = extract_singular_plural(soup, 'Theme', 'Themes')

        # Extract demographic
        try:
            demographic_element = soup.select_one('div.spaceit_pad:has(span:-soup-contains("Demographic")) a')
            demographic = demographic_element.text.strip() if demographic_element else "Unknown"
        except Exception as e:
            demographic = "Unknown"
            print(f"Error extracting demographic for {url}: {e}")

        # Extract review values (recommended, mixed feelings, not recommended)
        try:
            recommended_value = soup.select_one('div.recommended strong').text.strip()
        except AttributeError:
            recommended_value = "N/A"

        try:
            mixed_feeling_value = soup.select_one('div.mixed-feelings strong').text.strip()
        except AttributeError:
            mixed_feeling_value = "N/A"

        try:
            not_recommended_value = soup.select_one('div.not-recommended strong').text.strip()
        except AttributeError:
            not_recommended_value = "N/A"

        # Data dictionary with authors, genres, themes, and demographic
        manga_data = {
            "Title": title,
            "Type": manga_type,
            "Score": score,
            "Rank": rank,
            "Popularity": popularity,
            "Members": members,
            "Favourites": favourites,
            "Authors": authors,  # List of authors
            "Synopsis": synopsis,
            "Genres": genres,  # List of genres
            "Themes": themes,  # List of themes
            "Demographic": demographic,
            "Recommended": recommended_value,
            "Mixed Feelings": mixed_feeling_value,
            "Not Recommended": not_recommended_value
        }

        # Append the new manga data to the existing list
        # Check if the title already exists in the data
        number_processed = 0
        if not any(manga['Title'] == title for manga in data):
            data.append(manga_data)
            number_processed += 1
            print(number_processed, ". ", title, "Successfully added")  # Debug print for successful addition        
            print("=========================")

            # Save the updated list to the file incrementally
            with open(file_path, mode='w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                print(f"Data saved to {file_path}")  # Debug print after saving
        else:
            print(title, "Already exists in the dataset")
            print("=========================")

    except Exception as e:
        print(f"Error processing {url}: {e}")

# Close the Selenium driver after all pages have been processed
driver.quit()
