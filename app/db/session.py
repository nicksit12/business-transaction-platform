from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = "sqlite:///./business.db"

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
