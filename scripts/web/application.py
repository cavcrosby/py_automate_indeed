# #########APPLICATION FORM FUNCTIONS#########

# Standard Library Imports
import selenium, time, datetime
import selenium.common.exceptions

# Third Party Imports
import PySimpleGUI as sg

# Local Application Imports
from scripts.database import *
from scripts.logger import *

button_label_number = 1
current_url = ""
logger = create_general_logger(__name__, level="INFO")

# #########APPLICATION GENERIC FUNCTIONS#########

def get_time():

    """ TIME IS RETURNED AS 'YYYY-MM-DD_HH-MM-SS' """

    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def get_questions(driver, data_container):

    def apply_get_questions(procedure):

        return procedure(application_form)

    """ GETS APPLICATION FORM FOR THAT PAGE, ITERATES OVER KNOWN QUESTION TYPES AND GETS QUESTIONS OF KNOWN TYPES """

    question_texts = {}
    application_form = driver.find_element_by_id("ia-container")
    question_types = get_question_types(data_container)

    for question_type in question_types:
        question_texts[question_type] = \
            apply_get_questions(get_question_type_funcs(data_container, question_type)["get_questions"])

    append_questions(data_container, question_texts)

def getting_choices(question_to_obj, procedure, question):

    """ GENERIC FUNCTION FOR APPLYING 'getting_choices' FOR SOME FORM OF QUESTION """

    return procedure(question_to_obj, question)

def try_to_answer_questions(file, driver, cursor, connection_to_db, data_container):

    """ TRY AND ANSWER QUESTIONS, RETURN WHETHER OR NOT TO MOVE ON TO THE NEXT JOB """

    read_other_questions_and_quit = answer_questions(file, cursor, connection_to_db, data_container)
    time.sleep(1)
    driver.find_element_by_id("form-action-continue").click()

    if (read_other_questions_and_quit):
        logger.info("Found un-answered/new questions, regardless, moving to next job")
    else:
        logger.info("Answered, now going to next page...")

    return read_other_questions_and_quit  # IF SO, WE WANT TO MOVE ON TO THE NEXT JOB

def answer_questions(file, cursor, connection_to_db, data_container):

    """ FUNCTION FOR ANSWERING QUESTIONS, THIS WORKS FOR ANY 'KNOWN' TYPE """

    def apply_answer_question(question_to_obj, procedure, file, question):

        return procedure(question_to_obj, file, question)

    questions_types = get_question_types(data_container)
    read_questions_and_quit = False
    for question_type in questions_types:
        questions = get_question_type_questions(data_container, question_type)
        functions = get_question_type_funcs(data_container, question_type)
        for question in questions:
            if (question not in file):
                cursor.execute(""" INSERT INTO data VALUES (?, ?, ?, ?)""",
                               (question, None, question_type,
                                str(tuple(getting_choices(questions, functions["getting_choices"], question)))))
                connection_to_db.commit()
                read_questions_and_quit = True
            elif read_questions_and_quit:
                continue
            else:
                if (file[question] is None):  # NO ANSWER EXISTS FOR THIS QUESTION, GET ANY OTHER QUESTIONS AND QUIT
                    read_questions_and_quit = True
                    continue

                successful = apply_answer_question(questions,
                                      get_question_type_funcs(data_container, question_type)["answer_questions"],
                                      file, question)
                if(not successful):
                    read_questions_and_quit = True



    return read_questions_and_quit

