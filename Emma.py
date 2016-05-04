# ------------------------------------ Extended Multi Management Assistant ------------------------------------------- #
import re
import time
import random
import calendar
from Messenger import GoogleKeep
from Chef import MealPrep
from Accountant import Expenses
from time import strftime, localtime
from Messenger import ElementNotFound

'''
You can either fill each of the next variables manually or create a simple .cfg with the data of each variable in the
order they are declared. Ignore the lines between //
/-------setting.cfg---------/
Account
Password
Json File Name
Sheet Key
Keep Note link
Alternative mail configured for the account
/---------------------------/
'''

# Config File
with open('settings.cfg', 'r') as f:
    log_info = f.read().splitlines()
    account, password, json_auth, shtkey, note, backaccount, grocery_note, recipes_note = log_info

# Commands to search
expense = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>\d*.*\d*);'
                     r'(?P<currency>\w{3})', re.I | re.M)
signature = re.compile(r'(?P<place>SIG)(?P<month>\d{2});(?P<detail>[^;]*);(?P<amount>\d*.*\d*);(?P<currency>\w{3})',
                       re.I | re.M)
alive = re.compile(r'<are you alive\?>', re.I | re.M)
status = re.compile(r'<status>', re.I | re.M)
balance = re.compile(r'<balance (?P<month>1[0-2]|[1-9])>', re.I | re.M)
end = re.compile(r'<stop>', re.I | re.M)
mls = re.compile(r'<meals (?P<meals>\d*)>', re.I | re.M)

# Google Keep Note initialization
chromedriver = "C:\\Users\Tkwk\Documents\PyCharm Projects\Project-E.M.M.A\chromedriver.exe"
keep = GoogleKeep(account, password, note, backaccount, chromedriver, verbose='yes')
grocery = GoogleKeep(account, password, grocery_note, backaccount, chromedriver, verbose='yes')
recipes = GoogleKeep(account, password, recipes_note, backaccount, chromedriver, verbose='yes')

# Google Sheet initialization
sheet = Expenses(shtkey, json_auth, verbose='yes')

# Meal Prep initialization
meals = MealPrep(verbose='yes')


def search_for_commands(text):
    fexpenses = expense.findall(text)
    fsignature = signature.findall(text)
    fstop = end.findall(text)
    fstatus = status.findall(text)
    falive = alive.findall(text)
    fbalance = balance.findall(text)
    fmeals = mls.findall(text)

    return fexpenses, fsignature, fstop, fstatus, falive, fbalance, fmeals


def log(msg):
    print('[{}] Emma.{}'.format(strftime("%H:%M:%S", localtime()), msg))


def delete_note():
    try:
        keep.delete_content()
    except ElementNotFound:
        log('Couldn\'t delete note, will try on next run')


if __name__ == '__main__':

    runs = 0
    totTime = 0

    while True:

        start = time.time()
        runs += 1
        message = []

        log('Checking for commands')

        try:
            note = keep.read_note()
        except ElementNotFound:
            log('Couldn\'t reach note, will try on next run')

        wExpenses, wSignature, dStop, sStatus, sAlive, sBalance, sMeals = search_for_commands(note)

        if wExpenses or wSignature or dStop or sStatus or sAlive or sBalance or sMeals:
            log('Executing commands')

            if wExpenses or wSignature:

                if wExpenses:
                    sheet.add_expenses(wExpenses, ['B', 'C', 'D', 'E', 'F'])

                if wSignature:
                    sheet.add_expenses(wSignature, ['I', 'J', 'K'])

                delete_note()

            if sBalance:
                balances = sheet.get_balance(sBalance)

                for i in range(len(sBalance)):
                    message.append('{}: {}'.format(calendar.month_name[int(sBalance[i])], balances[i]))

            if sStatus:
                message.append('{} runs so far. That\'s {} days, {} hours or {} minutes. Real process time {}s'
                               .format(runs, int((((runs * 2) / 60) + totTime / 3600) / 24),
                                       int(((runs * 2) / 60) + totTime / 3600),
                                       int(runs * 2 + totTime / 60), int(totTime)))

            if sAlive:
                message.append('Yes, I\'m alive! :)')

            if sMeals or all_recipes or grocery_list:
                all_recipes = meals.create_recipes(int(sMeals[0]))
                grocery_list = meals.grocery_list(all_recipes)

                try:
                    recipes.send_message(all_recipes)
                    grocery.send_message(grocery_list)
                    time.sleep(10)
                    keep.delete_content()
                    all_recipes = []
                    grocery_list = []
                except ElementNotFound:
                    log('Couldn\'t send meals, will try on next run')
                    continue

            if message:
                try:
                    keep.send_message(message)
                except ElementNotFound:
                    log('Couldn\'t send message, will try on next run')
                    continue

            if dStop:
                break

        else:
            log('None found')

        finished = time.time() - start
        totTime += finished

        log('All done! Run {} took {:.2f} seconds, next scan in 120s'.format(runs, finished))
        time.sleep(120)

    goodbyes = ['Goodbye!', 'I\'ll be back', 'NOOOOoooo', 'Cya!', 'Ttyl', 'Don\'t kill me plz!']
    log(random.choice(goodbyes))
