# ------------------------------------ Extended Multi Management Assistant ------------------------------------------- #
import re
import time
import random
import calendar
from AccessKeep import Keep
from ManageExpenses import Expenses
from time import strftime, localtime
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException

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
    account, password, json_auth, shtkey, note, backaccount = log_info

# Commands to search
expense = re.compile(r'(?P<day>\d{2})(?P<month>\d{2});(?P<detail>[^;]*);(?P<category>[^;]*);(?P<amount>\d*.*\d*);'
                     r'(?P<currency>\w{3})', re.I | re.M)
signature = re.compile(r'(?P<place>SIG)(?P<month>\d{2});(?P<detail>[^;]*);(?P<amount>\d*.*\d*);(?P<currency>\w{3})',
                       re.I | re.M)
alive = re.compile(r'<are you alive\?>', re.I | re.M)
status = re.compile(r'<status>', re.I | re.M)
balance = re.compile(r'<balance (?P<month>1[0-2]|[1-9])>', re.I | re.M)
end = re.compile(r'<stop>', re.I | re.M)

# Google Keep Note initialization
keep = Keep(account, password, note, backaccount, verbose='yes')

# Google Sheet initialization
sheet = Expenses(shtkey, json_auth, verbose='yes')


def search_for_commands(text):

    fexpenses = expense.findall(text)
    fsignature = signature.findall(text)
    fstop = end.findall(text)
    fstatus = status.findall(text)
    falive = alive.findall(text)
    fbalance = balance.findall(text)

    return fexpenses, fsignature, fstop, fstatus, falive, fbalance


def log(msg):
    print('[{}] Emma.{}'.format(strftime("%H:%M:%S", localtime()), msg))


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
        except (InvalidElementStateException, NoSuchElementException):
            log('Couldn\'t reach note, will try on next run')

        wExpenses, wSignature, dStop, sStatus, sAlive, sBalance = search_for_commands(note)

        if wExpenses or wSignature or dStop or sStatus or sAlive or sBalance:
            log('Executing commands')

            if wExpenses:
                try:
                    sheet.add_expenses(wExpenses)
                    keep.delete_content()
                except (InvalidElementStateException, NoSuchElementException):
                    log('Couldn\'t update expenses, will try on next run')

            if wSignature:
                try:
                    sheet.add_signature(wSignature)
                    keep.delete_content()
                except (InvalidElementStateException, NoSuchElementException):
                    log('Couldn\'t update signature, will try on next run')

            if sBalance:
                balances = sheet.get_balance(sBalance)

                for i in range(len(sBalance)):
                    message.append('{}: {}'.format(calendar.month_name[int(sBalance[i])], balances[i]))

            if sStatus:
                message.append('{} runs so far. That\'s {} days, {} hours or {} minutes. Real process time {}s'
                               .format(runs, (runs*2)//1440, (runs*2)//60, runs*2, int(totTime)))

            if sAlive:
                message.append('Yes, I\'m alive! :)')

            if message:
                try:
                    keep.send_message(message)
                except(InvalidElementStateException, NoSuchElementException):
                    log('Couldn\'t send message, will try on next run')

            if dStop:
                break

        else:
            log('None found')

        finished = time.time()-start
        totTime += finished

        log('All done! Run {} took {} seconds, next scan in 120s'.format(runs, finished))
        time.sleep(120)

    goodbyes = ['Goodbye!', 'I\'ll be back', 'NOOOOoooo', 'Cya!', 'Ttyl', 'Don\'t kill me plz!']
    log(random.choice(goodbyes))
