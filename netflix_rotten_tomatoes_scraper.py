#!/usr/bin/env python3
"""
Netflix & Rotten Tomatoes Movie Scraper
Extracts 5 random movies from Netflix Top 10 and retrieves their Rotten Tomatoes data
"""

import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import argparse
import os
from urllib.parse import quote_plus


class MovieScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def get_netflix_top_10_movies(self):
        """Scrape top 10 movies from Netflix Tudum Top 10"""
        print("Fetching Netflix Top 10 movies...")
        self.driver.get('https://www.netflix.com/tudum/top10/')

        # Wait for page to load
        time.sleep(5)

        movies = []

        try:
            # Try multiple selectors as Netflix's page structure may vary
            selectors = [
                "//h3[contains(text(), 'Films')]/following::table[1]//tr",
                "//h2[contains(text(), 'Movies')]/following::table[1]//tr",
                "//table[contains(@class, 'top')]//tr",
                "//div[contains(@class, 'films')]//table//tr",
                "//td[contains(@class, 'name')]",
            ]

            # Try to find movies using different strategies
            for selector in selectors:
                try:
                    if 'td' in selector:
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.XPATH, selector)

                    if elements:
                        for elem in elements[:10]:
                            try:
                                text = elem.text.strip()
                                if text and len(text) > 1:
                                    # Clean up the text (remove rank numbers)
                                    parts = text.split('\n')
                                    for part in parts:
                                        part = part.strip()
                                        # Skip numbers and very short entries
                                        if part and not part.isdigit() and len(part) > 2:
                                            movies.append(part)
                                            if len(movies) >= 10:
                                                break
                            except:
                                continue

                    if len(movies) >= 10:
                        break
                except:
                    continue

            # If automated scraping fails, provide fallback option
            if len(movies) < 10:
                print("\nAutomated scraping encountered issues. Please enter the top 10 movies manually:")
                movies = []
                for i in range(10):
                    movie = input(f"Enter movie #{i+1}: ").strip()
                    if movie:
                        movies.append(movie)

        except Exception as e:
            print(f"Error fetching Netflix Top 10: {e}")
            print("\nPlease enter the top 10 movies manually:")
            movies = []
            for i in range(10):
                movie = input(f"Enter movie #{i+1}: ").strip()
                if movie:
                    movies.append(movie)

        # Remove duplicates while preserving order
        seen = set()
        unique_movies = []
        for movie in movies:
            if movie not in seen:
                seen.add(movie)
                unique_movies.append(movie)

        return unique_movies[:10]

    def search_rotten_tomatoes(self, movie_title):
        """Search for a movie on Rotten Tomatoes and return the movie page URL"""
        search_url = f"https://www.rottentomatoes.com/search?search={quote_plus(movie_title)}"
        self.driver.get(search_url)
        time.sleep(3)

        try:
            # Look for the first movie result
            movie_link = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//search-page-media-row[@type='movie']//a[@data-qa='info-name']"))
            )
            return movie_link.get_attribute('href')
        except TimeoutException:
            # Try alternative selectors
            try:
                movie_link = self.driver.find_element(By.XPATH, "//a[contains(@href, '/m/')]")
                return movie_link.get_attribute('href')
            except:
                return None

    def get_rotten_tomatoes_data(self, movie_title):
        """Get movie data from Rotten Tomatoes"""
        print(f"Fetching data for: {movie_title}")

        movie_url = self.search_rotten_tomatoes(movie_title)

        if not movie_url:
            print(f"  ⚠ Could not find {movie_title} on Rotten Tomatoes")
            return {
                'movie': movie_title,
                'duration': 'Not available!',
                'tomatometer': 'Not available!',
                'popcornmeter': 'Not available!',
                'description': 'Not available!'
            }

        self.driver.get(movie_url)
        time.sleep(3)

        data = {
            'movie': movie_title,
            'duration': 'Not available!',
            'tomatometer': 'Not available!',
            'popcornmeter': 'Not available!',
            'description': 'Not available!'
        }

        try:
            # Get Tomatometer score
            try:
                tomatometer = self.driver.find_element(By.XPATH,
                    "//rt-button[@slot='criticsScore']//rt-text[@slot='number']")
                data['tomatometer'] = tomatometer.text.strip()
            except:
                try:
                    tomatometer = self.driver.find_element(By.XPATH,
                        "//score-board[@data-qa='score-panel']//span[contains(@class, 'tometer')]")
                    data['tomatometer'] = tomatometer.text.strip()
                except:
                    pass

            # Get Popcornmeter (Audience) score
            try:
                popcornmeter = self.driver.find_element(By.XPATH,
                    "//rt-button[@slot='audienceScore']//rt-text[@slot='number']")
                data['popcornmeter'] = popcornmeter.text.strip()
            except:
                try:
                    popcornmeter = self.driver.find_element(By.XPATH,
                        "//score-board[@data-qa='score-panel']//span[contains(@class, 'audience')]")
                    data['popcornmeter'] = popcornmeter.text.strip()
                except:
                    pass

            # Get Movie duration
            try:
                duration = self.driver.find_element(By.XPATH,
                    "//rt-text[@slot='duration']")
                data['duration'] = duration.text.strip()
            except:
                try:
                    duration = self.driver.find_element(By.XPATH,
                        "//li[@class='meta-row runtime']//time")
                    data['duration'] = duration.text.strip()
                except:
                    pass

            # Get Movie description
            try:
                description = self.driver.find_element(By.XPATH,
                    "//rt-text[@slot='info']")
                data['description'] = description.text.strip()
            except:
                try:
                    description = self.driver.find_element(By.XPATH,
                        "//drawer-more[@data-qa='movie-info-synopsis']//p")
                    data['description'] = description.text.strip()
                except:
                    try:
                        description = self.driver.find_element(By.XPATH,
                            "//div[@id='movieSynopsis']")
                        data['description'] = description.text.strip()
                    except:
                        pass

            print(f"  ✓ Duration: {data['duration']}")
            print(f"  ✓ Tomatometer: {data['tomatometer']}")
            print(f"  ✓ Popcornmeter: {data['popcornmeter']}")

        except Exception as e:
            print(f"  ⚠ Error extracting data: {e}")

        return data

    def close(self):
        """Close the WebDriver"""
        self.driver.quit()


