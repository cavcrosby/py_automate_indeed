# ######### RUN-TIME LOGGING SETUP AND ERROR LOGGING#########

# Standard Library Imports
import logging

# Third Party Imports

# Local Application Imports

def create_general_logger(name = __name__, file_name ="errors.txt", level = logging.INFO):

    """ CURRENT WAY OF CREATING LOGGERS FOR THE PROGRAM, WILL LOG TO CONSOLE, AND FILES """

    logger = logging.getLogger(name)
    logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    file_handler1 = logging.FileHandler(r'.\scripts\logs\{0}'.format(file_name))
    formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter1)
    file_handler1.setFormatter(formatter1)
    file_handler1.setLevel(logging.ERROR)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler1)
    return logger

def create_html_logger(time, level = logging.ERROR):

    """ HTML LOGGERS ARE USED TO DOCUMENT HTML IN SINGLE FILES """

    html_logger = logging.getLogger('html_logger')
    html_handler = logging.FileHandler(r'.\scripts\logs\html\{0}.txt'.format(time))
    html_formatter = logging.Formatter('=============================================\n\n'
                                       '%(message)s\n\n'
                                       '=============================================\n')
    html_handler.setLevel(level)
    html_handler.setFormatter(html_formatter)
    html_logger.addHandler(html_handler)
    return html_logger
