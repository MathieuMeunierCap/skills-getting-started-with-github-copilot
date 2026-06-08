import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture providing a test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities database before and after each test."""
    original_activities = copy.deepcopy(activities)
    yield
    # Reset activities after test
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def sample_activities():
    """Fixture providing sample activities for testing."""
    return copy.deepcopy(activities)
