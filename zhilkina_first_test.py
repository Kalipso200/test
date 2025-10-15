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

    def test_1_загрузка_страницы(self, setup):
        """Тест 1: Загрузка страницы и основные элементы"""
        # Проверяем заголовок страницы
        assert "F-Bank" in self.driver.title

        # Проверяем наличие корневого элемента
        root_element = self.wait.until(
            EC.presence_of_element_located((By.ID, "root"))
        )
        assert root_element.is_displayed()

        # Ждем загрузки контента приложения
        time.sleep(3)
        
        # Проверяем наличие контента внутри root
        app_content = self.driver.find_elements(By.CSS_SELECTOR, "#root > *")
        assert len(app_content) > 0

    def test_2_отображение_интерфейса(self, setup):
        """Тест 2: Отображение элементов интерфейса"""
        time.sleep(2)
        
        # Проверяем наличие основных элементов интерфейса
        elements_to_check = [
            (By.TAG_NAME, "header"),
            (By.TAG_NAME, "main"),
            (By.TAG_NAME, "footer")
        ]
        
        for by, value in elements_to_check:
            element = self.driver.find_element(by, value)
            assert element.is_displayed()

    def test_3_взаимодействие_с_кнопками(self, setup):
        """Тест 3: Взаимодействие с кнопками"""
        time.sleep(2)
        
        # Ищем все кнопки на странице
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        assert len(buttons) > 0
        
        # Проверяем, что кнопки кликабельны
        for button in buttons[:2]:  # Проверяем первые 2 кнопки
            assert button.is_displayed()
            assert button.is_enabled()

    def test_4_проверка_полей_ввода(self, setup):
        """Тест 4: Проверка полей ввода"""
        time.sleep(2)
        
        # Ищем поля ввода
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        
        if len(inputs) > 0:
            # Проверяем первое поле ввода
            input_field = inputs[0]
            assert input_field.is_displayed()
            assert input_field.is_enabled()
            
            # Тестируем ввод текста
            test_text = "тест"
            input_field.clear()
            input_field.send_keys(test_text)
            
            # Проверяем, что текст введен
            assert input_field.get_attribute("value") == test_text

    def test_5_навигация_по_странице(self, setup):
        """Тест 5: Навигация по странице"""
        time.sleep(2)
        
        # Проверяем текущий URL
        current_url = self.driver.current_url
        assert "localhost" in current_url or "3000" in current_url
        
        # Обновляем страницу
        self.driver.refresh()
        time.sleep(2)
        
        # Проверяем, что страница загрузилась после обновления
        root_element = self.driver.find_element(By.ID, "root")
        assert root_element.is_displayed()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])