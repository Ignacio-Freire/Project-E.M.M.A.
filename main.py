import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from selenium import webdriver
import time
import re
import calendar

# Fill with Keep note, remember to share it with the bot email
expNote = 'https://keep.google.com/#NOTE/1445630158926.1066527822'
# Fill with mail
account = ''
# Fill with pass
password = ''
# Fill w/ json with Key
json_key = json.load(open(''))
# Fill with sheet key, remember to share it with the json email
shtkey = '1TH_jKk4Qhn2gVsx7QMTzxE4JHPILKzqIMZLEyocnc5c'

p = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>\d*.\d*);'
               r'(?P<currency>\w{3})')


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

    driver.get(note)
    time.sleep(5)
    expenses = p.findall(driver.find_element_by_css_selector('div.VIpgJd-TUo6Hb.XKSfm-L9AdLc.eo9XGd').text)
    time.sleep(5)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()


def update_spreadsheet():

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


# This has to be seriously optimized, do I really have to relog to delete the content?
def delete_keep():

    driver.close()
    log_in_goog(account, password)
    time.sleep(5)
    driver.get(expNote)
    time.sleep(5)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').clear()
    time.sleep(5)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()


print('Connecting to resources...')

print('Signing in Keep...')
log_in_goog(account, password)
print('Done')

print('Getting spreadheet auth...')
log_in_sheets(shtkey)
print('Done')

while True:
    start = time.time()
    print('Gettin expenses...')
    get_expenses(expNote)

    if len(expenses) != 0:
        print('Updating spreadsheet...')
        update_spreadsheet()
        print('Deleting Keep...')
        delete_keep()
    else:
        print('Nothing there.')

    print('All done! It took {} to process the expenses. Waiting 120s to check again.'. format(time.time()-start))

    # This is to keep the spreadsheet connection alive while waiting, otherwise it times out.
    for i in range(12):
        sht.worksheet('January').acell('A1')
        time.sleep(10)
