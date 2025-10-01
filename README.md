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
- **Total Draws:** 923
- **Date Range:** 2025-01-01 to 2025-10-01
- **Data Span:** 273 days
- **Average Draws/Day:** 4.0
- **Confidence Level:** High

### ⏰ Time Distribution
| Time | Frequency | Percentage |
|------|-----------|------------|
| Morning | 231 | 25.0% |
| Midday | 231 | 25.0% |
| Afternoon | 231 | 25.0% |
| Evening | 230 | 24.9% |

### 🔥 Hot Numbers (Most Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 11 | 40 | 25.6 | 🔥 Over |
| 16 | 39 | 25.6 | 🔥 Over |
| 32 | 35 | 25.6 | 🔥 Over |
| 31 | 32 | 25.6 | 🔥 Over |
| 20 | 31 | 25.6 | 🔥 Over |

### ❄️ Cold Numbers (Least Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 19 | 22 | 25.6 | Normal |
| 15 | 21 | 25.6 | Normal |
| 29 | 21 | 25.6 | Normal |
| 34 | 21 | 25.6 | Normal |
| 3 | 20 | 25.6 | ❄️ Under |

### 📈 Number Analysis
- **Average Number:** 18.7
- **Median Number:** 18.0
- **Standard Deviation:** 10.1
- **Even Numbers:** 468 (50.7%)
- **Odd Numbers:** 455 (49.3%)
- **Low Numbers (1-18):** 466 (50.5%)
- **High Numbers (19-36):** 457 (49.5%)

###  Promo Analysis
| Promo Type | Frequency | Percentage |
|------------|-----------|------------|
|  | 338 | 36.6% |
| Megaball | 178 | 19.3% |
| Mega Ultra Ball | 113 | 12.2% |
| Mega Extreme Ball | 92 | 10.0% |
| Megaball, Mega Ultra Ball | 64 | 6.9% |
- **Draws with Promo:** 585 (63.4%)
- **Draws without Promo:** 338 (36.6%)

### 🔍 Pattern Analysis
- **Consecutive Numbers:** 58 (6.3%)
- **Same Number Repeats:** 21 (2.3%)
- **Increasing Trends:** 441 (14700.0%)
- **Decreasing Trends:** 460 (15333.3%)

### 🔮 Predictive Insights
- **Hot Numbers:** 11, 16, 32, 31, 20
- **Cold Numbers:** 1, 33, 22, 6, 2
- **Over-Performing:** 11, 16, 32, 31, 20
- **Under-Performing:** 3, 1, 33, 22, 6
- **Next Predicted Time:** Morning

### 📊 Recent Trends (Last 20 Draws)
- **Recent Hot Numbers:** 36(2), 16(2), 17(2)
- **Recent Cold Numbers:** 25(1), 29(1), 35(1)

### 📈 Latest Results
- **Draw #26136** (2025-09-30) - Afternoon: Mark 14 
- **Draw #26137** (2025-09-30) - Evening: Mark 6 (Megaball)
- **Draw #26138** (2025-10-01) - Morning: Mark 25 
- **Draw #26139** (2025-10-01) - Midday: Mark 29 
- **Draw #26140** (2025-10-01) - Afternoon: Mark 35 (Megaball, Mega Ultra Ball)

---
*Last updated: 2025-10-01 22:02:01*

## 🚀 Execution Summary

### 📊 Scraping Results
- **Total Records Processed:** 923
- **New Records Added:** 4
- **Duplicate Records Skipped:** 919
- **Execution Time:** 48.65 seconds
- **Average Processing Speed:** 19.0 records/second

### 🔍 Data Quality
- **Database Records:** 919
- **Data Completeness:** 100.4% of total database
- **Date Coverage:** 273 days
- **Time Distribution Balance:** 24.9% - 25.0%

### 📈 Analysis Confidence
- **Confidence Level:** High
- **Statistical Significance:** High
- **Pattern Reliability:** Strong

---
*Execution completed at: 2025-10-01 22:02:01*
