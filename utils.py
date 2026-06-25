"""Shared utility functions for the PlayWhe scraper."""

import re
import datetime

from config import MONTH, VISIT_HOUR_START, VISIT_HOUR_END

# Pre-compiled regex patterns used for data extraction
DATE_RE = re.compile(r'(\d{2})-(\w{3})-(\d{2})')
DRAW_NUM_RE = re.compile(r'(\d{5})')
TIME_RE = re.compile(r'(Morning|Midday|Afternoon|Evening)')
MARK_RE = re.compile(r'\b([1-9]|[12]\d|3[0-6])\b')
PROMO_RE = re.compile(r'(Gold Ball|Megaball|Mega Ultra Ball|Mega Extreme Ball)')


def parse_draw_date(date_str):
    """Parse a date string from scraped PlayWhe HTML into a `datetime.date`.

    Supports formats like ``"02-Jan-25"`` (with 2-digit year) and
    ``"02-Jan-2025"`` (4-digit year).  Returns today's date as a fallback
    when the string cannot be parsed.
    """
    try:
        if '-' in date_str:
            parts = date_str.split('-')
            if len(parts) == 3:
                day, month_abbr, year_part = parts
                month_num = MONTH.index(month_abbr) + 1
                year_full = f"20{year_part}" if len(year_part) == 2 else year_part
                return datetime.datetime.strptime(
                    f"{day}-{month_num}-{year_full}", "%d-%m-%Y"
                ).date()
        return datetime.datetime.strptime(date_str, "%d-%b-%y").date()
    except (ValueError, IndexError):
        return datetime.datetime.now().date()


def safe_int(value, default=0):
    """Convert *value* to ``int``, returning *default* on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def is_within_visit_hours():
    """Return ``True`` if the current hour is inside the robots.txt window."""
    return VISIT_HOUR_START <= datetime.datetime.now().hour < VISIT_HOUR_END


def extract_patterns(text):
    """Run all pre-compiled regexes against *text* and return matches.

    Returns a dict with keys ``dates``, ``draws``, ``times``, ``numbers``,
    and ``promos``.
    """
    return {
        'dates': DATE_RE.findall(text),
        'draws': DRAW_NUM_RE.findall(text),
        'times': TIME_RE.findall(text),
        'numbers': MARK_RE.findall(text),
        'promos': PROMO_RE.findall(text),
    }
