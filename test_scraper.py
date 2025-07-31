#!/usr/bin/env python3
"""
Test script for PlayWhe scraper
Run this to test the scraper functionality
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import datetime
import os

async def test_website_connectivity():
    """Test if we can connect to the PlayWhe website"""
    print("🔍 Testing website connectivity...")
    
    url = 'https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"✅ Website accessible - Status: {response.status}")
                content = await response.text()
                print(f"📄 Content length: {len(content)} characters")
                
                # Check if it's the right page
                if 'play-whe' in content.lower() or 'playwhe' in content.lower():
                    print("✅ Correct PlayWhe page detected")
                else:
                    print("⚠️  Page content doesn't seem to be PlayWhe related")
                
                return content
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

async def test_form_submission():
    """Test if we can submit the search form"""
    print("\n🔍 Testing form submission...")
    
    url = 'https://www.nlcbplaywhelotto.com/nlcb-play-whe-results/'
    
    # Test parameters for January 2025
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
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params, headers=headers) as response:
                print(f"✅ Form submission successful - Status: {response.status}")
                content = await response.text()
                
                # Save test response
                with open('test_response.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("💾 Test response saved to test_response.html")
                
                # Check for table content
                soup = bs(content, 'html.parser')
                tables = soup.find_all('table')
                print(f"📊 Found {len(tables)} tables in response")
                
                for i, table in enumerate(tables):
                    rows = table.find_all('tr')
                    print(f"   Table {i+1}: {len(rows)} rows")
                    
                    # Show first few rows
                    for j, row in enumerate(rows[:3]):
                        cells = row.find_all(['td', 'th'])
                        cell_text = [cell.get_text(strip=True) for cell in cells]
                        print(f"     Row {j+1}: {cell_text}")
                
                return content
    except Exception as e:
        print(f"❌ Form submission failed: {e}")
        return None

def test_data_parsing():
    """Test parsing the saved response"""
    print("\n🔍 Testing data parsing...")
    
    if not os.path.exists('test_response.html'):
        print("❌ No test response file found")
        return
    
    try:
        with open('test_response.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = bs(content, 'html.parser')
        
        # Look for PlayWhe data patterns
        import re
        
        # Look for draw numbers
        draw_pattern = r'(\d{5})'
        draws = re.findall(draw_pattern, content)
        print(f"📊 Found {len(draws)} potential draw numbers")
        
        # Look for time patterns
        time_pattern = r'(Morning|Midday|Afternoon|Evening)'
        times = re.findall(time_pattern, content)
        print(f"⏰ Found {len(times)} time references")
        
        # Look for number patterns (1-36)
        number_pattern = r'\b([1-9]|[12]\d|3[0-6])\b'
        numbers = re.findall(number_pattern, content)
        print(f"🎲 Found {len(numbers)} potential mark numbers")
        
        # Look for promo patterns
        promo_pattern = r'(Gold Ball|Megaball|Mega Ultra Ball|Mega Extreme Ball)'
        promos = re.findall(promo_pattern, content)
        print(f"⭐ Found {len(promos)} promo references")
        
        print("\n✅ Data parsing test completed successfully!")
        
    except Exception as e:
        print(f"❌ Data parsing test failed: {e}")

async def main():
    """Run all tests"""
    print("🧪 PlayWhe Scraper Test Suite")
    print("=" * 50)
    
    # Test 1: Website connectivity
    await test_website_connectivity()
    
    # Test 2: Form submission
    await test_form_submission()
    
    # Test 3: Data parsing
    test_data_parsing()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 