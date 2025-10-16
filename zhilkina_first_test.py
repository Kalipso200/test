# test_fbank.py
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
        """Тест 1: Загрузка страницы и основные элементы"""
        # Проверяем заголовок страницы
        assert "F-Bank" in self.driver.title

        # Проверяем наличие корневого элемента
        root_element = self.wait.until(
            EC.presence_of_element_located((By.ID, "root"))
        )
        assert root_element.is_displayed()

        # Ждем загрузки контента приложения с использованием явного ожидания
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#root > *"))
        )
        
        # Проверяем наличие контента внутри root
        app_content = self.driver.find_elements(By.CSS_SELECTOR, "#root > *")
        assert len(app_content) > 0

    def test_2_interface_display(self, setup):
        """Тест 2: Отображение элементов интерфейса"""
        # Проверяем основные элементы интерфейса с явными ожиданиями
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
        """Тест 3: Взаимодействие с кнопками"""
        # Ищем все кнопки на странице
        buttons = self.wait.until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
        )
        assert len(buttons) > 0
        
        # Проверяем, что кнопки кликабельны
        for button in buttons[:2]:  # Проверяем первые 2 кнопки
            assert button.is_displayed()
            assert button.is_enabled()

    def test_4_input_fields(self, setup):
        """Тест 4: Проверка полей ввода"""
        # Ищем поля ввода
        inputs = self.wait.until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
        )
        
        if len(inputs) > 0:
            # Проверяем первое поле ввода
            input_field = inputs[0]
            assert input_field.is_displayed()
            assert input_field.is_enabled()
            
            # Тестируем ввод текста
            test_text = "test"
            input_field.clear()
            input_field.send_keys(test_text)
            
            # Проверяем, что текст введен
            assert input_field.get_attribute("value") == test_text

    def test_5_page_navigation(self, setup):
        """Тест 5: Навигация по странице"""
        # Проверяем текущий URL
        current_url = self.driver.current_url
        assert "localhost" in current_url or "3000" in current_url
        
        # Переходим по URL вместо использования refresh
        self.driver.get("http://localhost:3000")
        
        # Проверяем, что страница загрузилась после навигации
        root_element = self.wait.until(
            EC.presence_of_element_located((By.ID, "root"))
        )
        assert root_element.is_displayed()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
