# #########WEB BROWSER FUNCTIONS#########

# Standard Library Imports
import time

# Third Party Imports
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# Local Application Imports
from scripts.logger import *

logger = create_general_logger(__name__, level="INFO")

def sign_in_to_indeed(driver, email, password):

    """ SIGN IN TO INDEED.COM """

    logger.info("Now signing in into Indeed Account...")
    driver.get("https://www.indeed.com/account/login?dest=%2F")
    del_textbox_content_by_element_id(driver, "login-email-input")
    driver.find_element_by_id("login-email-input").click()
    driver.find_element_by_id("login-email-input").send_keys(email)
    time.sleep(2)
    del_textbox_content_by_element_id(driver, "login-password-input")
    driver.find_element_by_id("login-password-input").click()
    driver.find_element_by_id("login-password-input").send_keys(password)
    time.sleep(2)
    driver.find_element_by_id("login-submit-button").click()

    try:
        driver.find_element_by_id("login-password-input")
        logger.error("Failed to authenticate with given credentials...")
        return False
    except NoSuchElementException:
        logger.info("Successful login...")
        return True

def search_preference(driver, job_title, location):

    """ GOING TO INDEED AND SEARCHING FOR 'JOB' IN 'LOCATION' """

    logger.info("Now attempting to search for {0} positions in {1}...".format(job_title, location))
    driver.get("https://www.indeed.com")
    driver.find_element_by_id("text-input-where").click()
    del_textbox_content_by_element_id(driver, "text-input-what")
    driver.find_element_by_id("text-input-what").send_keys(job_title)
    driver.find_element_by_id("text-input-where").click()
    del_textbox_content_by_element_id(driver, "text-input-where")
    driver.find_element_by_id("text-input-where").send_keys(location)
    driver.find_element_by_tag_name("button").click()

def fetch_all_jobs_from_page(driver):

    """
        FETCHES JOB DIVS (FOR THE CURRENT PAGE) FOR FURTHER USE
        WEBSITE MIGHT CHANGE UP THESE CLASS NAMES, NEED TO CHECK HERE IN CASE NOTHING WORKS
    """

    logger.info("Fetching jobs from web-page...")
    page_job_divs = driver.find_elements_by_xpath("""//div[@class="jobsearch-SerpJobCard row result clickcard"] | 
    //div[@class="jobsearch-SerpJobCard row result clickcard vjs-highlight"] | 
    //div[@class="jobsearch-SerpJobCard lastRow row result clickcard"] | 
    //div[@class="jobsearch-SerpJobCard row sjlast result clickcard"] | 
    //div[@class="jobsearch-SerpJobCard unifiedRow row result clickcard"]""")

    return page_job_divs

def parse_apply_w_indeed_resume(jobs):

    """ RUNS THROUGH JOB DIVS,
    CHECKING IF INDEED RESUME CAN BE USED,
    IF NOT SKIP, RETURNS JOB URLS THAT CAN USE INDEED RESUME """

    logger.info("Parsing jobs to find those that can be applied via Indeed Resume...")
    indeed_jobs_to_apply_for = list()
    for job_div in jobs:
        try:
            job_div.find_element_by_class_name("iaLabel")  # CAN THIS JOB BE APPLIED WITH INDEED'S RESUME?
            indeed_jobs_to_apply_for.append(job_div.find_element_by_tag_name("a").get_attribute("href"))
        except NoSuchElementException:
            continue  # APPLYING IS DONE ON COMPANY WEBSITE, SKIP THIS JOB

    return indeed_jobs_to_apply_for

def next_web_page(driver):

    """ CLICKS NEXT PAGE AND CLOSES POP WINDOW IF IT OCCURS, INFINITE LOOP POSSIBLE """

    try:
        for page in [page_link for page_link in driver.find_element_by_class_name("pagination").find_elements_by_tag_name("a")]:
            if page.text == "Next »":
                page.click()

        logger.info("===========!!!!! Going to next page... !!!!!===========")
        click_out_of_job_alert(driver)
    except:
        logger.warning("===========!!!!! Page error! Refreshing page... !!!!!===========")
        driver.refresh()
        next_web_page(driver)

def click_out_of_job_alert(driver):

    """
        SOMETIMES WHEN SWITCHING PAGES, A POPUP COULD GET IN THE WAY OF THE DRIVER
        THIS TRIES TO CLOSE OUT OF THAT POPUP AND CONTINUE
    """

    time.sleep(2)
    try:
        driver.find_element_by_id("popover-close-link").click()
    except NoSuchElementException:
        logger.info("No pop-up")

def del_textbox_content_by_element_id(driver, element_id):

    """ THIS DELETES TEXTBOX CONTENT, BASED ON THE TEXTBOX'S ID """

    driver.find_element_by_id(element_id).send_keys(Keys.CONTROL, "a")
    driver.find_element_by_id(element_id).send_keys(Keys.DELETE)
