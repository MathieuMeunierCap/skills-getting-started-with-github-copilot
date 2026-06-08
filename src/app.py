"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import re
from pathlib import Path
from datetime import datetime


def parse_schedule(schedule: str):
    """Parse schedule string to extract days and times.
    
    Returns: (days_list, start_time, end_time) or None if parsing fails
    """
    try:
        # Extract days and times using regex
        # Format: "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM"
        match = re.match(r"(.+?),\s*(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))", schedule)
        if not match:
            return None
        
        days_str = match.group(1)
        start_time_str = match.group(2)
        end_time_str = match.group(3)
        
        # Parse days
        days = re.findall(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", days_str)
        
        # Convert times to 24-hour format for comparison
        start_time = datetime.strptime(start_time_str.strip(), "%I:%M %p").time()
        end_time = datetime.strptime(end_time_str.strip(), "%I:%M %p").time()
        
        return (days, start_time, end_time)
    except Exception:
        return None


def check_schedule_conflict(email: str, new_activity_name: str, new_schedule: str):
    """Check if a student has a schedule conflict with the new activity.
    
    Returns: conflicting_activity_name or None
    """
    new_parsed = parse_schedule(new_schedule)
    if not new_parsed:
        return None
    
    new_days, new_start, new_end = new_parsed
    
    # Check all activities for conflicts
    for activity_name, activity_data in activities.items():
        if activity_name == new_activity_name:
            continue
        
        # Check if student is already in this activity
        if email in activity_data["participants"]:
            existing_parsed = parse_schedule(activity_data["schedule"])
            if not existing_parsed:
                continue
            
            existing_days, existing_start, existing_end = existing_parsed
            
            # Check if days overlap
            days_overlap = any(day in new_days for day in existing_days)
            
            # Check if times overlap
            times_overlap = not (new_end <= existing_start or new_start >= existing_end)
            
            if days_overlap and times_overlap:
                return activity_name
    
    return None


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Play and train in soccer, the world’s most popular sport",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 30,
        "participants": ["noah@mergington.edu", "mia@mergington.edu"]
    },
    "Rugby Team": {
        "description": "Train for rugby matches and learn teamwork on the field",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 30,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Painting Club": {
        "description": "Explore painting techniques and create visual art projects",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    },
    "Drama Club": {
        "description": "Practice acting, stage production, and performance skills",
        "schedule": "Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 18,
        "participants": ["amelia@mergington.edu", "sophia@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills for competitions",
        "schedule": "Mondays and Wednesdays, 5:00 PM - 6:30 PM",
        "max_participants": 16,
        "participants": ["noah@mergington.edu", "emma@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Design and build robots while learning engineering concepts",
        "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
        "max_participants": 14,
        "participants": ["jack@mergington.edu", "isabella@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")
    
    # Check for schedule conflicts
    conflicting_activity = check_schedule_conflict(email, activity_name, activity["schedule"])
    if conflicting_activity:
        raise HTTPException(
            status_code=409, 
            detail=f"Schedule conflict: Student is already registered for {conflicting_activity} at the same time"
        )
    
    # Validate activity is not full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student not registered for this activity")

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
