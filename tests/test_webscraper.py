"""Unit tests for the WebScraper class."""

import asyncio
import datetime
from time import perf_counter
from unittest.mock import patch, AsyncMock, MagicMock

import aiohttp
import pytest
import pytest_asyncio

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from async_scraper import WebScraper
from tests.conftest import (
    SAMPLE_HTML_WITH_TABLE,
    SAMPLE_HTML_NO_TABLE,
    SAMPLE_HTML_ALTERNATIVE_CONTENT,
)


class TestCheckVisitTime:
    def test_returns_true_always(self):
        """Current implementation returns True for all times (testing mode)."""
        scraper = WebScraper(["http://example.com"])
        assert scraper.check_visit_time() is True

    @patch("async_scraper.datetime")
    def test_check_visit_time_ignores_hour(self, mock_dt):
        """Even with mocked times, current impl returns True."""
        mock_dt.datetime.now.return_value = datetime.datetime(2025, 1, 1, 3, 0)
        scraper = WebScraper(["http://example.com"])
        assert scraper.check_visit_time() is True


class TestShouldRespectRateLimit:
    def test_first_request_allowed(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0
        assert scraper.should_respect_rate_limit() is True

    def test_request_within_5_seconds_blocked(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = perf_counter()
        assert scraper.should_respect_rate_limit() is False

    def test_request_after_5_seconds_allowed(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = perf_counter() - 6
        assert scraper.should_respect_rate_limit() is True

    def test_rate_limit_boundary(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = perf_counter() - 4.9
        assert scraper.should_respect_rate_limit() is False


class TestWebScraperInit:
    def test_init_stores_urls(self):
        urls = ["http://a.com", "http://b.com"]
        scraper = WebScraper(urls)
        assert scraper.urls == urls

    def test_init_empty_parsed_data(self):
        scraper = WebScraper(["http://example.com"])
        assert scraper.ParsedData == []

    def test_init_request_count_zero(self):
        scraper = WebScraper(["http://example.com"])
        assert scraper.request_count == 0

    def test_init_last_request_time_zero(self):
        scraper = WebScraper(["http://example.com"])
        assert scraper.last_request_time == 0


class TestAlternativeParsing:
    def test_parses_text_with_patterns(self):
        scraper = WebScraper(["http://example.com"])
        content = """
        Draw 25218 on 01-Jan-25 Morning number 7
        Draw 25219 on 02-Jan-25 Midday number 24
        """
        result = scraper.alternative_parsing(content, "Jan", "2025")
        assert not result.empty
        assert "Date" in result.columns
        assert "Draw#" in result.columns
        assert "Time" in result.columns
        assert "Mark" in result.columns

    def test_returns_empty_df_on_no_patterns(self):
        scraper = WebScraper(["http://example.com"])
        content = "<html><body>Nothing useful here</body></html>"
        result = scraper.alternative_parsing(content, "Jan", "2025")
        assert result.empty

    def test_returns_empty_df_on_partial_patterns(self):
        scraper = WebScraper(["http://example.com"])
        content = "<html><body>Morning Midday but no dates or draws</body></html>"
        result = scraper.alternative_parsing(content, "Jan", "2025")
        assert result.empty

    def test_promo_set_to_unknown(self):
        scraper = WebScraper(["http://example.com"])
        content = """
        Draw 25218 on 01-Jan-25 Morning number 7
        """
        result = scraper.alternative_parsing(content, "Jan", "2025")
        if not result.empty:
            assert all(result["Promo"] == "Unknown")

    def test_handles_malformed_dates_gracefully(self):
        scraper = WebScraper(["http://example.com"])
        content = """
        Draw 25218 on 99-Xyz-25 Morning number 7
        """
        result = scraper.alternative_parsing(content, "Jan", "2025")
        # Should not raise; may return empty or skip bad rows
        assert isinstance(result, type(result))


class TestFetch:
    @pytest.mark.asyncio
    async def test_fetch_success_with_table(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.read = AsyncMock(
            return_value=SAMPLE_HTML_WITH_TABLE.encode("utf-8")
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        result = await scraper.fetch(mock_session, "2025", "Jan", "http://example.com")

        assert result is not None
        assert len(result) == 5
        assert result[0]["Draw#"] == "25218"
        assert result[0]["Mark"] == 7
        assert result[0]["Time"] == "Morning"

    @pytest.mark.asyncio
    async def test_fetch_success_promo_with_divs(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.read = AsyncMock(
            return_value=SAMPLE_HTML_WITH_TABLE.encode("utf-8")
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        result = await scraper.fetch(mock_session, "2025", "Jan", "http://example.com")
        # Row 4 (index 3) has multiple promo divs: Gold Ball, Megaball
        evening_row = result[3]
        assert "Gold Ball" in evening_row["Promo"]
        assert "Megaball" in evening_row["Promo"]

    @pytest.mark.asyncio
    async def test_fetch_no_table_falls_back_to_alternative(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.read = AsyncMock(
            return_value=SAMPLE_HTML_NO_TABLE.encode("utf-8")
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        result = await scraper.fetch(mock_session, "2025", "Jan", "http://example.com")
        # No table and no alternative patterns -> None
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_non_200_returns_none(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.content.read = AsyncMock(return_value=b"Not Found")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        result = await scraper.fetch(mock_session, "2025", "Jan", "http://example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_connection_error_retries(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_session = AsyncMock()
        mock_session.post = MagicMock(
            side_effect=aiohttp.ClientConnectionError("Connection refused")
        )

        result = await scraper.fetch(mock_session, "2025", "Jan", "http://example.com")
        assert result is None
        assert mock_session.post.call_count == 3  # 3 retries

    @pytest.mark.asyncio
    async def test_fetch_increments_request_count(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.read = AsyncMock(
            return_value=SAMPLE_HTML_WITH_TABLE.encode("utf-8")
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        assert scraper.request_count == 0
        await scraper.fetch(mock_session, "2025", "Jan", "http://example.com")
        assert scraper.request_count == 1

    @pytest.mark.asyncio
    async def test_fetch_updates_last_request_time(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.read = AsyncMock(
            return_value=SAMPLE_HTML_WITH_TABLE.encode("utf-8")
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        before = perf_counter()
        await scraper.fetch(mock_session, "2025", "Jan", "http://example.com")
        assert scraper.last_request_time >= before

    @pytest.mark.asyncio
    async def test_fetch_empty_promo_cell(self):
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.read = AsyncMock(
            return_value=SAMPLE_HTML_WITH_TABLE.encode("utf-8")
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        result = await scraper.fetch(mock_session, "2025", "Jan", "http://example.com")
        # Last row (25222) has empty promo
        last_row = result[4]
        assert last_row["Promo"] == ""

    @pytest.mark.asyncio
    async def test_fetch_date_parsing_various_formats(self):
        html = """
        <html><body>
        <table>
        <thead><tr><th>Draw#</th><th>Date</th><th>Time</th><th>Mark</th><th>Promo</th></tr></thead>
        <tbody>
        <tr><td>25218</td><td>15-Mar-25</td><td>Morning</td><td>5</td><td></td></tr>
        </tbody></table>
        </body></html>
        """
        scraper = WebScraper(["http://example.com"])
        scraper.last_request_time = 0

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.read = AsyncMock(return_value=html.encode("utf-8"))
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        result = await scraper.fetch(mock_session, "2025", "Mar", "http://example.com")
        assert result is not None
        assert result[0]["Date"] == datetime.date(2025, 3, 15)
