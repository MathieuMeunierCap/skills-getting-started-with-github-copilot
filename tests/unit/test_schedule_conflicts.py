import pytest
import copy
from src.app import check_schedule_conflict, activities


class TestScheduleConflict:
    """Test suite for check_schedule_conflict() function."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test by copying original activities."""
        self.original_activities = copy.deepcopy(activities)
        yield
        # Restore original activities after test
        activities.clear()
        activities.update(copy.deepcopy(self.original_activities))

    def test_no_conflict_different_days(self):
        """Test no conflict when activities are on different days."""
        email = "test@mergington.edu"
        # Add student to Monday activity
        activities["Gym Class"]["participants"].append(email)
        
        # Try to sign up for Friday activity
        conflict = check_schedule_conflict(email, "Chess Club", "Fridays, 3:30 PM - 5:00 PM")
        
        assert conflict is None

    def test_no_conflict_different_times(self):
        """Test no conflict when activities are at different times."""
        email = "test@mergington.edu"
        # Add student to early afternoon activity
        activities["Gym Class"]["participants"].append(email)
        
        # Try to sign up for late evening activity
        conflict = check_schedule_conflict(email, "Drama Club", "Thursdays, 4:30 PM - 6:00 PM")
        
        assert conflict is None

    def test_conflict_same_day_overlapping_times(self):
        """Test conflict when activities are on same day with overlapping times."""
        email = "test@mergington.edu"
        # Add student to Tuesday/Thursday 3:30-4:30 activity
        activities["Programming Class"]["participants"].append(email)
        
        # Try to sign up for Tuesday/Thursday 4:00-5:30 activity (overlap)
        conflict = check_schedule_conflict(email, "Soccer Club", "Tuesdays and Thursdays, 4:00 PM - 5:30 PM")
        
        assert conflict == "Programming Class"

    def test_conflict_exact_same_schedule(self):
        """Test conflict when trying to register for same schedule."""
        email = "test@mergington.edu"
        # Add student to Programming Class
        activities["Programming Class"]["participants"].append(email)
        
        # Try to sign up for another activity with exact same schedule
        conflict = check_schedule_conflict(email, "Robotics Club", "Tuesdays and Thursdays, 3:30 PM - 4:30 PM")
        
        assert conflict == "Programming Class"

    def test_no_conflict_when_not_registered(self):
        """Test no conflict when student isn't registered for any activities."""
        email = "new_student@mergington.edu"
        
        conflict = check_schedule_conflict(email, "Chess Club", "Fridays, 3:30 PM - 5:00 PM")
        
        assert conflict is None

    def test_conflict_multiple_registrations(self):
        """Test conflict detection when student has multiple registrations."""
        email = "test@mergington.edu"
        # Add student to two activities
        activities["Gym Class"]["participants"].append(email)
        activities["Chess Club"]["participants"].append(email)
        
        # Try to sign up for activity that conflicts with Chess Club
        # Rugby Team: Wednesdays and Fridays, 3:30-5:00 PM
        # Chess Club: Fridays, 3:30-5:00 PM (conflict on Friday)
        conflict = check_schedule_conflict(email, "Painting Club", "Fridays, 3:30 PM - 5:00 PM")
        
        assert conflict == "Chess Club"

    def test_no_conflict_time_gap(self):
        """Test no conflict when there's a time gap between activities."""
        email = "test@mergington.edu"
        # Add student to 2:00-3:00 PM activity
        activities["Gym Class"]["participants"].append(email)
        
        # Try to sign up for 3:30-5:00 PM activity (30 min gap)
        conflict = check_schedule_conflict(email, "Chess Club", "Fridays, 3:30 PM - 5:00 PM")
        
        assert conflict is None
