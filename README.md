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
- **Total Draws:** 161
- **Date Range:** 2026-11-03 to 2026-11-03
- **Data Span:** 0 days
- **Average Draws/Day:** 161.0
- **Confidence Level:** Low

### ⏰ Time Distribution
| Time | Frequency | Percentage |
|------|-----------|------------|
| 7 | 23 | 14.3% |
| 31 | 23 | 14.3% |
| 17 | 23 | 14.3% |
| 15 | 23 | 14.3% |
| 25 | 23 | 14.3% |
| 28 | 23 | 14.3% |
| 6 | 23 | 14.3% |

### 🔥 Hot Numbers (Most Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 32 | 23 | 4.5 | 🔥 Over |
| 23 | 23 | 4.5 | 🔥 Over |
| 31 | 23 | 4.5 | 🔥 Over |
| 25 | 23 | 4.5 | 🔥 Over |
| 4 | 23 | 4.5 | 🔥 Over |

### ❄️ Cold Numbers (Least Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 32 | 23 | 4.5 | Normal |
| 23 | 23 | 4.5 | Normal |
| 31 | 23 | 4.5 | Normal |
| 25 | 23 | 4.5 | Normal |
| 4 | 23 | 4.5 | Normal |

### 📈 Number Analysis
- **Average Number:** 21.7
- **Median Number:** 25.0
- **Standard Deviation:** 10.4
- **Even Numbers:** 69 (42.9%)
- **Odd Numbers:** 92 (57.1%)
- **Low Numbers (1-18):** 46 (28.6%)
- **High Numbers (19-36):** 115 (71.4%)

###  Promo Analysis
| Promo Type | Frequency | Percentage |
|------------|-----------|------------|
| 35 | 23 | 14.3% |
| 14 | 23 | 14.3% |
| 25 | 23 | 14.3% |
| 6 | 23 | 14.3% |
| 32 | 23 | 14.3% |
- **Draws with Promo:** 161 (100.0%)
- **Draws without Promo:** 0 (0.0%)

### 🔍 Pattern Analysis
- **Consecutive Numbers:** 0 (0.0%)
- **Same Number Repeats:** 0 (0.0%)
- **Increasing Trends:** 68 (3400.0%)
- **Decreasing Trends:** 92 (4600.0%)

### 🔮 Predictive Insights
- **Hot Numbers:** 32, 23, 31, 25, 4
- **Cold Numbers:** 31, 25, 4, 29, 8
- **Over-Performing:** 32, 23, 31, 25, 4
- **Under-Performing:** 
- **Next Predicted Time:** 7

### 📊 Recent Trends (Last 20 Draws)
- **Recent Hot Numbers:** 23(3), 31(3), 25(3)
- **Recent Cold Numbers:** 29(3), 8(3), 32(2)

### 📈 Latest Results
- **Draw #29-Sep** (2026-11-03) - 17: Mark 31 (25)
- **Draw #06-Oct** (2026-11-03) - 15: Mark 25 (6)
- **Draw #13-Oct** (2026-11-03) - 25: Mark 4 (32)
- **Draw #20-Oct** (2026-11-03) - 28: Mark 29 (22)
- **Draw #27-Oct** (2026-11-03) - 6: Mark 8 (3)

---
*Last updated: 2026-11-03 03:07:56*

## 🚀 Execution Summary

### 📊 Scraping Results
- **Total Records Processed:** 161
- **New Records Added:** 7
- **Duplicate Records Skipped:** 154
- **Execution Time:** 116.93 seconds
- **Average Processing Speed:** 1.4 records/second

### 🔍 Data Quality
- **Database Records:** 2,407
- **Data Completeness:** 6.7% of total database
- **Date Coverage:** 0 days
- **Time Distribution Balance:** 14.3% - 14.3%

### 📈 Analysis Confidence
- **Confidence Level:** Low
- **Statistical Significance:** Low
- **Pattern Reliability:** Strong

---
*Execution completed at: 2026-11-03 03:07:56*
