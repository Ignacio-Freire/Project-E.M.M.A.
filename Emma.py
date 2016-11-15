# ------------------------------------ Extended Multi Management Assistant ------------------------------------------- #
import re
import time
import random
import calendar
from time import strftime, localtime

from Accountant import SpreadsheetManager, PostgreDBManager
from Messenger import EvernoteManager

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

log('Booting up Emma.')

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
status = re.compile(r'/status', re.I | re.M)
balance = re.compile(r'/balance (?P<month>1[0-2]|[1-9])', re.I | re.M)
end = re.compile(r'/stop', re.I | re.M)
cur = re.compile(r'/usd|/eur', re.I | re.M)

# Evernote initialization
log('Initializing Evernote Manager.')
evernote = EvernoteManager(evernote_token, 'Emma', verbose='yes')

# DB initialization
log('Initializing DB Manager.')
postgre_db = PostgreDBManager(db, verbose='yes')

# Google Sheet initialization
log('Initializing Spreadsheet Manager.')
sheet = SpreadsheetManager(shtkey, json_auth, verbose='yes')

# Initializing variables
log('Initializing variables.')
runs = 0
totTime = 0
FREQUENCY = 120


def search_for_commands(text):
    fexpenses = expense.findall(text)
    fstop = end.findall(text)
    fstatus = status.findall(text)
    fbalance = balance.findall(text)
    fcur = cur.findall(text)

    return fexpenses, fstop, fstatus, fbalance, fcur


def display_time(seconds, granularity=2):
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )

    result = []

    for name, count in intervals:
        t_value = seconds // count
        if t_value:
            seconds -= t_value * count
            if t_value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(t_value, name))
    return ', '.join(result[:granularity])


log('Hi, I\'m ready to go!')

if __name__ == '__main__':

    while True:

        start = time.time()
        runs += 1
        message = []

        log('Checking for commands')

        try:
            note_store, full_note, note = evernote.get_content()
        except:
            log('Couldn\'t reach note, will try on next run')
            note = ''

        wExpenses, dStop, sStatus, sBalance, sCur = search_for_commands(note)

        if wExpenses or dStop or sStatus or sBalance or sCur:

            spreadsheet = sheet.log_in_sheets()

            log('Executing commands')

            if wExpenses:
                correct = True

                if wExpenses:
                    correct = postgre_db.add_expenses(wExpenses)
                    if correct:
                        sheet.add_expenses(wExpenses, ['B', 'C', 'D', 'E', 'F', 'G'], spreadsheet)
                    else:
                        log('Something is wrong in transaction.')

                if correct:
                    evernote.delete_content(note_store, full_note)

            if sBalance:
                balances = sheet.get_balance(sBalance, spreadsheet)

                for month, bal in enumerate(balances):
                    message.append('{}: {}'.format(calendar.month_name[int(sBalance[month])], bal))

            if sCur:
                values = sheet.get_currency(sCur, spreadsheet)

                for currency, value in enumerate(values):
                    message.append('{}: {}'.format(sCur[currency], value))

            if sStatus:
                message.append('{} runs so far. That\'s {}.'
                               .format(runs, display_time(totTime, granularity=5)))

            if message:
                evernote.send_message(message, note_store, full_note)

            if dStop:
                break

        else:
            log('None found')

        finished = time.time() - start
        totTime += finished

        log('All done! Run {} took {:.2f} seconds, next scan in {}s'.format(runs, finished, FREQUENCY))
        time.sleep(FREQUENCY)

    goodbyes = ['Goodbye!', 'I\'ll be back', 'NOOOOoooo', 'Cya!', 'Ttyl', 'Don\'t kill me plz!',
                'Cyka blyat, don\'t do it', 'Peace out', '*Drops mic*']
    log(random.choice(goodbyes))
