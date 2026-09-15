import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import models  # noqa: F401 — registers all models with Base
from app.database.base import Base


def _in_memory_engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def db_session():
    engine = _in_memory_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def session_factory():
    engine = _in_memory_engine()
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)
