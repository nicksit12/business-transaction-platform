import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.dependencies import get_session
from app.db.models import Category, Merchant, MerchantAlias
from app.main import app
from app.services.merchant_classifier import normalize_description


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as session:
        merchants = {
            "Coffee": ["Starbucks"],
            "Groceries": ["Whole Foods"],
            "Transportation": ["Uber"],
            "Retail": ["Amazon"],
        }
        for category_name, merchant_names in merchants.items():
            category = Category(name=category_name, category_type="expense")
            session.add(category)
            for merchant_name in merchant_names:
                merchant = Merchant(
                    canonical_name=merchant_name,
                    default_category=category,
                )
                merchant.aliases.append(
                    MerchantAlias(
                        normalized_alias=normalize_description(merchant_name)
                    )
                )
                session.add(merchant)
        session.commit()
        yield session


@pytest.fixture
def client(session):
    def use_test_session():
        yield session

    app.dependency_overrides[get_session] = use_test_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
