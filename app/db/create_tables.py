from base import Base
from session import engine

import app.db.models

def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Database tables created.")