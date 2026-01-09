"""
Google Gemini AI Client for generating personalized messages
"""
import os
import google.generativeai as genai
import time
from typing import List, Optional
import config


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key (if not provided, reads from env)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in .env file.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    def generate_connection_note(
        self,
        company: str,
        role: str,
        skills: List[str]
    ) -> str:
        """
        Generate a personalized connection request note
        
        Args:
            company: Target company name
            role: Recruiter's role/title
            skills: List of your skills
        
        Returns:
            Personalized connection note
        """
        skills_str = ", ".join(skills[:3])  # Top 3 skills
        
        prompt = config.CONNECTION_NOTE_TEMPLATE.format(
            company=company,
            role=role,
            skills=skills_str
        )
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                note = response.text.strip()
                
                # Ensure it's under character limit
                if len(note) > config.CONNECTION_NOTE_MAX_LENGTH:
                    note = note[:config.CONNECTION_NOTE_MAX_LENGTH - 3] + "..."
                
                return note
            
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota exceeded" in error_str:
                    wait_time = 10 * (attempt + 1)
                    print(f"  ⏳ Gemini Quota exceeded. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"⚠️  Error generating connection note: {str(e)}")
                    break

        # Fallback to simple template
        return f"Hi! I'm interested in opportunities at {company}. I specialize in {skills_str}. Would love to connect!"
    
    def generate_message(
        self,
        name: str,
        company: str,
        role: str,
        skills: List[str],
        experience: str,
        resume_text: str = None
    ) -> str:
        """
        Generate a personalized message for an existing connection
        
        Args:
            name: Recruiter's name
            company: Company name
            role: Recruiter's role
            skills: List of your skills
            experience: Your experience summary
            resume_text: Full text of your resume
        
        Returns:
            Personalized message
        """
        skills_str = ", ".join(skills[:5])  # Top 5 skills
        
        if resume_text:
            # Deep analysis prompt
            prompt = f"""
            Generate a professional, highly personalized LinkedIn message (under 1500 characters) for a recruiter.
            
            Target:
            - Name: {name}
            - Role: {role}
            - Company: {company}
            
            My Profile (RESUME CONTENT):
            {resume_text[:2500]}
            
            Instructions:
            1. Analyze my resume to understand my specific experience level (e.g. 1.8 years), key projects, and strengths.
            2. specific mention of my "1.8 years of experience" if applicable (or exact years found).
            3. Write a message that bridges my specific background to their company.
            4. Keep it professional, concise, and engaging.
            5. Ask for a conversation about relevant roles.
            
            Tone: Confident, specific, professional.
            """
        else:
            prompt = config.MESSAGE_TEMPLATE.format(
                name=name,
                company=company,
                role=role,
                skills=skills_str,
                experience=experience
            )
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                message = response.text.strip()
                
                # Ensure it's under character limit
                if len(message) > config.MESSAGE_MAX_LENGTH:
                    message = message[:config.MESSAGE_MAX_LENGTH - 3] + "..."
                
                return message
            
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota exceeded" in error_str:
                    wait_time = 10 * (attempt + 1)
                    print(f"  ⏳ Gemini Quota exceeded. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"⚠️  Error generating message: {str(e)}")
                    break

        # Fallback to simple template
        return f"""Hi {name},

I hope this message finds you well. I'm reaching out because I'm very interested in opportunities at {company}.

I'm an {experience} with expertise in {skills_str}. I've been following {company}'s work and would love to explore how my skills could contribute to your team.

Would you be open to a brief conversation about potential roles that might be a good fit?

Thank you for your time!

Best regards"""

    def verify_candidate(self, profile_data: dict, target_company: str, full_profile_text: str = None) -> bool:
        """
        Verify if the candidate is relevant using Gemini with retry logic
        
        Args:
            profile_data: Dictionary containing name, role, etc.
            target_company: The company we are targeting
            full_profile_text: Optional full text content of the profile page
            
        Returns:
            True if relevant, False otherwise
        """
        # FAST PASS: Check for obvious matches to save API quota & time
        role_lower = profile_data.get('role', '').lower()
        company_lower = target_company.lower()
        
        # If they explicitly state they work at the company as a recruiter
        # Relaxed check: Just needs "recruiter" keyword AND company name somewhere
        if (company_lower in role_lower) and \
           ("recruiter" in role_lower or "talent" in role_lower or "staffing" in role_lower or "hiring" in role_lower or "hr" in role_lower):
            print(f"  ⚡ Fast pass: Verified '{profile_data.get('role')[:40]}...'")
            return True

        if full_profile_text:
            print(f"  🧠 Deep Analysis: Checking full profile text...")
            prompt = f"""
            I am looking for recruiters, talent acquisition professionals, or HR at '{target_company}'.
            
            Profile Information:
            Name: {profile_data.get('name')}
            Role/Headline: {profile_data.get('role')}
            
            FULL PROFILE CONTENT:
            {full_profile_text[:2000]}  # Limit to 2000 chars to save tokens
            
            Based on the profile text, is this person CURRENTLY a recruiter/HR/Talent Acquisition person at '{target_company}'?
            
            Reply strictly with only 'YES' or 'NO'.
            """
        else:    
            print(f"  🔍 Analysing role: '{profile_data.get('role')[:40]}...' with AI (Not an exact Fast Pass match)")
            prompt = f"""
            I am looking for recruiters, talent acquisition professionals, or HR at '{target_company}'.
            
            Profile Information:
            Name: {profile_data.get('name')}
            Role/Headline: {profile_data.get('role')}
            
            Is this person likely a recruiter, HR, or talent acquisition person CURRENTLY WORKING AT (or hiring for) '{target_company}'?
            
            Reply strictly with only 'YES' or 'NO'.
            """
        
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                result = response.text.strip().upper()
                return "YES" in result
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota exceeded" in error_str:
                    wait_time = 10 * (attempt + 1) # 10s, 20s
                    print(f"  ⏳ Gemini Quota exceeded. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"⚠️  Error verifying candidate with Gemini: {error_str}")
                    break
        
        # Fallback: Simple keyword matching if API fails
        print("  ⚠️  Gemini failed, using fallback keyword check...")
        role = profile_data.get('role', '').lower()
        company = target_company.lower()
        
        # More permissive fallback
        is_recruiter = 'recruiter' in role or 'talent' in role or 'hr' in role or 'human resources' in role or 'hiring' in role
        
        # Check if company name is in role OR if we assume they are from the search results which were company-specific
        # If the search query was strict, we might trust the result if it's a recruiter role
        return is_recruiter
