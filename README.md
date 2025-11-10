# UIPath

## Netflix & Rotten Tomatoes Movie Scraper

This automation randomly extracts 5 movies from the top 10 most-watched movies on Netflix and retrieves detailed information from Rotten Tomatoes.

### Features

- Scrapes the top 10 movies from [Netflix Tudum Top 10](https://www.netflix.com/tudum/top10/)
- Randomly selects 5 movies from the top 10
- For each selected movie, retrieves from [Rotten Tomatoes](https://www.rottentomatoes.com/):
  - Movie duration
  - Tomatometer score (critics rating)
  - Popcornmeter score (audience rating)
  - Movie description
- Exports data to CSV or Excel format
- Handles missing data gracefully (displays "Not available!" for unavailable information)

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser installed
- ChromeDriver (compatible with your Chrome version)

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install ChromeDriver:

**Option 1: Automatic (Recommended)**
```bash
pip install webdriver-manager
```
If using this option, update the script to use WebDriver Manager.

**Option 2: Manual**
- Download ChromeDriver from https://chromedriver.chromium.org/
- Ensure it matches your Chrome browser version
- Add ChromeDriver to your system PATH

**Linux/Mac:**
```bash
# Download ChromeDriver
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# Extract and move to /usr/local/bin
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

**Windows:**
- Download ChromeDriver from the link above
- Extract to a folder (e.g., C:\chromedriver)
- Add the folder to your system PATH

### Usage

**Basic usage (saves to movies_data.csv in current directory):**
```bash
python netflix_rotten_tomatoes_scraper.py
```

**Specify custom output file:**
```bash
python netflix_rotten_tomatoes_scraper.py --output /path/to/output.csv
```

**Export to Excel format:**
```bash
python netflix_rotten_tomatoes_scraper.py --output movies_data.xlsx
```

**Run with visible browser (for debugging):**
```bash
python netflix_rotten_tomatoes_scraper.py --no-headless
```

### Command Line Arguments

- `--output`, `-o`: Specify the output file path (default: movies_data.csv)
  - Supports .csv and .xlsx extensions
- `--headless`: Run browser in headless mode (default: True)
- `--no-headless`: Run browser in visible mode for debugging

### Output Format

The script generates a table with the following columns:

| Column | Description |
|--------|-------------|
| movie | Movie title |
| duration | Movie runtime |
| tomatometer | Critics score (Tomatometer) |
| popcornmeter | Audience score (Popcornmeter) |
| description | Movie synopsis |

If any information is unavailable, the cell will display "Not available!"

### Example Output

```
movie                    duration    tomatometer  popcornmeter  description
The Movie Title 1        2h 15m      85%          90%           A thrilling adventure...
The Movie Title 2        1h 45m      Not available! 75%         An inspiring story...
```

### Troubleshooting

**Issue: ChromeDriver version mismatch**
- Solution: Ensure ChromeDriver version matches your Chrome browser version

**Issue: Selenium can't find Chrome**
- Solution: Install Google Chrome or specify the Chrome binary location in the script

**Issue: 403 Forbidden or Access Denied**
- Solution: The script uses Selenium with proper headers to avoid detection, but websites may still block requests. Try running with `--no-headless` flag.

**Issue: Missing data in output**
- Solution: This is expected behavior when Rotten Tomatoes doesn't have certain information for a movie. The script will display "Not available!"

### Notes

- The script includes delays between requests to be respectful to the websites' servers
- Scraping may take a few minutes depending on network speed
- If automatic scraping fails, the script will prompt for manual input of movie titles
- Some movies on Netflix might not be available on Rotten Tomatoes

### Legal & Ethical Considerations

This tool is for educational purposes. Please:
- Use responsibly and respect the websites' Terms of Service
- Don't overload servers with excessive requests
- Consider rate limiting if running multiple times

### License

This project is provided as-is for educational purposes.