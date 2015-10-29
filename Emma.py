import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from selenium import webdriver
import time
import re
import calendar

# Fill with Keep note, remember to share it with the bot email
expNote = 'https://keep.google.com/#NOTE/1445630158926.1066527822'
# Fill with mail, remember to wipe before push
account = ''
# Fill with pass, remember to wipe before push
password = ''
# Fill w/ json with Key, remember to wipe before push
json_key = json.load(open(''))
# Fill with sheet key, remember to share it with the json email
shtkey = '1TH_jKk4Qhn2gVsx7QMTzxE4JHPILKzqIMZLEyocnc5c'

# This has to be customized depending on the spreadsheet
p = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>\d*.\d*);'
               r'(?P<currency>\w{3})', re.I | re.M)

z = re.compile(r'(?P<place>SIG)(?P<month>\d{2});(?P<detail>[^;]*);(?P<amount>\d*.\d*);(?P<currency>\w{3})', re.I | re.M)


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

    driver.get(note)
    time.sleep(1)
    expenses = p.findall(driver.find_element_by_css_selector('div.VIpgJd-TUo6Hb.XKSfm-L9AdLc.eo9XGd').text)
    vexpenses = z.findall(driver.find_element_by_css_selector('div.VIpgJd-TUo6Hb.XKSfm-L9AdLc.eo9XGd').text)
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()


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

    driver.close()
    log_in_goog(account, password)
    time.sleep(1)
    driver.get(expNote)
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').clear()
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()


if __name__ == '__main__':

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

        if len(expenses) + len(vexpenses) != 0:
            print('Updating spreadsheet...')
            update_spreadsheet()
            print('Deleting Keep...')
            delete_keep()
        else:
            print('Nothing there.')

        print('All done! It took {} to process the expenses. Waiting 120s to check again.'. format(time.time()-start))

        # This is to keep the spreadsheet connection alive while waiting, otherwise it times out.
        for i in range(12):
            try:
                sht.sheet1.acell('A1')
                time.sleep(10)
            except NameError:
                print('Minor error while waiting, can\'t be ignored if happens more than three times.')
                time.sleep(10)
