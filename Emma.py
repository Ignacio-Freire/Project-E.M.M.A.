# ------------------------------------ Extended Multi Management Assistant ------------------------------------------- #
import re
import time
import random
import calendar
from Chef import MealPrep
from Accountant import Expenses
from Messenger import GoogleKeep
from Messenger import Evernote
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


def log(msg):
    print('[{}] Emma: {}'.format(strftime("%H:%M:%S", localtime()), msg))


# Config File
log('Loading settings.')
with open('settings.cfg', 'r') as f:
    log_info = f.read().splitlines()
    account, password, json_auth, shtkey, note, backaccount, grocery_note, recipes_note, evernote_token, db = log_info

# Commands to search
log('Compiling Regex.')
expense = re.compile(
    r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>[^;]*);(?P<currency>\w{3});(?P<method>\bEFVO|\bMASTER|\bVISA|\bDEBITO)',
    re.I | re.M)
signature = re.compile(
    r'(?P<place>SIG)(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>[^;]*);(?P<currency>\w{3})',
    re.I | re.M)
alive = re.compile(r'/are you alive\?', re.I | re.M)
status = re.compile(r'/status', re.I | re.M)
balance = re.compile(r'/balance (?P<month>1[0-2]|[1-9])', re.I | re.M)
end = re.compile(r'/stop', re.I | re.M)
mls = re.compile(r'/meals (?P<meals>\d*)', re.I | re.M)
cur = re.compile(r'/usd|/eur', re.I | re.M)
sig = re.compile(r'/sig (?P<month>1[0-2]|[1-9])', re.I | re.M)

# Google Keep Note initialization
log('Creating Messenger objects.')
chromedriver = "/home/Projects/Project-E.M.M.A./chromedriver"
phantomjs = "/home/Projects/Project-E.M.M.A./phantomjs"
keep = GoogleKeep(account, password, note, backaccount, verbose='yes')
grocery = GoogleKeep(account, password, grocery_note, backaccount, verbose='yes')
recipes = GoogleKeep(account, password, recipes_note, backaccount, verbose='yes')

# Evernote initialization
evernote = Evernote(evernote_token, 'Emma', verbose='yes')

# Meal Prep initialization
log('Creating Chef object.')
meals = MealPrep(verbose='yes')

# Google Sheet initialization
log('Initializing spreadsheet.')
sheet = Expenses(shtkey, json_auth, db, verbose='yes')


def search_for_commands(text):

    fexpenses = expense.findall(text)
    fsignature = signature.findall(text)
    fstop = end.findall(text)
    fstatus = status.findall(text)
    falive = alive.findall(text)
    fbalance = balance.findall(text)
    fmeals = mls.findall(text)
    fcur = cur.findall(text)
    fsig = sig.findall(text)

    return fexpenses, fsignature, fstop, fstatus, falive, fbalance, fmeals, fcur, fsig


def delete_note(driv):
    try:
        keep.delete_content(logged='YES', driver=driv)
    except ElementNotFound:
        log('Couldn\'t delete note, will try on next run')


if __name__ == '__main__':

    runs = 0
    totTime = 0
    log('Initializing Emma.')
    frequency = 120

    while True:

        start = time.time()
        runs += 1
        message = []

        if runs == 1:
            log('Hi, I\'m ready to go!')

        log('Checking for commands')

        '''
        try:
            note, driver = keep.read_note(cont='YES')
        except ElementNotFound:
            log('Couldn\'t reach note, will try on next run')
        '''

        try:
            note_store, full_note, note = evernote.get_content()
        except:
            log('Couldn\'t reach note, will try on next run')
            note = ''

        wExpenses, wSignature, dStop, sStatus, sAlive, sBalance, sMeals, sCur, sSig = search_for_commands(note)

        if wExpenses or wSignature or dStop or sStatus or sAlive or sBalance or sMeals or sCur or sSig:
            log('Executing commands')

            if wExpenses or wSignature:
                correct = True

                if wExpenses:
                    correct = sheet.add_db(wExpenses)
                    if correct:
                        sheet.add_expenses(wExpenses, ['B', 'C', 'D', 'E', 'F', 'G'])
                    else:
                        log('Something is wrong in transaction.')

                if wSignature:
                    sheet.add_expenses(wSignature, ['I', 'J', 'K'])

                # delete_note(driver)
                if correct:
                    evernote.delete_content(note_store, full_note)

            if sBalance:
                balances = sheet.get_balance(sBalance)

                for month, bal in enumerate(balances):
                    message.append('{}: {}'.format(calendar.month_name[int(sBalance[month])], bal))

            if sCur:
                values = sheet.get_currency(sCur)

                for currency, value in enumerate(values):
                    message.append('{}: {}'.format(sCur[currency], value))

            if sSig:
                remaining = sheet.get_sig_remaining(sSig)

                for month, rem in enumerate(remaining):
                    message.append('Remaining in {}: ${}'.format(calendar.month_name[int(sSig[month])], rem))

            if sMeals:
                all_recipes = meals.create_recipes(int(sMeals[0]))
                grocery_list = meals.grocery_list(all_recipes)

                try:
                    recipes.send_message(all_recipes)
                    grocery.send_message(grocery_list)
                    time.sleep(10)
                    # delete_note(driver)
                    evernote.delete_content(note_store, full_note)
                    all_recipes = []
                    grocery_list = []
                except ElementNotFound:
                    log('Couldn\'t send meals, will try on next run')
                    continue

            if sStatus:
                message.append('{} runs so far. That\'s {} days, {} hours or {} minutes. Real process time {}s'
                               .format(runs, int((((runs * 2) / 60) + totTime / 3600) / 24),
                                       int(((runs * 2) / 60) + totTime / 3600),
                                       int(runs * 2 + totTime / 60), int(totTime)))

            if sAlive:
                message.append('Yes, I\'m alive! :)')

            if message:
                '''
                try:
                    keep.send_message(message, logged='YES', driver=driver)
                except ElementNotFound:
                    log('Couldn\'t send message, will try on next run')
                    continue
                '''

                evernote.send_message(message, note_store, full_note)

            if dStop:
                break

        else:
            log('None found')
            # keep.close_driver(driver)

        finished = time.time() - start
        totTime += finished

        log('All done! Run {} took {:.2f} seconds, next scan in {}s'.format(runs, finished, frequency))
        time.sleep(frequency)

    goodbyes = ['Goodbye!', 'I\'ll be back', 'NOOOOoooo', 'Cya!', 'Ttyl', 'Don\'t kill me plz!',
                'Cyka blyat, don\'t do it', 'Peace out', '*Drops mic*']
    log(random.choice(goodbyes))

