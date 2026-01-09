# Quick Start Guide

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd /home/rehan/Music/linkdin-agent
pip install -r requirements.txt
```

### 2. Configure Credentials

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your credentials:

```
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=YourSecurePassword
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get Gemini API Key**: Visit <https://ai.google.dev/> and sign up for a free API key.

### 3. Add Your Resume

Replace the sample resume with your own:

```bash
# Copy your resume (PDF or TXT format)
cp /path/to/your/resume.pdf data/resume.pdf
# OR
cp /path/to/your/resume.txt data/resume.txt
```

**Note**: You can use `data/resume_sample.txt` as a template.

### 4. Add Target Companies

Edit the companies list:

```bash
nano data/companies.txt
```

Add one company name per line:

```
Google
Microsoft
Amazon
Apple
Meta
Netflix
Tesla
```

**Tips:**

- Use exact company names as they appear on LinkedIn
- Start with 2-3 companies for testing
- You can add more later

### 5. Run the Agent

```bash
python main.py
```

The agent will:

1. ✅ Parse your resume
2. ✅ Login to LinkedIn (may require manual 2FA verification)
3. ✅ Search for recruiters at each company
4. ✅ Send personalized messages/connection requests
5. ✅ Log all activities

### 6. Monitor Progress

Watch the console output for real-time progress. After completion, check:

- `data/outreach_log.csv` - Detailed activity log
- `data/outreach.db` - SQLite database with all records

## Customization

### Adjust Rate Limits

Edit `config.py`:

```python
MAX_CONNECTIONS_PER_DAY = 25  # Increase/decrease as needed
MAX_MESSAGES_PER_DAY = 30
MIN_DELAY_SECONDS = 5  # Minimum delay between actions
MAX_DELAY_SECONDS = 15  # Maximum delay between actions
```

**Warning**: Higher limits increase detection risk!

### Customize Message Templates

Edit the prompt templates in `config.py`:

```python
CONNECTION_NOTE_TEMPLATE = """
Your custom template here...
"""

MESSAGE_TEMPLATE = """
Your custom message template...
"""
```

### Change Recruiter Search Terms

Modify the search terms in `config.py`:

```python
RECRUITER_TITLES = [
    "Talent Acquisition",
    "Recruiter",
    "HR Manager",
    "Your Custom Title",
]
```

## Testing

### Test Individual Components

**Test Resume Parser:**

```bash
python -c "from src.resume_parser import ResumeParser; p = ResumeParser('data/resume.pdf'); print(p.extract_skills())"
```

**Test Gemini AI:**

```bash
python -c "from src.gemini_client import GeminiClient; c = GeminiClient(); print(c.generate_connection_note('Google', 'Recruiter', ['Python', 'AI']))"
```

**Run Unit Tests:**

```bash
pytest tests/ -v
```

## Troubleshooting

### Browser Not Opening

- Update Chrome: `google-chrome --version`
- Reinstall Selenium: `pip install --upgrade selenium webdriver-manager`

### Login Fails

- Check credentials in `.env`
- Complete 2FA manually when prompted (60 seconds timeout)
- Try disabling headless mode in `config.py`: `HEADLESS_MODE = False`

### No Profiles Found

- Use exact company names
- Try broader search terms in `RECRUITER_TITLES`
- Check if companies have public profiles

### Gemini API Errors

- Verify API key is correct
- Check API quota at <https://ai.google.dev/>
- Fallback templates will be used automatically

## Safety Tips

✅ **DO:**

- Start with small batches (2-3 companies)
- Review generated messages in logs
- Monitor your LinkedIn account for restrictions
- Keep rate limits conservative

❌ **DON'T:**

- Run continuously for hours
- Ignore LinkedIn warnings
- Use overly aggressive rate limits
- Share your credentials or API keys

## Support

Check logs for errors:

```bash
cat data/outreach_log.csv
```

View database records:

```bash
sqlite3 data/outreach.db "SELECT * FROM outreach_log;"
```

---

**Need help?** Review the main [README.md](README.md) for detailed documentation.
