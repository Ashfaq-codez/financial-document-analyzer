from sqlalchemy import create_engine, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone

SQLALCHEMY_DATABASE_URL = "sqlite:///./financial_analyses.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 Base class
class Base(DeclarativeBase):
    pass

class AnalysisRecord(Base):
    __tablename__ = "analyses"

    # Explicit type hints (Mapped) tell Pylance exactly what Python type to expect,
    # while mapped_column tells SQLAlchemy how to build the database.
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String)
    query: Mapped[str] = mapped_column(String)
    result: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)