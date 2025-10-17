import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class TestFBank:
    @pytest.fixture(scope="function")
    def setup(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get("http://localhost:3000")
        self.wait = WebDriverWait(self.driver, 10)
        yield
        self.driver.quit()

    def test_1_page_loading(self, setup):
        """Test 1: Page loading and basic elements"""
        # Check page title
        assert "F-Bank" in self.driver.title

        # Check root element presence
        root_element = self.wait.until(
            EC.presence_of_element_located((By.ID, "root"))
        )
        assert root_element.is_displayed()

        # Wait for application content loading with explicit wait
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#root > *"))
        )
        
        # Check content inside root
        app_content = self.driver.find_elements(By.CSS_SELECTOR, "#root > *")
        assert len(app_content) > 0

    def test_2_interface_display(self, setup):
        """Test 2: Interface elements display"""
        # Check main interface elements with explicit waits
        elements_to_check = [
            (By.TAG_NAME, "header"),
            (By.TAG_NAME, "main"), 
            (By.TAG_NAME, "footer")
        ]
        
        for by, value in elements_to_check:
            element = self.wait.until(
                EC.presence_of_element_located((by, value))
            )
            assert element.is_displayed()

    def test_3_button_interaction(self, setup):
        """Test 3: Button interaction"""
        # Find all buttons on page
        buttons = self.wait.until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
        )
        assert len(buttons) > 0
        
        # Check that buttons are clickable
        for button in buttons[:2]:  # Check first 2 buttons
            assert button.is_displayed()
            assert button.is_enabled()

    def test_4_input_fields(self, setup):
        """Test 4: Input fields verification"""
        # Find input fields
        inputs = self.wait.until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
        )
        
        if len(inputs) > 0:
            # Check first input field
            input_field = inputs[0]
            assert input_field.is_displayed()
            assert input_field.is_enabled()
            
            # Test text input
            test_text = "test"
            input_field.clear()
            input_field.send_keys(test_text)
            
            # Verify text was entered
            assert input_field.get_attribute("value") == test_text

    def test_5_page_navigation(self, setup):
        """Test 5: Page navigation"""
        # Check current URL
        current_url = self.driver.current_url
        assert "localhost" in current_url or "3000" in current_url
        
        # Navigate to URL instead of using refresh
        self.driver.get("http://localhost:3000")
        
        # Verify page loaded after navigation
        root_element = self.wait.until(
            EC.presence_of_element_located((By.ID, "root"))
        )
        assert root_element.is_displayed()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
