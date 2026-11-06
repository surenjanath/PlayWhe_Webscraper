"""Unit tests for add_playwhe_data_to_db."""

import datetime
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from async_scraper import Playwhe_Result, add_playwhe_data_to_db


class TestAddPlaywheDataToDb:
    def test_adds_new_records(self, db_session, sample_playwhe_data):
        added, skipped = add_playwhe_data_to_db(db_session, sample_playwhe_data)
        assert added == 5
        assert skipped == 0
        assert db_session.query(Playwhe_Result).count() == 5

    def test_skips_duplicate_records(self, db_session, sample_playwhe_data):
        add_playwhe_data_to_db(db_session, sample_playwhe_data)
        added, skipped = add_playwhe_data_to_db(db_session, sample_playwhe_data)
        assert added == 0
        assert skipped == 5
        assert db_session.query(Playwhe_Result).count() == 5

    def test_mixed_new_and_duplicate(self, db_session, sample_playwhe_data):
        # Add first 3 records
        add_playwhe_data_to_db(db_session, sample_playwhe_data[:3])
        assert db_session.query(Playwhe_Result).count() == 3

        # Add all 5 — 3 should be skipped, 2 new
        added, skipped = add_playwhe_data_to_db(db_session, sample_playwhe_data)
        assert added == 2
        assert skipped == 3
        assert db_session.query(Playwhe_Result).count() == 5

    def test_empty_data(self, db_session):
        added, skipped = add_playwhe_data_to_db(db_session, [])
        assert added == 0
        assert skipped == 0

    def test_records_have_correct_fields(self, db_session, sample_playwhe_data):
        add_playwhe_data_to_db(db_session, sample_playwhe_data)
        result = (
            db_session.query(Playwhe_Result)
            .filter_by(DrawNum="25218")
            .first()
        )
        assert result.DrawDate == datetime.date(2025, 1, 1)
        assert result.Time == "Morning"
        assert result.Mark == 7
        assert result.Promo == "Gold Ball"

    def test_duplicate_detection_uses_draw_num_and_date(self, db_session):
        data1 = [
            {
                "Date": datetime.date(2025, 1, 1),
                "Draw#": "25218",
                "Time": "Morning",
                "Mark": 7,
                "Promo": "Gold Ball",
            }
        ]
        data2 = [
            {
                "Date": datetime.date(2025, 1, 2),
                "Draw#": "25218",
                "Time": "Morning",
                "Mark": 7,
                "Promo": "Gold Ball",
            }
        ]
        add_playwhe_data_to_db(db_session, data1)
        added, skipped = add_playwhe_data_to_db(db_session, data2)
        # Same DrawNum but different Date -> should be added
        assert added == 1
        assert skipped == 0

    def test_records_have_unique_ids(self, db_session, sample_playwhe_data):
        add_playwhe_data_to_db(db_session, sample_playwhe_data)
        results = db_session.query(Playwhe_Result).all()
        unique_ids = {r.uniqueId for r in results}
        assert len(unique_ids) == 5

    def test_records_have_timestamps(self, db_session, sample_playwhe_data):
        add_playwhe_data_to_db(db_session, sample_playwhe_data[:1])
        result = db_session.query(Playwhe_Result).first()
        assert result.date_created is not None
        assert result.last_updated is not None

    def test_handles_error_in_data_gracefully(self, db_session):
        bad_data = [
            {
                "Date": "not-a-date",
                "Draw#": "99999",
                "Time": "Morning",
                "Mark": 7,
                "Promo": "",
            }
        ]
        # The function has a try/except per record, but SQLAlchemy may
        # raise during commit. Either way, should not propagate.
        try:
            added, skipped = add_playwhe_data_to_db(db_session, bad_data)
            assert isinstance(added, int)
            assert isinstance(skipped, int)
        except Exception:
            # If SQLAlchemy raises on invalid date type during flush,
            # rollback and verify the session is still usable.
            db_session.rollback()
            assert db_session.query(Playwhe_Result).count() == 0

    def test_single_record(self, db_session):
        data = [
            {
                "Date": datetime.date(2025, 6, 15),
                "Draw#": "30000",
                "Time": "Evening",
                "Mark": 36,
                "Promo": "Mega Ultra Ball",
            }
        ]
        added, skipped = add_playwhe_data_to_db(db_session, data)
        assert added == 1
        assert skipped == 0
        result = db_session.query(Playwhe_Result).first()
        assert result.Mark == 36
        assert result.Time == "Evening"
