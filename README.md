# nexusAI 🚀

**Autonomous LinkedIn Outreach Agent**

`nexusAI` is a powerful, AI-driven automation tool designed to help professionals connect with recruiters and hiring managers on LinkedIn. It uses Google's Gemini AI to analyze your resume and generate hyper-personalized outreach messages that actually get responses.

---

## ✨ Features

- 🧠 **AI-Powered Personalization**: Deeply analyzes your resume (experience, skills, projects) to write unique messages.
- ⚡ **Fast Pass Verification**: Instantly identifies obvious recruiter profiles to save API quota.
- 🔍 **Deep Verification**: Visits ambiguous profiles in new tabs to extract full text for AI verification.
- 🛡️ **Safety First**: Implements human-like delays, daily action limits, and randomized behavior to protect your LinkedIn account.
- 📊 **Activity Tracking**: Logs all outreach in an SQLite database and prevents duplicate contacts.
- 🔄 **Smart Follow-up**: Automatically detects if a previously contacted person is now "connected" and follows up with a deep message.

---

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Google Chrome installed

### 2. Clone and Initialize

```bash
git clone git@github.com:Rehan018/-nexusAI.git
cd -nexusAI
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory and add your credentials:

```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
GEMINI_API_KEY=your_gemini_api_key
```

### 6. Add Your Resume

Replace `Rehan_AI_Resume.pdf` with your own resume or update the path in `main.py`.

---

## 🚀 Usage

### 1. Configure Target Companies

Edit `data/companies.txt` to add the companies you want to target (one per line).

### 2. Run the Agent

```bash
python main.py
```

### 3. Monitoring

- Check the console for live progress.
- Logs are stored in `data/outreach.db`.
- View `data/outreach_log.csv` for an easy-to-read summary of actions.

---

## ⚙️ Configuration

You can fine-tune the agent's behavior in `config.py`:

- `MAX_CONNECTIONS_PER_DAY`: Max connection requests (Default: 20)
- `MAX_MESSAGES_PER_DAY`: Max messages to existing connections (Default: 15)
- `RECRUITER_TITLES`: Keywords to search for in recruiters.
- `SEARCH_LOCATION`: Target location for your search (Default: "India").

---

## ⚖️ Disclaimer

This tool is for educational purposes only. Automated use of LinkedIn may violate their Terms of Service. Use responsibly and at your own risk.
