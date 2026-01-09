"""
Rate Limiter - Control action frequency to avoid detection
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict
import config
from src.utils import random_delay, take_break


class RateLimiter:
    """Manage rate limiting for LinkedIn actions"""
    
    def __init__(self, state_file: str = "data/rate_limit_state.json"):
        """
        Initialize rate limiter
        
        Args:
            state_file: Path to file storing rate limit state
        """
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load rate limit state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return self._get_default_state()
    
    def _get_default_state(self) -> Dict:
        """Get default state structure"""
        today = datetime.now().strftime('%Y-%m-%d')
        return {
            'date': today,
            'connections_sent': 0,
            'messages_sent': 0,
            'actions_count': 0,
            'last_action_time': None
        }
    
    def _save_state(self):
        """Save rate limit state to file"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _reset_if_new_day(self):
        """Reset counters if it's a new day"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.state['date'] != today:
            print(f"📅 New day detected. Resetting rate limits.")
            self.state = self._get_default_state()
            self._save_state()
    
    def can_send_connection(self) -> bool:
        """
        Check if we can send a connection request
        
        Returns:
            True if within rate limits
        """
        self._reset_if_new_day()
        return self.state['connections_sent'] < config.MAX_CONNECTIONS_PER_DAY
    
    def can_send_message(self) -> bool:
        """
        Check if we can send a message
        
        Returns:
            True if within rate limits
        """
        self._reset_if_new_day()
        return self.state['messages_sent'] < config.MAX_MESSAGES_PER_DAY
    
    def record_connection(self):
        """Record that a connection request was sent"""
        self.state['connections_sent'] += 1
        self.state['actions_count'] += 1
        self.state['last_action_time'] = datetime.now().isoformat()
        self._save_state()
        print(f"📊 Connections today: {self.state['connections_sent']}/{config.MAX_CONNECTIONS_PER_DAY}")
    
    def record_message(self):
        """Record that a message was sent"""
        self.state['messages_sent'] += 1
        self.state['actions_count'] += 1
        self.state['last_action_time'] = datetime.now().isoformat()
        self._save_state()
        print(f"📊 Messages today: {self.state['messages_sent']}/{config.MAX_MESSAGES_PER_DAY}")
    
    def apply_delay(self):
        """Apply random delay and check if break is needed"""
        # Random delay between actions
        random_delay()
        
        # Take a break after certain number of actions
        if self.state['actions_count'] > 0 and \
           self.state['actions_count'] % config.BREAK_AFTER_ACTIONS == 0:
            take_break()
    
    def get_stats(self) -> Dict:
        """Get current rate limit statistics"""
        return {
            'date': self.state['date'],
            'connections_sent': self.state['connections_sent'],
            'connections_remaining': config.MAX_CONNECTIONS_PER_DAY - self.state['connections_sent'],
            'messages_sent': self.state['messages_sent'],
            'messages_remaining': config.MAX_MESSAGES_PER_DAY - self.state['messages_sent'],
            'total_actions': self.state['actions_count']
        }
