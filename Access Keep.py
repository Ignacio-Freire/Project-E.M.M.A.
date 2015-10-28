from selenium import webdriver
import time
import re
import calendar

driver = webdriver.PhantomJS()
expNote = 'https://keep.google.com/#NOTE/1445630158926.1066527822'
mail = 'TheProjectEmma'
passw = ''

p = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]{0,});(?P<category>[^;]{0,});(?P<amount>\d*.\d*);'
                   r'(?P<currency>\w{3})')

def logInGoog(mail, passw):
    driver.get("http://keep.google.com/")
    driver.find_element_by_id('Email').send_keys(mail)
    driver.find_element_by_id('next').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="Passwd"]').send_keys(passw)
    driver.find_element_by_id('signIn').click()


def getExpenses(note):
    global expenses
    driver.get(note)
    expenses = p.findall(driver.find_element_by_css_selector('div.VIpgJd-TUo6Hb.XKSfm-L9AdLc.eo9XGd').text)

print('Logging in...')
log = time.time()
logInGoog(mail, passw)
logged = time.time() - log

print('Getting Expenses...')
get = time.time()
getExpenses(expNote)
got = time.time()-get

print('Processing expenses...')
process = time.time()
for i in range(len(expenses)):
    day      = expenses[i][0]
    month    = expenses[i][1]
    detail   = expenses[i][2]
    category = expenses[i][3]
    amount   = expenses[i][4]
    currency = expenses[i][5]
    print('You spent {} {} on the {} of {} in {} which enters in the category {}.'.format(amount, currency, day,
                                                               calendar.month_name[int(month)], detail, category))
processed = time.time() - process

print('It took {} for the whole thing but just {} to get the expenses. To process the expenses it took {}.'
                                                                       .format(logged + got, got, processed))
