# NLCB PlayWhe Results Web Scraper

This is a Python web scraper designed to fetch NLCB (National Lotteries Control Board) PlayWhe results from [https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/](https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/) and store them in a SQLite database. It utilizes asyncio and aiohttp for asynchronous web scraping and SQLAlchemy for database operations.

## About NLCB PlayWhe

The NLCB PlayWhe is a popular lottery game in Trinidad and Tobago that draws four times daily:
- **Morning**: Early morning draw
- **Midday**: Noon draw  
- **Afternoon**: Afternoon draw
- **Evening**: Evening draw

The game involves selecting one number from 1-36, with various promo balls (Gold Ball, Megaball, Mega Ultra Ball, Mega Extreme Ball) that can multiply winnings.

## Features

- **Robots.txt Compliant**: Fully respects the website's robots.txt guidelines including crawl delays and visit time restrictions
- **Asynchronous Scraping**: Efficient fetching of PlayWhe results using asyncio and aiohttp
- **BeautifulSoup Parsing**: Robust HTML parsing using BeautifulSoup for reliable data extraction
- **SQLite Database Storage**: Structured storage of historical lottery data using SQLAlchemy ORM
- **Rate Limiting**: Implements proper rate limiting (1 request per 5 seconds) as per robots.txt
- **Visit Time Compliance**: Only scrapes during allowed hours (6 AM - 10 AM) as specified in robots.txt
- **Error Handling**: Comprehensive error handling with retry logic and connection recovery
- **HTML Response Saving**: Saves raw HTML responses for debugging and verification
- **Advanced Data Analysis**: Generates comprehensive analysis reports including:
  - Time distribution analysis (Morning/Midday/Afternoon/Evening)
  - Number frequency analysis (1-36)
  - Promo ball analysis (Gold Ball, Megaball, etc.)
  - Pattern detection and predictive insights
  - Hot and cold number identification
- **Automated Scheduling**: GitHub Actions integration for automated runs (Daily at 10 PM)

## Requirements

- Python 3.7 or higher
- aiohttp
- pandas
- SQLAlchemy
- beautifulsoup4
- lxml
- html5lib
- numpy

## Installation

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. The scraper is pre-configured to scrape NLCB PlayWhe results from the official website.
2. Run the scraper:
   ```bash
   python async_scraper.py
   ```
3. The scraper will:
   - Check if current time is within allowed visiting hours (6 AM - 10 AM)
   - Fetch PlayWhe results with proper rate limiting (1 request per 5 seconds)
   - Parse the HTML data using BeautifulSoup
   - Store results in the SQLite database
   - Generate comprehensive analysis reports
   - Save HTML responses for debugging

## Robots.txt Compliance

This scraper strictly follows the website's robots.txt guidelines:

- **Crawl-delay: 5** - 5-second delay between requests
- **Request-rate: 1/5** - Maximum 1 request per 5 seconds  
- **Visit-time: 0600-1000** - Only visits during 6 AM to 10 AM
- **User-agent identification** - Proper bot identification in headers

The scraper includes built-in checks to ensure compliance and will warn users if running outside allowed hours.

## Configuration

- **Database Settings**: Customize database name and location by modifying `Database_Name` and `Location` variables
- **Date Range**: Adjust scraping range by modifying `YEAR` and `MONTH` variables (currently set to 2024-2025)
- **Rate Limiting**: Built-in rate limiting ensures compliance with robots.txt (1 request per 5 seconds)
- **Visit Time**: Automatic time checking ensures scraping only during allowed hours (6 AM - 10 AM)

## Data Structure

The scraper extracts the following data for each PlayWhe draw:

- **Draw Date**: Date of the draw
- **Draw Number**: Unique draw identifier (e.g., 24010, 24011)
- **Time**: Time of day (Morning, Midday, Afternoon, Evening)
- **Mark**: The winning number (1-36)
- **Promo**: Promo balls (Gold Ball, Megaball, Mega Ultra Ball, Mega Extreme Ball, or combinations)

## Output Files

- **Database**: `Database/PlayWhe_Results_Database.db` - SQLite database with all scraped data
- **Analysis Summary**: `analysis_summary.md` - Generated comprehensive analysis summary for README
- **Debug Files**: `response_{month}_{year}.html` - Raw HTML responses for debugging

## Analysis Features

The scraper provides comprehensive analysis including:

### Basic Statistics
- Total draws and date range
- Unique draws and dates
- Average, median, and standard deviation of numbers

### Time Analysis
- Distribution across Morning, Midday, Afternoon, Evening
- Most and least common draw times

### Number Analysis
- Hot numbers (most frequently drawn)
- Cold numbers (least frequently drawn)
- Number range and frequency distribution

### Promo Analysis
- Frequency of different promo balls
- Combination analysis (multiple promos per draw)

### Pattern Analysis
- Consecutive number detection
- Pattern identification

### Predictive Insights
- Hot numbers to watch
- Cold numbers due for appearance
- Next predicted draw time

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvement, please open an issue or submit a pull request.

## GitHub Actions

This repository includes a GitHub Actions workflow that automatically performs analysis on the scraped PlayWhe results. The workflow is triggered on each push to the `main` branch and runs daily at 10 PM. It analyzes the data and generates comprehensive reports.

