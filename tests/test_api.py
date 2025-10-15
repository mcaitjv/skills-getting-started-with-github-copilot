"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient


def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client, reset_activities):
    """Test GET /activities endpoint"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Should have 9 activities
    
    # Check that Chess Club exists with expected structure
    assert "Chess Club" in data
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert chess_club["max_participants"] == 12
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client, reset_activities):
    """Test successful signup for an activity"""
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify the student was added to the activity
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]


def test_signup_for_nonexistent_activity(client, reset_activities):
    """Test signup for an activity that doesn't exist"""
    email = "student@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_duplicate_registration(client, reset_activities):
    """Test signing up the same student twice for the same activity"""
    email = "michael@mergington.edu"  # Already registered for Chess Club
    activity = "Chess Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success(client, reset_activities):
    """Test successful unregistration from an activity"""
    email = "michael@mergington.edu"  # Already registered for Chess Club
    activity = "Chess Club"
    
    # First verify the student is registered
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]
    
    # Unregister the student
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify the student was removed from the activity
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity]["participants"]


def test_unregister_from_nonexistent_activity(client, reset_activities):
    """Test unregistration from an activity that doesn't exist"""
    email = "student@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_student_not_registered(client, reset_activities):
    """Test unregistering a student who isn't registered for the activity"""
    email = "notregistered@mergington.edu"
    activity = "Chess Club"
    
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"] == "Student is not registered for this activity"


def test_complete_signup_unregister_workflow(client, reset_activities):
    """Test a complete workflow of signup and unregister"""
    email = "workflow@mergington.edu"
    activity = "Programming Class"
    
    # Initial state - student not registered
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    initial_participants = activities_data[activity]["participants"].copy()
    assert email not in initial_participants
    
    # Sign up for activity
    signup_response = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_response.status_code == 200
    
    # Verify signup
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]
    assert len(activities_data[activity]["participants"]) == len(initial_participants) + 1
    
    # Unregister from activity
    unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert unregister_response.status_code == 200
    
    # Verify unregistration
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity]["participants"]
    assert len(activities_data[activity]["participants"]) == len(initial_participants)


def test_activity_data_structure(client, reset_activities):
    """Test that all activities have the required data structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    
    for activity_name, activity_data in data.items():
        # Check required fields exist
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Check data types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        
        # Check constraints
        assert activity_data["max_participants"] > 0
        assert len(activity_data["participants"]) <= activity_data["max_participants"]
        
        # Check that all participants are email strings
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant  # Basic email validation


def test_url_encoding_in_activity_names(client, reset_activities):
    """Test that activity names with spaces are properly URL encoded"""
    email = "urltest@mergington.edu"
    activity = "Chess Club"  # Has a space
    
    # Test signup with URL encoding
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Test unregister with URL encoding
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200