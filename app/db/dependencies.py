
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from collections.abc import Iterator

def get_session() -> Iterator[Session]:
    with SessionLocal() as session: 
        yield session




