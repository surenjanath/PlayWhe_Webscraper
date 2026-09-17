import asyncio
import aiohttp
import pandas as pd
from io import StringIO
import os
import datetime
from uuid import uuid4
import warnings
import logging
import traceback
from time import perf_counter
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Date, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
from bs4 import BeautifulSoup as bs
import numpy as np
from collections import Counter

warnings.simplefilter(action='ignore', category=FutureWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

MONTH = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
YEAR = [str(i) for i in range(2025, datetime.datetime.now().year + 1)]

cwd = os.getcwd()
Database_Name = 'PlayWhe_Results_Database.db'
Location = r'Database'
WorkingDir = os.path.join(cwd, Location)
if not os.path.exists(WorkingDir):
    os.mkdir(WorkingDir)

Database = os.path.join(WorkingDir, Database_Name)

Base = declarative_base()

class Playwhe_Result(Base):
    __tablename__ = 'playwhe_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    DrawDate = Column(Date)
    DrawNum = Column(String)
    Time = Column(String)  # Morning, Midday, Afternoon, Evening
    Mark = Column(Integer)  # The winning number (1-36)
    Promo = Column(String)  # Gold Ball, Megaball, Mega Extreme Ball, etc.
    uniqueId = Column(String)
    last_updated = Column(DateTime)
    date_created = Column(DateTime)

    def __init__(self, DrawDate, DrawNum, Time, Mark, Promo):
        self.DrawDate = DrawDate
        self.DrawNum = DrawNum
        self.Time = Time
        self.Mark = Mark
        self.Promo = Promo
        self.uniqueId = str(uuid4()).split('-')[4]
        self.date_created = datetime.datetime.now()
        self.last_updated = datetime.datetime.now()

    def __repr__(self):
        return f"<Playwhe_Result(DrawDate='{self.DrawDate}', Time='{self.Time}', Mark={self.Mark}')>"

class WebScraper:
    def __init__(self, urls):
        self.urls = urls
        self.ParsedData = []
        self.request_count = 0
        self.last_request_time = 0
        
    def check_visit_time(self):
        """Check if current time is within allowed visiting hours (0600-1000)"""
        current_hour = datetime.datetime.now().hour
        return True  # Temporarily allow all times for testing
        
    def should_respect_rate_limit(self):
        """Ensure we don't exceed 1 request per 5 seconds"""
        current_time = perf_counter()
        if current_time - self.last_request_time < 5:
            return False
        return True

    async def fetch(self, session, year, month, url):
        # Check if we're within allowed visiting hours
        if not self.check_visit_time():
            logger.warning(
                'Outside allowed visiting hours (0600-1000). Current time: %s',
                datetime.datetime.now().strftime("%H:%M")
            )
            return None

        # Ensure rate limiting
        while not self.should_respect_rate_limit():
            await asyncio.sleep(1)

        params = {
            'playwhe_month': f'{month}',
            'playwhe_year': f'{year}',
            'sid': '7bdb0e5bd65120db4a046487d5ba59b90b243ecb69127964ca720d0be9473e4f',
            'date_btn': 'SEARCH'
        }
        headers = {
            'User-Agent': 'PlayWheScraper/1.0 (Respectful bot following robots.txt guidelines)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        # Update request tracking
        self.request_count += 1
        self.last_request_time = perf_counter()

        retries = 3
        for attempt in range(retries):
            try:
                async with session.post(url, data=params, headers=headers) as response:
                    response_content = await response.content.read()

                    if response.status == 200:
                        return self._parse_response(response_content, month, year)
                    else:
                        logger.error(
                            'HTTP %d for %s-%s', response.status, month, year
                        )
                        return None

            except aiohttp.ClientConnectionError as e:
                if attempt < retries - 1:
                    logger.warning(
                        'Connection error for %s-%s (attempt %d/%d): %s',
                        month, year, attempt + 1, retries, e
                    )
                    await asyncio.sleep(2)
                else:
                    logger.error(
                        'Max retries reached for %s-%s. Last error: %s',
                        month, year, e
                    )
                    return None
            except asyncio.TimeoutError:
                if attempt < retries - 1:
                    logger.warning(
                        'Timeout for %s-%s (attempt %d/%d)',
                        month, year, attempt + 1, retries
                    )
                    await asyncio.sleep(2)
                else:
                    logger.error('Max retries reached for %s-%s due to timeout', month, year)
                    return None
            except aiohttp.ClientError as e:
                logger.error(
                    'Client error fetching %s-%s: %s', month, year, e
                )
                return None

    def _parse_response(self, response_content, month, year):
        """Parse HTML response content and return list of record dicts, or None."""
        try:
            content = response_content.decode('utf-8', errors='replace')
        except (UnicodeDecodeError, AttributeError) as e:
            logger.error('Failed to decode response for %s-%s: %s', month, year, e)
            return None

        soup = bs(content, 'html.parser')
        results_list = []

        # Look for PlayWhe results table - try multiple selectors
        table_selectors = [
            'table',
            'table.table',
            'table.results-table',
            'table#results',
            '.results table',
            'table[class*="table"]',
        ]

        html_table = None
        for selector in table_selectors:
            html_table = soup.select_one(selector)
            if html_table:
                logger.debug('Found table with selector: %s', selector)
                break

        if html_table:
            rows = html_table.find_all('tr')
            logger.info('Found %d table rows for %s-%s', len(rows), month, year)

            for row_idx, row in enumerate(rows[1:], start=2):  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) < 5:
                    continue
                try:
                    record = self._parse_row(cells, month, year, row_idx)
                    if record:
                        results_list.append(record)
                except (ValueError, IndexError) as e:
                    logger.warning(
                        'Skipping malformed row %d for %s-%s: %s',
                        row_idx, month, year, e
                    )
                    continue

        table = pd.DataFrame(results_list)
        if table.empty:
            logger.info('No data found in primary table for %s-%s, trying alternative', month, year)
            table = self.alternative_parsing(content, month, year)

        if not table.empty:
            logger.info('Scraped %d records for %s-%s', len(table), month, year)
            return table.to_dict('records')
        else:
            logger.info('No data found for %s-%s', month, year)
            return None

    def _parse_row(self, cells, month, year, row_idx):
        """Parse a single table row into a record dict.

        Raises ValueError if the row contains invalid data that cannot be recovered.
        Returns None if required fields are empty (row is skipped silently).
        """
        draw_num = cells[0].get_text(strip=True)
        date_str = cells[1].get_text(strip=True)
        time_val = cells[2].get_text(strip=True)
        mark = cells[3].get_text(strip=True)

        # Handle promo column with div elements
        promo_divs = cells[4].find_all('div')
        if promo_divs:
            promo = ', '.join([div.get_text(strip=True) for div in promo_divs])
        else:
            promo = cells[4].get_text(strip=True)

        if not (draw_num and date_str and time_val and mark):
            return None

        # Convert date format
        date_obj = self._parse_date(date_str, month, year, row_idx)

        # Convert mark to integer
        try:
            mark_int = int(mark)
        except ValueError:
            raise ValueError(
                f"Non-integer mark value '{mark}' in row {row_idx} for {month}-{year}"
            )

        return {
            'Date': date_obj,
            'Draw#': draw_num,
            'Time': time_val,
            'Mark': mark_int,
            'Promo': promo
        }

    def _parse_date(self, date_str, month, year, row_idx):
        """Parse date string into a date object.

        Raises ValueError if the date cannot be parsed in any supported format.
        """
        if '-' in date_str:
            date_parts = date_str.split('-')
            if len(date_parts) == 3:
                day, month_abbr, year_short = date_parts
                try:
                    month_num = MONTH.index(month_abbr) + 1
                except ValueError:
                    raise ValueError(
                        f"Unknown month abbreviation '{month_abbr}' in date '{date_str}' "
                        f"(row {row_idx}, {month}-{year})"
                    )
                year_full = f"20{year_short}" if len(year_short) == 2 else year_short
                return datetime.datetime.strptime(
                    f"{day}-{month_num}-{year_full}", "%d-%m-%Y"
                ).date()
            else:
                return datetime.datetime.strptime(date_str, "%d-%b-%y").date()
        else:
            return datetime.datetime.strptime(date_str, "%d-%b-%y").date()

    def alternative_parsing(self, content, month, year):
        """Alternative parsing method using regex patterns if the main table method fails."""
        import re

        try:
            soup = bs(content, 'html.parser')
            text_content = soup.get_text()
        except Exception as e:
            logger.error('Alternative parsing: failed to extract text for %s-%s: %s', month, year, e)
            return pd.DataFrame()

        results_list = []

        date_pattern = r'(\d{2})-(\w{3})-(\d{2})'
        dates = re.findall(date_pattern, text_content)

        draw_pattern = r'(\d{5})'  # 5-digit draw numbers
        draws = re.findall(draw_pattern, text_content)

        time_pattern = r'(Morning|Midday|Afternoon|Evening)'
        times = re.findall(time_pattern, text_content)

        number_pattern = r'\b([1-9]|[12]\d|3[0-6])\b'
        numbers = re.findall(number_pattern, text_content)

        if not (dates and draws and times and numbers):
            logger.info('Alternative parsing: no pattern matches for %s-%s', month, year)
            return pd.DataFrame()

        matched_count = 0
        skipped_count = 0
        for i in range(min(len(dates), len(draws), len(times), len(numbers))):
            day, month_abbr, year_short = dates[i]
            try:
                month_num = MONTH.index(month_abbr) + 1
            except ValueError:
                logger.debug(
                    'Alternative parsing: unknown month "%s" at index %d for %s-%s',
                    month_abbr, i, month, year
                )
                skipped_count += 1
                continue

            year_full = f"20{year_short}"
            try:
                date_obj = datetime.datetime.strptime(
                    f"{day}-{month_num}-{year_full}", "%d-%m-%Y"
                ).date()
            except ValueError as e:
                logger.debug(
                    'Alternative parsing: invalid date at index %d for %s-%s: %s',
                    i, month, year, e
                )
                skipped_count += 1
                continue

            try:
                mark_int = int(numbers[i])
            except ValueError:
                logger.debug(
                    'Alternative parsing: non-integer mark "%s" at index %d for %s-%s',
                    numbers[i], i, month, year
                )
                skipped_count += 1
                continue

            results_list.append({
                'Date': date_obj,
                'Draw#': draws[i],
                'Time': times[i],
                'Mark': mark_int,
                'Promo': 'Unknown'
            })
            matched_count += 1

        if skipped_count > 0:
            logger.warning(
                'Alternative parsing: %d entries skipped due to parse errors for %s-%s',
                skipped_count, month, year
            )
        if matched_count > 0:
            logger.info('Alternative parsing: extracted %d records for %s-%s', matched_count, month, year)

        return pd.DataFrame(results_list)

    async def main(self):
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            current_year = datetime.datetime.now().year
            current_month = datetime.datetime.now().strftime('%b')
            current_month_index = MONTH.index(current_month)

            # Create list of all requests to make
            requests_to_make = [
                (year, month, url)
                for year in YEAR
                for month_index, month in enumerate(MONTH)
                for url in self.urls
                if not (int(year) > current_year or (int(year) == current_year and month_index > current_month_index))
            ]

            logger.info(
                'Starting PlayWhe scraping with %d requests to process', len(requests_to_make)
            )
            logger.info('Respecting robots.txt: Visit-time 0600-1000, Request-rate 1/5, Crawl-delay 5')

            failed_requests = []
            for i, (year, month, url) in enumerate(requests_to_make, 1):
                logger.info('Processing request %d/%d: %s-%s', i, len(requests_to_make), month, year)

                data = await self.fetch(session, year, month, url)
                if data is not None:
                    self.ParsedData.extend(data)
                    logger.info('Scraped %d records for %s-%s', len(data), month, year)
                else:
                    failed_requests.append(f'{month}-{year}')
                    logger.info('No data retrieved for %s-%s', month, year)

                # Additional delay to ensure we respect the rate limit
                if i < len(requests_to_make):
                    await asyncio.sleep(5)

            if failed_requests:
                logger.warning(
                    'Failed to retrieve data for %d request(s): %s',
                    len(failed_requests), ', '.join(failed_requests[:10])
                )

def add_playwhe_data_to_db(session, playwhe_data):
    """Add PlayWhe data to database with duplicate checking.

    Raises:
        RuntimeError: If the database commit fails after all inserts.
    """
    added_count = 0
    skipped_count = 0
    error_count = 0

    for data in playwhe_data:
        try:
            existing_result = session.query(Playwhe_Result).filter_by(
                DrawNum=data['Draw#'],
                DrawDate=data['Date']
            ).first()

            if existing_result:
                skipped_count += 1
                continue

            playwhe_instance = Playwhe_Result(
                DrawDate=data['Date'],
                DrawNum=data['Draw#'],
                Time=data['Time'],
                Mark=data['Mark'],
                Promo=data['Promo']
            )
            session.add(playwhe_instance)
            added_count += 1

        except KeyError as e:
            logger.error('Missing required field %s in record: %s', e, data)
            error_count += 1
            continue
        except Exception as e:
            logger.error('Unexpected error adding record %s: %s', data, e)
            error_count += 1
            continue

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.critical('Database commit failed, rolled back %d pending inserts: %s', added_count, e)
        raise RuntimeError(f'Database commit failed: {e}') from e

    logger.info(
        'Database update: added=%d, skipped=%d, errors=%d', added_count, skipped_count, error_count
    )
    if error_count > 0:
        logger.warning('%d records failed to insert due to data errors', error_count)

    return added_count, skipped_count

def comprehensive_analysis(data):
    """Perform comprehensive analysis on PlayWhe data.

    Raises:
        ValueError: If data is empty or cannot be converted to a usable DataFrame.
    """
    if not data:
        raise ValueError('No data available for analysis.')

    df = pd.DataFrame(data)
    df['Mark'] = pd.to_numeric(df['Mark'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Drop rows where critical fields could not be parsed
    rows_before = len(df)
    df = df.dropna(subset=['Mark', 'Date'])
    rows_dropped = rows_before - len(df)
    if rows_dropped > 0:
        logger.warning('Dropped %d rows with unparseable Mark/Date values', rows_dropped)

    if df.empty:
        raise ValueError('All rows had unparseable data; cannot perform analysis.')
    
    # Basic statistics
    basic_stats = {
        'total_draws': len(df),
        'date_range': f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}",
        'unique_draws': df['Draw#'].nunique(),
        'unique_dates': df['Date'].dt.date.nunique(),
        'data_span_days': (df['Date'].max() - df['Date'].min()).days,
        'avg_draws_per_day': len(df) / df['Date'].dt.date.nunique()
    }
    
    # Time analysis
    time_distribution = df['Time'].value_counts().to_dict()
    time_analysis = {
        'time_distribution': time_distribution,
        'most_common_time': max(time_distribution, key=time_distribution.get),
        'least_common_time': min(time_distribution, key=time_distribution.get),
        'time_balance': {time: count/len(df)*100 for time, count in time_distribution.items()}
    }
    
    # Number analysis
    number_counts = df['Mark'].value_counts().sort_values(ascending=False)
    number_analysis = {
        'average_number': df['Mark'].mean(),
        'median_number': df['Mark'].median(),
        'std_deviation': df['Mark'].std(),
        'number_range': f"{df['Mark'].min()} to {df['Mark'].max()}",
        'most_common_numbers': number_counts.head(10).to_dict(),
        'least_common_numbers': number_counts.tail(10).to_dict(),
        'number_frequency': {num: count/len(df)*100 for num, count in number_counts.items()},
        'even_numbers': len(df[df['Mark'] % 2 == 0]),
        'odd_numbers': len(df[df['Mark'] % 2 == 1]),
        'low_numbers_1_18': len(df[df['Mark'] <= 18]),
        'high_numbers_19_36': len(df[df['Mark'] >= 19])
    }
    
    # Promo analysis
    promo_distribution = df['Promo'].value_counts().to_dict()
    promo_analysis = {
        'promo_distribution': promo_distribution,
        'total_promos': len(promo_distribution),
        'most_common_promo': max(promo_distribution, key=promo_distribution.get) if promo_distribution else 'None',
        'promo_frequency': {promo: count/len(df)*100 for promo, count in promo_distribution.items()},
        'draws_with_promo': len(df[df['Promo'] != '']),
        'draws_without_promo': len(df[df['Promo'] == '']),
        'promo_percentage': len(df[df['Promo'] != '']) / len(df) * 100
    }
    
    # Pattern analysis
    consecutive_count = 0
    same_number_count = 0
    number_trends = []
    
    for i in range(len(df) - 1):
        current_mark = df.iloc[i]['Mark']
        next_mark = df.iloc[i+1]['Mark']
        
        # Consecutive numbers
        if abs(current_mark - next_mark) == 1:
            consecutive_count += 1
        
        # Same number repeated
        if current_mark == next_mark:
            same_number_count += 1
        
        # Number trends
        if current_mark < next_mark:
            number_trends.append('increasing')
        elif current_mark > next_mark:
            number_trends.append('decreasing')
        else:
            number_trends.append('same')
    
    # Calculate trends
    trend_counts = pd.Series(number_trends).value_counts()
    
    patterns = {
        'consecutive_numbers': consecutive_count,
        'consecutive_percentage': (consecutive_count / len(df)) * 100,
        'same_number_repeats': same_number_count,
        'same_number_percentage': (same_number_count / len(df)) * 100,
        'increasing_trends': trend_counts.get('increasing', 0),
        'decreasing_trends': trend_counts.get('decreasing', 0),
        'trend_balance': {
            'increasing': trend_counts.get('increasing', 0) / len(trend_counts) * 100,
            'decreasing': trend_counts.get('decreasing', 0) / len(trend_counts) * 100,
            'same': trend_counts.get('same', 0) / len(trend_counts) * 100
        }
    }
    
    # Predictive insights with enhanced logic
    hot_numbers = list(number_counts.head(5).index)
    cold_numbers = list(number_counts.tail(5).index)
    next_predicted_time = max(time_distribution, key=time_distribution.get)
    
    # Calculate expected vs actual frequencies
    expected_frequency = len(df) / 36  # Expected if all numbers were equally likely
    over_performing = {num: count for num, count in number_counts.items() if count > expected_frequency * 1.2}
    under_performing = {num: count for num, count in number_counts.items() if count < expected_frequency * 0.8}
    
    predictions = {
        'hot_numbers': hot_numbers,
        'cold_numbers': cold_numbers,
        'next_predicted_time': next_predicted_time,
        'over_performing_numbers': list(over_performing.keys())[:5],
        'under_performing_numbers': list(under_performing.keys())[:5],
        'expected_frequency': expected_frequency,
        'confidence_level': 'High' if len(df) > 500 else 'Medium' if len(df) > 200 else 'Low'
    }
    
    # Recent performance analysis
    recent_draws = df.tail(20)  # Last 20 draws
    recent_trends = {
        'recent_hot_numbers': recent_draws['Mark'].value_counts().head(3).to_dict(),
        'recent_cold_numbers': recent_draws['Mark'].value_counts().tail(3).to_dict(),
        'recent_time_distribution': recent_draws['Time'].value_counts().to_dict(),
        'recent_promo_distribution': recent_draws['Promo'].value_counts().head(5).to_dict()
    }
    
    return {
        'basic_stats': basic_stats,
        'time_analysis': time_analysis,
        'number_analysis': number_analysis,
        'promo_analysis': promo_analysis,
        'patterns': patterns,
        'predictions': predictions,
        'recent_trends': recent_trends
    }



def generate_markdown_summary(analysis_results, latest_entries):
    """Generate Markdown-compatible summary for README"""
    
    markdown_summary = f"""
## 🎯 PlayWhe Analysis Summary

### 📊 Basic Statistics
- **Total Draws:** {analysis_results['basic_stats']['total_draws']:,}
- **Date Range:** {analysis_results['basic_stats']['date_range']}
- **Data Span:** {analysis_results['basic_stats']['data_span_days']} days
- **Average Draws/Day:** {analysis_results['basic_stats']['avg_draws_per_day']:.1f}
- **Confidence Level:** {analysis_results['predictions']['confidence_level']}

### ⏰ Time Distribution
| Time | Frequency | Percentage |
|------|-----------|------------|
{chr(10).join([f"| {time} | {count} | {analysis_results['time_analysis']['time_balance'][time]:.1f}% |" for time, count in analysis_results['time_analysis']['time_distribution'].items()])}

### 🔥 Hot Numbers (Most Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
{chr(10).join([f"| {num} | {freq} | {analysis_results['predictions']['expected_frequency']:.1f} | {'🔥 Over' if num in analysis_results['predictions']['over_performing_numbers'] else 'Normal'} |" for num, freq in list(analysis_results['number_analysis']['most_common_numbers'].items())[:5]])}

### ❄️ Cold Numbers (Least Frequent)
| Number | Frequency | Expected | Performance |
|--------|-----------|----------|-------------|
{chr(10).join([f"| {num} | {freq} | {analysis_results['predictions']['expected_frequency']:.1f} | {'❄️ Under' if num in analysis_results['predictions']['under_performing_numbers'] else 'Normal'} |" for num, freq in list(analysis_results['number_analysis']['least_common_numbers'].items())[:5]])}

### 📈 Number Analysis
- **Average Number:** {analysis_results['number_analysis']['average_number']:.1f}
- **Median Number:** {analysis_results['number_analysis']['median_number']:.1f}
- **Standard Deviation:** {analysis_results['number_analysis']['std_deviation']:.1f}
- **Even Numbers:** {analysis_results['number_analysis']['even_numbers']} ({analysis_results['number_analysis']['even_numbers']/analysis_results['basic_stats']['total_draws']*100:.1f}%)
- **Odd Numbers:** {analysis_results['number_analysis']['odd_numbers']} ({analysis_results['number_analysis']['odd_numbers']/analysis_results['basic_stats']['total_draws']*100:.1f}%)
- **Low Numbers (1-18):** {analysis_results['number_analysis']['low_numbers_1_18']} ({analysis_results['number_analysis']['low_numbers_1_18']/analysis_results['basic_stats']['total_draws']*100:.1f}%)
- **High Numbers (19-36):** {analysis_results['number_analysis']['high_numbers_19_36']} ({analysis_results['number_analysis']['high_numbers_19_36']/analysis_results['basic_stats']['total_draws']*100:.1f}%)

###  Promo Analysis
| Promo Type | Frequency | Percentage |
|------------|-----------|------------|
{chr(10).join([f"| {promo} | {count} | {analysis_results['promo_analysis']['promo_frequency'][promo]:.1f}% |" for promo, count in list(analysis_results['promo_analysis']['promo_distribution'].items())[:5]])}
- **Draws with Promo:** {analysis_results['promo_analysis']['draws_with_promo']} ({analysis_results['promo_analysis']['promo_percentage']:.1f}%)
- **Draws without Promo:** {analysis_results['promo_analysis']['draws_without_promo']} ({100-analysis_results['promo_analysis']['promo_percentage']:.1f}%)

### 🔍 Pattern Analysis
- **Consecutive Numbers:** {analysis_results['patterns']['consecutive_numbers']} ({analysis_results['patterns']['consecutive_percentage']:.1f}%)
- **Same Number Repeats:** {analysis_results['patterns']['same_number_repeats']} ({analysis_results['patterns']['same_number_percentage']:.1f}%)
- **Increasing Trends:** {analysis_results['patterns']['increasing_trends']} ({analysis_results['patterns']['trend_balance']['increasing']:.1f}%)
- **Decreasing Trends:** {analysis_results['patterns']['decreasing_trends']} ({analysis_results['patterns']['trend_balance']['decreasing']:.1f}%)

### 🔮 Predictive Insights
- **Hot Numbers:** {', '.join(map(str, analysis_results['predictions']['hot_numbers']))}
- **Cold Numbers:** {', '.join(map(str, analysis_results['predictions']['cold_numbers']))}
- **Over-Performing:** {', '.join(map(str, analysis_results['predictions']['over_performing_numbers']))}
- **Under-Performing:** {', '.join(map(str, analysis_results['predictions']['under_performing_numbers']))}
- **Next Predicted Time:** {analysis_results['predictions']['next_predicted_time']}

### 📊 Recent Trends (Last 20 Draws)
- **Recent Hot Numbers:** {', '.join([f"{num}({freq})" for num, freq in analysis_results['recent_trends']['recent_hot_numbers'].items()])}
- **Recent Cold Numbers:** {', '.join([f"{num}({freq})" for num, freq in analysis_results['recent_trends']['recent_cold_numbers'].items()])}

### 📈 Latest Results
{chr(10).join([f"- **Draw #{entry.get('Draw#', 'N/A')}** ({entry.get('Date', 'N/A')}) - {entry.get('Time', 'N/A')}: Mark {entry.get('Mark', 'N/A')} {'(' + entry.get('Promo', '') + ')' if entry.get('Promo') else ''}" for entry in latest_entries[-5:]])}

---
*Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return markdown_summary

async def run_scraper(urls, db_session):
    start_time = perf_counter()
    scraper = WebScraper(urls)
    await scraper.main()

    if not scraper.ParsedData:
        logger.error('No data was scraped. Check the website structure or try again later.')
        return

    # Get database counts before adding new data
    total_db_records = db_session.query(Playwhe_Result).count()

    # Add data to database (may raise RuntimeError on commit failure)
    new_records_count, duplicate_records_count = add_playwhe_data_to_db(db_session, scraper.ParsedData)

    execution_time = perf_counter() - start_time

    # Perform comprehensive analysis
    try:
        analysis_results = comprehensive_analysis(scraper.ParsedData)
    except ValueError as e:
        logger.error('Analysis failed: %s', e)
        logger.info('Scraping completed but analysis could not run. Data was still saved to DB.')
        return

    latest_entries = scraper.ParsedData[-10:] if len(scraper.ParsedData) >= 10 else scraper.ParsedData

    # Generate Markdown summary for README
    try:
        markdown_summary = generate_markdown_summary(analysis_results, latest_entries)
    except (KeyError, TypeError, ZeroDivisionError) as e:
        logger.error('Failed to generate markdown summary: %s', e)
        return

    try:
        with open('analysis_summary.md', 'w', encoding='utf-8') as file:
            file.write(markdown_summary)
    except OSError as e:
        logger.error('Failed to write analysis_summary.md: %s', e)
        return

    # Avoid division by zero if total_db_records is 0
    db_completeness = (
        f"{len(scraper.ParsedData) / total_db_records * 100:.1f}%"
        if total_db_records > 0 else 'N/A (empty database)'
    )

    execution_summary = f"""
## Execution Summary

### Scraping Results
- **Total Records Processed:** {len(scraper.ParsedData):,}
- **New Records Added:** {new_records_count}
- **Duplicate Records Skipped:** {duplicate_records_count}
- **Execution Time:** {execution_time:.2f} seconds
- **Average Processing Speed:** {len(scraper.ParsedData)/execution_time:.1f} records/second

### Data Quality
- **Database Records:** {total_db_records:,}
- **Data Completeness:** {db_completeness} of total database
- **Date Coverage:** {analysis_results['basic_stats']['data_span_days']} days
- **Time Distribution Balance:** {min(analysis_results['time_analysis']['time_balance'].values()):.1f}% - {max(analysis_results['time_analysis']['time_balance'].values()):.1f}%

### Analysis Confidence
- **Confidence Level:** {analysis_results['predictions']['confidence_level']}
- **Statistical Significance:** {'High' if analysis_results['basic_stats']['total_draws'] > 500 else 'Medium' if analysis_results['basic_stats']['total_draws'] > 200 else 'Low'}
- **Pattern Reliability:** {'Strong' if analysis_results['patterns']['consecutive_percentage'] < 10 else 'Moderate'}

---
*Execution completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    try:
        with open('analysis_summary.md', 'a', encoding='utf-8') as file:
            file.write(execution_summary)
    except OSError as e:
        logger.error('Failed to append execution summary: %s', e)

    logger.info('Analysis report generated successfully.')
    logger.info('Total records processed: %d', len(scraper.ParsedData))
    logger.info('Summary saved to: analysis_summary.md')

if __name__ == "__main__":
    start = perf_counter()

    # Check if we're within allowed visiting hours before starting
    current_hour = datetime.datetime.now().hour
    if not (6 <= current_hour < 10):
        logger.warning(
            'Current time is %s. Robots.txt specifies Visit-time: 0600-1000. '
            'Continuing anyway for testing purposes.',
            datetime.datetime.now().strftime("%H:%M")
        )

    urls = ['https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/']

    engine = create_engine(f'sqlite:///{Database}', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        asyncio.run(run_scraper(urls, db_session))
    except RuntimeError as e:
        logger.critical('Fatal database error: %s', e)
    except aiohttp.ClientError as e:
        logger.critical('Fatal network error: %s', e)
    except KeyboardInterrupt:
        logger.info('Scraper interrupted by user.')
    except Exception as e:
        logger.critical('Unexpected error: %s\n%s', e, traceback.format_exc())
    finally:
        db_session.close()

    stop = perf_counter()
    logger.info('Total execution time: %.2f seconds', stop - start)
