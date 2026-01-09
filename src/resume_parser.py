"""
Resume Parser - Extract skills and information from resume
"""
import os
import re
from typing import Dict, List, Optional
import PyPDF2


class ResumeParser:
    """Parse resume to extract relevant information"""
    
    def __init__(self, resume_path: str):
        """
        Initialize resume parser
        
        Args:
            resume_path: Path to resume file (PDF or TXT)
        """
        self.resume_path = resume_path
        self.text = self._extract_text()
        
    def _extract_text(self) -> str:
        """
        Extract text from resume file
        
        Returns:
            Extracted text content
        """
        if not os.path.exists(self.resume_path):
            raise FileNotFoundError(f"Resume file not found: {self.resume_path}")
        
        ext = os.path.splitext(self.resume_path)[1].lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf()
        elif ext == '.txt':
            return self._extract_from_txt()
        else:
            raise ValueError(f"Unsupported file format: {ext}. Use PDF or TXT.")
    
    def _extract_from_pdf(self) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(self.resume_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def _extract_from_txt(self) -> str:
        """Extract text from TXT file"""
        try:
            with open(self.resume_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    def extract_skills(self) -> List[str]:
        """
        Extract skills from resume
        
        Returns:
            List of identified skills
        """
        # Common technical skills to look for
        skill_keywords = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#', 'ruby', 'go',
            'php', 'swift', 'kotlin', 'rust', 'scala', 'r\\b',
            # Frameworks & Libraries
            'react', 'angular', 'vue', 'node\\.?js', 'django', 'flask', 'spring',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn',
            # Technologies
            'machine learning', 'deep learning', 'ai', 'artificial intelligence',
            'data science', 'nlp', 'computer vision', 'neural networks',
            'cloud computing', 'aws', 'azure', 'gcp', 'google cloud',
            'docker', 'kubernetes', 'devops', 'ci/cd',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'git', 'agile', 'scrum', 'rest api', 'graphql',
            'microservices', 'blockchain', 'iot',
            # Soft Skills
            'leadership', 'communication', 'problem solving', 'team work',
            'project management', 'analytical', 'critical thinking'
        ]
        
        text_lower = self.text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + skill + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Capitalize properly
                skill_clean = skill.replace('\\b', '').replace('\\+\\+', '++').replace('\\.?', '.')
                if skill_clean not in [s.lower() for s in found_skills]:
                    # Proper capitalization
                    if skill_clean in ['ai', 'nlp', 'aws', 'gcp', 'iot', 'ci/cd', 'sql', 'nosql']:
                        found_skills.append(skill_clean.upper())
                    elif 'node' in skill_clean:
                        found_skills.append('Node.js')
                    elif skill_clean == 'c#':
                        found_skills.append('C#')
                    elif skill_clean == 'c++':
                        found_skills.append('C++')
                    else:
                        found_skills.append(skill_clean.title())
        
        return found_skills[:10]  # Return top 10 skills
    
    def extract_experience_summary(self) -> str:
        """
        Extract a brief experience summary
        
        Returns:
            Experience summary string
        """
        # Look for years of experience (supports decimals, e.g. 1.8 years)
        years_pattern = r'(\d+(?:\.\d+)?)\+?\s*years?\s*(of)?\s*experience'
        years_match = re.search(years_pattern, self.text, re.IGNORECASE)
        
        if years_match:
            years = years_match.group(1)
            return f"{years} years of professional experience"
        
        # Look for job titles
        title_keywords = ['engineer', 'developer', 'scientist', 'analyst', 'manager', 
                         'architect', 'consultant', 'specialist', 'lead']
        
        for keyword in title_keywords:
            pattern = r'(senior\s+|junior\s+|lead\s+)?' + keyword
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return f"Experienced {match.group(0).strip()}"
        
        return "Experienced professional"
    
    def get_summary(self) -> Dict[str, any]:
        """
        Get complete resume summary
        
        Returns:
            Dictionary with skills and experience
        """
        return {
            'skills': self.extract_skills(),
            'experience': self.extract_experience_summary(),
            'full_text': self.text[:4000]  # Increased limit for deep analysis
        }
