"""
LinkedIn Authentication - Handle browser automation and login
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import config


class LinkedInAuth:
    """Handle LinkedIn authentication and browser session"""
    
    def __init__(self, email: str = None, password: str = None, headless: bool = None):
        """
        Initialize LinkedIn authentication
        
        Args:
            email: LinkedIn email (from env if not provided)
            password: LinkedIn password (from env if not provided)
            headless: Run browser in headless mode
        """
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        
        if not self.email or not self.password:
            raise ValueError("LinkedIn credentials not found. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file.")
        
        self.headless = headless if headless is not None else config.HEADLESS_MODE
        self.driver = None
        self.wait = None
    
    def init_browser(self):
        """Initialize Chrome browser with proper settings"""
        print("🌐 Initializing browser...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Add options to appear more human-like
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Ignore SSL errors
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument('--ignore-ssl-errors')
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, config.BROWSER_TIMEOUT)
        print("✅ Browser initialized")
    
    def login(self) -> bool:
        """
        Login to LinkedIn
        
        Returns:
            True if login successful
        """
        if not self.driver:
            self.init_browser()
        
        try:
            print("🔐 Logging in to LinkedIn...")
            self.driver.get(config.LINKEDIN_LOGIN_URL)
            time.sleep(2)
            
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.email)
            time.sleep(1)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            time.sleep(1)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                print("✅ Successfully logged in to LinkedIn")
                return True
            elif "checkpoint" in self.driver.current_url or "challenge" in self.driver.current_url:
                print("⚠️  LinkedIn security checkpoint detected!")
                print("Please complete the verification manually in the browser window.")
                print("Waiting for manual verification... (you have 60 seconds)")
                
                # Wait for user to complete verification
                for i in range(60):
                    time.sleep(1)
                    if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                        print("✅ Verification completed! Logged in successfully.")
                        return True
                
                print("❌ Verification timeout. Please try again.")
                return False
            else:
                print("❌ Login failed. Please check your credentials.")
                return False
        
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
            return False
    
    def is_logged_in(self) -> bool:
        """
        Check if currently logged in
        
        Returns:
            True if logged in
        """
        if not self.driver:
            return False
        
        try:
            current_url = self.driver.current_url
            return "linkedin.com" in current_url and "login" not in current_url
        except:
            return False
    
    def close(self):
        """Close browser session"""
        if self.driver:
            print("🔒 Closing browser...")
            self.driver.quit()
            self.driver = None
