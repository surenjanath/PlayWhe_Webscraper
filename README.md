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
- **Total Draws:** 867
- **Date Range:** 2025-01-01 to 2025-09-15
- **Data Span:** 257 days
- **Average Draws/Day:** 4.0
- **Confidence Level:** High

### ⏰ Time Distribution
| Time | Frequency | Percentage |
|------|-----------|------------|
| Morning | 217 | 25.0% |
| Midday | 217 | 25.0% |
| Afternoon | 217 | 25.0% |
| Evening | 216 | 24.9% |

### 🔥 Hot Numbers (Most Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 16 | 36 | 24.1 | 🔥 Over |
| 11 | 35 | 24.1 | 🔥 Over |
| 32 | 32 | 24.1 | 🔥 Over |
| 20 | 31 | 24.1 | 🔥 Over |
| 31 | 30 | 24.1 | 🔥 Over |

### ❄️ Cold Numbers (Least Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
| 12 | 21 | 24.1 | Normal |
| 19 | 20 | 24.1 | Normal |
| 33 | 20 | 24.1 | Normal |
| 29 | 20 | 24.1 | Normal |
| 36 | 20 | 24.1 | Normal |

### 📈 Number Analysis
- **Average Number:** 18.8
- **Median Number:** 19.0
- **Standard Deviation:** 10.1
- **Even Numbers:** 441 (50.9%)
- **Odd Numbers:** 426 (49.1%)
- **Low Numbers (1-18):** 433 (49.9%)
- **High Numbers (19-36):** 434 (50.1%)

###  Promo Analysis
| Promo Type | Frequency | Percentage |
|------------|-----------|------------|
|  | 319 | 36.8% |
| Megaball | 168 | 19.4% |
| Mega Ultra Ball | 104 | 12.0% |
| Mega Extreme Ball | 83 | 9.6% |
| Megaball, Mega Ultra Ball | 59 | 6.8% |
- **Draws with Promo:** 548 (63.2%)
- **Draws without Promo:** 319 (36.8%)

### 🔍 Pattern Analysis
- **Consecutive Numbers:** 54 (6.2%)
- **Same Number Repeats:** 18 (2.1%)
- **Increasing Trends:** 413 (13766.7%)
- **Decreasing Trends:** 435 (14500.0%)

### 🔮 Predictive Insights
- **Hot Numbers:** 16, 11, 32, 20, 31
- **Cold Numbers:** 3, 1, 6, 22, 2
- **Over-Performing:** 16, 11, 32, 20, 31
- **Under-Performing:** 3, 1, 6, 22, 2
- **Next Predicted Time:** Morning

### 📊 Recent Trends (Last 20 Draws)
- **Recent Hot Numbers:** 20(3), 13(2), 32(2)
- **Recent Cold Numbers:** 16(1), 12(1), 26(1)

### 📈 Latest Results
- **Draw #26080** (2025-09-13) - Afternoon: Mark 22 (Mega Ultra Ball)
- **Draw #26081** (2025-09-13) - Evening: Mark 20 (Megaball)
- **Draw #26082** (2025-09-15) - Morning: Mark 20 (Mega Ultra Ball)
- **Draw #26083** (2025-09-15) - Midday: Mark 22 (Megaball)
- **Draw #26084** (2025-09-15) - Afternoon: Mark 26 

---
*Last updated: 2025-09-15 22:02:11*

## 🚀 Execution Summary

### 📊 Scraping Results
- **Total Records Processed:** 867
- **New Records Added:** 3
- **Duplicate Records Skipped:** 864
- **Execution Time:** 45.50 seconds
- **Average Processing Speed:** 19.1 records/second

### 🔍 Data Quality
- **Database Records:** 864
- **Data Completeness:** 100.3% of total database
- **Date Coverage:** 257 days
- **Time Distribution Balance:** 24.9% - 25.0%

### 📈 Analysis Confidence
- **Confidence Level:** High
- **Statistical Significance:** High
- **Pattern Reliability:** Strong

---
*Execution completed at: 2025-09-15 22:02:11*
