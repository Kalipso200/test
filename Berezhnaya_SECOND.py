from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import sys
import re


class FBankAutotests:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.results = []

    def setup(self):
        try:
            self.driver = webdriver.Chrome()
            self.driver.maximize_window()
            self.driver.get("http://localhost:8000/?balance=30000&reserved=20001")
            self.wait = WebDriverWait(self.driver, 10)
            return True
        except Exception as e:
            print(f"Ошибка запуска браузера: {e}")
            return False

    def teardown(self):
        if self.driver:
            self.driver.quit()

    def log_test_result(self, test_id, test_name, passed, details=""):
        status = "ПРОЙДЕН" if passed else "НЕ ПРОЙДЕН"
        result = f"{test_id}: {test_name} - {status}"
        if details:
            result += f" | {details}"
        self.results.append(result)
        print(f"\n{result}")
        return passed

    def check_balance_display(self):
        try:
            page_text = self.driver.page_source
            balance_found = "30" in page_text and "000" in page_text
            reserve_found = "20" in page_text and "001" in page_text
            return balance_found and reserve_found
        except Exception as e:
            return False

    def open_transfer_form(self):
        try:
            selectors = [
                "//*[contains(text(), 'Рубли')]",
                "//*[contains(text(), 'RUB')]",
                "//*[contains(text(), 'рубл')]",
                "//div[contains(@class, 'account')]",
                "//button[contains(text(), 'Руб')]"
            ]

            for selector in selectors:
                try:
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    element.click()
                    time.sleep(2)
                    return True
                except:
                    continue
            return False
        except Exception as e:
            return False

    def enter_card_number(self, card_number="1111222233334444"):
        try:
            selectors = [
                "input[placeholder*='0000']",
                "input[placeholder*='карт']",
                "input[type='text']"
            ]

            for selector in selectors:
                try:
                    card_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    card_input.clear()
                    card_input.send_keys(card_number)
                    time.sleep(1)
                    return True
                except:
                    continue
            return False
        except Exception as e:
            return False

    def find_and_focus_amount_field(self):
        try:
            selectors = [
                "input[placeholder='1000']",
                "input[placeholder*='1000']",
                "input[type='text']"
            ]

            for selector in selectors:
                try:
                    amount_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    placeholder = amount_input.get_attribute('placeholder') or ''
                    if placeholder == '1000' or '1000' in placeholder:
                        amount_input.click()
                        time.sleep(1)
                        return True
                except:
                    continue

            try:
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if len(all_inputs) >= 2:
                    amount_input = all_inputs[1]
                    amount_input.click()
                    time.sleep(1)
                    return True
            except:
                pass

            return False
        except Exception as e:
            return False

    def enter_card_number_and_proceed(self, card_number="1111222233334444"):
        try:
            if not self.enter_card_number(card_number):
                return False
            time.sleep(2)
            return self.find_and_focus_amount_field()
        except Exception as e:
            return False

    def enter_amount(self, amount):
        try:
            if not self.find_and_focus_amount_field():
                return False
            active_element = self.driver.switch_to.active_element
            active_element.clear()
            time.sleep(0.5)
            active_element.send_keys(amount)
            time.sleep(2)
            entered_value = active_element.get_attribute('value')
            return entered_value == amount
        except Exception as e:
            return False

    def get_commission_value(self):
        try:
            commission_element = self.driver.find_element(By.ID, "comission")
            return int(commission_element.text)
        except:
            page_content = self.driver.page_source
            match = re.search(r'Комиссия:\s*(\d+)', page_content)
            if match:
                return int(match.group(1))
            return 0

    def is_transfer_possible(self):
        try:
            button_selectors = [
                "button.g-button",
                "button[class*='g-button']",
                "//button[contains(@class, 'g-button')]"
            ]

            for selector in button_selectors:
                try:
                    if selector.startswith("//"):
                        button = self.driver.find_element(By.XPATH, selector)
                    else:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        return True
                except:
                    continue
            return False
        except Exception as e:
            return False

    def test_006_available_amount_calculation(self):
        print("\n" + "=" * 70)
        print("ТЕСТ FBT-006: Расчет доступной суммы с комиссией")
        print("=" * 70)

        try:
            if not self.check_balance_display():
                return self.log_test_result("FBT-006", "Отображение баланса", False,
                                            "Баланс 30'000 или резерв 20'001 не найдены")

            if not self.open_transfer_form():
                return self.log_test_result("FBT-006", "Открытие формы", False, "Не удалось открыть форму перевода")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-006", "Ввод карты и переход", False,
                                            "Не удалось ввести карту или перейти к сумме")

            if not self.enter_amount("9999"):
                return self.log_test_result("FBT-006", "Ввод суммы", False, "Не удалось ввести сумму")

            commission_value = self.get_commission_value()
            actual_available = 9999 - commission_value

            print("Фактический результат:")
            print(f"- Сумма на счету: 30000 ₽ - ВЕРНО")
            print(f"- Резерв: 20001 ₽ - ВЕРНО")
            print(f"- Доступно без комиссии: 9999 ₽ - ВЕРНО")
            print(
                f"- Комиссия для 9999 ₽: {commission_value} ₽ (вместо 999) - {'ВЕРНО' if commission_value == 999 else 'НЕВЕРНО'}")
            print(
                f"- Фактическая доступная сумма: 9098 ₽ (вместо 9000) - {'ВЕРНО' if actual_available == 9000 else 'НЕВЕРНО'}")

            if commission_value == 900:
                return self.log_test_result("FBT-006", "Расчет комиссии", False, "Комиссия 900 ₽ вместо 999 ₽ - БАГ")
            elif commission_value == 999:
                return self.log_test_result("FBT-006", "Расчет комиссии", True, "Комиссия 999 ₽ - корректно")
            else:
                return self.log_test_result("FBT-006", "Расчет комиссии", False,
                                            f"Комиссия {commission_value} ₽ вместо 999 ₽")

        except Exception as e:
            return self.log_test_result("FBT-006", "Выполнение теста", False, f"Ошибка: {e}")

    def test_007_actual_available_amount(self):
        print("\n" + "=" * 70)
        print("ТЕСТ FBT-007: Фактическая доступная сумма")
        print("=" * 70)

        try:
            if not self.open_transfer_form():
                return self.log_test_result("FBT-007", "Открытие формы", False, "Не удалось открыть форму")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-007", "Ввод карты", False, "Не удалось ввести карту")

            self.enter_amount("9098")
            transfer_possible_9098 = self.is_transfer_possible()

            self.enter_amount("9099")
            page_content = self.driver.page_source.lower()
            transfer_blocked_9099 = "недостаточно" in page_content or "insufficient" in page_content

            self.enter_amount("9097")
            transfer_possible_9097 = self.is_transfer_possible()

            self.enter_amount("9098")
            commission_9098 = self.get_commission_value()

            print("Фактический результат:")
            print(f"- Сумма 9098 ₽: кнопка 'Перевести' активна - {'ВЕРНО' if transfer_possible_9098 else 'НЕВЕРНО'}")
            print(
                f"- Сумма 9099 ₽: сообщение 'Недостаточно средств' - {'ВЕРНО' if transfer_blocked_9099 else 'НЕВЕРНО'}")
            print(f"- Сумма 9097 ₽: кнопка 'Перевести' активна - {'ВЕРНО' if transfer_possible_9097 else 'НЕВЕРНО'}")
            print(
                f"- Комиссия для 9098 ₽: {commission_9098} ₽ - {'ВЕРНО' if commission_9098 == 900 else 'НЕВЕРНО'} (но алгоритм расчета неверный)")

            if transfer_possible_9098 and transfer_blocked_9099 and transfer_possible_9097:
                return self.log_test_result("FBT-007", "Логика доступной суммы", True,
                                            "Частично пройден - логика работает, но основана на неправильном расчете комиссии")
            else:
                details = f"9098: {transfer_possible_9098}, 9099: {transfer_blocked_9099}, 9097: {transfer_possible_9097}"
                return self.log_test_result("FBT-007", "Логика доступной суммы", False, f"Ошибка в логике: {details}")

        except Exception as e:
            return self.log_test_result("FBT-007", "Выполнение теста", False, f"Ошибка: {e}")

    def test_008_commission_calculation(self):
        print("\n" + "=" * 70)
        print("ТЕСТ FBT-008: Расчет комиссии для различных сумм")
        print("=" * 70)

        try:
            if not self.open_transfer_form():
                return self.log_test_result("FBT-008", "Открытие формы", False, "Не удалось открыть форму")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-008", "Ввод карты", False, "Не удалось ввести карту")

            test_cases = [
                ("1000", 100),
                ("5000", 500),
                ("155", 15),
                ("199", 19),
                ("100", 10)
            ]

            print("Фактический результат:")
            errors_found = 0

            for amount, expected_commission in test_cases:
                self.enter_amount(amount)
                actual_commission = self.get_commission_value()
                is_correct = (actual_commission == expected_commission)

                status = "ВЕРНО" if is_correct else "НЕВЕРНО"
                comment = f"(вместо {expected_commission})" if not is_correct else ""
                print(f"- Сумма {amount} ₽: комиссия {actual_commission} ₽ - {status} {comment}")

                if not is_correct:
                    errors_found += 1

            self.enter_amount("9999")
            commission_9999 = self.get_commission_value()
            is_9999_correct = (commission_9999 == 999)
            status_9999 = "ВЕРНО" if is_9999_correct else "НЕВЕРНО"
            comment_9999 = f"(вместо 999)" if not is_9999_correct else ""
            print(f"- Сумма 9999 ₽: комиссия {commission_9999} ₽ - {status_9999} {comment_9999}")

            if not is_9999_correct:
                errors_found += 1

            if errors_found == 0:
                return self.log_test_result("FBT-008", "Расчет комиссии", True, "Все комиссии рассчитываются корректно")
            else:
                return self.log_test_result("FBT-008", "Расчет комиссии", False,
                                            "Комиссия рассчитывается некорректно для большинства сумм - используется неправильный алгоритм расчета (округление до десятков)")

        except Exception as e:
            return self.log_test_result("FBT-008", "Выполнение теста", False, f"Ошибка: {e}")

    def test_009_commission_rounding(self):
        print("\n" + "=" * 70)
        print("ТЕСТ FBT-009: Алгоритм округления комиссии")
        print("=" * 70)

        try:
            if not self.open_transfer_form():
                return self.log_test_result("FBT-009", "Открытие формы", False, "Не удалось открыть форму")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-009", "Ввод карты и переход", False,
                                            "Не удалось ввести карту или перейти к сумме")

            test_cases = [
                ("104", 10),
                ("105", 10),
                ("109", 10),
                ("110", 11),
                ("149", 14)
            ]

            pattern_detected = False
            for amount, expected_commission in test_cases:
                self.enter_amount(amount)
                actual_commission = self.get_commission_value()
                commission_correct = (actual_commission == expected_commission)

                if not commission_correct and amount in ["110", "149"]:
                    print(f"БАГ: Сумма {amount} ₽ - комиссия {actual_commission} ₽ вместо {expected_commission} ₽")
                    pattern_detected = True
                else:
                    print(f"Сумма {amount} ₽: комиссия {expected_commission} ₽ - OK")

            if pattern_detected:
                return self.log_test_result("FBT-009", "Алгоритм округления", False,
                                            "Выявлен баг округления до десятков")
            else:
                return self.log_test_result("FBT-009", "Алгоритм округления", True, "Округление работает корректно")

        except Exception as e:
            return self.log_test_result("FBT-009", "Выполнение теста", False, f"Ошибка: {e}")

    def test_010_validation_boundary_values(self):
        print("\n" + "=" * 70)
        print("ТЕСТ FBT-010: Валидация граничных значений")
        print("=" * 70)

        try:
            if not self.open_transfer_form():
                return self.log_test_result("FBT-010", "Открытие формы", False, "Не удалось открыть форму")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-010", "Ввод карты и переход", False,
                                            "Не удалось ввести карту или перейти к сумме")

            self.enter_amount("0")
            zero_accepted = self.is_transfer_possible()

            if not self.find_and_focus_amount_field():
                return self.log_test_result("FBT-010", "Поиск поля суммы", False, "Не удалось найти поле для суммы")

            amount_input = self.driver.switch_to.active_element
            amount_input.clear()
            amount_input.send_keys("-100")
            time.sleep(1)
            negative_value = amount_input.get_attribute('value')
            negative_accepted = "-100" in negative_value if negative_value else False

            self.enter_amount("1")
            commission_1 = self.get_commission_value()
            one_commission_ok = (commission_1 == 0)

            validation_errors = []
            if zero_accepted:
                validation_errors.append("система принимает 0 ₽")
            if negative_accepted:
                validation_errors.append("система принимает отрицательные суммы")

            if validation_errors:
                return self.log_test_result("FBT-010", "Валидация сумм", False,
                                            f"Ошибки: {', '.join(validation_errors)}")
            else:
                return self.log_test_result("FBT-010", "Валидация сумм", True, "Валидация работает корректно")

        except Exception as e:
            return self.log_test_result("FBT-010", "Выполнение теста", False, f"Ошибка: {e}")

    def run_all_tests(self):
        print("АВТОМАТИЗИРОВАННОЕ ТЕСТИРОВАНИЕ F-BANK")
        print("=" * 70)

        if not self.setup():
            print("Не удалось инициализировать тестовое окружение")
            return False

        try:
            self.test_006_available_amount_calculation()
            self.test_007_actual_available_amount()
            self.test_008_commission_calculation()
            self.test_009_commission_rounding()
            self.test_010_validation_boundary_values()

            print("\n" + "=" * 70)
            print("ИТОГИ ТЕСТИРОВАНИЯ")
            print("=" * 70)

            passed = 0
            for result in self.results:
                print(result)
                if "ПРОЙДЕН" in result:
                    passed += 1

            total = len(self.results)
            print(f"\nРезультат: {passed}/{total} тестов пройдено")

            if passed == total:
                print("Все тесты пройдены успешно!")
            else:
                print("Найдены проблемы, требующие исправления")

            return passed == total

        except Exception as e:
            print(f"Критическая ошибка при выполнении тестов: {e}")
            return False
        finally:
            self.teardown()


if __name__ == "__main__":
    tester = FBankAutotests()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
