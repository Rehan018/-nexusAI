"""
Tests for Rate Limiter
"""
import pytest
import os
import json
from datetime import datetime
from src.rate_limiter import RateLimiter


def test_rate_limiter_init():
    """Test rate limiter initialization"""
    test_state_file = "/tmp/test_rate_limit.json"
    
    # Clean up if exists
    if os.path.exists(test_state_file):
        os.remove(test_state_file)
    
    limiter = RateLimiter(state_file=test_state_file)
    
    assert limiter.state['connections_sent'] == 0
    assert limiter.state['messages_sent'] == 0
    assert limiter.state['actions_count'] == 0
    
    # Cleanup
    if os.path.exists(test_state_file):
        os.remove(test_state_file)


def test_can_send_connection():
    """Test connection sending check"""
    test_state_file = "/tmp/test_rate_limit_conn.json"
    
    if os.path.exists(test_state_file):
        os.remove(test_state_file)
    
    limiter = RateLimiter(state_file=test_state_file)
    
    # Should be able to send initially
    assert limiter.can_send_connection() == True
    
    # Cleanup
    if os.path.exists(test_state_file):
        os.remove(test_state_file)


def test_record_connection():
    """Test recording connection request"""
    test_state_file = "/tmp/test_rate_limit_record.json"
    
    if os.path.exists(test_state_file):
        os.remove(test_state_file)
    
    limiter = RateLimiter(state_file=test_state_file)
    
    initial_count = limiter.state['connections_sent']
    limiter.record_connection()
    
    assert limiter.state['connections_sent'] == initial_count + 1
    assert limiter.state['actions_count'] == 1
    
    # Cleanup
    if os.path.exists(test_state_file):
        os.remove(test_state_file)


def test_get_stats():
    """Test getting statistics"""
    test_state_file = "/tmp/test_rate_limit_stats.json"
    
    if os.path.exists(test_state_file):
        os.remove(test_state_file)
    
    limiter = RateLimiter(state_file=test_state_file)
    stats = limiter.get_stats()
    
    assert 'date' in stats
    assert 'connections_sent' in stats
    assert 'messages_sent' in stats
    assert 'connections_remaining' in stats
    
    # Cleanup
    if os.path.exists(test_state_file):
        os.remove(test_state_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
