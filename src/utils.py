"""
Utility functions for the LinkedIn Outreach Agent
"""
import time
import random
import re
from typing import Optional
import config


def random_delay(min_seconds: Optional[int] = None, max_seconds: Optional[int] = None):
    """
    Add a random delay to mimic human behavior
    
    Args:
        min_seconds: Minimum delay in seconds (default from config)
        max_seconds: Maximum delay in seconds (default from config)
    """
    min_sec = min_seconds or config.MIN_DELAY_SECONDS
    max_sec = max_seconds or config.MAX_DELAY_SECONDS
    delay = random.uniform(min_sec, max_sec)
    print(f"⏱️  Waiting {delay:.1f} seconds...")
    time.sleep(delay)


def take_break():
    """Take a longer break to avoid detection"""
    print(f"☕ Taking a {config.BREAK_DURATION_SECONDS} second break...")
    time.sleep(config.BREAK_DURATION_SECONDS)


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might break formatting
    text = text.strip()
    return text


def is_valid_linkedin_url(url: str) -> bool:
    """
    Validate if a URL is a valid LinkedIn profile URL
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid LinkedIn profile URL
    """
    pattern = r'^https?://(www\.)?linkedin\.com/in/[\w-]+/?$'
    return bool(re.match(pattern, url))


def extract_profile_id(url: str) -> Optional[str]:
    """
    Extract profile ID from LinkedIn URL
    
    Args:
        url: LinkedIn profile URL
    
    Returns:
        Profile ID or None
    """
    match = re.search(r'linkedin\.com/in/([\w-]+)', url)
    return match.group(1) if match else None


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_skills_list(skills: list, max_skills: int = 5) -> str:
    """
    Format a list of skills into a readable string
    
    Args:
        skills: List of skills
        max_skills: Maximum number of skills to include
    
    Returns:
        Formatted skills string
    """
    if not skills:
        return "various technical skills"
    
    skills = skills[:max_skills]
    if len(skills) == 1:
        return skills[0]
    elif len(skills) == 2:
        return f"{skills[0]} and {skills[1]}"
    else:
        return ", ".join(skills[:-1]) + f", and {skills[-1]}"
