import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from selenium import webdriver
import time
import re
import calendar

driver = webdriver.PhantomJS()
expNote = 'https://keep.google.com/#NOTE/1445630158926.1066527822'
account = '' #Insert mail
password = '' #Insert pass
json_key = json.load(open('')) #Insert json with Key

p = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>\d*.\d*);'
               r'(?P<currency>\w{3})')


def logingoog(mail, passw):
    global sht

    print('Signing in Keep...')
    driver.get("http://keep.google.com/")
    driver.find_element_by_id('Email').send_keys(mail)
    driver.find_element_by_id('next').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="Passwd"]').send_keys(passw)
    driver.find_element_by_id('signIn').click()
    print('Done')

    print('Getting spreadheet auth...')
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    sht = gc.open_by_key('1uVvqxtRWIBN8foiBLPFNVzRog-97ZXRlX7KpNA47GlM')
    print('Done')


def getexpenses(note):
    global expenses
    driver.get(note)
    time.sleep(1)
    expenses = p.findall(driver.find_element_by_css_selector('div.VIpgJd-TUo6Hb.XKSfm-L9AdLc.eo9XGd').text)


def updatespreadsheet():
    lastmonth = ''
    prevrow = 0

    for i in range(len(expenses)):
        day = expenses[i][0]
        msheet = calendar.month_name[int(expenses[i][1])]
        detail = expenses[i][2]
        category = expenses[i][3]
        amount = expenses[i][4]
        currency = expenses[i][5]

        e = 2

        if lastmonth == msheet:
            lastrow = prevrow + 1
        else:
            while sht.worksheet(msheet).acell('B'+str(e)).value != '':
                    lastrow = e + 1
                    lastmonth = msheet
                    prevrow = lastrow
                    e += 1

        sht.worksheet(msheet).update_acell('B' + str(lastrow), day)
        sht.worksheet(msheet).update_acell('C' + str(lastrow), detail)
        sht.worksheet(msheet).update_acell('D' + str(lastrow), category)
        sht.worksheet(msheet).update_acell('E' + str(lastrow), amount)
        sht.worksheet(msheet).update_acell('F' + str(lastrow), currency.upper())

print('Connecting to resources...')
logingoog(account, password)

while True:
    start = time.time()
    print('Gettin expenses...')
    getexpenses(expNote)
    print('Updating spreadsheet...')

    if len(expenses) != 0:
        updatespreadsheet()
        print('Deleting Keep...')
        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').clear()
        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()

    print('All done! It took {} to process the expenses. Waiting 120s to check again.'. format(time.time()-start))
    time.sleep(30)
