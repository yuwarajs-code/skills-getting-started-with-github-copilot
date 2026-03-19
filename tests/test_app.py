"""
Test suite for the Mergington High School API endpoints.
Tests cover getting activities, signup (success/failure), and participant removal.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_200_and_data():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert email in response.json()["message"]

    response_after = client.get("/activities")
    assert email in response_after.json()[activity_name]["participants"]


def test_signup_for_activity_duplicate():
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"

    response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response1.status_code == 200

    response2 = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_remove_participant_success():
    activity_name = "Art Studio"
    email = "remove_test@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert delete_response.status_code == 200

    response_after = client.get("/activities")
    assert email not in response_after.json()[activity_name]["participants"]


def test_remove_participant_not_found():
    activity_name = "Tennis Club"
    email = "notfound@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]
