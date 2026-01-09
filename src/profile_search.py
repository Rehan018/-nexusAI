"""
Profile Search - Search for recruiters and HR professionals
"""
import time
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import config
from src.utils import random_delay


class ProfileSearch:
    """Search for LinkedIn profiles"""
    
    def __init__(self, driver, wait: WebDriverWait):
        """
        Initialize profile search
        
        Args:
            driver: Selenium WebDriver instance
            wait: WebDriverWait instance
        """
        self.driver = driver
        self.wait = wait
    
    def search_recruiters(self, company: str, max_results: int = 10, gemini_client=None) -> List[Dict]:
        """
        Search for recruiters at a specific company
        
        Args:
            company: Company name
            max_results: Maximum number of results to return
        
        Returns:
            List of profile dictionaries
        """
        print(f"\n🔍 Searching for recruiters at {company}...")
        
        profiles = []
        
        # Build Boolean search query: ("Title1" OR "Title2") AND "Company"
        # We take top 4 titles to avoid query being too long
        titles = config.RECRUITER_TITLES[:4]
        title_query = " OR ".join([f'"{title}"' for title in titles])
        search_query = f'({title_query}) AND "{company}"'
        
        # URL encode the query
        import urllib.parse
        encoded_query = urllib.parse.quote(search_query)
        
        # Construct search URL with filters
        # origin=SWITCH_SEARCH_VERTICAL&sid=... are standard LinkedIn params but might not be strictly needed
        # We add location filter if configured. GeoUrn for India is roughly 102713980, but using keywords is safer if we don't have IDs.
        # However, accurate location filtering usually requires the geoUrn parameter.
        # For now, we will add the location to the keywords if generic, but the user requested explicit filters.
        # Let's try to append the location to the query first as " AND Location" which works reasonably well.
        
        if hasattr(config, 'SEARCH_LOCATION') and config.SEARCH_LOCATION:
            encoded_query = urllib.parse.quote(f'{search_query} AND "{config.SEARCH_LOCATION}"')
            
        search_url = f"{config.LINKEDIN_SEARCH_URL}?keywords={encoded_query}"
        
        try:
            print(f"  🔗 Visiting: {search_url}")
            self.driver.get(search_url)
            random_delay(5, 8) # Initial delay after navigation
            
            # Check for security checkpoint
            if "checkpoint" in self.driver.current_url or "challenge" in self.driver.current_url:
                print("⚠️  Security checkpoint detected! Please verify manually.")
                time.sleep(30) # Give user time to solve
            
            # Wait for results to load
            try:
                # Wait for either the results list or distinct result items
                # Using the stable selector we found
                self.wait.until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "div[data-view-name='people-search-result']") or 
                              d.find_elements(By.CLASS_NAME, "reusable-search__result-container") or
                              d.find_elements(By.XPATH, "//ul[contains(@class, 'reusable-search__entity-result-list')]")
                )
            except TimeoutException:
                print("⚠️  Timeout waiting for results. Taking debug screenshot...")
                self.driver.save_screenshot(f"debug_search_fail_{company}.png")
                # Dump page source to file for debugging
                with open(f"debug_page_source_{company}.html", "w", encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                
                # Check for "No results found" message
                if "No results found" in self.driver.page_source:
                    print(f"⚠️  No recruiters found at {company}")
                    return []
                
                # Try simpler fallback search
                print("🔄 Retrying with simpler query...")
                simple_search_url = f"https://www.linkedin.com/search/results/people/?keywords=Recruiter%20at%20{company}&origin=GLOBAL_SEARCH_HEADER"
                self.driver.get(simple_search_url)
                random_delay(5, 8) # Delay after fallback navigation
                
                # If still no results, return empty
                if "No results found" in self.driver.page_source:
                     print("❌ Fallback search also failed. Saving debug screenshot.")
                     self.driver.save_screenshot(f"debug_search_fail_fallback_{company}.png")
                     return []
            
            # Scroll to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract profile information using multiple strategies
            result_elements = []
            
            # Strategy 1: Use stable data-view-name attribute (Best for 2024/2025)
            result_elements = self.driver.find_elements(By.XPATH, "//div[@data-view-name='people-search-result']")
            
            # Strategy 2: Fallback to list items
            if not result_elements:
                try:
                    result_elements = self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'reusable-search__entity-result-list')]/li")
                except:
                    pass
            
            # Strategy 3: Fallback to class name
            if not result_elements:
                result_elements = self.driver.find_elements(By.CLASS_NAME, "reusable-search__result-container")
            
            if not result_elements:
                print("⚠️  Could not find result elements even after wait")
                # Debug: print page source length
                print(f"  Debug: Page source length: {len(self.driver.page_source)}")
                return profiles

            for element in result_elements[:max_results]:
                try:
                    profile = self._extract_profile_info(element, company)
                    if profile:
                        # User Request Enhancement: "Gemini se verify karwao" + Deep Verification
                        if gemini_client:
                             # 1. Try Fast Pass / Basic Verification first
                             print(f"  🤖 Verifying snippet: {profile['name']} ({profile['role']})")
                             
                             # We check if it's an obvious fast pass match locally to avoid API if possible
                             role_lower = profile['role'].lower()
                             company_lower = company.lower()
                             is_fast_pass = (company_lower in role_lower) and \
                                            ("recruiter" in role_lower or "talent" in role_lower or "staffing" in role_lower or "hiring" in role_lower or "hr" in role_lower)
                             
                             should_deep_verify = False
                             
                             if is_fast_pass:
                                 print(f"  ⚡ Fast pass: Verified from snippet!")
                                 is_relevant = True
                             else:
                                 # 2. Deep Verification: Open Profile in New Tab
                                 print(f"  🔍 Snippet ambiguous. Opening profile for Deep Analysis...")
                                 should_deep_verify = True
                                 
                             if should_deep_verify:
                                 try:
                                     # Store current handle
                                     main_window = self.driver.current_window_handle
                                     
                                     # Open new tab
                                     self.driver.execute_script(f"window.open('{profile['profile_url']}', '_blank');")
                                     time.sleep(2)
                                     
                                     # Switch to new tab
                                     self.driver.switch_to.window(self.driver.window_handles[-1])
                                     random_delay(3, 5) # Human-like delay
                                     
                                     # Extract Full Text
                                     body_text = self.driver.find_element(By.TAG_NAME, "body").text
                                     
                                     # Verify with Gemini using FULL text
                                     is_relevant = gemini_client.verify_candidate(profile, company, full_profile_text=body_text)
                                     
                                     # Close tab and switch back
                                     self.driver.close()
                                     self.driver.switch_to.window(main_window)
                                     
                                 except Exception as e:
                                     print(f"  ⚠️  Deep verification failed: {e}")
                                     # Fallback to basic assumption
                                     is_relevant = False
                                     try:
                                         if len(self.driver.window_handles) > 1:
                                             self.driver.close()
                                             self.driver.switch_to.window(main_window)
                                     except: pass
                             
                             if not is_relevant:
                                 print(f"  ❌ Skipped by AI: Not a relevant recruiter for {company}")
                                 continue
                             print(f"  ✅ Verified by AI!")
                        
                        profiles.append(profile)
                        print(f"  ✓ Found: {profile['name']} - {profile['role']}")
                except Exception as e:
                    # Don't print error for every element to avoid clutter
                    continue
            
            print(f"✅ Found {len(profiles)} recruiters at {company}")
            return profiles
        
        except Exception as e:
            print(f"❌ Error searching for recruiters: {str(e)}")
            return profiles
    
    def _extract_profile_info(self, element, company: str) -> Dict:
        """Extract profile information from a result element."""
        name = "Unknown"
        profile_url = ""
        role = "Recruiter"
        
        try:
            # 1. Extract Name and URL using robust data-view-name
            try:
                # This is the most stable selector for 2024/2025
                anchor = element.find_element(By.XPATH, ".//a[@data-view-name='search-result-lockup-title']")
                name = anchor.text.strip()
                profile_url = anchor.get_attribute('href')
                
                # Clean up URL (remove query params)
                if "?" in profile_url:
                    profile_url = profile_url.split("?")[0]
            except:
                # Fallback to older methods
                try:
                    anchor = element.find_element(By.TAG_NAME, "a")
                    profile_url = anchor.get_attribute('href')
                    name = anchor.text.split("\n")[0].strip()
                except:
                    pass

            # 2. Extract Role (Headline)
            try:
                # The headline is usually in a paragraph tag avoiding the name structure
                # We essentially look for the text content that isn't the name
                full_text = element.text
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                
                # Heuristic: The name is usually first. The next substantial text is the headline.
                # We filter out "2nd", "3rd", "Connect", "Follow" etc.
                for line in lines:
                    if line == name: 
                        continue
                        
                    # Ignore connection degrees and metadata
                    line_lower = line.lower()
                    if line_lower in ["2nd", "3rd", "1st", "3rd+"]: continue
                    if line in ["• 2nd", "• 3rd", "• 3rd+", "• 1st"]: continue
                    if line.startswith("•"): continue
                    
                    # Ignore button text
                    if line in ["Connect", "Follow", "Message", "Save", "View full profile", "Pending"]:
                        continue
                    if "followers" in line_lower or "connections" in line_lower:
                        continue
                    if "shared connections" in line_lower or "mutual connection" in line_lower:
                        continue
                    
                    # This looks like a candidate for the role/headline
                    role = line
                    break
            except:
                pass
            
            # Simple validation
            if not name or name == "Unknown" or not profile_url:
                return None
            
            # Since we removed strict company checking, we'll just trust the search results
            # but maybe log if it looks suspicious
            
            return {
                "name": name,
                "profile_url": profile_url,
                "role": role,
                "company": company # Assign target company as we are searching explicitly for it
            }
            
        except Exception as e:
            # console.log equivalent for python debugging
            # print(f"Error extracting info: {e}")
            return None
    
    def check_connection_status(self, profile_url: str) -> str:
        """
        Check if we're already connected with a profile
        
        Args:
            profile_url: LinkedIn profile URL
        
        Returns:
            'connected', 'pending', or 'not_connected'
        """
        try:
            self.driver.get(profile_url)
            random_delay(2, 4)
            
            # Look for connection status indicators
            try:
                # Check for "Message" button (indicates already connected)
                message_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Message')]")
                return 'connected'
            except NoSuchElementException:
                pass
            
            try:
                # Check for "Pending" status
                pending = self.driver.find_element(By.XPATH, "//button[contains(., 'Pending')]")
                return 'pending'
            except NoSuchElementException:
                pass
            
            # If neither, assume not connected
            return 'not_connected'
        
        except Exception as e:
            print(f"⚠️  Error checking connection status: {str(e)}")
            return 'unknown'
