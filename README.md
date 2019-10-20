# py_automate_indeed

***THIS APPLICATION IS NOT LONGER BEING SUPPORTED BY MY EFFORTS***

# Brief

**py_automate_indeed** is a python application/scripts to automate the process of applying to a job on https://www.indeed.com/ using an Indeed resume.

## Disclaimer 1

Please read the ToS from https://www.indeed.com/legal, as Indeed prohibits the use of 'automated' software to scrape their website. If you do use my application, I am not liable for any consequences you may face.

## Disclaimer 2

The script has never been tested to apply for jobs. Hence it is unfinished, but the current state of the program is very close to doing just that (as to why I do not wish to finish the program, see disclaimer 1).

## Description

**py_indeed.py** is the script that does majority of the work. It is currently configured to use a headless browser to:
 * Login in to Indeed
 * Iterate over each page pulling jobs to apply for
 * Parse for jobs that can be applied for using an Indeed Resume
 * Attempts to apply to each job
  - Each job could have supplement questions, the questions that the script cannot answer are stored into a database file
 * Continues to until the end of the page, goes to the next page and repeats

**py_answer.py** is the script to use for interfacing with questions pulled from py_indeed.

## Usage

py_indeed and py_answer can both be ran the same way.

```python
python py_indeed.py
```

```python
python py_answer.py
```

For debugging purpose, check the directory ..\py_automate_indeed\scripts\logs. This is where error messages are dumped.

## Installation

***(Main pre-requisite: Python 3)***

1. First, download the application as a zip file or clone the repo.

2. From there use pip to install the requirements needed for the application.

```python
pip install -r requirements.txt
```

3. Also edit the app.ini and add values for the fields 'email_address', 'password', 'job_title', and 'location'. **This data is necessary or else py_indeed will not work.**
- These are needed to sign in into your indeed account, and to search for the job title you desire in the location.

4. The application will need a Chrome driver to work with. Visit https://docs.seleniumhq.org/download/ and download a chrome driver. For reference, testing has been done with the Chrome driver version 76.0.3809.68. Get the executable and put it into the directory of the application.

5. Finally, install Google chrome https://www.google.com/chrome/.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.