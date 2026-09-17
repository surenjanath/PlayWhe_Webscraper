"""Unit tests for comprehensive_analysis and generate_markdown_summary."""

import datetime
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from async_scraper import comprehensive_analysis, generate_markdown_summary


class TestComprehensiveAnalysis:
    def test_returns_string_on_empty_data(self):
        result = comprehensive_analysis([])
        assert isinstance(result, str)
        assert "No data" in result

    def test_returns_string_on_none(self):
        result = comprehensive_analysis(None)
        assert isinstance(result, str)

    def test_returns_dict_with_data(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        assert isinstance(result, dict)

    def test_basic_stats_keys(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        stats = result["basic_stats"]
        assert "total_draws" in stats
        assert "date_range" in stats
        assert "unique_draws" in stats
        assert "unique_dates" in stats
        assert "data_span_days" in stats
        assert "avg_draws_per_day" in stats

    def test_total_draws_count(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        assert result["basic_stats"]["total_draws"] == len(large_playwhe_data)

    def test_time_analysis_keys(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        ta = result["time_analysis"]
        assert "time_distribution" in ta
        assert "most_common_time" in ta
        assert "least_common_time" in ta
        assert "time_balance" in ta

    def test_time_distribution_includes_all_periods(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        dist = result["time_analysis"]["time_distribution"]
        for t in ["Morning", "Midday", "Afternoon", "Evening"]:
            assert t in dist

    def test_time_balance_sums_to_100(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        balance = result["time_analysis"]["time_balance"]
        total = sum(balance.values())
        assert abs(total - 100.0) < 0.1

    def test_number_analysis_keys(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        na = result["number_analysis"]
        assert "average_number" in na
        assert "median_number" in na
        assert "std_deviation" in na
        assert "most_common_numbers" in na
        assert "least_common_numbers" in na
        assert "even_numbers" in na
        assert "odd_numbers" in na
        assert "low_numbers_1_18" in na
        assert "high_numbers_19_36" in na

    def test_even_odd_sum_equals_total(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        na = result["number_analysis"]
        assert na["even_numbers"] + na["odd_numbers"] == len(large_playwhe_data)

    def test_low_high_sum_equals_total(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        na = result["number_analysis"]
        assert na["low_numbers_1_18"] + na["high_numbers_19_36"] == len(large_playwhe_data)

    def test_average_in_range(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        avg = result["number_analysis"]["average_number"]
        assert 1 <= avg <= 36

    def test_promo_analysis_keys(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        pa = result["promo_analysis"]
        assert "promo_distribution" in pa
        assert "total_promos" in pa
        assert "most_common_promo" in pa
        assert "draws_with_promo" in pa
        assert "draws_without_promo" in pa
        assert "promo_percentage" in pa

    def test_promo_with_and_without_sum(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        pa = result["promo_analysis"]
        assert pa["draws_with_promo"] + pa["draws_without_promo"] == len(large_playwhe_data)

    def test_patterns_keys(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        p = result["patterns"]
        assert "consecutive_numbers" in p
        assert "consecutive_percentage" in p
        assert "same_number_repeats" in p
        assert "same_number_percentage" in p
        assert "increasing_trends" in p
        assert "decreasing_trends" in p
        assert "trend_balance" in p

    def test_predictions_keys(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        pred = result["predictions"]
        assert "hot_numbers" in pred
        assert "cold_numbers" in pred
        assert "next_predicted_time" in pred
        assert "over_performing_numbers" in pred
        assert "under_performing_numbers" in pred
        assert "expected_frequency" in pred
        assert "confidence_level" in pred

    def test_hot_numbers_are_top_5(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        assert len(result["predictions"]["hot_numbers"]) == 5

    def test_cold_numbers_are_bottom_5(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        assert len(result["predictions"]["cold_numbers"]) == 5

    def test_confidence_level_low_for_200(self, large_playwhe_data):
        # large_playwhe_data has exactly 200 entries (50 days * 4 draws)
        # 200 is not > 200, so confidence is "Low"
        result = comprehensive_analysis(large_playwhe_data)
        assert result["predictions"]["confidence_level"] == "Low"

    def test_confidence_level_low_for_small_data(self, sample_playwhe_data):
        result = comprehensive_analysis(sample_playwhe_data)
        assert result["predictions"]["confidence_level"] == "Low"

    def test_recent_trends_keys(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        rt = result["recent_trends"]
        assert "recent_hot_numbers" in rt
        assert "recent_cold_numbers" in rt
        assert "recent_time_distribution" in rt
        assert "recent_promo_distribution" in rt

    def test_expected_frequency_calculation(self, large_playwhe_data):
        result = comprehensive_analysis(large_playwhe_data)
        expected = len(large_playwhe_data) / 36
        assert abs(result["predictions"]["expected_frequency"] - expected) < 0.01

    def test_small_dataset(self, sample_playwhe_data):
        result = comprehensive_analysis(sample_playwhe_data)
        assert isinstance(result, dict)
        assert result["basic_stats"]["total_draws"] == 5


class TestGenerateMarkdownSummary:
    def test_returns_markdown_string(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        assert isinstance(md, str)
        assert len(md) > 0

    def test_contains_section_headers(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        assert "Basic Statistics" in md
        assert "Time Distribution" in md
        assert "Hot Numbers" in md
        assert "Cold Numbers" in md
        assert "Number Analysis" in md
        assert "Promo Analysis" in md
        assert "Pattern Analysis" in md
        assert "Predictive Insights" in md
        assert "Recent Trends" in md
        assert "Latest Results" in md

    def test_contains_total_draws(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        assert str(analysis["basic_stats"]["total_draws"]) in md

    def test_contains_table_formatting(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        # Markdown tables use pipes
        assert "|" in md
        assert "---" in md

    def test_contains_last_updated_timestamp(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        assert "Last updated:" in md

    def test_contains_hot_numbers(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        for num in analysis["predictions"]["hot_numbers"]:
            assert str(num) in md

    def test_contains_latest_entries(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        for entry in latest:
            assert str(entry["Draw#"]) in md

    def test_empty_latest_entries(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        md = generate_markdown_summary(analysis, [])
        assert isinstance(md, str)
        assert "Latest Results" in md

    def test_contains_confidence_level(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        assert analysis["predictions"]["confidence_level"] in md

    def test_contains_even_odd_stats(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        assert "Even Numbers" in md
        assert "Odd Numbers" in md

    def test_contains_promo_percentage(self, large_playwhe_data):
        analysis = comprehensive_analysis(large_playwhe_data)
        latest = large_playwhe_data[-5:]
        md = generate_markdown_summary(analysis, latest)
        assert "Draws with Promo" in md
        assert "Draws without Promo" in md
