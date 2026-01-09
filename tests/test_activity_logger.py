"""
Tests for Activity Logger
"""
import pytest
import os
from src.activity_logger import ActivityLogger


def test_activity_logger_init():
    """Test activity logger initialization"""
    test_db = "/tmp/test_outreach.db"
    
    # Clean up if exists
    if os.path.exists(test_db):
        os.remove(test_db)
    
    logger = ActivityLogger(db_path=test_db)
    
    # Check database was created
    assert os.path.exists(test_db)
    
    # Cleanup
    os.remove(test_db)


def test_log_action():
    """Test logging an action"""
    test_db = "/tmp/test_outreach_log.db"
    
    if os.path.exists(test_db):
        os.remove(test_db)
    
    logger = ActivityLogger(db_path=test_db)
    
    # Log an action
    logger.log_action(
        company="Google",
        profile_url="https://linkedin.com/in/test123",
        name="Test User",
        role="Recruiter",
        connection_status="not_connected",
        action_type="connection_request",
        message_sent="Test message",
        status="success"
    )
    
    # Verify it was logged
    logs = logger.get_all_logs()
    assert len(logs) == 1
    assert logs[0]['company'] == "Google"
    assert logs[0]['name'] == "Test User"
    
    # Cleanup
    os.remove(test_db)


def test_is_duplicate():
    """Test duplicate detection"""
    test_db = "/tmp/test_outreach_dup.db"
    
    if os.path.exists(test_db):
        os.remove(test_db)
    
    logger = ActivityLogger(db_path=test_db)
    
    profile_url = "https://linkedin.com/in/test456"
    
    # Should not be duplicate initially
    assert logger.is_duplicate(profile_url) == False
    
    # Log an action
    logger.log_action(
        company="Microsoft",
        profile_url=profile_url,
        name="Test User 2",
        role="HR Manager",
        connection_status="connected",
        action_type="message",
        message_sent="Test",
        status="success"
    )
    
    # Should now be duplicate
    assert logger.is_duplicate(profile_url) == True
    
    # Cleanup
    os.remove(test_db)


def test_get_summary():
    """Test getting summary statistics"""
    test_db = "/tmp/test_outreach_summary.db"
    
    if os.path.exists(test_db):
        os.remove(test_db)
    
    logger = ActivityLogger(db_path=test_db)
    
    # Log multiple actions
    logger.log_action("Google", "https://linkedin.com/in/test1", "User1", "Recruiter", 
                     "not_connected", "connection_request", "Message1", "success")
    logger.log_action("Google", "https://linkedin.com/in/test2", "User2", "HR Manager",
                     "connected", "message", "Message2", "success")
    
    summary = logger.get_summary()
    
    assert summary['total_actions'] == 2
    assert summary['companies_contacted'] == 1
    assert summary['connections_sent'] == 1
    assert summary['messages_sent'] == 1
    
    # Cleanup
    os.remove(test_db)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