def main():
    parser = argparse.ArgumentParser(description='Scrape Netflix Top 10 movies and get Rotten Tomatoes data')
    parser.add_argument('--output', '-o', type=str, default='movies_data.csv',
                        help='Output file path (CSV or Excel format)')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run browser in headless mode')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                        help='Run browser in visible mode')

    args = parser.parse_args()

    scraper = None

    try:
        print("=" * 60)
        print("Netflix & Rotten Tomatoes Movie Scraper")
        print("=" * 60)

        scraper = MovieScraper(headless=args.headless)

        # Step 1: Get top 10 movies from Netflix
        top_10_movies = scraper.get_netflix_top_10_movies()

        if len(top_10_movies) < 10:
            print(f"\n⚠ Warning: Only found {len(top_10_movies)} movies instead of 10")

        print(f"\nTop 10 Movies found:")
        for i, movie in enumerate(top_10_movies, 1):
            print(f"{i}. {movie}")

        # Step 2: Randomly select 5 movies
        if len(top_10_movies) >= 5:
            selected_movies = random.sample(top_10_movies, 5)
        else:
            selected_movies = top_10_movies
            print(f"\n⚠ Warning: Only {len(selected_movies)} movies available, selecting all")

        print(f"\nRandomly selected 5 movies:")
        for i, movie in enumerate(selected_movies, 1):
            print(f"{i}. {movie}")

        # Step 3: Get Rotten Tomatoes data for each selected movie
        print("\n" + "=" * 60)
        print("Fetching Rotten Tomatoes data...")
        print("=" * 60 + "\n")

        movies_data = []
        for movie in selected_movies:
            data = scraper.get_rotten_tomatoes_data(movie)
            movies_data.append(data)
            time.sleep(2)  # Be polite to the server

        # Step 4: Save to file
        df = pd.DataFrame(movies_data)

        # Reorder columns for better readability
        df = df[['movie', 'duration', 'tomatometer', 'popcornmeter', 'description']]

        # Determine output format based on file extension
        output_path = args.output
        if output_path.endswith('.xlsx'):
            df.to_excel(output_path, index=False, engine='openpyxl')
        else:
            if not output_path.endswith('.csv'):
                output_path += '.csv'
            df.to_csv(output_path, index=False)

        print("\n" + "=" * 60)
        print(f"✓ Data successfully saved to: {os.path.abspath(output_path)}")
        print("=" * 60)

        # Display summary
        print("\nData Summary:")
        print(df.to_string(index=False))

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if scraper:
            scraper.close()


if __name__ == '__main__':
    main()
