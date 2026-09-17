#!/usr/bin/env python3
"""
Test script for PlayWhe scraper
Run this to test the scraper functionality
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import datetime
import logging
import os
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


async def test_website_connectivity():
    """Test if we can connect to the PlayWhe website"""
    logger.info('Testing website connectivity...')

    url = 'https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/'

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                logger.info('Website accessible - Status: %d', response.status)
                content = await response.text()
                logger.info('Content length: %d characters', len(content))

                if 'play-whe' in content.lower() or 'playwhe' in content.lower():
                    logger.info('Correct PlayWhe page detected')
                else:
                    logger.warning('Page content does not appear to be PlayWhe related')

                return content
    except aiohttp.ClientConnectionError as e:
        logger.error('Connection failed: %s', e)
        return None
    except asyncio.TimeoutError:
        logger.error('Connection timed out after 15 seconds')
        return None
    except aiohttp.ClientError as e:
        logger.error('HTTP client error: %s', e)
        return None


async def test_form_submission():
    """Test if we can submit the search form"""
    logger.info('Testing form submission...')

    url = 'https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/'

    params = {
        'playwhe_month': 'Jan',
        'playwhe_year': '2025',
        'sid': '7bdb0e5bd65120db4a046487d5ba59b90b243ecb69127964ca720d0be9473e4f',
        'date_btn': 'SEARCH'
    }

    headers = {
        'User-Agent': 'PlayWheScraper/1.0 (Test bot)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, data=params, headers=headers) as response:
                if response.status != 200:
                    logger.error('Form submission returned HTTP %d', response.status)
                    return None

                logger.info('Form submission successful - Status: %d', response.status)
                content = await response.text()

                try:
                    with open('test_response.html', 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info('Test response saved to test_response.html')
                except OSError as e:
                    logger.error('Failed to save test response: %s', e)

                soup = bs(content, 'html.parser')
                tables = soup.find_all('table')
                logger.info('Found %d tables in response', len(tables))

                for i, table in enumerate(tables):
                    rows = table.find_all('tr')
                    logger.info('  Table %d: %d rows', i + 1, len(rows))

                    for j, row in enumerate(rows[:3]):
                        cells = row.find_all(['td', 'th'])
                        cell_text = [cell.get_text(strip=True) for cell in cells]
                        logger.debug('    Row %d: %s', j + 1, cell_text)

                return content
    except aiohttp.ClientConnectionError as e:
        logger.error('Form submission connection failed: %s', e)
        return None
    except asyncio.TimeoutError:
        logger.error('Form submission timed out')
        return None
    except aiohttp.ClientError as e:
        logger.error('Form submission HTTP error: %s', e)
        return None


def test_data_parsing():
    """Test parsing the saved response"""
    logger.info('Testing data parsing...')

    if not os.path.exists('test_response.html'):
        logger.error('No test response file found - skipping parse test')
        return False

    try:
        with open('test_response.html', 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        logger.error('Failed to read test_response.html: %s', e)
        return False

    soup = bs(content, 'html.parser')

    draw_pattern = r'(\d{5})'
    draws = re.findall(draw_pattern, content)
    logger.info('Found %d potential draw numbers', len(draws))

    time_pattern = r'(Morning|Midday|Afternoon|Evening)'
    times = re.findall(time_pattern, content)
    logger.info('Found %d time references', len(times))

    number_pattern = r'\b([1-9]|[12]\d|3[0-6])\b'
    numbers = re.findall(number_pattern, content)
    logger.info('Found %d potential mark numbers', len(numbers))

    promo_pattern = r'(Gold Ball|Megaball|Mega Ultra Ball|Mega Extreme Ball)'
    promos = re.findall(promo_pattern, content)
    logger.info('Found %d promo references', len(promos))

    if not (draws and times):
        logger.warning('No draw numbers or time references found - page structure may have changed')
        return False

    logger.info('Data parsing test completed successfully')
    return True


async def main():
    """Run all tests"""
    logger.info('PlayWhe Scraper Test Suite')
    logger.info('=' * 50)

    results = {'connectivity': False, 'form_submission': False, 'parsing': False}

    # Test 1: Website connectivity
    content = await test_website_connectivity()
    results['connectivity'] = content is not None

    # Test 2: Form submission
    form_content = await test_form_submission()
    results['form_submission'] = form_content is not None

    # Test 3: Data parsing
    results['parsing'] = test_data_parsing()

    # Summary
    logger.info('=' * 50)
    passed = sum(results.values())
    total = len(results)
    logger.info('Tests completed: %d/%d passed', passed, total)

    for test_name, passed_flag in results.items():
        status = 'PASS' if passed_flag else 'FAIL'
        logger.info('  [%s] %s', status, test_name)

    if passed < total:
        logger.warning('Some tests failed. Check logs above for details.')


if __name__ == "__main__":
    asyncio.run(main())
