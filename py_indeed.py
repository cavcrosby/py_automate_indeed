#######################################################################################
#
#       Author: Conner Crosby
#       Description:
#       The purpose of the code written is to automate the process of applying to jobs
#       on Indeed that can be applied via a 'Indeed Resume'.
#
#
#######################################################################################

# Standard Library Imports
import os, logging, sqlite3, configparser

# Third Party Imports
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# Local Application Imports
from scripts.web import sign_in_to_indeed, search_preference, fetch_all_jobs_from_page,\
    parse_apply_w_indeed_resume, apply, next_web_page, construct_container
from scripts.database import *
from scripts.logger import *

# #########CONFIGURATIONS#############################################################
# #########EXTERNAL INI FILE SETUP#########
config_app = configparser.ConfigParser()
config_app.read('app.ini')
py_indeed_configs = config_app['py_indeed']

# #########SETTING UP CHROME DRIVER (OR ANOTHER DRIVER TYPE)#########
chrome_option = Options()
chrome_option.add_argument("--headless")
chrome_option.add_argument("--window-size=1366,768")
# chrome_option.binary_location = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
chrome = webdriver.Chrome(executable_path=(os.getcwd() + r'\chromedriver.exe'),
                          options=chrome_option)

# #########CONNECTING TO DB FILE 'questions__answers_db', INITIAL CREATION OF THE 'data' TABLE#########
connection_to_db = sqlite3.connect("questions__answers_db.db")
cursor = connection_to_db.cursor()
data_table_creation(cursor, connection_to_db)

# #########LOGGERS#########
general_runtime_logger = create_general_logger(__name__, level="INFO")

# #########SPECIFIC CONTAINER CREATION#########
data_container = construct_container()

# #########APPLICATION CONFIGS#########
email_address = py_indeed_configs['email_address']
password = py_indeed_configs['password']
job_title = py_indeed_configs['job_title']
location = py_indeed_configs['location']
#######################################################################################

def main():

    """ MAIN PROGRAM EXECUTION """

    signed_in = sign_in_to_indeed(chrome, email_address, password)
    if(signed_in):
        search_preference(chrome, job_title, location)
        while(True):
            jobs = fetch_all_jobs_from_page(chrome)
            jobs_indeed_resume = parse_apply_w_indeed_resume(jobs)
            apply(chrome, jobs_indeed_resume, cursor, connection_to_db, data_container)
            next_web_page(chrome)
    else:
        general_runtime_logger.error("Could not sign into indeed account...")

def test_main():

    """ THIS MAIN IS MEANT FOR TESTING SPECIFIC JOB APPLICATIONS """

    sign_in_to_indeed(chrome, email_address, password)
    jobs_indeed_resume = []

    apply(chrome, jobs_indeed_resume, cursor, connection_to_db, data_container)

main()
#test_main()

connection_to_db.close()
logging.shutdown()
