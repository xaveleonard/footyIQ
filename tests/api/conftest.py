import pytest
from fastapi.testclient import TestClient

from api.dependencies import build_analytics_bundle, get_analytics_bundle
from api.main import app


@pytest.fixture
def client(teams_parquet_path):
    bundle = build_analytics_bundle(str(teams_parquet_path))
    app.dependency_overrides[get_analytics_bundle] = lambda: bundle

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
