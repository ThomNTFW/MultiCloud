import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app(environment="test")

    with app.test_client() as client:
        yield client