def apply(driver, jobs_urls, cursor, connection_to_db, data_container):

    def go_through_application():

        move_to_next_job = False
        kill_switch = 5

        while (not move_to_next_job and kill_switch > 0):
            try:
                driver.find_element_by_id("form-action-submit")
                logger.info("!!! End and ready to submit !!!")
                break
            except:
                try:
                    time.sleep(1)
                    driver.find_element_by_id("form-action-continue").click()
                    # CLICK CONTINUE AGAIN AS APPLY IS NOT ON SCREEN

                    driver.find_element_by_xpath("//div[@role='alert']")
                    # OTHER QUESTIONS ARE ASKED AND NEED TO BE FILLED

                    logger.info("There are questions that still need to be answered...")
                    get_questions(driver, data_container)
                    move_to_next_job = try_to_answer_questions(get_file_contents(cursor), driver, cursor,
                                                               connection_to_db, data_container)
                    flush_questions(data_container)
                    # QUESTIONS SHOULD BE FILLED OUT, READY TO PROCEED TO NEXT PAGE OR NOT

                    kill_switch -= 1
                    logger.info("Kill switch decremented, now: " + str(kill_switch))
                except selenium.common.exceptions.NoSuchElementException as e:
                    continue
                except Exception as e:
                    time_error_occurred = get_time()
                    logger.error(e)
                    logger.error(current_url)
                    logger.error("Unexpected error occurred while going through application...")
                    html_logger = create_html_logger(time_error_occurred)
                    logger.error("HTML page that error occurred on: {0}".format('{0}.txt'.format(time_error_occurred)))
                    html_logger.error(driver.page_source)
                    break
            finally:
                if (kill_switch <= 0):
                    logger.warning("Job got stuck, thus kill switch ended loop...")

    global button_label_number

    for url in jobs_urls:
        global current_url
        current_url = url
        button_label_number = 1
        logger.info("!!! Now going into job browser tab... !!!")
        logger.info("Job url: " + url)
        try:
            driver.execute_script(
                '''window.open("''' + url + '''", "_blank");''')
            # NEW TAB WITH JOB URL

            time.sleep(3)
            job_browser_tab = driver.window_handles[1]
            driver.switch_to.window(job_browser_tab)
            driver.find_element_by_xpath(
                "//div//span[@class='indeed-apply-widget indeed-apply-button-container indeed-apply-status-not-applied']").click()
            # JOB POPUP FRAME SHOULD APPEAR

            logger.info("Now applying...")
            time.sleep(3)
            first_frame = driver.find_element_by_class_name("indeed-apply-popup").find_element_by_tag_name("iframe")
            driver.switch_to.frame(first_frame)
            second_frame = driver.find_element_by_tag_name("iframe")
            driver.switch_to.frame(second_frame)
            # SWITCHES TO JOB APPLICATION FRAME, WHICH IS EMBEDDED IN ANOTHER FRAME

            time.sleep(3)
            driver.find_element_by_id("form-action-continue").click()
            # GOING PAST THE FIRST FORM

            go_through_application()
            logger.info("!!! Exiting job browser tab... !!!")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            # CLOSE JOB TAB, SWAP BACK TO ORIGINAL TAB

        except selenium.common.exceptions.NoSuchElementException as e:
            logger.warning("Job picked up cannot be applied with indeed resume...")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue
        except Exception as e:
            logger.error(e)
            logger.error("Unexpected error occurred while transitioning from job to job...")
            logger.error(url)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue

# #########APPLICATION SPECIFIC FUNCTIONS#########

def get_textbox_questions(application_form):

    """ QUESTION TITLE --> TEXTBOX ARE PULLED INTO DICTIONARY """
    # TODO, HAVE SOME UNIFORM WAY THAT THEY STORE WEB OBJECTS? FOR ALL TYPES...

    return {question.find_element_by_class_name("icl-TextInput-labelWrapper").text: question.find_element_by_tag_name("input")
            for question in application_form.find_elements_by_class_name("icl-TextInput") if question.text != ''}

def get_radiobuttons_questions(application_form):

    """ QUESTION TITLE --> ENTIRE DIV ARE PULLED INTO DICTIONARY FOR EACH """

    return {question.find_element_by_class_name("icl-Radio-legend").text: question
            for question in application_form.find_elements_by_class_name("icl-Radio-container")
            if question.text != ''}

def get_select_questions(application_form):

    """ QUESTION TITLE --> SELECTION BOX ARE PULLED INTO DICTIONARY FOR EACH QUESTION """

    return {question.find_element_by_class_name("icl-Select-label").text: question.find_element_by_class_name("icl-Select-wrapper")
            for question in application_form.find_elements_by_class_name("icl-Select")
            if question.find_element_by_class_name("icl-Select-label").text != ''}

def getting_textbox_choices(question_to_obj, question):

    """ TEXTBOX QUESTIONS DO NOT HAVE ANSWER CHOICES """

    return ""

def getting_radio_choices(text_to_div_box, question):

    """
        BASED ON THE QUESTION ARE THE APPROPRIATE RADIO BUTTONS PULLED FROM
        AN INDEX IS ALSO ATTACHED, WITH THE LOGICAL BUTTON
    """

    radio_buttons = text_to_div_box[question].find_elements_by_class_name("icl-Radio-item")
    radio_container = dict()
    global button_label_number
    for radio_button in radio_buttons:
        radio_container[radio_button.text] = {"logicalbutton": radio_button, "index": button_label_number}
        button_label_number += 1

    return radio_container

