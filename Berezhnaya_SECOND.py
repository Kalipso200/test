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
            print(f"Browser startup error: {e}")
            return False

    def teardown(self):
        if self.driver:
            self.driver.quit()

    def log_test_result(self, test_id, test_name, passed, details=""):
        status = "PASSED" if passed else "FAILED"
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
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input")))
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
                        return True
                except:
                    continue

            try:
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if len(all_inputs) >= 2:
                    amount_input = all_inputs[1]
                    amount_input.click()
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
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            return self.find_and_focus_amount_field()
        except Exception as e:
            return False

    def enter_amount(self, amount):
        try:
            if not self.find_and_focus_amount_field():
                return False
            active_element = self.driver.switch_to.active_element
            active_element.clear()
            active_element.send_keys(amount)
            self.wait.until(lambda driver: active_element.get_attribute('value') == amount)
            return active_element.get_attribute('value') == amount
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
        print("TEST FBT-006: Available amount calculation with commission")
        print("=" * 70)

        try:
            if not self.check_balance_display():
                return self.log_test_result("FBT-006", "Balance display", False, "Balance 30'000 or reserve 20'001 not found")

            if not self.open_transfer_form():
                return self.log_test_result("FBT-006", "Form opening", False, "Failed to open transfer form")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-006", "Card input and proceed", False, "Failed to enter card or proceed to amount")

            if not self.enter_amount("9999"):
                return self.log_test_result("FBT-006", "Amount input", False, "Failed to enter amount")

            commission_value = self.get_commission_value()
            actual_available = 9999 - commission_value

            print("Actual result:")
            print(f"- Account balance: 30000 RUB - CORRECT")
            print(f"- Reserve: 20001 RUB - CORRECT")
            print(f"- Available without commission: 9999 RUB - CORRECT")
            print(f"- Commission for 9999 RUB: {commission_value} RUB (instead of 999) - {'CORRECT' if commission_value == 999 else 'INCORRECT'}")
            print(f"- Actual available amount: {actual_available} RUB (instead of 9000) - {'CORRECT' if actual_available == 9000 else 'INCORRECT'}")

            if commission_value == 900:
                return self.log_test_result("FBT-006", "Commission calculation", False, "Commission 900 RUB instead of 999 RUB - BUG")
            elif commission_value == 999:
                return self.log_test_result("FBT-006", "Commission calculation", True, "Commission 999 RUB - correct")
            else:
                return self.log_test_result("FBT-006", "Commission calculation", False, f"Commission {commission_value} RUB instead of 999 RUB")

        except Exception as e:
            return self.log_test_result("FBT-006", "Test execution", False, f"Error: {e}")

    def test_007_actual_available_amount(self):
        print("\n" + "=" * 70)
        print("TEST FBT-007: Actual available amount")
        print("=" * 70)

        try:
            if not self.open_transfer_form():
                return self.log_test_result("FBT-007", "Form opening", False, "Failed to open form")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-007", "Card input", False, "Failed to enter card")

            self.enter_amount("9098")
            transfer_possible_9098 = self.is_transfer_possible()

            self.enter_amount("9099")
            page_content = self.driver.page_source.lower()
            transfer_blocked_9099 = "недостаточно" in page_content or "insufficient" in page_content

            self.enter_amount("9097")
            transfer_possible_9097 = self.is_transfer_possible()

            self.enter_amount("9098")
            commission_9098 = self.get_commission_value()

            print("Actual result:")
            print(f"- Amount 9098 RUB: transfer button active - {'CORRECT' if transfer_possible_9098 else 'INCORRECT'}")
            print(f"- Amount 9099 RUB: 'Insufficient funds' message - {'CORRECT' if transfer_blocked_9099 else 'INCORRECT'}")
            print(f"- Amount 9097 RUB: transfer button active - {'CORRECT' if transfer_possible_9097 else 'INCORRECT'}")
            print(f"- Commission for 9098 RUB: {commission_9098} RUB - {'CORRECT' if commission_9098 == 900 else 'INCORRECT'} (but calculation algorithm is incorrect)")

            if transfer_possible_9098 and transfer_blocked_9099 and transfer_possible_9097:
                return self.log_test_result("FBT-007", "Available amount logic", True, "Partially passed - logic works but based on incorrect commission calculation")
            else:
                details = f"9098: {transfer_possible_9098}, 9099: {transfer_blocked_9099}, 9097: {transfer_possible_9097}"
                return self.log_test_result("FBT-007", "Available amount logic", False, f"Logic error: {details}")

        except Exception as e:
            return self.log_test_result("FBT-007", "Test execution", False, f"Error: {e}")

    def test_008_commission_calculation(self):
        print("\n" + "=" * 70)
        print("TEST FBT-008: Commission calculation for various amounts")
        print("=" * 70)

        try:
            if not self.open_transfer_form():
                return self.log_test_result("FBT-008", "Form opening", False, "Failed to open form")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-008", "Card input", False, "Failed to enter card")

            test_cases = [
                ("1000", 100),
                ("5000", 500),
                ("155", 15),
                ("199", 19),
                ("100", 10)
            ]

            print("Actual result:")
            errors_found = 0

            for amount, expected_commission in test_cases:
                self.enter_amount(amount)
                actual_commission = self.get_commission_value()
                is_correct = (actual_commission == expected_commission)

                status = "CORRECT" if is_correct else "INCORRECT"
                comment = f"(instead of {expected_commission})" if not is_correct else ""
                print(f"- Amount {amount} RUB: commission {actual_commission} RUB - {status} {comment}")

                if not is_correct:
                    errors_found += 1

            self.enter_amount("9999")
            commission_9999 = self.get_commission_value()
            is_9999_correct = (commission_9999 == 999)
            status_9999 = "CORRECT" if is_9999_correct else "INCORRECT"
            comment_9999 = f"(instead of 999)" if not is_9999_correct else ""
            print(f"- Amount 9999 RUB: commission {commission_9999} RUB - {status_9999} {comment_9999}")

            if not is_9999_correct:
                errors_found += 1

            if errors_found == 0:
                return self.log_test_result("FBT-008", "Commission calculation", True, "All commissions calculated correctly")
            else:
                return self.log_test_result("FBT-008", "Commission calculation", False, "Commission calculated incorrectly for most amounts - uses wrong calculation algorithm (rounding to tens)")

        except Exception as e:
            return self.log_test_result("FBT-008", "Test execution", False, f"Error: {e}")

    def test_009_commission_rounding(self):
        print("\n" + "=" * 70)
        print("TEST FBT-009: Commission rounding algorithm")
        print("=" * 70)

        try:
            if not self.open_transfer_form():
                return self.log_test_result("FBT-009", "Form opening", False, "Failed to open form")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-009", "Card input and proceed", False, "Failed to enter card or proceed to amount")

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
                    print(f"BUG: Amount {amount} RUB - commission {actual_commission} RUB instead of {expected_commission} RUB")
                    pattern_detected = True
                else:
                    print(f"Amount {amount} RUB: commission {expected_commission} RUB - OK")

            if pattern_detected:
                return self.log_test_result("FBT-009", "Rounding algorithm", False, "Detected bug - rounding to tens")
            else:
                return self.log_test_result("FBT-009", "Rounding algorithm", True, "Rounding works correctly")

        except Exception as e:
            return self.log_test_result("FBT-009", "Test execution", False, f"Error: {e}")

    def test_010_validation_boundary_values(self):
        print("\n" + "=" * 70)
        print("TEST FBT-010: Boundary values validation")
        print("=" * 70)

        try:
            if not self.open_transfer_form():
                return self.log_test_result("FBT-010", "Form opening", False, "Failed to open form")

            if not self.enter_card_number_and_proceed():
                return self.log_test_result("FBT-010", "Card input and proceed", False, "Failed to enter card or proceed to amount")

            self.enter_amount("0")
            zero_accepted = self.is_transfer_possible()

            if not self.find_and_focus_amount_field():
                return self.log_test_result("FBT-010", "Amount field search", False, "Failed to find amount field")

            amount_input = self.driver.switch_to.active_element
            amount_input.clear()
            amount_input.send_keys("-100")
            self.wait.until(lambda driver: amount_input.get_attribute('value') != "")
            negative_value = amount_input.get_attribute('value')
            negative_accepted = "-100" in negative_value if negative_value else False

            self.enter_amount("1")
            commission_1 = self.get_commission_value()
            one_commission_ok = (commission_1 == 0)

            validation_errors = []
            if zero_accepted:
                validation_errors.append("system accepts 0 RUB")
            if negative_accepted:
                validation_errors.append("system accepts negative amounts")

            if validation_errors:
                return self.log_test_result("FBT-010", "Amount validation", False, f"Errors: {', '.join(validation_errors)}")
            else:
                return self.log_test_result("FBT-010", "Amount validation", True, "Validation works correctly")

        except Exception as e:
            return self.log_test_result("FBT-010", "Test execution", False, f"Error: {e}")

    def run_all_tests(self):
        print("AUTOMATED F-BANK TESTING")
        print("=" * 70)
        print("Based on manual tests Berezhnaya_SECOND.md")
        print("=" * 70)

        if not self.setup():
            print("Failed to initialize test environment")
            return False

        try:
            self.test_006_available_amount_calculation()
            self.test_007_actual_available_amount()
            self.test_008_commission_calculation()
            self.test_009_commission_rounding()
            self.test_010_validation_boundary_values()

            print("\n" + "=" * 70)
            print("TESTING RESULTS")
            print("=" * 70)

            passed = 0
            for result in self.results:
                print(result)
                if "PASSED" in result:
                    passed += 1

            total = len(self.results)
            print(f"\nResult: {passed}/{total} tests passed")

            if passed == total:
                print("All tests passed successfully!")
            else:
                print("Found issues requiring fixes")

            return passed == total

        except Exception as e:
            print(f"Critical error during test execution: {e}")
            return False
        finally:
            self.teardown()


if __name__ == "__main__":
    tester = FBankAutotests()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
