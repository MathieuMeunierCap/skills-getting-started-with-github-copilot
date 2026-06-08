import pytest
from src.app import parse_schedule


class TestParseSchedule:
    """Test suite for parse_schedule() function."""

    def test_parse_valid_schedule_single_day(self):
        """Test parsing a valid schedule with a single day."""
        schedule = "Fridays, 3:30 PM - 5:00 PM"
        result = parse_schedule(schedule)
        
        assert result is not None
        days, start_time, end_time = result
        assert "Friday" in days
        assert start_time.hour == 15
        assert start_time.minute == 30
        assert end_time.hour == 17
        assert end_time.minute == 0

    def test_parse_valid_schedule_multiple_days(self):
        """Test parsing a valid schedule with multiple days."""
        schedule = "Tuesdays and Thursdays, 3:30 PM - 4:30 PM"
        result = parse_schedule(schedule)
        
        assert result is not None
        days, start_time, end_time = result
        assert "Tuesday" in days
        assert "Thursday" in days
        assert start_time.hour == 15
        assert start_time.minute == 30
        assert end_time.hour == 16
        assert end_time.minute == 30

    def test_parse_valid_schedule_multiple_comma_separated_days(self):
        """Test parsing a schedule with multiple comma-separated days."""
        schedule = "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM"
        result = parse_schedule(schedule)
        
        assert result is not None
        days, start_time, end_time = result
        assert "Monday" in days
        assert "Wednesday" in days
        assert "Friday" in days

    def test_parse_valid_schedule_morning_time(self):
        """Test parsing a schedule with morning times."""
        schedule = "Tuesdays, 9:00 AM - 10:30 AM"
        result = parse_schedule(schedule)
        
        assert result is not None
        days, start_time, end_time = result
        assert start_time.hour == 9
        assert start_time.minute == 0
        assert end_time.hour == 10
        assert end_time.minute == 30

    def test_parse_invalid_schedule_no_time(self):
        """Test parsing an invalid schedule without times."""
        schedule = "Mondays and Fridays"
        result = parse_schedule(schedule)
        
        assert result is None

    def test_parse_invalid_schedule_malformed(self):
        """Test parsing a malformed schedule."""
        schedule = "some random text"
        result = parse_schedule(schedule)
        
        assert result is None

    def test_parse_invalid_schedule_empty_string(self):
        """Test parsing an empty schedule."""
        schedule = ""
        result = parse_schedule(schedule)
        
        assert result is None
