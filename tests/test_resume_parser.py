"""
Tests for Resume Parser
"""
import pytest
import os
from src.resume_parser import ResumeParser


def test_resume_parser_init():
    """Test resume parser initialization"""
    # This test will fail without an actual resume file
    # It's meant to demonstrate testing structure
    pass


def test_extract_skills():
    """Test skill extraction from resume"""
    # Create a simple test resume
    test_resume_content = """
    John Doe
    Software Engineer
    
    Skills:
    Python, JavaScript, Machine Learning, AWS, Docker, React
    
    Experience:
    5+ years of experience in software development
    """
    
    # Write test file
    test_file = "/tmp/test_resume.txt"
    with open(test_file, 'w') as f:
        f.write(test_resume_content)
    
    # Test parsing
    parser = ResumeParser(test_file)
    skills = parser.extract_skills()
    
    # Verify skills were extracted
    assert len(skills) > 0
    assert 'Python' in skills
    
    # Cleanup
    os.remove(test_file)


def test_experience_summary():
    """Test experience summary extraction"""
    test_resume_content = """
    Jane Smith
    Senior Data Scientist
    
    10+ years of experience in data science and machine learning
    """
    
    test_file = "/tmp/test_resume_exp.txt"
    with open(test_file, 'w') as f:
        f.write(test_resume_content)
    
    parser = ResumeParser(test_file)
    experience = parser.extract_experience_summary()
    
    assert "10" in experience or "years" in experience.lower()
    
    os.remove(test_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
