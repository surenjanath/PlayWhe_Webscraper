import asyncio
import aiohttp
import pandas as pd
import datetime
import warnings
from time import perf_counter
from bs4 import BeautifulSoup as bs
import numpy as np

from config import (
    MONTH, YEAR, PLAYWHE_URL, CRAWL_DELAY_SECONDS,
    MAX_RETRIES, HTTP_HEADERS, build_search_params,
)
from utils import parse_draw_date, safe_int, is_within_visit_hours, extract_patterns
from db import PlaywheResult, get_engine, get_session, add_playwhe_data

warnings.simplefilter(action='ignore', category=FutureWarning)

class WebScraper:
    def __init__(self, urls):
        self.urls = urls
        self.ParsedData = []
        self.request_count = 0
        self.last_request_time = 0
        
    def should_respect_rate_limit(self):
        """Ensure we don't exceed 1 request per 5 seconds"""
        current_time = perf_counter()
        if current_time - self.last_request_time < CRAWL_DELAY_SECONDS:
            return False
        return True

    async def fetch(self, session, year, month, url):
        # Ensure rate limiting
        while not self.should_respect_rate_limit():
            await asyncio.sleep(1)

        params = build_search_params(month, year)
           
        # Update request tracking
        self.request_count += 1
        self.last_request_time = perf_counter()

        for attempt in range(MAX_RETRIES):
            try:
                async with session.post(url, data=params, headers=HTTP_HEADERS) as response:
                    # Save the raw HTML response for debugging
                    response_content = await response.content.read()
                    # filename = f'response_{month}_{year}.html'
                    # with open(filename, 'wb') as file:
                    #     file.write(response_content)
                    # print(f'[*] Saved response to: {filename}')

                    if response.status == 200:
                        try:
                            # Decode the raw response content
                            content = response_content.decode('utf-8', errors='ignore')
                            
                            # Parse the HTML with BeautifulSoup
                            soup = bs(content, 'html.parser')
                            
                            results_list = []
                            
                            html_table = self._find_results_table(soup)
                            
                            if html_table:
                                results_list = self._parse_table_rows(html_table)
                            
                            # Create DataFrame and check if it's empty
                            table = pd.DataFrame(results_list)
                            if table.empty:
                                print(f'[*] No data found in table for {month}-{year}')
                                # Try alternative parsing method
                                table = self.alternative_parsing(content, month, year)
                            
                            if not table.empty:
                                print('[*] Data Scraped : ', params['playwhe_month'], params['playwhe_year'])
                                return table.to_dict('records')
                            else:
                                print(f'[*] No data found for {month}-{year}')
                                return None

                        except Exception as e:
                            print(f'[*] Error {e} Occurred : {month}-{year}')
                            return None
                    else:
                        print(f'[*] Error {response.status} Occurred while fetching data for {month}-{year}')
                        return None
                        
            except aiohttp.ClientConnectionError:
                if attempt < MAX_RETRIES - 1:
                    print(f'[*] Connection error occurred. Retrying... Attempt {attempt + 1}/{MAX_RETRIES}')
                    await asyncio.sleep(2)
                else:
                    print('[*] Maximum retries reached. Unable to establish connection.')
                    return None

    @staticmethod
    def _find_results_table(soup):
        """Try several CSS selectors to locate the results table."""
        selectors = [
            'table', 'table.table', 'table.results-table',
            'table#results', '.results table', 'table[class*="table"]',
        ]
        for selector in selectors:
            table = soup.select_one(selector)
            if table:
                print(f'[*] Found table with selector: {selector}')
                return table
        return None

    @staticmethod
    def _parse_table_rows(html_table):
        """Extract result dicts from an HTML <table> element."""
        results = []
        rows = html_table.find_all('tr')
        print(f'[*] Found {len(rows)} table rows')

        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 5:
                continue
            try:
                draw_num = cells[0].get_text(strip=True)
                date_str = cells[1].get_text(strip=True)
                time_val = cells[2].get_text(strip=True)
                mark_str = cells[3].get_text(strip=True)

                promo_divs = cells[4].find_all('div')
                promo = (
                    ', '.join(d.get_text(strip=True) for d in promo_divs)
                    if promo_divs
                    else cells[4].get_text(strip=True)
                )

                if draw_num and date_str and time_val and mark_str:
                    results.append({
                        'Date': parse_draw_date(date_str),
                        'Draw#': draw_num,
                        'Time': time_val,
                        'Mark': safe_int(mark_str),
                        'Promo': promo,
                    })
            except Exception as e:
                print(f'[*] Error parsing row: {e}')
                continue
        return results

    def alternative_parsing(self, content, month, year):
        """Alternative parsing method if the main method fails"""
        try:
            soup = bs(content, 'html.parser')
            text_content = soup.get_text()
            matches = extract_patterns(text_content)

            dates = matches['dates']
            draws = matches['draws']
            times = matches['times']
            numbers = matches['numbers']

            results_list = []
            if dates and draws and times and numbers:
                for i in range(min(len(dates), len(draws), len(times), len(numbers))):
                    try:
                        date_str = '-'.join(dates[i])
                        results_list.append({
                            'Date': parse_draw_date(date_str),
                            'Draw#': draws[i],
                            'Time': times[i],
                            'Mark': safe_int(numbers[i]),
                            'Promo': 'Unknown',
                        })
                    except Exception:
                        continue

            return pd.DataFrame(results_list)
        except Exception as e:
            print(f'[*] Alternative parsing failed: {e}')
            return pd.DataFrame()

    async def main(self):
        async with aiohttp.ClientSession() as session:
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

            print(f'[*] Starting PlayWhe scraping with {len(requests_to_make)} requests to process')
            print(f'[*] Respecting robots.txt: Visit-time 0600-1000, Request-rate 1/{CRAWL_DELAY_SECONDS}, Crawl-delay {CRAWL_DELAY_SECONDS}')
            
            for i, (year, month, url) in enumerate(requests_to_make, 1):
                print(f'[*] Processing request {i}/{len(requests_to_make)}: {month}-{year}')
                print(f'[*] URL: {url}')
                
                data = await self.fetch(session, year, month, url)
                if data is not None:
                    self.ParsedData.extend(data)
                    print(f'[*] Successfully scraped {len(data)} records for {month}-{year}')
                else:
                    print(f'[*] No data retrieved for {month}-{year}')
                
                # Additional delay to ensure we respect the rate limit
                if i < len(requests_to_make):
                    print(f'[*] Waiting {CRAWL_DELAY_SECONDS} seconds before next request...')
                    await asyncio.sleep(CRAWL_DELAY_SECONDS)


