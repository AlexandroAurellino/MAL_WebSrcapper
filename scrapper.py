from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import json
import os  # To check if the file exists

# Initialize Selenium
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# List of manga URLs to scrape
list_of_page_to_run = [
    "https://myanimelist.net/manga/2/Berserk",
    "https://myanimelist.net/manga/1706/JoJo_no_Kimyou_na_Bouken_Part_7__Steel_Ball_Run",
    "https://myanimelist.net/manga/656/Vagabond",
    "https://myanimelist.net/manga/13/One_Piece",
    "https://myanimelist.net/manga/1/Monster"
]

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

# Loop through each URL in the list
for url in list_of_page_to_run:
    # Open the MyAnimeList manga page
    driver.get(url)

    # Wait for the page to fully load
    time.sleep(5)

    # Get page source
    html = driver.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Extracting the data from the page
    title = soup.find('span', {'itemprop': 'name'}).text.strip()  # Manga title
    score = soup.find('div', class_='score-label').text.strip()  # Score/Rating
    rank = soup.select_one('span.ranked strong').text.strip()  # Rank
    popularity = soup.select_one('span.popularity strong').text.strip()  # Popularity rank
    members = soup.select_one('span.members strong').text.strip()  # Members count
    favourites = soup.find('span', string='Favorites:').next_sibling.strip()  # Favorites count

    # Extract author information as a list
    author_info = soup.select('span.author a')
    authors = [a.text for a in author_info]  # Store multiple authors as a list

    # Extract synopsis
    synopsis = soup.find('span', {'itemprop': 'description'}).text.strip()

    # Extract genres as a list
    genres = [genre.text.strip() for genre in soup.select('div.spaceit_pad a[href*="/manga/genre"]')]

    # Function to handle singular and plural cases for themes and similar elements
    def extract_singular_plural(soup, singular, plural):
        section = soup.find('span', string=f'{singular}:') or soup.find('span', string=f'{plural}:')
        if section:
            return [item.text.strip() for item in section.parent.find_all('a')]
        return []

    # Extract themes using the helper function for singular/plural cases
    themes = extract_singular_plural(soup, 'Theme', 'Themes')

    # Extract demographic
    demographic = soup.select_one('div.spaceit_pad:has(span:-soup-contains("Demographic")) a').text.strip()

    # Extract review values (recommended, mixed feelings, not recommended)
    recommended_value = soup.select_one('div.recommended strong').text.strip()
    mixed_feeling_value = soup.select_one('div.mixed-feelings strong').text.strip()
    not_recommended_value = soup.select_one('div.not-recommended strong').text.strip()

    # Data dictionary with authors, genres, themes, and demographic
    manga_data = {
        "Title": title,
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
    data.append(manga_data)

    # Print the title to confirm it's been added
    print(title, "Successfully added")

# Save the updated list back to the file after all URLs are processed
with open(file_path, mode='w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

# Close the Selenium driver after all pages have been processed
driver.quit()
