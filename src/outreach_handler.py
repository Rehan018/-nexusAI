"""
Outreach Handler - Send connection requests and messages
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from src.utils import random_delay


class OutreachHandler:
    """Handle sending connection requests and messages"""
    
    def __init__(self, driver, wait: WebDriverWait):
        """
        Initialize outreach handler
        
        Args:
            driver: Selenium WebDriver instance
            wait: WebDriverWait instance
        """
        self.driver = driver
        self.wait = wait
    
    def send_connection_request(self, profile_url: str, note: str) -> bool:
        """
        Send a connection request with personalized note
        
        Args:
            profile_url: LinkedIn profile URL
            note: Personalized connection note
        
        Returns:
            True if successful
        """
        try:
            print(f"📤 Sending connection request...")
            
            # Navigate to profile if not already there
            if self.driver.current_url != profile_url:
                self.driver.get(profile_url)
                random_delay(2, 4)
            
            # Click "Connect" button
            try:
                connect_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Connect')]"))
                )
                connect_button.click()
                time.sleep(2)
            except TimeoutException:
                print("❌ Could not find Connect button")
                return False
            
            # Click "Add a note" button if available
            try:
                add_note_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Add a note')]")
                add_note_button.click()
                time.sleep(1)
                
                # Enter note
                note_field = self.wait.until(
                    EC.presence_of_element_located((By.ID, "custom-message"))
                )
                note_field.clear()
                note_field.send_keys(note)
                time.sleep(1)
                
                print(f"  ✓ Added personalized note")
            except NoSuchElementException:
                print("  ⚠️  Note field not available, sending without note")
            
            # Click "Send" button
            try:
                send_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Send')]"))
                )
                send_button.click()
                time.sleep(2)
                
                print("✅ Connection request sent successfully")
                return True
            except TimeoutException:
                # Try to close modal if stuck
                try:
                    cancel_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Cancel')]")
                    cancel_button.click()
                except:
                    pass
                print("❌ Failed to send connection request")
                return False
        
        except Exception as e:
            print(f"❌ Error sending connection request: {str(e)}")
            return False
    
    def send_message(self, profile_url: str, message: str, attach_resume: bool = False) -> bool:
        """
        Send a message to an existing connection
        
        Args:
            profile_url: LinkedIn profile URL
            message: Personalized message
            attach_resume: Whether to mention resume (LinkedIn messaging has limitations)
        
        Returns:
            True if successful
        """
        try:
            print(f"📧 Sending message...")
            
            # Navigate to profile if not already there
            if self.driver.current_url != profile_url:
                self.driver.get(profile_url)
                random_delay(2, 4)
            
            # Click "Message" button
            message_button = None
            try:
                # Strategy 1: Primary "Message" button (exact text match)
                try:
                    message_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Message']"))
                    )
                except TimeoutException:
                    pass
                
                # Strategy 2: Link styled as button
                if not message_button:
                    try:
                         message_button = self.driver.find_element(By.XPATH, "//a[normalize-space()='Message']")
                    except NoSuchElementException:
                        pass

                # Strategy 3: Check "More" dropdown if button not found
                if not message_button:
                    print("  Button not found, checking 'More' actions...")
                    try:
                        more_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'More actions')]")
                        self.driver.execute_script("arguments[0].click();", more_button) # JS Click
                        time.sleep(1)
                        message_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'artdeco-dropdown')]//div[normalize-space()='Message']"))
                        )
                    except:
                        pass

                if message_button:
                    # Use JS click to avoid click intercepted errors
                    self.driver.execute_script("arguments[0].click();", message_button)
                    time.sleep(2)
                else:
                    print("❌ Could not find Message button (checked main and dropdown)")
                    return False

            except Exception as e:
                print(f"❌ Error finding Message button: {e}")
                return False
            
            # Close any overlapping chat windows first
            try:
                close_bubbles = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'msg-overlay-bubble-header__control') and contains(@aria-label, 'Close')]")
                for bubble in close_bubbles:
                    self.driver.execute_script("arguments[0].click();", bubble)
            except:
                pass

            # Find message input field
            try:
                # Wait for message box to appear
                message_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.msg-form__contenteditable"))
                )
                
                # Click to focus
                message_box.click()
                time.sleep(1)
                
                # Type message
                message_box.send_keys(message)
                time.sleep(2)
                
                # Add resume note if requested
                if attach_resume:
                    resume_note = "\n\nI've attached my resume for your reference."
                    message_box.send_keys(resume_note)
                    time.sleep(1)
                
                # Send message (Ctrl+Enter or click send button)
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, "button.msg-form__send-button")
                    send_button.click()
                except NoSuchElementException:
                    # Try keyboard shortcut
                    message_box.send_keys(Keys.CONTROL + Keys.RETURN)
                
                time.sleep(2)
                print("✅ Message sent successfully")
                return True
            
            except TimeoutException:
                print("❌ Could not find message input field")
                return False
        
        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            return False
    
    def close_message_modal(self):
        """Close any open message modal"""
        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-test-modal-close-btn]")
            close_button.click()
            time.sleep(1)
        except NoSuchElementException:
            pass
