"""Shared fixtures for PlayWhe Webscraper tests."""

import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from async_scraper import Base, Playwhe_Result


SAMPLE_HTML_WITH_TABLE = """
<html><body>
<table id='monthResults'>
<thead><tr><th>Draw#</th><th>Date</th><th>Time</th><th>Mark</th><th>Promo</th></tr></thead>
<tbody>
<tr>
    <td>25218</td>
    <td>01-Jan-25</td>
    <td>Morning</td>
    <td>7</td>
    <td><div>Gold Ball</div></td>
</tr>
<tr>
    <td>25219</td>
    <td>01-Jan-25</td>
    <td>Midday</td>
    <td>24</td>
    <td><div>Megaball</div></td>
</tr>
<tr>
    <td>25220</td>
    <td>01-Jan-25</td>
    <td>Afternoon</td>
    <td>11</td>
    <td><div>Mega Extreme Ball</div></td>
</tr>
<tr class='eveningRow'>
    <td>25221</td>
    <td>01-Jan-25</td>
    <td>Evening</td>
    <td>32</td>
    <td><div>Gold Ball</div><div>Megaball</div></td>
</tr>
<tr>
    <td>25222</td>
    <td>02-Jan-25</td>
    <td>Morning</td>
    <td>12</td>
    <td></td>
</tr>
</tbody>
</table>
</body></html>
"""

SAMPLE_HTML_NO_TABLE = """
<html><body>
<p>No results found</p>
</body></html>
"""

SAMPLE_HTML_ALTERNATIVE_CONTENT = """
<html><body>
<p>Draw 25218 on 01-Jan-25 Morning number 7</p>
<p>Draw 25219 on 01-Jan-25 Midday number 24</p>
<p>Draw 25220 on 01-Jan-25 Afternoon number 11</p>
<p>Draw 25221 on 01-Jan-25 Evening number 32</p>
</body></html>
"""


@pytest.fixture
def db_engine():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_playwhe_data():
    """Sample PlayWhe data as returned by the scraper."""
    return [
        {
            "Date": datetime.date(2025, 1, 1),
            "Draw#": "25218",
            "Time": "Morning",
            "Mark": 7,
            "Promo": "Gold Ball",
        },
        {
            "Date": datetime.date(2025, 1, 1),
            "Draw#": "25219",
            "Time": "Midday",
            "Mark": 24,
            "Promo": "Megaball",
        },
        {
            "Date": datetime.date(2025, 1, 1),
            "Draw#": "25220",
            "Time": "Afternoon",
            "Mark": 11,
            "Promo": "Mega Extreme Ball",
        },
        {
            "Date": datetime.date(2025, 1, 1),
            "Draw#": "25221",
            "Time": "Evening",
            "Mark": 32,
            "Promo": "Gold Ball, Megaball",
        },
        {
            "Date": datetime.date(2025, 1, 2),
            "Draw#": "25222",
            "Time": "Morning",
            "Mark": 12,
            "Promo": "",
        },
    ]


@pytest.fixture
def large_playwhe_data():
    """Generate a larger dataset for comprehensive_analysis testing."""
    import random
    random.seed(42)
    data = []
    times = ["Morning", "Midday", "Afternoon", "Evening"]
    promos = ["Gold Ball", "Megaball", "Mega Extreme Ball", "Mega Ultra Ball", ""]
    base_date = datetime.date(2025, 1, 1)
    draw_num = 25218

    for day_offset in range(50):
        for t in times:
            data.append({
                "Date": base_date + datetime.timedelta(days=day_offset),
                "Draw#": str(draw_num),
                "Time": t,
                "Mark": random.randint(1, 36),
                "Promo": random.choice(promos),
            })
            draw_num += 1

    return data
