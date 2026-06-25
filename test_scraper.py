#!/usr/bin/env python3
"""
Test script for PlayWhe scraper
Run this to test the scraper functionality
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import os

from config import PLAYWHE_URL, HTTP_HEADERS, build_search_params
from utils import extract_patterns

async def test_website_connectivity():
    """Test if we can connect to the PlayWhe website"""
    print("🔍 Testing website connectivity...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PLAYWHE_URL) as response:
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
    
    params = build_search_params('Jan', '2025')
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(PLAYWHE_URL, data=params, headers=HTTP_HEADERS) as response:
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
        
        matches = extract_patterns(content)
        print(f"📊 Found {len(matches['draws'])} potential draw numbers")
        print(f"⏰ Found {len(matches['times'])} time references")
        print(f"🎲 Found {len(matches['numbers'])} potential mark numbers")
        print(f"⭐ Found {len(matches['promos'])} promo references")
        
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