## Technical Details

### Scraping Method
- Uses POST requests with form data to search for specific month/year combinations
- Implements BeautifulSoup for robust HTML parsing
- Handles dynamic content and table structures with proper div element parsing
- Saves raw HTML responses for debugging and verification

### Error Handling
- Retry logic for connection failures (3 attempts)
- Graceful handling of parsing errors
- Comprehensive logging for debugging
- Rate limiting to prevent server overload
- Alternative parsing methods for different HTML structures

### Database Schema
- Uses SQLAlchemy ORM for data management
- Auto-incrementing primary key for data integrity
- Automatic timestamp tracking for data freshness
- Unique ID generation for each record
- Proper indexing for efficient queries

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project was inspired by the need to automate the collection of NLCB PlayWhe results for analysis and historical record-keeping.
- Special thanks to the developers of aiohttp, pandas, SQLAlchemy, and BeautifulSoup for their excellent libraries.
- Respectful web scraping practices following robots.txt guidelines and ethical data collection standards.

## Recent Analysis Results

{{analysis_placeholder}}

## 🎯 PlayWhe Analysis Summary

### 📊 Basic Statistics
- **Total Draws:** 1,415
- **Date Range:** 2025-01-01 to 2026-02-21
- **Data Span:** 416 days
- **Average Draws/Day:** 4.0
- **Confidence Level:** High

### ⏰ Time Distribution
| Time | Frequency | Percentage |
|------|-----------|------------|
| Morning | 354 | 25.0% |
| Midday | 354 | 25.0% |
| Afternoon | 354 | 25.0% |
| Evening | 353 | 24.9% |

### 🔥 Hot Numbers (Most Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 16 | 58 | 39.3 | 🔥 Over |
| 11 | 53 | 39.3 | 🔥 Over |
| 31 | 49 | 39.3 | 🔥 Over |
| 8 | 48 | 39.3 | 🔥 Over |
| 9 | 48 | 39.3 | 🔥 Over |

### ❄️ Cold Numbers (Least Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 15 | 34 | 39.3 | Normal |
| 19 | 34 | 39.3 | Normal |
| 34 | 34 | 39.3 | Normal |
| 36 | 33 | 39.3 | Normal |
| 5 | 33 | 39.3 | Normal |

### 📈 Number Analysis
- **Average Number:** 18.5
- **Median Number:** 18.0
- **Standard Deviation:** 10.1
- **Even Numbers:** 719 (50.8%)
- **Odd Numbers:** 696 (49.2%)
- **Low Numbers (1-18):** 718 (50.7%)
- **High Numbers (19-36):** 697 (49.3%)

###  Promo Analysis
| Promo Type | Frequency | Percentage |
|------------|-----------|------------|
|  | 497 | 35.1% |
| Megaball | 245 | 17.3% |
| Mega Ultra Ball | 155 | 11.0% |
| Mega Extreme Ball | 117 | 8.3% |
| Gold Ball | 92 | 6.5% |
- **Draws with Promo:** 918 (64.9%)
- **Draws without Promo:** 497 (35.1%)

### 🔍 Pattern Analysis
- **Consecutive Numbers:** 85 (6.0%)
- **Same Number Repeats:** 37 (2.6%)
- **Increasing Trends:** 676 (22533.3%)
- **Decreasing Trends:** 701 (23366.7%)

### 🔮 Predictive Insights
- **Hot Numbers:** 16, 11, 31, 8, 9
- **Cold Numbers:** 10, 6, 3, 33, 2
- **Over-Performing:** 16, 11, 31, 8, 9
- **Under-Performing:** 3, 33, 2
- **Next Predicted Time:** Morning

### 📊 Recent Trends (Last 20 Draws)
- **Recent Hot Numbers:** 21(2), 16(2), 27(1)
- **Recent Cold Numbers:** 17(1), 25(1), 23(1)

### 📈 Latest Results
- **Draw #26628** (2026-02-20) - Afternoon: Mark 19 (Megaball)
- **Draw #26629** (2026-02-20) - Evening: Mark 17 (Mega Ultra Ball, Mega Extreme Ball)
- **Draw #26630** (2026-02-21) - Morning: Mark 21 
- **Draw #26631** (2026-02-21) - Midday: Mark 25 
- **Draw #26632** (2026-02-21) - Afternoon: Mark 23 (Megaball, Mega Ultra Ball)

---
*Last updated: 2026-02-21 22:02:26*

## 🚀 Execution Summary

### 📊 Scraping Results
- **Total Records Processed:** 1,415
- **New Records Added:** 4
- **Duplicate Records Skipped:** 1411
- **Execution Time:** 70.08 seconds
- **Average Processing Speed:** 20.2 records/second

### 🔍 Data Quality
- **Database Records:** 1,411
- **Data Completeness:** 100.3% of total database
- **Date Coverage:** 416 days
- **Time Distribution Balance:** 24.9% - 25.0%

### 📈 Analysis Confidence
- **Confidence Level:** High
- **Statistical Significance:** High
- **Pattern Reliability:** Strong

---
*Execution completed at: 2026-02-21 22:02:26*
