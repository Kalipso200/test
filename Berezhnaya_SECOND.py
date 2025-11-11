from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
            self.base_url = "http://localhost:8000/?balance=30000&reserved=20001"
            self.driver.get(self.base_url)
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

    def navigate_to_main_page(self):
        """Navigate to main page using URL instead of refresh"""
        try:
            self.driver.get(self.base_url)
            return True
        except Exception as e:
            print(f"Navigation error: {e}")
            return False

    def check_balance_display(self):
        try:
            balance_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), \"30'000\")]"))
            )
            reserve_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), \"20'001\")]"))
            )
            return balance_element.is_displayed() and reserve_element.is_displayed()
        except Exception as e:
            return False

    def open_transfer_form(self):
        try:
            selectors = [
                "//*[contains(text(), 'Рубли')]",
                "//*[contains(text(), 'RUB')]",
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
                "input[placeholder*='card']",
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

    def find_amount_field(self):
        try:
            selectors = [
                "input[placeholder='1000']",
                "input[placeholder*='1000']",
                "input[type='number']"
            ]

            for selector in selectors:
                try:
                    amount_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    return amount_input
                except:
                    continue
            return None
        except Exception as e:
            return None

    def enter_amount(self, amount):
        try:
            amount_input = self.find_amount_field()
            if not amount_input:
                return False

            amount_input.clear()
            amount_input.send_keys(str(amount))

            # Wait for value to be set using Selenium wait
            self.wait.until(lambda driver: amount_input.get_attribute('value') == str(amount))
            return True
        except Exception as e:
            return False

    def get_commission_value(self):
        try:
            # Try different selectors for commission element
            commission_selectors = [
                "//*[contains(text(), 'Commission')]//following-sibling::*",
                "//*[contains(text(), 'Комиссия')]//following-sibling::*",
                "//*[contains(text(), 'commission')]",
                ".commission",
                "#commission"
            ]

            for selector in commission_selectors:
                try:
                    if selector.startswith("//"):
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)

                    text = element.text
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        return int(numbers[0])
                except:
                    continue

            return 0
        except Exception as e:
            return 0

    def is_transfer_possible(self):
        try:
            button_selectors = [
                "button.g-button",
                "button[class*='g-button']",
                "//button[contains(@class, 'g-button')]",
                "//button[contains(text(), 'Transfer')]",
                "//button[contains(text(), 'Перевести')]"
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
                return self.log_test_result("FBT-006", "Balance display", False,
                                            "Balance 30000 or reserve 20001 not found")

            if not self.open_transfer_form():
                return self.log_test_result("FBT-006", "Form opening", False, "Failed to open transfer form")

            if not self.enter_card_number():
                return self.log_test_result("FBT-006", "Card input", False, "Failed to enter card number")

            if not self.enter_amount("9999"):
                return self.log_test_result("FBT-006", "Amount input", False, "Failed to enter amount")

            commission_value = self.get_commission_value()
            actual_available = 9999 - commission_value

            print("Actual result:")
            print(f"- Account balance: 30000 RUB - CORRECT")
            print(f"- Reserve: 20001 RUB - CORRECT")
            print(f"- Available without commission: 9999 RUB - CORRECT")
            print(
                f"- Commission for 9999 RUB: {commission_value} RUB (expected: 999) - {'CORRECT' if commission_value == 999 else 'INCORRECT'}")
            print(
                f"- Actual available amount: {actual_available} RUB (expected: 9000) - {'CORRECT' if actual_available == 9000 else 'INCORRECT'}")

            if commission_value == 900:
                return self.log_test_result("FBT-006", "Commission calculation", False,
                                            "Commission 900 RUB instead of 999 RUB - BUG")
            elif commission_value == 999:
                return self.log_test_result("FBT-006", "Commission calculation", True, "Commission 999 RUB - correct")
            else:
                return self.log_test_result("FBT-006", "Commission calculation", False,
                                            f"Commission {commission_value} RUB instead of 999 RUB")

        except Exception as e:
            return self.log_test_result("FBT-006", "Test execution", False, f"Error: {e}")

    def test_007_actual_available_amount(self):
        print("\n" + "=" * 70)
        print("TEST FBT-007: Actual available amount verification")
        print("=" * 70)

        try:
            if not self.navigate_to_main_page():
                return self.log_test_result("FBT-007", "Page navigation", False, "Failed to navigate to main page")

            if not self.open_transfer_form():
                return self.log_test_result("FBT-007", "Form opening", False, "Failed to open transfer form")

            if not self.enter_card_number():
                return self.log_test_result("FBT-007", "Card input", False, "Failed to enter card number")

            # Test amount 9098
            self.enter_amount("9098")
            transfer_possible_9098 = self.is_transfer_possible()

            # Test amount 9099
            self.enter_amount("9099")
            page_content = self.driver.page_source.lower()
            transfer_blocked_9099 = "недостаточно" in page_content or "insufficient" in page_content

            # Test amount 9097
            self.enter_amount("9097")
            transfer_possible_9097 = self.is_transfer_possible()

            print("Actual result:")
            print(f"- Amount 9098 RUB: transfer possible - {'CORRECT' if transfer_possible_9098 else 'INCORRECT'}")
            print(f"- Amount 9099 RUB: transfer blocked - {'CORRECT' if transfer_blocked_9099 else 'INCORRECT'}")
            print(f"- Amount 9097 RUB: transfer possible - {'CORRECT' if transfer_possible_9097 else 'INCORRECT'}")

            if transfer_possible_9098 and transfer_blocked_9099 and transfer_possible_9097:
                return self.log_test_result("FBT-007", "Available amount logic", True, "Transfer logic works correctly")
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
            if not self.navigate_to_main_page():
                return self.log_test_result("FBT-008", "Page navigation", False, "Failed to navigate to main page")

            if not self.open_transfer_form():
                return self.log_test_result("FBT-008", "Form opening", False, "Failed to open transfer form")

            if not self.enter_card_number():
                return self.log_test_result("FBT-008", "Card input", False, "Failed to enter card number")

            test_cases = [
                ("1000", 100),
                ("5000", 500),
                ("155", 15),
                ("199", 19),
                ("100", 10)
            ]

            print("Commission calculation results:")
            errors_found = 0

            for amount, expected_commission in test_cases:
                self.enter_amount(amount)
                actual_commission = self.get_commission_value()
                is_correct = (actual_commission == expected_commission)

                status = "CORRECT" if is_correct else "INCORRECT"
                comment = f"(expected: {expected_commission})" if not is_correct else ""
                print(f"- Amount {amount} RUB: commission {actual_commission} RUB - {status} {comment}")

                if not is_correct:
                    errors_found += 1

            if errors_found == 0:
                return self.log_test_result("FBT-008", "Commission calculation", True,
                                            "All commissions calculated correctly")
            else:
                return self.log_test_result("FBT-008", "Commission calculation", False,
                                            f"Errors in {errors_found} out of {len(test_cases)} test cases")

        except Exception as e:
            return self.log_test_result("FBT-008", "Test execution", False, f"Error: {e}")

    def test_009_commission_rounding(self):
        print("\n" + "=" * 70)
        print("TEST FBT-009: Commission rounding algorithm")
        print("=" * 70)

        try:
            if not self.navigate_to_main_page():
                return self.log_test_result("FBT-009", "Page navigation", False, "Failed to navigate to main page")

            if not self.open_transfer_form():
                return self.log_test_result("FBT-009", "Form opening", False, "Failed to open transfer form")

            if not self.enter_card_number():
                return self.log_test_result("FBT-009", "Card input", False, "Failed to enter card number")

            test_cases = [
                ("104", 10),
                ("105", 10),
                ("109", 10),
                ("110", 11),
                ("149", 14)
            ]

            errors_found = 0
            for amount, expected_commission in test_cases:
                self.enter_amount(amount)
                actual_commission = self.get_commission_value()

                if actual_commission != expected_commission:
                    print(
                        f"ERROR: Amount {amount} RUB - commission {actual_commission} RUB (expected: {expected_commission} RUB)")
                    errors_found += 1
                else:
                    print(f"Amount {amount} RUB: commission {actual_commission} RUB - CORRECT")

            if errors_found > 0:
                return self.log_test_result("FBT-009", "Rounding algorithm", False,
                                            f"Found {errors_found} rounding errors")
            else:
                return self.log_test_result("FBT-009", "Rounding algorithm", True, "All rounding calculations correct")

        except Exception as e:
            return self.log_test_result("FBT-009", "Test execution", False, f"Error: {e}")

    def test_010_validation_boundary_values(self):
        print("\n" + "=" * 70)
        print("TEST FBT-010: Boundary values validation")
        print("=" * 70)

        try:
            if not self.navigate_to_main_page():
                return self.log_test_result("FBT-010", "Page navigation", False, "Failed to navigate to main page")

            if not self.open_transfer_form():
                return self.log_test_result("FBT-010", "Form opening", False, "Failed to open transfer form")

            if not self.enter_card_number():
                return self.log_test_result("FBT-010", "Card input", False, "Failed to enter card number")

            # Test zero amount
            self.enter_amount("0")
            zero_accepted = self.is_transfer_possible()

            # Test negative amount
            amount_input = self.find_amount_field()
            if amount_input:
                amount_input.clear()
                amount_input.send_keys("-100")
                negative_value = self.wait.until(
                    lambda driver: amount_input.get_attribute('value')
                )
                negative_accepted = "-100" in negative_value
            else:
                negative_accepted = False

            validation_errors = []
            if zero_accepted:
                validation_errors.append("System accepts zero amount")
            if negative_accepted:
                validation_errors.append("System accepts negative amount")

            if validation_errors:
                return self.log_test_result("FBT-010", "Amount validation", False,
                                            f"Validation issues: {', '.join(validation_errors)}")
            else:
                return self.log_test_result("FBT-010", "Amount validation", True, "Amount validation works correctly")

        except Exception as e:
            return self.log_test_result("FBT-010", "Test execution", False, f"Error: {e}")

    def run_all_tests(self):
        print("F-BANK AUTOMATED TEST SUITE")
        print("=" * 70)
        print("Based on manual test cases from Berezhnaya_SECOND.md")
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
            print("TEST SUMMARY")
            print("=" * 70)

            passed_count = sum(1 for result in self.results if "PASSED" in result)
            total_count = len(self.results)

            for result in self.results:
                print(result)

            print(f"\nTotal: {passed_count}/{total_count} tests passed")

            return passed_count == total_count

        except Exception as e:
            print(f"Critical error during test execution: {e}")
            return False
        finally:
            self.teardown()


if __name__ == "__main__":
    tester = FBankAutotests()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
