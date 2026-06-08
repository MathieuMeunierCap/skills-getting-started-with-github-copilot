import pytest
import copy
from src.app import activities


class TestEndpoints:
    """Integration tests for FastAPI endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, client, reset_activities):
        """Setup test environment."""
        self.client = client

    def test_get_activities_returns_all_activities(self, client):
        """Test GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self, client):
        """Test GET /activities contains required activity fields."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}", )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity."""
        email = "test@mergington.edu"
        activity = "NonExistentActivity"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_registration(self, client, reset_activities):
        """Test signup fails when student already registered."""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_activity_full(self, client, reset_activities):
        """Test signup fails when activity is at maximum capacity."""
        activity = "Painting Club"  # max_participants: 15
        
        # Fill the activity to capacity (already has 2 participants)
        for i in range(13):
            email = f"student{i}@mergington.edu"
            activities[activity]["participants"].append(email)
        
        # Try to signup when full
        new_email = "fulltest@mergington.edu"
        response = client.post(f"/activities/{activity}/signup?email={new_email}")
        
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_signup_schedule_conflict(self, client, reset_activities):
        """Test signup fails when schedule conflicts with existing registration."""
        email = "test@mergington.edu"
        
        # Add student to Programming Class (Tues/Thurs 3:30-4:30 PM)
        activities["Programming Class"]["participants"].append(email)
        
        # Try to signup for Soccer Club (Tues/Thurs 4:00-5:30 PM - overlaps)
        response = client.post(f"/activities/Soccer Club/signup?email={email}")
        
        assert response.status_code == 409
        assert "conflict" in response.json()["detail"].lower()

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from activity."""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_student_not_registered(self, client):
        """Test unregister fails when student not registered."""
        email = "notstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_activity_not_found(self, client):
        """Test unregister fails for non-existent activity."""
        email = "test@mergington.edu"
        activity = "NonExistentActivity"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_then_unregister_workflow(self, client, reset_activities):
        """Test complete workflow: signup and then unregister."""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify student is registered
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify student is unregistered
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity]["participants"]

    def test_signup_then_signup_different_activity(self, client, reset_activities):
        """Test signup for different activities without conflict."""
        email = "multiactivity@mergington.edu"
        
        # Signup for Chess Club (Friday)
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Signup for Painting Club (Monday) - no conflict
        response2 = client.post(f"/activities/Painting Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both registrations
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Painting Club"]["participants"]
