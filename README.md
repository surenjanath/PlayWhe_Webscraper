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
- **Total Draws:** 1,359
- **Date Range:** 2025-01-01 to 2026-02-07
- **Data Span:** 402 days
- **Average Draws/Day:** 4.0
- **Confidence Level:** High

### ⏰ Time Distribution
| Time | Frequency | Percentage |
|------|-----------|------------|
| Morning | 340 | 25.0% |
| Midday | 340 | 25.0% |
| Afternoon | 340 | 25.0% |
| Evening | 339 | 24.9% |

### 🔥 Hot Numbers (Most Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 11 | 53 | 37.8 | 🔥 Over |
| 16 | 53 | 37.8 | 🔥 Over |
| 31 | 49 | 37.8 | 🔥 Over |
| 18 | 47 | 37.8 | 🔥 Over |
| 9 | 47 | 37.8 | 🔥 Over |

### ❄️ Cold Numbers (Least Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 36 | 33 | 37.8 | Normal |
| 19 | 33 | 37.8 | Normal |
| 10 | 32 | 37.8 | Normal |
| 5 | 32 | 37.8 | Normal |
| 34 | 31 | 37.8 | Normal |

### 📈 Number Analysis
- **Average Number:** 18.6
- **Median Number:** 18.0
- **Standard Deviation:** 10.1
- **Even Numbers:** 687 (50.6%)
- **Odd Numbers:** 672 (49.4%)
- **Low Numbers (1-18):** 687 (50.6%)
- **High Numbers (19-36):** 672 (49.4%)

###  Promo Analysis
| Promo Type | Frequency | Percentage |
|------------|-----------|------------|
|  | 478 | 35.2% |
| Megaball | 234 | 17.2% |
| Mega Ultra Ball | 152 | 11.2% |
| Mega Extreme Ball | 113 | 8.3% |
| Gold Ball | 88 | 6.5% |
- **Draws with Promo:** 881 (64.8%)
- **Draws without Promo:** 478 (35.2%)

### 🔍 Pattern Analysis
- **Consecutive Numbers:** 84 (6.2%)
- **Same Number Repeats:** 36 (2.6%)
- **Increasing Trends:** 650 (21666.7%)
- **Decreasing Trends:** 672 (22400.0%)

### 🔮 Predictive Insights
- **Hot Numbers:** 11, 16, 31, 18, 9
- **Cold Numbers:** 17, 6, 3, 33, 2
- **Over-Performing:** 11, 16, 31, 18, 9
- **Under-Performing:** 6, 3, 33, 2
- **Next Predicted Time:** Morning

### 📊 Recent Trends (Last 20 Draws)
- **Recent Hot Numbers:** 33(2), 35(2), 10(2)
- **Recent Cold Numbers:** 23(1), 19(1), 6(1)

### 📈 Latest Results
- **Draw #26572** (2026-02-06) - Afternoon: Mark 6 (Megaball)
- **Draw #26573** (2026-02-06) - Evening: Mark 10 (Mega Extreme Ball)
- **Draw #26574** (2026-02-07) - Morning: Mark 9 
- **Draw #26575** (2026-02-07) - Midday: Mark 35 
- **Draw #26576** (2026-02-07) - Afternoon: Mark 10 (Megaball)

---
*Last updated: 2026-02-07 22:13:04*

## 🚀 Execution Summary

### 📊 Scraping Results
- **Total Records Processed:** 1,359
- **New Records Added:** 4
- **Duplicate Records Skipped:** 1355
- **Execution Time:** 70.40 seconds
- **Average Processing Speed:** 19.3 records/second

### 🔍 Data Quality
- **Database Records:** 1,355
- **Data Completeness:** 100.3% of total database
- **Date Coverage:** 402 days
- **Time Distribution Balance:** 24.9% - 25.0%

### 📈 Analysis Confidence
- **Confidence Level:** High
- **Statistical Significance:** High
- **Pattern Reliability:** Strong

---
*Execution completed at: 2026-02-07 22:13:04*
