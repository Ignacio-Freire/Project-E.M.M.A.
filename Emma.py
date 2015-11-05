# ------------------------------------- Expense Management Mad Assistant --------------------------------------------- #
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from selenium import webdriver
import time
from time import strftime, localtime
from selenium.common.exceptions import NoSuchElementException
import re
import calendar


'''
You can either fill each of the next variables manually or create a simple .cfg with the data of each variable in the
order they are declared.
-------setting.cfg---------
Account
Password
Json Key
Sheet Key
Keep Note link
'''

with open('settings.cfg', 'r') as f:
    log_info = f.readlines()

account = log_info[0].strip()
password = log_info[1].strip()
json_key = json.load(open(log_info[2].strip()))
shtkey = log_info[3].strip()
expNote = log_info[4].strip()

# This has to be customized depending on the spreadsheet
exp = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>\d*.*\d*);'
                 r'(?P<currency>\w{3})', re.I | re.M)

sig = re.compile(r'(?P<place>SIG)(?P<month>\d{2});(?P<detail>[^;]*);(?P<amount>\d*.*\d*);(?P<currency>\w{3})',
                 re.I | re.M)
end = re.compile(r'<stop>', re.I | re.M)
rstatus = re.compile(r'<are you alive\?>', re.I | re.M)
stat = re.compile(r'<status>', re.I | re.M)


def log_in_goog(mail, passw):

    drive = webdriver.PhantomJS()
    drive.get("http://keep.google.com/")
    drive.find_element_by_id('Email').send_keys(mail)
    drive.find_element_by_id('next').click()
    time.sleep(1)
    drive.find_element_by_xpath('//*[@id="Passwd"]').send_keys(passw)
    drive.find_element_by_id('signIn').click()
    time.sleep(1)
    drive.get(expNote)
    time.sleep(1)

    return drive


def log_in_sheets(key):

    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    sht = gc.open_by_key(key)

    return sht


# Check for commands and expenses
def read_note():

    driver = log_in_goog(account, password)
    fexpenses, fvexpenses, fstop, fstatus, fstats = [], [], [], [], []

    try:
        note = driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').text
        time.sleep(1)
        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()
        fexpenses = exp.findall(note)
        fvexpenses = sig.findall(note)
        fstop = end.findall(note)
        fstatus = rstatus.findall(note)
        fstats = stat.findall(note)
    except NoSuchElementException:
        print('{} Can\'t find element, will relog and try on next run.'.format(timestamp()))

    driver.quit()

    return fexpenses, fvexpenses, fstop, fstatus, fstats


# This has to be customized depending on the spreadsheet.
def update_spreadsheet():

        if len(expenses) != 0:
            for data in expenses:
                day = data[0]
                msheet = calendar.month_name[int(data[1])]
                detail = data[2]
                category = data[3]
                amount = data[4]
                currency = data[5]

                lastrow = len(sheet.worksheet(msheet).col_values(2)) + 1

                col = ['B', 'C', 'D', 'E', 'F']
                colnm = [day, detail.title(), category.title(), amount, currency.upper()]

                for j in range(len(col)):
                        sheet.worksheet(msheet).update_acell(col[j] + str(lastrow), colnm[j])

        if len(vexpenses) != 0:
            for e in vexpenses:
                msheet = calendar.month_name[int(e[1])]
                detail = e[2]
                amount = e[3]
                currency = e[4]

                lastrow = len(sheet.worksheet(msheet).col_values(9)) + 1

                col = ['I', 'J', 'K']
                colnm = [detail.title(), amount, currency.upper()]

                for j in range(len(col)):
                        sheet.worksheet(msheet).update_acell(col[j] + str(lastrow), colnm[j])


# Erases the content of the note.
def delete_keep():
    driver = log_in_goog(account, password)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').clear()
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()
    time.sleep(1)
    driver.quit()


# Writes a message on the note.
def send_message(message):
    driver = log_in_goog(account, password)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]')\
        .send_keys(message)
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()
    time.sleep(1)
    driver.quit()


# Returns current time.
def timestamp():
    return '[{}]'.format(strftime("%H:%M:%S", localtime()))

if __name__ == '__main__':

    runs = 0

    while True:

        start = time.time()
        runs += 1

        print('{} Logging into Keep...'.format(timestamp()))
        print('{} Getting expenses...'.format(timestamp()))
        expenses, vexpenses, stop, status, stats = read_note()

        if len(expenses) + len(vexpenses) != 0:
            print('{} Getting spreadheet auth...'.format(timestamp()))
            sheet = log_in_sheets(shtkey)
            print('{} Updating spreadsheet...'.format(timestamp()))
            update_spreadsheet()
            print('{} Deleting Keep...'.format(timestamp()))
            delete_keep()
        else:
            print('{} No expenses found'.format(timestamp()))

        if len(status) != 0:
            print('{} Sending status...'.format(timestamp()))
            delete_keep()
            send_message('Yes! I\'m alive :)')

        if len(stats) != 0:
            print('{} Sending stats...'.format(timestamp()))
            delete_keep()
            send_message('{} runs so far. That\'s {} hours or {} minutes.'
                         .format(runs, (runs*2)//60, runs*2))

        if len(stop) != 0:
            break
        else:
            print('{} All done! Run {} took {} seconds. Next scan in 120s.'
                  .format(timestamp(), runs, time.time()-start))
            time.sleep(120)

    print('{} Goodbye!'.format(timestamp()))