def getting_select_choices(selection_box_questions_to_divs, question):

    """ BASED ON THE QUESTION ARE THE APPROPRIATE SELECT OPTIONS PULLED FROM """

    selection_choices_to_value = {selection.text: selection.get_attribute("value")
                                  for selection in
                                  selection_box_questions_to_divs[question].find_elements_by_tag_name("option")}
    return selection_choices_to_value.keys()

def answer_textbox_questions(text_box_questions_and_inputs, file, question):

    """ THE APPROPRIATE TEXTBOX IS CLICKED ON, FROM THERE AN ANSWER IS FILLED IN """

    try:
        text_box_questions_and_inputs[question].click()
        text_box_questions_and_inputs[question].send_keys(file[question])
        return True
    except selenium.common.exceptions.NoSuchElementException as e:
        logger.error(e)
        logger.error("Could not click on textbox input-box...")
        return False

def answer_radiobuttons_questions(radio_questions_to_divs, file, question):

    """
        RADIO BUTTONS TEXT TO LOGICAL BUTTON IS COLLECTED
        THESE BUTTONS ARE GATHERED AND GIVEN A LABEL NUMBER IN ORDER OF APPEARANCE
        XPATH IS BUILT TO TRY AND INTERACT WITH RADIO BUTTON
    """

    radio_labels_logical_buttons_and_indexes = getting_radio_choices(radio_questions_to_divs, question)
    files_answer = file[question]
    try:
        button_to_click = radio_labels_logical_buttons_and_indexes[files_answer]["logicalbutton"]
        build_x_path = "//input[@id=" + "\'" + (
                'radio-option-' + str(radio_labels_logical_buttons_and_indexes[files_answer]["index"])) + "\'" + "]"
        button_to_click.find_element_by_xpath(build_x_path).click()
        return True
    except selenium.common.exceptions.NoSuchElementException as e:
        logger.error(e)
        logger.error("Url is: {0}".format(current_url))
        logger.error("Question was: {0}".format(question))
        logger.error("Answer provided for the question was: {0}".format(files_answer))
        logger.error("Answers to choose from for the question: {0}".format
                     ([radio_button for radio_button in radio_labels_logical_buttons_and_indexes]))
        logger.error("x-path was: //input[@id='radio-option-{0}']".format
                     (radio_labels_logical_buttons_and_indexes[files_answer]["index"]))
        logger.error("Could not click on radio button...")
        return False
    except KeyError as e:
        logger.error(e)
        logger.error("This is a re-occurring radio-button question, but with different answers...")
        return False

def answer_select_questions(select_questions_to_divs, file, question):

    """ XPATH IS BUILT TO LOCATE THE VALUE CHOSEN/ANSWERED IN THE FILE, CLICKING ON IT """

    files_answer = file[question]
    box_to_click_on = select_questions_to_divs[question]
    try:
        box_to_click_on.find_element_by_xpath("//select//option[@value=" + "'" +
                                              getting_select_choices(select_questions_to_divs, question)[files_answer]
                                              + "']").click()
        return True
    except selenium.common.exceptions.NoSuchElementException as e:
        logger.error(e)
        logger.error("Question was: {0}".format(question))
        logger.error("Answer to question was: {0}".format(files_answer))
        logger.error("x-path was: //select//option[@value='{0}']".format
                     (getting_select_choices(select_questions_to_divs, question)[files_answer]))
        logger.error("Could not click on selection value...")
        return False

def display_textbox_question(question, question_choices):

    """ PRESENTS THE USER WITH A SIMPLE TEXTBOX TO TYPE IN AND CLICK SUBMIT """

    layout = [
                  [sg.Text("{0}:".format(question))],
                  [sg.InputText(key="answer")],
                  [sg.Submit(), sg.Cancel()]
              ]

    window = sg.Window('py_answer', layout)
    event, value = window.Read()
    window.Close()
    if event == 'Cancel':
        value['answer'] = 'Cancel'
    return value['answer']

def display_radiobuttons_question(question, question_choices):

    """ FOR NOW, RADIOBUTTONS QUESTIONS ARE DISPLAYED LIKE SELECT QUESTIONS """

    return display_select_question(question, question_choices)

