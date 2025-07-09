import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager
from models.persona import PersonaManager
import json

class BehaviorSimulator:
    def __init__(self):
        self.persona_manager = PersonaManager()
    
    def run_simulation(self, simulation_id, config):
        """Run a complete behavior simulation"""
        persona = self.persona_manager.get_persona(config['persona_id'])
        if not persona:
            raise ValueError("Persona not found")
        
        # Initialize browser
        driver = self._setup_browser(config['device_type'])
        
        try:
            results = {
                'simulation_id': simulation_id,
                'persona': persona,
                'config': config,
                'actions': [],
                'analytics': {
                    'time_to_first_interaction': 0,
                    'total_interactions': 0,
                    'bounce_points': [],
                    'confusion_clicks': [],
                    'success_rate': 0,
                    'completion_time': 0
                },
                'heatmap_data': [],
                'success': False,
                'error_message': None
            }
            
            start_time = time.time()
            
            # Navigate to URL
            driver.get(config['url'])
            self._log_action(results, 'page_load', config['url'], start_time)
            
            # Simulate user behavior based on persona
            self._simulate_user_journey(driver, persona, config, results)
            
            # Calculate final analytics
            results['analytics']['completion_time'] = time.time() - start_time
            results['analytics']['total_interactions'] = len(results['actions'])
            
            # Determine success based on goal completion
            results['success'] = self._evaluate_goal_completion(results, config['goal'])
            results['analytics']['success_rate'] = 1.0 if results['success'] else 0.0
            
            return results
            
        except Exception as e:
            return {
                'simulation_id': simulation_id,
                'error': str(e),
                'success': False
            }
        finally:
            driver.quit()
    
    def _setup_browser(self, device_type):
        """Setup Chrome browser with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        if device_type == 'mobile':
            chrome_options.add_argument('--window-size=375,667')  # iPhone dimensions
            chrome_options.add_experimental_option("mobileEmulation", {
                "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
            })
        else:
            chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except:
            # Fallback to basic setup if ChromeDriverManager fails
            chrome_options.add_argument('--disable-extensions')
            driver = webdriver.Chrome(options=chrome_options)
        
        return driver
    
    def _simulate_user_journey(self, driver, persona, config, results):
        """Simulate user journey based on persona characteristics"""
        wait = WebDriverWait(driver, 10)
        actions = ActionChains(driver)
        
        # Get persona traits
        traits = persona['traits']
        tech_savviness = persona['tech_savviness']
        goal = config['goal']
        
        # Simulate initial page scanning
        self._simulate_page_scan(driver, persona, results)
        
        # Behavior patterns based on persona
        if 'impatient' in traits:
            interaction_delay = random.uniform(0.5, 1.5)
        elif 'careful' in traits:
            interaction_delay = random.uniform(2.0, 4.0)
        else:
            interaction_delay = random.uniform(1.0, 2.5)
        
        # Simulate interactions for goal completion
        max_actions = 15  # Prevent infinite loops
        action_count = 0
        
        while action_count < max_actions:
            try:
                # Find interactive elements
                interactive_elements = self._find_interactive_elements(driver)
                
                if not interactive_elements:
                    self._log_action(results, 'confusion_click', 'No interactive elements found', time.time())
                    results['analytics']['confusion_clicks'].append({
                        'timestamp': time.time(),
                        'reason': 'no_interactive_elements'
                    })
                    break
                
                # Choose element based on persona and goal
                chosen_element = self._choose_element(interactive_elements, persona, goal, results)
                
                if chosen_element:
                    # Simulate realistic interaction
                    self._perform_interaction(driver, chosen_element, persona, results)
                    
                    # Wait based on persona
                    time.sleep(interaction_delay)
                    
                    # Check if goal is potentially completed
                    if self._check_goal_indicators(driver, goal):
                        break
                
                action_count += 1
                
            except (TimeoutException, ElementNotInteractableException) as e:
                self._log_action(results, 'error', str(e), time.time())
                results['analytics']['bounce_points'].append({
                    'timestamp': time.time(),
                    'reason': str(e)
                })
                break
            except Exception as e:
                # Log unexpected errors but continue
                self._log_action(results, 'unexpected_error', str(e), time.time())
                break
    
    def _simulate_page_scan(self, driver, persona, results):
        """Simulate initial page scanning behavior"""
        # Record initial viewport elements for heatmap
        viewport_height = driver.execute_script("return window.innerHeight")
        viewport_width = driver.execute_script("return window.innerWidth")
        
        # Simulate eye tracking patterns
        scan_points = []
        if 'mobile-first' in persona['traits']:
            # Mobile users scan vertically
            scan_points = [(viewport_width//2, y) for y in range(0, viewport_height, 50)]
        else:
            # Desktop users follow F-pattern
            scan_points = [
                (50, 50), (viewport_width-50, 50),  # Top horizontal
                (50, viewport_height//3), (viewport_width//2, viewport_height//3),  # Middle partial
                (50, viewport_height*2//3)  # Bottom left
            ]
        
        for point in scan_points:
            results['heatmap_data'].append({
                'x': point[0],
                'y': point[1],
                'intensity': random.uniform(0.3, 0.8),
                'duration': random.uniform(100, 500)
            })
        
        self._log_action(results, 'page_scan', f'Scanned {len(scan_points)} points', time.time())
    
    def _find_interactive_elements(self, driver):
        """Find interactive elements on the page"""
        selectors = [
            'button', 'a[href]', 'input[type="submit"]', 'input[type="button"]',
            '[role="button"]', '.btn', '.button', '[onclick]',
            'input[type="text"]', 'input[type="email"]', 'input[type="password"]',
            'select', 'textarea'
        ]
        
        elements = []
        for selector in selectors:
            try:
                found_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in found_elements:
                    if element.is_displayed() and element.is_enabled():
                        elements.append({
                            'element': element,
                            'tag': element.tag_name,
                            'text': element.text[:50],
                            'type': element.get_attribute('type'),
                            'role': element.get_attribute('role'),
                            'location': element.location,
                            'size': element.size
                        })
            except:
                continue
        
        return elements
    
    def _choose_element(self, elements, persona, goal, results):
        """Choose which element to interact with based on persona and goal"""
        if not elements:
            return None
        
        # Score elements based on goal relevance and persona preferences
        scored_elements = []
        
        for elem_info in elements:
            score = 0
            text = elem_info['text'].lower()
            
            # Goal-based scoring
            goal_keywords = goal.lower().split()
            for keyword in goal_keywords:
                if keyword in text:
                    score += 5
            
            # Persona-based preferences
            if 'price-conscious' in persona['traits']:
                if any(word in text for word in ['price', 'cost', 'cheap', 'discount', 'sale']):
                    score += 3
            
            if 'social-proof-driven' in persona['traits']:
                if any(word in text for word in ['review', 'rating', 'testimonial', 'customer']):
                    score += 3
            
            if 'help-seeking' in persona['traits']:
                if any(word in text for word in ['help', 'support', 'faq', 'guide', 'tutorial']):
                    score += 3
            
            # Element type preferences
            if elem_info['tag'] == 'button' or 'button' in (elem_info['role'] or ''):
                score += 2  # Buttons are naturally appealing
            
            # Tech savviness affects interaction with complex elements
            if persona['tech_savviness'] < 3:
                if elem_info['tag'] in ['select', 'input'] and elem_info['type'] != 'submit':
                    score -= 1  # Less tech-savvy users might avoid complex inputs
            
            scored_elements.append((elem_info, score))
        
        # Sort by score and add some randomness
        scored_elements.sort(key=lambda x: x[1] + random.uniform(-0.5, 0.5), reverse=True)
        
        # Return the highest scoring element
        if scored_elements:
            chosen = scored_elements[0][0]
            self._log_action(results, 'element_chosen', f"Selected: {chosen['text'][:30]}", time.time())
            return chosen['element']
        
        return None
    
    def _perform_interaction(self, driver, element, persona, results):
        """Perform interaction with an element"""
        try:
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            # Record heatmap data for the interaction
            location = element.location
            size = element.size
            results['heatmap_data'].append({
                'x': location['x'] + size['width']//2,
                'y': location['y'] + size['height']//2,
                'intensity': random.uniform(0.7, 1.0),
                'duration': random.uniform(200, 800)
            })
            
            tag_name = element.tag_name.lower()
            element_type = element.get_attribute('type')
            
            if tag_name == 'input' and element_type in ['text', 'email', 'password']:
                # Handle text input
                self._handle_text_input(element, persona, results)
            
            elif tag_name in ['button', 'a'] or element.get_attribute('role') == 'button':
                # Handle clicks
                element.click()
                self._log_action(results, 'click', element.text[:30], time.time())
                time.sleep(1)  # Wait for page response
            
            elif tag_name == 'select':
                # Handle dropdown selection
                from selenium.webdriver.support.ui import Select
                select = Select(element)
                if select.options:
                    # Choose a random option (or goal-relevant one)
                    option = random.choice(select.options[1:])  # Skip first (usually placeholder)
                    select.select_by_visible_text(option.text)
                    self._log_action(results, 'select', option.text[:30], time.time())
            
        except Exception as e:
            self._log_action(results, 'interaction_error', str(e), time.time())
            results['analytics']['confusion_clicks'].append({
                'timestamp': time.time(),
                'reason': f'interaction_error: {str(e)}'
            })
    
    def _handle_text_input(self, element, persona, results):
        """Handle text input based on persona"""
        input_type = element.get_attribute('type')
        placeholder = element.get_attribute('placeholder') or ''
        
        # Generate realistic input based on type and persona
        if input_type == 'email':
            test_email = f"test.user{random.randint(1, 999)}@example.com"
            element.send_keys(test_email)
            self._log_action(results, 'input', f'email: {test_email}', time.time())
        
        elif input_type == 'password':
            password = 'TestPassword123!' if persona['tech_savviness'] > 2 else 'password123'
            element.send_keys(password)
            self._log_action(results, 'input', 'password: [hidden]', time.time())
        
        elif 'search' in placeholder.lower() or 'find' in placeholder.lower():
            # Search based on goal
            search_terms = ['product', 'item', 'service', 'help']
            element.send_keys(random.choice(search_terms))
            self._log_action(results, 'input', f'search: {element.get_attribute("value")}', time.time())
        
        else:
            # Generic text input
            test_text = f'Test Input {random.randint(1, 99)}'
            element.send_keys(test_text)
            self._log_action(results, 'input', f'text: {test_text}', time.time())
    
    def _check_goal_indicators(self, driver, goal):
        """Check if there are indicators that the goal might be completed"""
        goal_keywords = goal.lower().split()
        page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
        
        success_indicators = [
            'success', 'complete', 'thank you', 'confirmation', 'done',
            'submitted', 'added to cart', 'checkout', 'purchase', 'order'
        ]
        
        # Check for success indicators
        for indicator in success_indicators:
            if indicator in page_text:
                return True
        
        # Check for goal-specific keywords
        keyword_matches = sum(1 for keyword in goal_keywords if keyword in page_text)
        return keyword_matches >= len(goal_keywords) // 2
    
    def _evaluate_goal_completion(self, results, goal):
        """Evaluate if the goal was successfully completed"""
        actions = results['actions']
        
        # Simple heuristics for goal completion
        if not actions:
            return False
        
        # Check for successful action patterns
        action_types = [action['type'] for action in actions]
        
        if 'click' in action_types and 'input' in action_types:
            # User interacted meaningfully
            return True
        
        # Check for goal keywords in actions
        goal_keywords = goal.lower().split()
        action_texts = ' '.join([action.get('details', '') for action in actions]).lower()
        
        keyword_matches = sum(1 for keyword in goal_keywords if keyword in action_texts)
        return keyword_matches >= len(goal_keywords) // 2
    
    def _log_action(self, results, action_type, details, timestamp):
        """Log an action to the results"""
        results['actions'].append({
            'type': action_type,
            'details': details,
            'timestamp': timestamp,
            'relative_time': timestamp - (results['actions'][0]['timestamp'] if results['actions'] else timestamp)
        })
        
        # Update time to first interaction
        if action_type in ['click', 'input', 'select'] and results['analytics']['time_to_first_interaction'] == 0:
            results['analytics']['time_to_first_interaction'] = timestamp - (results['actions'][0]['timestamp'] if results['actions'] else timestamp)