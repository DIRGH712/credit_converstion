from selenium import webdriver
import os
from datetime import date, datetime, timedelta
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import random
import json

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Initialize an empty list to store the data
data_list = []
set_nextInLoop = []
with open("config.json") as config_file: #Add ASUruite and password to config file.
    config = json.load(config_file)

username = config.get("username")
password = config.get("password")


def read_CSV():
    global data_list
    final_num = ''
    # Open the CSV file for reading
    with open('/2237BC-Courses.csv', 'r') as csv_file: #change file path[Its the input .csv] according to your local machine
        # Create a CSV reader
        csv_reader = csv.DictReader(csv_file)

        # Loop through rows and add each row as a dictionary to the list
        row_number = 0
        for row in csv_reader:
            data_list.append(row)
            current_num = data_list[row_number]['Course Offering ID: Course Num']
            if current_num != final_num:
                set_nextInLoop.append(row_number)
                final_num = current_num
            row_number += 1
        # print(set_nextInLoop)



def is_at_least_one_month_later(register_datetime, complete_datetime):
    # Calculate the difference between the two timestamps
    time_difference = complete_datetime - register_datetime

    # Calculate the equivalent of one month in seconds (approximately)
    one_month_seconds = timedelta(days=30).total_seconds()

    # Compare the time difference with one month in seconds
    return time_difference.total_seconds() >= one_month_seconds


def initialize_browser():
    global data_list
    global set_nextInLoop
    driver.get("https://weblogin-qa.asu.edu/edx-onboarding/admin")
    driver.find_element(By.ID, "username").send_keys(username)  # argument 1 should contain username
    driver.find_element(By.ID, "password").send_keys(password)  # argument 2 should contain password
    driver.find_element(By.NAME, "submit").click()

    # Buffer time for page to load
    sleep(3)

    # Duo Authentication Verfication
    frame = driver.find_element(By.XPATH, '//iframe[@id="duo_iframe"]')
    driver.switch_to.frame(frame)

    # Verify Authentication on phone
    driver.find_element(By.ID, "auth_methods").find_element(By.CSS_SELECTOR, "button").click()
    sleep(10)
    print("Logged In, looking up transfer credit ")


    # desired - 2 for row
    for index in set_nextInLoop:
        for offset in range(15):
            row_number = offset + index
            if row_number < len(data_list):
                row_data = data_list[row_number]
                print(row_data)
            else:
                print(f"Row {row_number} does not exist in the dataset.")

            # Access specific column values for a row like this:
            if row_number < len(data_list):
                user_email = data_list[row_number]['Email']
                user_username = data_list[row_number]['ASURITE ID']
                course_run = data_list[row_number]['Course Offering ID: Course Run']
                course_org = data_list[row_number]['Course Offering ID: Course Org']
                course_num = data_list[row_number]['Course Offering ID: Course Num']
                final_grade = data_list[row_number]['Grade']
                register_date = data_list[row_number]['Registration Date']
                if data_list[row_number]['Course Completed Date'] == '':
                    complete_date = date.today().strftime('%m/%d/%Y')
                    print(complete_date)
                else:
                    complete_date = data_list[row_number]['Course Completed Date']

            else:
                print(f"Row {row_number} does not exist in the dataset.")

            try:

                input_upstream = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "upstreamSystem")))

                input_uuid = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='request_uuid']")))

                input_courseOrg = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='course_org']")))

                input_courseNum = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='course_num']")))

                input_courseRun = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='course_run']")))

                input_finalGrade = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='final_grade']")))

                input_userName = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='user_username']")))

                input_userEmail = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='user_email']")))

                input_completion_timestamp = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='course_completion_timestamp']")))

                input_enrollment_timestamp = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='enrollment_timestamp']")))

                submit_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "// input[ @ type = 'submit']")))

                input_upstream.send_keys('Open Scale Pathways Program Open edX')
                input_uuid.clear()
                input_courseOrg.clear()
                input_courseNum.clear()
                input_courseRun.clear()
                input_finalGrade.clear()
                input_userName.clear()
                input_userEmail.clear()
                input_completion_timestamp.clear()
                input_enrollment_timestamp.clear()

                date_format = "%m/%d/%Y"
                # print(register_date,complete_date)


                register_datetime = datetime.strptime(register_date, date_format)
                complete_datetime = datetime.strptime(complete_date, date_format)
                register_timestamp = int(register_datetime.timestamp())
                complete_timestamp = int(complete_datetime.timestamp())

                input_uuid.send_keys(''.join(random.choice('0123456789abcdef') for _ in range(32)))
                input_courseOrg.send_keys(course_org)
                input_courseNum.send_keys(course_num)
                input_courseRun.send_keys(course_run)
                input_finalGrade.send_keys(final_grade)
                input_userName.send_keys(user_username)
                input_userEmail.send_keys(user_email)

                if is_at_least_one_month_later(register_datetime, complete_datetime):
                    input_completion_timestamp.send_keys(complete_timestamp)
                    input_enrollment_timestamp.send_keys(register_timestamp)
                    sleep(2)
                    submit_button.click()
                else:
                    print("Completion date is not at least one month later than the registration.")
                    continue

                if driver.window_handles:
                    message_box = WebDriverWait(driver, 50).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='messageBox']")))
                    message = message_box.text

                    csv_filename = '../person_data.csv'

                    status = "Success" if "Congratulations" in message else "Failed"
                    data = {
                        'Name': user_username,
                        'CourseNum': course_num,
                        'Status': status
                    }
                    add_to_csv(csv_filename, data)

                else:
                    print("Error: Browser window is closed or not found.")

            except (TimeoutException, WebDriverException) as e:
                print(f"An error occurred during form submission: {e}")

            sleep(6)
            driver.get("https://weblogin-qa.asu.edu/edx-onboarding/admin")
            sleep(2)
            if status == "Success":
                print("Success: ASU credit successfully converted")
                break

        print("Out of FOR loop inner")

    print("Out of FOR loop main")

def add_to_csv(filename, data):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        fieldnames = ['Name', 'CourseNum', 'Status']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

if __name__ == "__main__":
    read_CSV()
    initialize_browser()
