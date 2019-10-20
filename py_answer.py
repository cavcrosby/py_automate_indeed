#######################################################################################
#
#       Author: Conner Crosby
#       Description:
#       The purpose of the code written is to interface with the database file
#       created by the py_indeed.py script. Questions that have NULL as an answer will
#       be displayed and the user will be prompted for an answer to write to the database.
#
#
#######################################################################################

""" DATABASE CURRENTLY RETURNS QUESTION [0], ANSWER (NONE)[1], QUESTION TYPE[2], AND QUESTION TYPE ANSWERS [3] """

# Standard Library Imports
import sqlite3

# Third Party Imports

# Local Application Imports
from scripts.web import display_textbox_question, display_radiobuttons_question, display_select_question, \
    construct_container, get_question_types, get_question_type_funcs

# #########CONFIGURATIONS#############################################################
# #########DATABASE CONNECTION AND QUERIES#########
connection_to_db = sqlite3.connect("questions__answers_db.db")
cursor = connection_to_db.cursor()

initial_load_query = """SELECT * FROM data WHERE answer IS NULL;"""

# #########SPECIFIC CONTAINER CREATION#########
data_container = construct_container()
#######################################################################################

def print_welcome():
    print(
        '####################################################################\n',
        "\r# Hi! This is where you will answer questions scrapped from py_indeed.py.\n",
        "\r# Close the pop-up window or click 'Cancel' when finished or want to quit.\n",
        "\r# Author: Conner Crosby\n",
        '\r####################################################################')

    input("# Press Enter To Begin...\n")

def can_query(query):

    """ THIS FUNCTION IS USED WHEN ATTEMPTING TO QUERY THE DB FILE, TO INSURE PROPER CONNECTION """

    try:
        cursor.execute(query)
        return True
    except sqlite3.OperationalError:
        return False

def display_question(question, procedure, question_choices):

    """ GENERIC FUNCTION FOR DISPLAYING A QUESTION """

    return procedure(question, question_choices)

def write_to_database(question, what_to_write):

    """ CURRENTLY THE ONLY FUNCTION USED FOR WRITING TO THE DATABASE FILE """

    parameters = {"input": what_to_write, "question": question}
    cursor.execute("""UPDATE data SET answer=:input WHERE question=:question""", parameters)
    connection_to_db.commit()

def load_into(db_row):

    """ FUNCTION USED TO LOAD THE DATA INTO THE PROGRAM """

    return db_row[0], db_row[2], db_row[3]

def quit(answer):

    """ BASED ON THE BUTTONS PRESENT IN THE FUNCTIONS, WILL DETERMINE HOW A USER CAN QUIT """

    if (answer != None and answer != 'Cancel'):
        return False
    else:
        return True

def main():

    """ MAIN PROGRAM EXECUTION """

    known_types = get_question_types(data_container)
    print_welcome()
    if (not can_query(initial_load_query)):
        print("Error! If database (db) file does not exist, then run py_indeed first...")
        print("Click Enter to quit...")
    else:
        db_rows = cursor.fetchall()
        for db_row in db_rows:
            question, question_type, question_choices = load_into(db_row)
            funcs = get_question_type_funcs(data_container, question_type)
            answer = display_question(question, funcs["print_question"], question_choices)
            if(quit(answer)):
                break
            else:
                write_to_database(question, answer)


main()
connection_to_db.close()