def display_select_question(question, question_choices):

    """ 'eval' TAKES THE EXPRESSION OF dbRow[3] AND CONVERTS IT BACK INTO A TUPLE """
    question_choices = eval(question_choices)

    layout = list()
    layout.append([sg.Text("{0}:".format(question))])
    layout.append([sg.Combo([question_choice for question_choice in question_choices])])
    layout.append([sg.Submit(), sg.Cancel()])
    window = sg.Window('py_answer', layout)
    event, value = window.Read()
    window.Close()
    if event == 'Cancel':
        value[0] = 'Cancel'
    return value[0]

# #########APPLICATION-CONTAINER#########

""" 
    CURRENT STRUCTURE OF HOW THIS application_container 
    (ABSTRACT DATA STRUCTURE) IS TREATED, SHOULD BE INTERFACED WITH SELECTORS ONLY
    DICTIONARIES AND STRINGS ARE THE DOMAINS OF THESE FUNCTIONS 
"""

# {'textbox' : ... --> types
#   {'functions': ... --> type_property
#     {'get_questions': ... --> sub_property of type_property
#   {'questions': ...
#     {'How many years of experience do you have in blah blah blah': ...} --> value will depend on type of question

def construct_container():
    container = dict()
    append_types(container)
    append_runtime_properties(container)
    append_app_specific_functions(container)
    return container

def append_types(container):

    """ TYPES (KNOWN TYPES) ARE QUESTION TYPES APPENDED WITH PROPERTIES """

    types = [
        "textbox",
        "radiobuttons",
        "select"
    ]

    for question_type in types:
        container[question_type] = dict()

def append_type_property(container, type_property):

    """ THIS APPENDS A TYPE_PROPERTY TO ALL TYPES (E.G. FUNCTIONS) """

    for question_type in container:
        container[question_type][type_property] = dict()

def append_sub_properties(container, property, value_container):

    """ THIS APPENDS SUB_PROPERTIES TO A TYPE's TYPE_PROPERTY """

    for question_type in container:
        property_container = container[question_type][property]
        sub_properties = list(value_container[question_type].keys())
        for sub_property in sub_properties:
            property_container[sub_property] = value_container[question_type][sub_property]

def append_runtime_properties(container):

    """ THESE ARE KNOWN PROPERTIES AT RUNTIME """

    append_type_property(container, "questions")
    append_type_property(container, "functions")

def append_app_specific_functions(container):

    """ THESE ARE SUB_PROPERTIES TO BE ADDED UNDER THE FUNCTIONS PROPERTY """

    functions = {
        "textbox":
            {"get_questions": get_textbox_questions,
             "answer_questions": answer_textbox_questions,
             "getting_choices": getting_textbox_choices,
             "print_question": display_textbox_question},
        "radiobuttons":
            {"get_questions": get_radiobuttons_questions,
             "answer_questions": answer_radiobuttons_questions,
             "getting_choices": getting_radio_choices,
             "print_question": display_radiobuttons_question},
        "select":
            {"get_questions": get_select_questions,
             "answer_questions": answer_select_questions,
             "getting_choices": getting_select_choices,
             "print_question": display_select_question}
    }

    append_sub_properties(container, "functions", value_container=functions)

def append_questions(container, questions_texts):

    """ THESE ARE SUB_PROPERTIES TO BE ADDED UNDER THE QUESTIONS PROPERTY, WILL COME FROM 'application.py' """

    append_sub_properties(container, "questions", value_container=questions_texts)

def flush_questions(container):

    """ TAKES EACH TYPE AND DELETES THEIR QUESTION TYPE_PROPERTY, ADDING A FRESH ONE INSTEAD """

    for question_type in get_question_types(container):
        application_container = container[question_type]
        del application_container["questions"]

    append_type_property(container, "questions")

# ######### SELECTORS #########

def get_question_types(container):

    """ SELECTOR FOR RETURNING QUESTION TYPES """

    return container.keys()

def get_question_type_questions(container, question_type):

    """ SELECTOR FOR RETURNING QUESTIONS OF A QUESTION TYPE """

    return container[question_type]["questions"]

def get_question_type_funcs(container, question_type):

    """ SELECTOR FOR RETURNING FUNCTIONS OF A QUESTION TYPE """

    return container[question_type]["functions"]
