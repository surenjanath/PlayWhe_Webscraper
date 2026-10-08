"""Shared constants and configuration for the PlayWhe scraper."""

import os
import datetime

MONTH = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

YEAR = [str(i) for i in range(2025, datetime.datetime.now().year + 1)]

PLAYWHE_URL = 'https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/'

SEARCH_SID = '7bdb0e5bd65120db4a046487d5ba59b90b243ecb69127964ca720d0be9473e4f'

# Rate-limiting / robots.txt compliance
CRAWL_DELAY_SECONDS = 5
VISIT_HOUR_START = 6
VISIT_HOUR_END = 10
MAX_RETRIES = 3

# Database
DATABASE_DIR = 'Database'
DATABASE_NAME = 'PlayWhe_Results_Database.db'

_cwd = os.getcwd()
DATABASE_PATH = os.path.join(_cwd, DATABASE_DIR, DATABASE_NAME)

# Ensure the database directory exists
os.makedirs(os.path.join(_cwd, DATABASE_DIR), exist_ok=True)

HTTP_HEADERS = {
    'User-Agent': 'PlayWheScraper/1.0 (Respectful bot following robots.txt guidelines)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


def build_search_params(month, year):
    """Build the POST form parameters for a PlayWhe results search."""
    return {
        'playwhe_month': month,
        'playwhe_year': year,
        'sid': SEARCH_SID,
        'date_btn': 'SEARCH',
    }
