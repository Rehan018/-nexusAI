# LinkedIn Outreach Agent - Setup Guide for Rehan

## ✅ What's Already Done

Your resume **Rehan_AI_Resume.pdf** is already in the project! The agent successfully extracted:

**Your Skills:**
- Python, Javascript, R
- Tensorflow, Pytorch, AI, NLP
- Postgresql, Mysql, Redis

**Your Experience:**
- 8+ years of professional experience

These will be automatically used to personalize all messages!

## 🚀 Quick Setup Steps

### 1. Create Your Credentials File

Create a `.env` file with your LinkedIn and Gemini API credentials:

```bash
cd /home/rehan/Music/linkdin-agent
cp .env.example .env
nano .env
```

Add your credentials:
```env
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get Gemini API Key:** Visit https://ai.google.dev/ (it's free!)

### 2. Add Target Companies

Edit the companies list:

```bash
nano data/companies.txt
```

Add companies you're targeting (one per line):
```
Google
Microsoft
Amazon
Meta
Netflix
```

### 3. Run the Agent

Activate virtual environment and run:

```bash
source venv/bin/activate
python main.py
```

The agent will:
1. ✅ Parse your resume (already configured!)
2. ✅ Login to LinkedIn
3. ✅ Search for recruiters at each company
4. ✅ Send personalized messages using AI based on YOUR skills
5. ✅ Track everything in `data/outreach_log.csv`

## 📊 What Messages Will Look Like

The AI (Gemini) will generate unique messages for each recruiter like:

**For Connection Requests:**
> "Hi! I'm an AI/ML professional with 8+ years of experience specializing in Python, Tensorflow, and NLP. I'm very interested in opportunities at Google. Would love to connect!"

**For Existing Connections:**
> "Hi [Name], I hope this finds you well. I'm reaching out because I'm very interested in opportunities at Google. I'm an 8+ years professional with expertise in Python, Tensorflow, Pytorch, AI, and NLP. I've been following Google's work in AI/ML and would love to explore how my skills could contribute. Would you be open to a brief conversation about potential roles?"

## ⚙️ Customization (Optional)

### Adjust Daily Limits

Edit `config.py`:
```python
MAX_CONNECTIONS_PER_DAY = 25  # Default is conservative
MAX_MESSAGES_PER_DAY = 30
```

### Change Message Style

Edit the templates in `config.py` to match your tone.

## 📋 Logs & Tracking

After running, check:
- `data/outreach_log.csv` - Full activity log
- `data/outreach.db` - SQLite database
- Console output - Real-time progress

## ⚠️ Important Reminders

- Start with 2-3 companies to test
- LinkedIn may require 2FA verification (complete it in browser)
- Review messages in logs before scaling up
- Default limits are safe: 25 connections/day, 30 messages/day

## 🆘 Need Help?

**Test your setup:**
```bash
source venv/bin/activate

# Test resume parsing (already works!)
python -c "from src.resume_parser import ResumeParser; p = ResumeParser('Rehan_AI_Resume.pdf'); print(p.get_summary())"

# Test Gemini AI (needs API key)
python -c "from src.gemini_client import GeminiClient; c = GeminiClient(); print(c.generate_connection_note('Google', 'Recruiter', ['Python', 'AI']))"
```

---

**You're all set!** Just add your LinkedIn credentials and Gemini API key to `.env`, then run `python main.py`
