import asyncio
import aiohttp
import pandas as pd
from io import StringIO
import os
import datetime
from uuid import uuid4
import warnings
from time import perf_counter
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Date, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
from bs4 import BeautifulSoup as bs
import numpy as np
from collections import Counter

warnings.simplefilter(action='ignore', category=FutureWarning)

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
            print(f'[*] Outside allowed visiting hours (0600-1000). Current time: {datetime.datetime.now().strftime("%H:%M")}')
            return None
            
        # Ensure rate limiting
        while not self.should_respect_rate_limit():
            await asyncio.sleep(1)
            
        params = {
            'playwhe_month': f'{month}', 
            'playwhe_year': f'{year}', 
            'sid':'7bdb0e5bd65120db4a046487d5ba59b90b243ecb69127964ca720d0be9473e4f', 
            'date_btn':'SEARCH'
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
                            
                            # Look for PlayWhe results table - try multiple selectors
                            table_selectors = [
                                'table',  # Generic table
                                'table.table',  # Bootstrap table
                                'table.results-table',  # Results table
                                'table#results',  # Table with id results
                                '.results table',  # Table within results div
                                'table[class*="table"]',  # Any table with "table" in class
                            ]
                            
                            html_table = None
                            for selector in table_selectors:
                                html_table = soup.select_one(selector)
                                if html_table:
                                    print(f'[*] Found table with selector: {selector}')
                                    break
                            
                            if html_table:
                                # Extract table rows
                                rows = html_table.find_all('tr')
                                print(f'[*] Found {len(rows)} table rows')
                                
                                for row in rows[1:]:  # Skip header row
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 5:  # Ensure we have enough columns
                                        try:
                                            draw_num = cells[0].get_text(strip=True)
                                            date_str = cells[1].get_text(strip=True)
                                            time = cells[2].get_text(strip=True)
                                            mark = cells[3].get_text(strip=True)
                                            # Handle promo column with div elements
                                            promo_divs = cells[4].find_all('div')
                                            if promo_divs:
                                                promo = ', '.join([div.get_text(strip=True) for div in promo_divs])
                                            else:
                                                promo = cells[4].get_text(strip=True)
                                            
                                            # Clean and validate data
                                            if draw_num and date_str and time and mark:
                                                # Convert date format
                                                try:
                                                    # Handle different date formats
                                                    if '-' in date_str:
                                                        date_parts = date_str.split('-')
                                                        if len(date_parts) == 3:
                                                            day, month_abbr, year_short = date_parts
                                                            month_num = MONTH.index(month_abbr) + 1
                                                            year_full = f"20{year_short}" if len(year_short) == 2 else year_short
                                                            date_obj = datetime.datetime.strptime(f"{day}-{month_num}-{year_full}", "%d-%m-%Y").date()
                                                        else:
                                                            date_obj = datetime.datetime.strptime(date_str, "%d-%b-%y").date()
                                                    else:
                                                        date_obj = datetime.datetime.strptime(date_str, "%d-%b-%y").date()
                                                except:
                                                    # If date parsing fails, use current date
                                                    date_obj = datetime.datetime.now().date()
                                                
                                                # Convert mark to integer
                                                try:
                                                    mark_int = int(mark)
                                                except:
                                                    mark_int = 0
                                                
                                                results_list.append({
                                                    'Date': date_obj,
                                                    'Draw#': draw_num,
                                                    'Time': time,
                                                    'Mark': mark_int,
                                                    'Promo': promo
                                                })
                                        except Exception as e:
                                            print(f'[*] Error parsing row: {e}')
                                            continue
                            
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
                if attempt < retries - 1:
                    print(f'[*] Connection error occurred. Retrying... Attempt {attempt + 1}/{retries}')
                    await asyncio.sleep(2)
                else:
                    print('[*] Maximum retries reached. Unable to establish connection.')
                    return None

    def alternative_parsing(self, content, month, year):
        """Alternative parsing method if the main method fails"""
        try:
            # Try to find any table-like structure
            soup = bs(content, 'html.parser')
            
            # Look for any divs or spans that might contain the data
            results_list = []
            
            # Try to find patterns like "Draw# 25218" or similar
            text_content = soup.get_text()
            
            # Look for date patterns
            import re
            date_pattern = r'(\d{2})-(\w{3})-(\d{2})'
            dates = re.findall(date_pattern, text_content)
            
            # Look for draw number patterns
            draw_pattern = r'(\d{5})'  # 5-digit draw numbers
            draws = re.findall(draw_pattern, text_content)
            
            # Look for time patterns
            time_pattern = r'(Morning|Midday|Afternoon|Evening)'
            times = re.findall(time_pattern, text_content)
            
            # Look for number patterns (1-36)
            number_pattern = r'\b([1-9]|[12]\d|3[0-6])\b'
            numbers = re.findall(number_pattern, text_content)
            
            # Try to match these patterns
            if dates and draws and times and numbers:
                for i in range(min(len(dates), len(draws), len(times), len(numbers))):
                    try:
                        day, month_abbr, year_short = dates[i]
                        month_num = MONTH.index(month_abbr) + 1
                        year_full = f"20{year_short}"
                        date_obj = datetime.datetime.strptime(f"{day}-{month_num}-{year_full}", "%d-%m-%Y").date()
                        
                        results_list.append({
                            'Date': date_obj,
                            'Draw#': draws[i],
                            'Time': times[i],
                            'Mark': int(numbers[i]),
                            'Promo': 'Unknown'
                        })
                    except:
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
            print(f'[*] Respecting robots.txt: Visit-time 0600-1000, Request-rate 1/5, Crawl-delay 5')
            
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
                    print(f'[*] Waiting 5 seconds before next request...')
                    await asyncio.sleep(5)

def add_playwhe_data_to_db(session, playwhe_data):
    """Add PlayWhe data to database with duplicate checking"""
    added_count = 0
    skipped_count = 0
    
    for data in playwhe_data:
        try:
            # Check for existing record based on Draw# and Date
            existing_result = session.query(Playwhe_Result).filter_by(
                DrawNum=data['Draw#'],
                DrawDate=data['Date']
            ).first()
            
            if existing_result:
                skipped_count += 1
                continue
            else:
                playwhe_instance = Playwhe_Result(
                    DrawDate=data['Date'],
                    DrawNum=data['Draw#'],
                    Time=data['Time'],
                    Mark=data['Mark'],
                    Promo=data['Promo']
                )
                session.add(playwhe_instance)
                added_count += 1
                
        except Exception as e:
            print('[*] Error adding data:', e)
            continue
    
    session.commit()
    print(f'[*] Added {added_count} new records, skipped {skipped_count} duplicates')

def comprehensive_analysis(data):
    """Perform comprehensive analysis on PlayWhe data"""
    if not data:
        return "No data available for analysis."
    
    df = pd.DataFrame(data)
    
    analysis_results = {
        'basic_stats': {},
        'time_analysis': {},
        'number_analysis': {},
        'promo_analysis': {},
        'patterns': {},
        'predictions': {}
    }
    
    # Basic Statistics
    analysis_results['basic_stats'] = {
        'total_draws': len(df),
        'date_range': f"{df['Date'].min()} to {df['Date'].max()}",
        'unique_draws': df['Draw#'].nunique(),
        'unique_dates': df['Date'].nunique()
    }
    
    # Time Analysis
    time_counts = df['Time'].value_counts()
    analysis_results['time_analysis'] = {
        'time_distribution': time_counts.to_dict(),
        'most_common_time': time_counts.index[0] if len(time_counts) > 0 else 'Unknown',
        'least_common_time': time_counts.index[-1] if len(time_counts) > 0 else 'Unknown'
    }
    
    # Number Analysis (Mark)
    mark_counts = df['Mark'].value_counts()
    analysis_results['number_analysis'] = {
        'most_common_numbers': mark_counts.head(10).to_dict(),
        'least_common_numbers': mark_counts.tail(10).to_dict(),
        'number_range': f"{df['Mark'].min()} to {df['Mark'].max()}",
        'average_number': df['Mark'].mean(),
        'median_number': df['Mark'].median(),
        'number_std': df['Mark'].std()
    }
    
    # Promo Analysis
    promo_counts = df['Promo'].value_counts()
    analysis_results['promo_analysis'] = {
        'promo_distribution': promo_counts.to_dict(),
        'most_common_promo': promo_counts.index[0] if len(promo_counts) > 0 else 'Unknown'
    }
    
    # Pattern Analysis
    # Check for consecutive numbers
    df_sorted = df.sort_values(['Date', 'Time'])
    consecutive_count = 0
    for i in range(1, len(df_sorted)):
        if abs(df_sorted.iloc[i]['Mark'] - df_sorted.iloc[i-1]['Mark']) == 1:
            consecutive_count += 1
    
    analysis_results['patterns'] = {
        'consecutive_numbers': consecutive_count,
        'consecutive_percentage': (consecutive_count / len(df)) * 100 if len(df) > 0 else 0
    }
    
    # Simple Predictions (based on frequency)
    hot_numbers = mark_counts.head(5).index.tolist()
    cold_numbers = mark_counts.tail(5).index.tolist()
    
    analysis_results['predictions'] = {
        'hot_numbers': hot_numbers,
        'cold_numbers': cold_numbers,
        'next_predicted_time': time_counts.index[0] if len(time_counts) > 0 else 'Unknown'
    }
    
    return analysis_results

def generate_enhanced_html_report(analysis_results, latest_entries):
    """Generate enhanced HTML report with comprehensive analysis"""
    
    html_report = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PlayWhe Comprehensive Analysis Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                border-left: 4px solid #3498db;
                padding-left: 15px;
                margin-top: 30px;
            }}
            h3 {{
                color: #2c3e50;
                margin-top: 25px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: #ecf0f1;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }}
            .stat-card h4 {{
                margin: 0 0 10px 0;
                color: #2c3e50;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #e74c3c;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            .highlight {{
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #ffc107;
                margin: 15px 0;
            }}
            .prediction {{
                background-color: #d4edda;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #28a745;
                margin: 15px 0;
            }}
            .latest-results {{
                background-color: #e3f2fd;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 PlayWhe Comprehensive Analysis Report</h1>
            
            <div class="highlight">
                <h3>📊 Executive Summary</h3>
                <p>This report provides a comprehensive analysis of PlayWhe lottery data, including statistical patterns, 
                frequency analysis, and predictive insights based on historical data.</p>
            </div>
            
            <h2> Basic Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Total Draws</h4>
                    <div class="stat-value">{analysis_results['basic_stats']['total_draws']}</div>
                </div>
                <div class="stat-card">
                    <h4>Date Range</h4>
                    <div class="stat-value">{analysis_results['basic_stats']['date_range']}</div>
                </div>
                <div class="stat-card">
                    <h4>Unique Draws</h4>
                    <div class="stat-value">{analysis_results['basic_stats']['unique_draws']}</div>
                </div>
                <div class="stat-card">
                    <h4>Unique Dates</h4>
                    <div class="stat-value">{analysis_results['basic_stats']['unique_dates']}</div>
                </div>
            </div>
            
            <h2>⏰ Time Analysis</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Most Common Time</h4>
                    <div class="stat-value">{analysis_results['time_analysis']['most_common_time']}</div>
                </div>
                <div class="stat-card">
                    <h4>Least Common Time</h4>
                    <div class="stat-value">{analysis_results['time_analysis']['least_common_time']}</div>
                </div>
            </div>
            
            <h3>Time Distribution</h3>
            <table>
                <tr><th>Time</th><th>Frequency</th></tr>
                {''.join([f"<tr><td>{time}</td><td>{count}</td></tr>" for time, count in analysis_results['time_analysis']['time_distribution'].items()])}
            </table>
            
            <h2> Number Analysis</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Average Number</h4>
                    <div class="stat-value">{analysis_results['number_analysis']['average_number']:.1f}</div>
                </div>
                <div class="stat-card">
                    <h4>Median Number</h4>
                    <div class="stat-value">{analysis_results['number_analysis']['median_number']:.1f}</div>
                </div>
                <div class="stat-card">
                    <h4>Number Range</h4>
                    <div class="stat-value">{analysis_results['number_analysis']['number_range']}</div>
                </div>
            </div>
            
            <h3>🔥 Hot Numbers (Most Frequent)</h3>
            <table>
                <tr><th>Number</th><th>Frequency</th></tr>
                {''.join([f"<tr><td>{num}</td><td>{freq}</td></tr>" for num, freq in list(analysis_results['number_analysis']['most_common_numbers'].items())[:10]])}
            </table>
            
            <h3>❄️ Cold Numbers (Least Frequent)</h3>
            <table>
                <tr><th>Number</th><th>Frequency</th></tr>
                {''.join([f"<tr><td>{num}</td><td>{freq}</td></tr>" for num, freq in list(analysis_results['number_analysis']['least_common_numbers'].items())[:10]])}
            </table>
            
            <h2> Promo Analysis</h2>
            <h3>Promo Distribution</h3>
            <table>
                <tr><th>Promo Type</th><th>Frequency</th></tr>
                {''.join([f"<tr><td>{promo}</td><td>{count}</td></tr>" for promo, count in analysis_results['promo_analysis']['promo_distribution'].items()])}
            </table>
            
            <h2> Pattern Analysis</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Consecutive Numbers</h4>
                    <div class="stat-value">{analysis_results['patterns']['consecutive_numbers']}</div>
                </div>
                <div class="stat-card">
                    <h4>Consecutive %</h4>
                    <div class="stat-value">{analysis_results['patterns']['consecutive_percentage']:.1f}%</div>
                </div>
            </div>
            
            <h2>🔮 Predictive Insights</h2>
            <div class="prediction">
                <h3>Hot Numbers (High Frequency)</h3>
                <p><strong>Numbers to watch:</strong> {', '.join(map(str, analysis_results['predictions']['hot_numbers']))}</p>
                
                <h3>Cold Numbers (Low Frequency)</h3>
                <p><strong>Numbers due for appearance:</strong> {', '.join(map(str, analysis_results['predictions']['cold_numbers']))}</p>
                
                <h3>Next Predicted Time</h3>
                <p><strong>Most likely next draw time:</strong> {analysis_results['predictions']['next_predicted_time']}</p>
            </div>
            
            <h2> Latest Results</h2>
            <div class="latest-results">
                {''.join([f"""
                <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                    <h4>Draw #{entry['Draw#']} - {entry['Date']}</h4>
                    <p><strong>Time:</strong> {entry['Time']}</p>
                    <p><strong>Mark:</strong> {entry['Mark']}</p>
                    <p><strong>Promo:</strong> {entry['Promo']}</p>
                </div>
                """ for entry in latest_entries[-5:]])}
            </div>
            
            <div class="highlight">
                <h3>⚠️ Disclaimer</h3>
                <p>This analysis is for informational purposes only. Lottery games are based on random chance, 
                and past results do not guarantee future outcomes. Please play responsibly.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_report

async def run_scraper(urls, db_session):
    scraper = WebScraper(urls)
    await scraper.main()
    
    if scraper.ParsedData:
        add_playwhe_data_to_db(db_session, scraper.ParsedData)
        
        # Perform comprehensive analysis
        analysis_results = comprehensive_analysis(scraper.ParsedData)
        
        # Get latest entries for the report
        latest_entries = scraper.ParsedData[-10:] if len(scraper.ParsedData) >= 10 else scraper.ParsedData
        
        # Generate enhanced HTML report
        html_report = generate_enhanced_html_report(analysis_results, latest_entries)
        
        # Write HTML report to file
        with open('analysis_report.html', 'w', encoding='utf-8') as file:
            file.write(html_report)
        
        print("✅ Enhanced analysis report generated successfully.")
        print(f"📊 Total records processed: {len(scraper.ParsedData)}")
        print(f" Analysis saved to: analysis_report.html")
    else:
        print("❌ No data was scraped. Please check the website structure or try again later.")

if __name__ == "__main__":
    start = perf_counter()
    
    # Check if we're within allowed visiting hours before starting
    current_hour = datetime.datetime.now().hour
    if not (6 <= current_hour < 10):
        print(f'[*] WARNING: Current time is {datetime.datetime.now().strftime("%H:%M")}')
        print('[*] Robots.txt specifies Visit-time: 0600-1000')
        print('[*] Consider running during allowed hours to avoid potential issues')
        print('[*] Continuing anyway for testing purposes...')
        # response = input('[*] Continue anyway? (y/N): ')
        # if response.lower() != 'y':
        #     print('[*] Exiting...')
        #     exit()
    
    # Updated URL for PlayWhe results
    urls = ['https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/']
    
    engine = create_engine(f'sqlite:///{Database}', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
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
