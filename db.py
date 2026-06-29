"""Database models and helpers for the PlayWhe scraper."""

import datetime
from uuid import uuid4

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_PATH

Base = declarative_base()


class PlaywheResult(Base):
    __tablename__ = 'playwhe_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    DrawDate = Column(Date)
    DrawNum = Column(String)
    Time = Column(String)
    Mark = Column(Integer)
    Promo = Column(String)
    uniqueId = Column(String)
    last_updated = Column(DateTime)
    date_created = Column(DateTime)

    def __init__(self, DrawDate, DrawNum, Time, Mark, Promo):
        self.DrawDate = DrawDate
        self.DrawNum = DrawNum
        self.Time = Time
        self.Mark = Mark
        self.Promo = Promo
        self.uniqueId = str(uuid4()).split('-')[4]
        self.date_created = datetime.datetime.now()
        self.last_updated = datetime.datetime.now()

    def __repr__(self):
        return (
            f"<PlaywheResult(DrawDate='{self.DrawDate}', "
            f"Time='{self.Time}', Mark={self.Mark})>"
        )


def get_engine(echo=False):
    """Create and return a SQLAlchemy engine for the PlayWhe database."""
    return create_engine(f'sqlite:///{DATABASE_PATH}', echo=echo)


def get_session(engine=None):
    """Return a new database session, creating the engine if needed."""
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def add_playwhe_data(session, playwhe_data):
    """Add PlayWhe records to the database, skipping duplicates.

    Returns ``(added_count, skipped_count)``.
    """
    added = 0
    skipped = 0

    for data in playwhe_data:
        try:
            existing = session.query(PlaywheResult).filter_by(
                DrawNum=data['Draw#'],
                DrawDate=data['Date'],
            ).first()

            if existing:
                skipped += 1
                continue

            session.add(PlaywheResult(
                DrawDate=data['Date'],
                DrawNum=data['Draw#'],
                Time=data['Time'],
                Mark=data['Mark'],
                Promo=data['Promo'],
            ))
            added += 1
        except Exception as e:
            print(f'[*] Error adding data: {e}')
            continue

    session.commit()
    print(f'[*] Added {added} new records, skipped {skipped} duplicates')
    return added, skipped
