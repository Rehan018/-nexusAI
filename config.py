"""
Configuration settings for LinkedIn Outreach Agent
"""

# Rate Limiting Settings
MAX_CONNECTIONS_PER_DAY = 20  # Reduced to 20 based on safety recommendations
MAX_MESSAGES_PER_DAY = 15     # Reduced to 15 based on safety recommendations
MIN_DELAY_SECONDS = 10        # Increased minimum delay
MAX_DELAY_SECONDS = 30        # Increased maximum delay for human-like behavior
BREAK_AFTER_ACTIONS = 5       # Take a break more frequently
BREAK_DURATION_SECONDS = 120  # Longer breaks

# LinkedIn Search Settings
# Priority order: Technical Recruiter -> Senior Recruiter -> Talent Acquisition -> Hiring Manager
RECRUITER_TITLES = [
    "Technical Recruiter",
    "Senior Recruiter",
    "Talent Acquisition Partner",
    "Talent Acquisition",
    "University Recruiter",
    "Hiring Manager",
    "Engineering Manager",
    "HR Manager",
    "Recruiter"
]

# Search Filters
SEARCH_LOCATION = "India"  # Can be "India", "Bangalore", "Remote", etc.

# LinkedIn URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_SEARCH_URL = "https://www.linkedin.com/search/results/people/"

# Browser Settings
HEADLESS_MODE = False  # Set to True to run browser in background
BROWSER_TIMEOUT = 20  # Seconds to wait for page elements

# Database Settings
DATABASE_PATH = "data/outreach.db"
LOG_CSV_PATH = "data/outreach_log.csv"

# Gemini Settings
GEMINI_MODEL = "gemini-2.0-flash"
CONNECTION_NOTE_MAX_LENGTH = 250  # LinkedIn connection note character limit
MESSAGE_MAX_LENGTH = 1500  # Reasonable length for message

# Message Templates (used as guidance for Gemini)
CONNECTION_NOTE_TEMPLATE = """
Generate a SHORT, professional connection request note (under 250 characters) with:
- Brief introduction
- Mention of their company
- Your key relevant skill
- Professional interest

Context:
Company: {company}
Their Role: {role}
Your Skills: {skills}

Keep it concise, friendly, and professional. No generic templates.
"""

MESSAGE_TEMPLATE = """
Generate a professional, personalized message (under 1500 characters) for a LinkedIn recruiter:

Context:
- Their Name: {name}
- Their Role: {role}
- Company: {company}
- Your Skills: {skills}
- Your Experience Summary: {experience}

The message should:
1. Greet them professionally
2. Briefly introduce yourself (1-2 sentences)
3. Mention your interest in their company
4. Highlight 2-3 relevant skills/experiences
5. Express interest in relevant opportunities
6. Include a call to action (e.g., "I'd love to connect about potential opportunities")
7. Professional closing

Tone: Professional but warm, confident but not arrogant, genuine interest.
Avoid: Generic templates, excessive flattery, desperation.
"""