def comprehensive_analysis(data):
    """Perform comprehensive analysis on PlayWhe data"""
    if not data:
        return "No data available for analysis."
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(data)
    df['Mark'] = pd.to_numeric(df['Mark'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
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
    
    if scraper.ParsedData:
        # Get database counts before adding new data
        total_db_records = db_session.query(PlaywheResult).count()

        # Add data to database and get results
        new_records_count, duplicate_records_count = add_playwhe_data(db_session, scraper.ParsedData)
        
        # Calculate execution time
        execution_time = perf_counter() - start_time
        
        # Perform comprehensive analysis
        analysis_results = comprehensive_analysis(scraper.ParsedData)
        
        # Get latest entries for the report
        latest_entries = scraper.ParsedData[-10:] if len(scraper.ParsedData) >= 10 else scraper.ParsedData
        
        # Generate Markdown summary for README
        markdown_summary = generate_markdown_summary(analysis_results, latest_entries)
        
        # Write Markdown summary to file for GitHub Actions
        with open('analysis_summary.md', 'w', encoding='utf-8') as file:
            file.write(markdown_summary)
        
        # Generate execution summary
        execution_summary = f"""
## 🚀 Execution Summary

### 📊 Scraping Results
- **Total Records Processed:** {len(scraper.ParsedData):,}
- **New Records Added:** {new_records_count}
- **Duplicate Records Skipped:** {duplicate_records_count}
- **Execution Time:** {execution_time:.2f} seconds
- **Average Processing Speed:** {len(scraper.ParsedData)/execution_time:.1f} records/second

### 🔍 Data Quality
- **Database Records:** {total_db_records:,}
- **Data Completeness:** {len(scraper.ParsedData)/total_db_records*100:.1f}% of total database
- **Date Coverage:** {analysis_results['basic_stats']['data_span_days']} days
- **Time Distribution Balance:** {min(analysis_results['time_analysis']['time_balance'].values()):.1f}% - {max(analysis_results['time_analysis']['time_balance'].values()):.1f}%

### 📈 Analysis Confidence
- **Confidence Level:** {analysis_results['predictions']['confidence_level']}
- **Statistical Significance:** {'High' if analysis_results['basic_stats']['total_draws'] > 500 else 'Medium' if analysis_results['basic_stats']['total_draws'] > 200 else 'Low'}
- **Pattern Reliability:** {'Strong' if analysis_results['patterns']['consecutive_percentage'] < 10 else 'Moderate'}

---
*Execution completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Append execution summary to markdown file
        with open('analysis_summary.md', 'a', encoding='utf-8') as file:
            file.write(execution_summary)
        
        print("✅ Enhanced analysis report generated successfully.")
        print(f"📊 Total records processed: {len(scraper.ParsedData):,}")
        print(f"📋 Summary saved to: analysis_summary.md")
    else:
        print("❌ No data was scraped. Please check the website structure or try again later.")

if __name__ == "__main__":
    start = perf_counter()
    
    if not is_within_visit_hours():
        print(f'[*] WARNING: Current time is {datetime.datetime.now().strftime("%H:%M")}')
        print('[*] Robots.txt specifies Visit-time: 0600-1000')
        print('[*] Consider running during allowed hours to avoid potential issues')
        print('[*] Continuing anyway for testing purposes...')
    
    urls = [PLAYWHE_URL]

    engine = get_engine()
    db_session = get_session(engine)
    
    try:
        asyncio.run(run_scraper(urls, db_session))
        print('[*] Adding Data to Database ... ')

    except Exception as e:
        print('*'*100)
        print(f'Error Occurred : {e}')
        print('*'*100)
    finally:
        db_session.close()

    stop = perf_counter()
    print("[*] Time taken : ", stop - start)
