"""Unit tests for the Playwhe_Result SQLAlchemy model."""

import datetime
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from async_scraper import Playwhe_Result


class TestPlaywheResult:
    def test_init_sets_fields(self):
        result = Playwhe_Result(
            DrawDate=datetime.date(2025, 1, 1),
            DrawNum="25218",
            Time="Morning",
            Mark=7,
            Promo="Gold Ball",
        )
        assert result.DrawDate == datetime.date(2025, 1, 1)
        assert result.DrawNum == "25218"
        assert result.Time == "Morning"
        assert result.Mark == 7
        assert result.Promo == "Gold Ball"

    def test_init_generates_unique_id(self):
        r1 = Playwhe_Result(datetime.date(2025, 1, 1), "25218", "Morning", 7, "Gold Ball")
        r2 = Playwhe_Result(datetime.date(2025, 1, 1), "25219", "Midday", 24, "Megaball")
        assert r1.uniqueId is not None
        assert r2.uniqueId is not None
        assert r1.uniqueId != r2.uniqueId

    def test_init_sets_timestamps(self):
        before = datetime.datetime.now()
        result = Playwhe_Result(datetime.date(2025, 1, 1), "25218", "Morning", 7, "")
        after = datetime.datetime.now()
        assert before <= result.date_created <= after
        assert before <= result.last_updated <= after

    def test_repr(self):
        result = Playwhe_Result(datetime.date(2025, 1, 1), "25218", "Morning", 7, "Gold Ball")
        repr_str = repr(result)
        assert "2025-01-01" in repr_str
        assert "Morning" in repr_str
        assert "7" in repr_str

    def test_unique_id_is_hex_string(self):
        result = Playwhe_Result(datetime.date(2025, 1, 1), "25218", "Morning", 7, "")
        assert len(result.uniqueId) == 12
        assert all(c in "0123456789abcdef" for c in result.uniqueId)

    def test_empty_promo(self):
        result = Playwhe_Result(datetime.date(2025, 1, 1), "25218", "Morning", 7, "")
        assert result.Promo == ""

    def test_multiple_promos(self):
        result = Playwhe_Result(
            datetime.date(2025, 1, 1), "25221", "Evening", 32, "Gold Ball, Megaball"
        )
        assert "Gold Ball" in result.Promo
        assert "Megaball" in result.Promo

    def test_persist_to_db(self, db_session):
        result = Playwhe_Result(datetime.date(2025, 1, 1), "25218", "Morning", 7, "Gold Ball")
        db_session.add(result)
        db_session.commit()

        queried = db_session.query(Playwhe_Result).first()
        assert queried is not None
        assert queried.DrawNum == "25218"
        assert queried.Mark == 7

    def test_query_filter(self, db_session):
        r1 = Playwhe_Result(datetime.date(2025, 1, 1), "25218", "Morning", 7, "Gold Ball")
        r2 = Playwhe_Result(datetime.date(2025, 1, 1), "25219", "Midday", 24, "Megaball")
        db_session.add_all([r1, r2])
        db_session.commit()

        morning = db_session.query(Playwhe_Result).filter_by(Time="Morning").all()
        assert len(morning) == 1
        assert morning[0].DrawNum == "25218"

    def test_all_time_values(self, db_session):
        times = ["Morning", "Midday", "Afternoon", "Evening"]
        for i, t in enumerate(times):
            db_session.add(
                Playwhe_Result(datetime.date(2025, 1, 1), str(25218 + i), t, i + 1, "")
            )
        db_session.commit()
        assert db_session.query(Playwhe_Result).count() == 4

    def test_mark_boundary_values(self):
        r_low = Playwhe_Result(datetime.date(2025, 1, 1), "25218", "Morning", 1, "")
        r_high = Playwhe_Result(datetime.date(2025, 1, 1), "25219", "Morning", 36, "")
        assert r_low.Mark == 1
        assert r_high.Mark == 36
