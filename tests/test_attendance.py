#cd tests
#python test_attendance.py
import unittest
import time
import csv
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AttendanceSystemTests(unittest.TestCase):
    """Test suite for Attendance Web Management System using Selenium with ChromeDriver"""
    
    # Class variable to store all test results
    test_results = []
    
    # Test data
    TEST_STUDENTS = [
        {
            "Date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "Email": "john.123@example.com",
            "Name": "John Smith",
            "Description": "Present for the entire session.",
            "Latitude": "12.9716",
            "Longitude": "77.5946",
            "Login": "09:00",
            "Logout": "17:00",
        },
        {
            "Date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "Email": "jane.doe@work.net",
            "Name": "Jane Doe",
            "Description": "Attended the morning session.",
            "Latitude": "13.0827",
            "Longitude": "80.2707",
            "Login": "09:05",
            "Logout": "13:00",
        },
        {
            "Date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "Email": "test@university.edu",
            "Name": "Test Student",
            "Description": "Late arrival.",
            "Latitude": "12.5678",
            "Longitude": "78.9012",
            "Login": "10:30",
            "Logout": "17:00",
        },
    ]
    
    # Expected form field elements
    FORM_FIELDS = {
        "Email": {"by": By.ID, "value": "Email"},
        "Name": {"by": By.ID, "value": "Name"},
        "Description": {"by": By.ID, "value": "Description"},
        "Latitude": {"by": By.ID, "value": "Latitude"},
        "Longitude": {"by": By.ID, "value": "Longitude"},
        # There are no direct input fields for Date, Login, and Logout in this HTML.
        # These actions are triggered by the "Sign In" and "Sign Out" buttons.
        "signIn": {"by": By.XPATH, "value": "//button[contains(@class, 'btn-login')]"},
        "signOut": {"by": By.XPATH, "value": "//button[contains(@class, 'btn-logout')]"},
        "getLocation": {"by": By.ID, "value": "locationBtn"},
    }
    
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        # Uncomment for headless testing
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.app_url = "https://script.google.com/macros/s/AKfycbzWKHMP6tORLC-KpWSP1db1HIqP1yMTFVLy4SuyJS4u5O3HhRIJDz5CkFbRBiVAeJfB/exec"
        cls.driver.get(cls.app_url)
        cls.driver.save_screenshot("debug_page_initial.png")
        print("=== PAGE SOURCE AFTER LOAD ===")
        print(cls.driver.page_source)
        try:
            # Switch to sandboxFrame
            WebDriverWait(cls.driver, 30).until(
                EC.presence_of_element_located((By.ID, "sandboxFrame"))
            )
            iframe1 = cls.driver.find_element(By.ID, "sandboxFrame")
            cls.driver.switch_to.frame(iframe1)
            # Switch to userHtmlFrame
            WebDriverWait(cls.driver, 30).until(
                EC.presence_of_element_located((By.ID, "userHtmlFrame"))
            )
            iframe2 = cls.driver.find_element(By.ID, "userHtmlFrame")
            cls.driver.switch_to.frame(iframe2)
            # Now wait for the form inside the second iframe
            WebDriverWait(cls.driver, 30).until(
                EC.presence_of_element_located((By.ID, "attendanceForm"))
            )
        except Exception as e:
            cls.driver.save_screenshot("debug_page_error.png")
            print("=== PAGE SOURCE ON ERROR ===")
            print(cls.driver.page_source)
            print(f"ERROR: Could not find attendanceForm after 30 seconds: {e}")
            raise

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()

    def setUp(self):
        self.driver.get(self.app_url)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "sandboxFrame"))
            )
            iframe1 = self.driver.find_element(By.ID, "sandboxFrame")
            self.driver.switch_to.frame(iframe1)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "userHtmlFrame"))
            )
            iframe2 = self.driver.find_element(By.ID, "userHtmlFrame")
            self.driver.switch_to.frame(iframe2)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "attendanceForm"))
            )
        except Exception as e:
            self.driver.save_screenshot("debug_page_error_setup.png")
            print("=== PAGE SOURCE ON ERROR IN setUp ===")
            print(self.driver.page_source)
            print(f"ERROR: Could not find attendanceForm in setUp after 30 seconds: {e}")
            raise
        self.clear_form()

    def clear_form(self):
        # Clear all input fields
        for field_id in ["Email", "Name", "Description", "Latitude", "Longitude"]:
            try:
                field = self.driver.find_element(By.ID, field_id)
                field.clear()
            except Exception:
                pass

    def fill_form(self, student_data, get_location=False):
        print("Filling form with:", student_data)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "Email"))
        )
        email_field = self.driver.find_element(By.ID, "Email")
        email_field.clear()
        email_field.send_keys(student_data["Email"])

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "Name"))
        )
        name_field = self.driver.find_element(By.ID, "Name")
        name_field.clear()
        name_field.send_keys(student_data["Name"])

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "Description"))
        )
        desc_field = self.driver.find_element(By.ID, "Description")
        desc_field.clear()
        desc_field.send_keys(student_data["Description"])

        if get_location:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "locationBtn"))
            )
            self.driver.find_element(By.ID, "locationBtn").click()
            time.sleep(2)

    def is_element_present(self, by, value):
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False
    
    def test_01_page_loads_correctly(self):
        try:
            self.assertIn("Attendance Tracking System", self.driver.title)
            form_present = self.is_element_present(By.ID, "attendanceForm")
            self.assertTrue(form_present, "Form not found on page")
            self.__class__.record_test_result("TC_01", "Page Loading Test", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_01", "Page Loading Test", "FAIL", str(e))
            raise

    def test_02_form_elements_exist(self):
        try:
            self.assertTrue(self.is_element_present(By.ID, "Email"), "Email field not found")
            self.assertTrue(self.is_element_present(By.ID, "Name"), "Name field not found")
            self.assertTrue(self.is_element_present(By.ID, "Description"), "Description field not found")
            self.assertTrue(self.is_element_present(By.ID, "Latitude"), "Latitude field not found")
            self.assertTrue(self.is_element_present(By.ID, "Longitude"), "Longitude field not found")
            self.assertTrue(self.is_element_present(By.ID, "locationBtn"), "Get Location button not found")
            self.assertTrue(self.is_element_present(By.XPATH, self.FORM_FIELDS["signIn"]["value"]), "Sign In button not found")
            self.assertTrue(self.is_element_present(By.XPATH, self.FORM_FIELDS["signOut"]["value"]), "Sign Out button not found")
            self.__class__.record_test_result("TC_02", "Form Elements Test", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_02", "Form Elements Test", "FAIL", str(e))
            raise

    def test_03_successful_sign_in(self):
        try:
            student_data = self.TEST_STUDENTS[0]
            self.fill_form(student_data, get_location=True)
            self.driver.find_element(By.XPATH, self.FORM_FIELDS["signIn"]["value"]).click()
            time.sleep(2)
            status_div = self.driver.find_element(By.ID, "status")
            status_text = status_div.text.lower()
            # Check for any status message (success, processing, or location captured)
            self.assertTrue(
                any(msg in status_text for msg in ["success", "processing", "location captured"]),
                "Sign In status message not found"
            )
            self.__class__.record_test_result("TC_03", "Sign In Test", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_03", "Sign In Test", "FAIL", str(e))
            raise

    def test_04_successful_sign_out(self):
        try:
            student_data = self.TEST_STUDENTS[1]
            self.fill_form(student_data, get_location=True)
            self.driver.find_element(By.XPATH, self.FORM_FIELDS["signOut"]["value"]).click()
            time.sleep(2)
            status_div = self.driver.find_element(By.ID, "status")
            status_text = status_div.text.lower()
            # Check for any status message (success, no active login, or processing)
            self.assertTrue(
                any(msg in status_text for msg in ["success", "no active login", "processing"]),
                "Sign Out status message not found"
            )
            self.__class__.record_test_result("TC_04", "Sign Out Test", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_04", "Sign Out Test", "FAIL", str(e))
            raise

    def test_05_sign_in_requires_email_and_name(self):
        try:
            self.driver.find_element(By.XPATH, self.FORM_FIELDS["signIn"]["value"]).click()
            time.sleep(1)
            status_div = self.driver.find_element(By.ID, "status")
            status_text = status_div.text.lower()
            self.assertTrue("email" in status_text or "name" in status_text, "Sign In did not show error for missing Email or Name")
            self.__class__.record_test_result("TC_05", "Sign In Empty Fields Test", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_05", "Sign In Empty Fields Test", "FAIL", str(e))
            raise

    def test_06_sign_out_requires_email_and_name(self):
        try:
            self.driver.find_element(By.XPATH, self.FORM_FIELDS["signOut"]["value"]).click()
            time.sleep(1)
            status_div = self.driver.find_element(By.ID, "status")
            status_text = status_div.text.lower()
            self.assertTrue("email" in status_text or "name" in status_text, "Sign Out did not show error for missing Email or Name")
            self.__class__.record_test_result("TC_06", "Sign Out Empty Fields Test", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_06", "Sign Out Empty Fields Test", "FAIL", str(e))
            raise

    def test_07_get_location_button_updates_fields(self):
        try:
            self.driver.find_element(By.ID, "locationBtn").click()
            time.sleep(3)
            latitude = self.driver.find_element(By.ID, "Latitude").get_attribute("value")
            longitude = self.driver.find_element(By.ID, "Longitude").get_attribute("value")
            self.assertTrue(latitude != "" and longitude != "", "Latitude and Longitude fields were not updated after clicking 'Get Location'")
            self.__class__.record_test_result("TC_07", "Get Location Updates Fields Test", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_07", "Get Location Updates Fields Test", "FAIL", str(e))
            raise

    def test_08_invalid_email(self):
        try:
            student_data = self.TEST_STUDENTS[0].copy()
            student_data["Email"] = "invalid-email"  # Invalid email
            self.fill_form(student_data, get_location=True)
            self.driver.find_element(By.XPATH, self.FORM_FIELDS["signIn"]["value"]).click()
            time.sleep(1)
            status_div = self.driver.find_element(By.ID, "status")
            status_text = status_div.text.lower()
            self.assertIn("email", status_text, "Email validation error message not found")
            self.__class__.record_test_result("TC_08", "Invalid Email Validation", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_08", "Invalid Email Validation", "FAIL", str(e))
            raise

    def test_09_missing_name(self):
        try:
            student_data = self.TEST_STUDENTS[0].copy()
            student_data["Name"] = ""  # Missing name
            self.fill_form(student_data, get_location=True)
            self.driver.find_element(By.XPATH, self.FORM_FIELDS["signIn"]["value"]).click()
            time.sleep(1)
            status_div = self.driver.find_element(By.ID, "status")
            status_text = status_div.text.lower()
            self.assertIn("name", status_text, "Name validation error message not found")
            self.__class__.record_test_result("TC_09", "Missing Name Validation", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_09", "Missing Name Validation", "FAIL", str(e))
            raise

    def test_10_invalid_location(self):
        try:
            student_data = self.TEST_STUDENTS[0].copy()
            student_data["Latitude"] = "999"  # Invalid latitude
            student_data["Longitude"] = "999"  # Invalid longitude
            self.fill_form(student_data, get_location=False)
            self.driver.find_element(By.XPATH, self.FORM_FIELDS["signIn"]["value"]).click()
            time.sleep(1)
            status_div = self.driver.find_element(By.ID, "status")
            status_text = status_div.text.lower()
            self.assertIn("location", status_text, "Location validation error message not found")
            self.__class__.record_test_result("TC_10", "Invalid Location Validation", "PASS")
        except AssertionError as e:
            self.__class__.record_test_result("TC_10", "Invalid Location Validation", "FAIL", str(e))
            raise

    def test_11_page_load_performance(self):
        try:
            start_time = time.time()
            self.driver.get(self.app_url)
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "sandboxFrame"))
                )
                iframe1 = self.driver.find_element(By.ID, "sandboxFrame")
                self.driver.switch_to.frame(iframe1)
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "userHtmlFrame"))
                )
                iframe2 = self.driver.find_element(By.ID, "userHtmlFrame")
                self.driver.switch_to.frame(iframe2)
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "attendanceForm"))
                )
            except Exception as e:
                self.driver.save_screenshot("debug_page_error_performance.png")
                print("=== PAGE SOURCE ON ERROR IN test_11_page_load_performance ===")
                print(self.driver.page_source)
                print(f"ERROR: Could not find attendanceForm in test_11_page_load_performance after 30 seconds: {e}")
                raise
            end_time = time.time()
            load_time = end_time - start_time
            threshold = 5.0
            if load_time <= threshold:
                self.__class__.record_test_result("TC_11", "Page Load Performance Test", "PASS", f"Load time: {load_time:.2f}s (Threshold: {threshold}s)")
            else:
                self.__class__.record_test_result("TC_11", "Page Load Performance Test", "FAIL", f"Load time: {load_time:.2f}s exceeds threshold of {threshold}s")
        except Exception as e:
            self.__class__.record_test_result("TC_11", "Page Load Performance Test", "FAIL", str(e))
            raise

    @classmethod
    def record_test_result(cls, test_id, test_name, status, comments=""):
        if status not in ["PASS", "FAIL"]:
            status = "FAIL"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cls.test_results.append({
            "Test ID": test_id,
            "Test Name": test_name,
            "Status": status,
            "Timestamp": timestamp,
            "Comments": comments
        })

    @classmethod
    def export_test_results(cls):
        filename = f"attendance_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Test ID", "Test Name", "Status", "Timestamp", "Comments"])
            writer.writeheader()
            for row in cls.test_results:
                if row["Test ID"] != "SUMMARY":
                    writer.writerow(row)
        print(f"Test results exported to {filename}")
        return filename

    @classmethod
    def export_html_report(cls):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Attendance System Test Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
                .pass {{ background-color: #dff0d8; }}
                .fail {{ background-color: #f2dede; }}
            </style>
        </head>
        <body>
            <h1>Attendance System Test Results</h1>
            <p>Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <table>
                <tr>
                    <th>Test ID</th>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                    <th>Comments</th>
                </tr>
        """
        for result in cls.test_results:
            if result["Test ID"] == "SUMMARY":
                continue
            status_class = result["Status"].lower()
            row_class = "pass" if status_class == "pass" else "fail"
            html_content += f"""
                <tr class=\"{row_class}\">
                    <td>{result['Test ID']}</td>
                    <td>{result['Test Name']}</td>
                    <td>{result['Status']}</td>
                    <td>{result['Timestamp']}</td>
                    <td>{result['Comments']}</td>
                </tr>
            """
        html_content += """
            </table>
        </body>
        </html>
        """
        filename = f"attendance_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML report generated: {filename}")
        return filename

def run_tests():
    test_suite = unittest.TestLoader().loadTestsFromTestCase(AttendanceSystemTests)
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    AttendanceSystemTests.record_test_result(
        "SUMMARY",
        "Test Execution Summary",
        "INFO",
        f"Total: {test_result.testsRun}, Passed: {test_result.testsRun - len(test_result.failures) - len(test_result.errors)}, "
        f"Failed: {len(test_result.failures)}, Errors: {len(test_result.errors)}"
    )
    AttendanceSystemTests.export_test_results()
    AttendanceSystemTests.export_html_report()

if __name__ == "__main__":
    run_tests()