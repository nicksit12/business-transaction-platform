from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[0]
DATABASE_PATH = PROJECT_ROOT / "business.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    }
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session, 
    autoflush=False,
    expire_on_commit=False,
)
