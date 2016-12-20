# ------------------------------------ Extended Multi Management Assistant ------------------------------------------- #
# ------------------------------------                Main                 ------------------------------------------- #
import re
import time
import calendar
from datetime import datetime
from time import strftime, localtime

from Messenger import EvernoteManager
from Accountant import SpreadsheetManager, PostgreDBManager

'''
You can either fill each of the next variables manually or create a simple .cfg with the data of each variable in the
order they are declared. Ignore the lines between //
/-------setting.cfg---------/
Account
Password
Json File Name
Sheet Key
Evernote Token
DB
/---------------------------/
'''


def log(msg):
    """
    Displays message on console providing some context.
    :param msg: Message to print in log.
    :return:
    """
    print('[{}] Emma: {}'.format(strftime("%H:%M:%S", localtime()), msg))


log('Booting up Emma.')

# Config File
log('Loading settings.')
with open('settings.cfg', 'r') as f:
    log_info = f.read().splitlines()
    account, password, json_auth, shtkey, evernote_token, db = log_info

# Commands to search
log('Compiling Regex.')
expense = re.compile(
    r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);'
    r'(?P<amount>[^;]*);(?P<currency>\bARS|\bEUR|\bUSD);'
    r'(?P<method>\bEFVO|\bMASTER|\bVISA|\bDEBITO)(?P<paymts>\d{2})?',
    re.I | re.M)
status = re.compile(r'/status', re.I | re.M)
balance = re.compile(r'/balance (?P<month>1[0-2]|[1-9])', re.I | re.M)
end = re.compile(r'/stop', re.I | re.M)
cur = re.compile(r'/usd|/eur', re.I | re.M)
pay = re.compile(r'/payed (?P<entity>\bMASTER|\bVISA)', re.I | re.M)

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
processed = False


def search_for_commands(text):
    """
    Searches a string of text for certain command patterns using the compiled regex.
    :param text: String to check for commands.
    :return fexpenses: Returns a list of lists containing all fields of the expenses command.
    :return fstop: Returns a list of lists containing all fields of the stop command.
    :return fstatus: Returns a list of lists containing all fields of the status command.
    :return fbalance: Returns a list of lists containing all fields of the balance command.
    :return fcur: Returns a list of lists containing all fields of the currency command.
    :return fpay: Returns a list of lists containing all fields of the CC payment command.
    """
    fexpenses = expense.findall(text)
    fstop = end.findall(text)
    fstatus = status.findall(text)
    fbalance = balance.findall(text)
    fcur = cur.findall(text)
    fpay = pay.findall(text)

    return fexpenses, fstop, fstatus, fbalance, fcur, fpay


def display_time(seconds, granularity=2):
    """
    Converts seconds to higher values depending on the granularity.
    :param seconds: Seconds to convert.
    :param granularity: Rounds up the value to the higher unit the closer it is to zero.
    :return: Returns the converted value.
    """
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

        wExpenses, dStop, sStatus, sBalance, sCur, wPay = search_for_commands(note)

        if wExpenses or dStop or sStatus or sBalance or sCur or wPay:

            log('Executing commands')

            if wExpenses or sBalance or sCur or wPay:
                spreadsheet = sheet.log_in_sheets('A')
                correct = True

                if wExpenses:
                    # TODO Check if last ID is the same in both the DB and Spreadsheet. When not; equalize.

                    correct, id_exp = postgre_db.add_expenses(wExpenses)

                    if correct:
                        sheet.add_expenses(id_exp, ['B', 'C', 'D', 'E', 'F', 'G', 'I'], spreadsheet)
                    else:
                        log('Something is wrong in transaction.')

                    if correct:
                        evernote.delete_content(note_store, full_note)

                if sBalance:
                    balances = sheet.get_balance(sBalance, spreadsheet, 45)

                    for month, bal in enumerate(balances):
                        message.append('{}: {}'.format(calendar.month_name[int(sBalance[month])], bal))

                if sCur:
                    values = sheet.get_currency(sCur, spreadsheet, (5, 17), (6, 17))

                    for currency, value in enumerate(values):
                        message.append('{}: {}'.format(sCur[currency], value))

                if wPay:
                    postgre_db.lock_cur_value(wPay)
                    sheet.lock_cur_value(wPay, 7, 8, 9, spreadsheet)

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

    log('Shutting down. Goodbye!')
