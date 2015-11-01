# ----------------------------- Project Expense Management Mad Assistant --------------------------------------------- #
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from selenium import webdriver
import time
from time import strftime, localtime
from selenium.common.exceptions import NoSuchElementException
import re
import calendar


with open('settings.cfg', 'r') as f:
    log_info = f.readlines()

# Fill with Keep note, remember to share it with the bot email
expNote = 'https://keep.google.com/#NOTE/1445630158926.1066527822'
account = log_info[0].strip()
password = log_info[1].strip()
json_key = json.load(open(log_info[2].strip()))
# Fill with sheet key, remember to share it with the json email
shtkey = '1TH_jKk4Qhn2gVsx7QMTzxE4JHPILKzqIMZLEyocnc5c'

# This has to be customized depending on the spreadsheet
p = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>\d*.*\d*);'
               r'(?P<currency>\w{3})', re.I | re.M)

z = re.compile(r'(?P<place>SIG)(?P<month>\d{2});(?P<detail>[^;]*);(?P<amount>\d*.*\d*);(?P<currency>\w{3})',
               re.I | re.M)
s = re.compile(r'<stop>', re.I | re.M)


def log_in_goog(mail, passw):

    global driver

    driver = webdriver.PhantomJS()
    driver.get("http://keep.google.com/")
    driver.find_element_by_id('Email').send_keys(mail)
    driver.find_element_by_id('next').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="Passwd"]').send_keys(passw)
    driver.find_element_by_id('signIn').click()


def log_in_sheets(key):

    global sht

    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    sht = gc.open_by_key(key)


def get_expenses(note):

    global expenses
    global vexpenses
    global stop

    expenses = []
    vexpenses = []
    stop = []

    driver.get(note)
    time.sleep(1)

    try:
        expenses = p.findall(driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').text)
        vexpenses = z.findall(driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').text)
        stop = s.findall(driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').text)
        time.sleep(1)
        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()
    except NoSuchElementException:
        print('[{}] Can\'t find element, will relog and try on next run.'.format(strftime("%H:%M:%S", localtime())))
        driver.quit()
        log_in_goog(account, password)


# This has to be customized depending on the spreadsheet, not sure if it what's inside can be done in just one function
def update_spreadsheet():

        if len(expenses) != 0:
            for e in range(len(expenses)):
                day = expenses[e][0]
                msheet = calendar.month_name[int(expenses[e][1])]
                detail = expenses[e][2]
                category = expenses[e][3]
                amount = expenses[e][4]
                currency = expenses[e][5]

                lastrow = len(sht.worksheet(msheet).col_values(2)) + 1

                col = ['B', 'C', 'D', 'E', 'F']
                colnm = [day, detail.title(), category.title(), amount, currency.upper()]

                for j in range(len(col)):
                        sht.worksheet(msheet).update_acell(col[j] + str(lastrow), colnm[j])

        if len(vexpenses) != 0:
            for e in range(len(vexpenses)):
                msheet = calendar.month_name[int(vexpenses[e][1])]
                detail = vexpenses[e][2]
                amount = vexpenses[e][3]
                currency = vexpenses[e][4]

                lastrow = len(sht.worksheet(msheet).col_values(9)) + 1

                col = ['I', 'J', 'K']
                colnm = [detail.title(), amount, currency.upper()]

                for j in range(len(col)):
                        sht.worksheet(msheet).update_acell(col[j] + str(lastrow), colnm[j])


# This has to be seriously optimized, do I really have to relog to delete the content?
def delete_keep():

    driver.quit()
    log_in_goog(account, password)
    time.sleep(1)
    driver.get(expNote)
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').clear()
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()
    time.sleep(1)


if __name__ == '__main__':

    runs = 0
    go = 'Y'

    print('[{}] Signing in Google Keep...'.format(strftime("%H:%M:%S", localtime())))
    log_in_goog(account, password)
    print('[{}] Done'.format(strftime("%H:%M:%S", localtime())))

    print('[{}] Getting spreadheet auth...'.format(strftime("%H:%M:%S", localtime())))
    log_in_sheets(shtkey)
    print('[{}] Done'.format(strftime("%H:%M:%S", localtime())))

    while go == 'Y':

        start = time.time()
        print('[{}] Getting expenses...'.format(strftime("%H:%M:%S", localtime())))
        get_expenses(expNote)

        if len(expenses) + len(vexpenses) != 0:
            print('[{}] Updating spreadsheet...'.format(strftime("%H:%M:%S", localtime())))
            update_spreadsheet()
            print('[{}] Deleting Keep...'.format(strftime("%H:%M:%S", localtime())))
            delete_keep()
        else:
            print('[{}] Nothing there.'.format(strftime("%H:%M:%S", localtime())))

        runs += 1

# This is to keep the spreadsheet connection alive while waiting, otherwise it times out.
        if runs % 20 == 0:
            print('[{}] Relogging to keep connections alive...'.format(strftime("%H:%M:%S", localtime())))
            driver.quit()
            log_in_goog(account, password)
            log_in_sheets(shtkey)
            print('[{}] Done...'.format(strftime("%H:%M:%S", localtime())))

        if len(stop) != 0:
            break
        else:
            print('[{}] All done! Run {} took {} seconds. Next scan in 120s.'
                  .format(strftime("%H:%M:%S", localtime()), runs, time.time()-start))
            time.sleep(120)

    print('[{}] Goodbye!'.format(strftime("%H:%M:%S", localtime())))
