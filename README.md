### README

# Manga Scraper for MyAnimeList

This project is a web scraper designed to collect data about manga from MyAnimeList (MAL). The scraper uses Selenium and BeautifulSoup to extract various details such as title, score, rank, authors, genres, themes, and more from the manga pages.

### Features
- Extracts manga details like:
  - Title
  - Score/Rating
  - Rank
  - Popularity
  - Members count
  - Favorites count
  - Authors
  - Synopsis
  - Genres
  - Themes
  - Demographic
  - Review summary (recommended, mixed feelings, not recommended)
- Handles cases where attributes might appear in singular or plural forms (e.g., `Theme` vs `Themes`).
- Saves the collected data in a JSON file for easy access and processing.

### Installation

1. Clone the repository or download the script files.
2. Make sure you have [Google Chrome](https://www.google.com/chrome/) (or your browser of choice) installed on your system. Ensure it is up to date by navigating to `Settings > About Chrome`—this will automatically update Chrome if it's outdated.
3. Install the required Python libraries using the following command:
   ```bash
   pip install -r requirements.txt
   ```
4. Download the correct version of [ChromeDriver](https://sites.google.com/chromium.org/driver/) that matches your updated Chrome browser version. Place it in the root directory of the project.
   - Be sure to choose the correct installation for your setup (OS, architecture, etc.).
   - Make sure to update `chromedriver.exe` whenever Chrome updates to avoid compatibility issues.

### How to Run

1. Update the list of manga URLs you want to scrape in the `list_of_page_to_run` variable.
2. Run the scraper using:
   ```bash
   python manga_scraper.py
   ```
3. The scraper will navigate through each page, extract relevant data, and save it to `manga_data.json`.

### Data Saved

The scraper collects the following information from each manga page:
- **Title**: The name of the manga.
- **Score**: The average user rating on MAL.
- **Rank**: The rank of the manga based on its score.
- **Popularity**: The manga's popularity rank on MAL.
- **Members**: The number of users who have added the manga to their lists.
- **Favorites**: The number of users who have marked the manga as their favorite.
- **Authors**: List of authors.
- **Synopsis**: Short summary of the manga's story.
- **Genres**: List of genres.
- **Themes**: List of themes (if available).
- **Demographic**: The target demographic (if available).
- **Recommended, Mixed Feelings, Not Recommended**: Review summary counts for user opinions.

### Customizing the Scraper

To change the manga pages to scrape, simply modify the `list_of_page_to_run` variable in the Python script. You can add or remove URLs as needed.

### Notes
- The script uses a 5-second delay to ensure the page is fully loaded before extracting data. You may need to adjust this depending on your internet speed or the response time of the website.
- Make sure that your ChromeDriver version matches your Chrome browser version to avoid compatibility issues. You can check and update Chrome by going to `Settings > About Chrome` and get the correct ChromeDriver version from [this link](https://sites.google.com/chromium.org/driver/).

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---