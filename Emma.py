# ------------------------------------ Extended Multi Management Assistant ------------------------------------------- #
import re
import json
import time
from time import strftime, localtime
from AccessKeep import Keep
from ManageExpenses import Expenses
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
    log_info = f.readlines()

account = log_info[0].strip()
password = log_info[1].strip()
shtkey = log_info[3].strip()
note = log_info[4].strip()
backaccount = log_info[5].strip()
json_key = json.load(open(log_info[2].strip()))

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
sheet = Expenses(shtkey, json_key, verbose='yes')


def search_for_commands(message):

    fexpenses = expense.findall(message)
    fsignature = signature.findall(message)
    fstop = end.findall(message)
    fstatus = status.findall(message)
    falive = alive.findall(message)
    fbalance = balance.findall(message)

    return fexpenses, fsignature, fstop, fstatus, falive, fbalance


def log(message):
    print('[{}] Emma.{}'.format(strftime("%H:%M:%S", localtime()), message))


if __name__ == '__main__':

    runs = 0
    totTime = 0

    while True:

        start = time.time()
        runs += 1

        try:
            note = keep.read_note()
        except (InvalidElementStateException, NoSuchElementException):
            log('Couldn\'t reach note, will try on next run')

        log('Checking for commands')
        wExpenses, wSignature, dStop, sStatus, sAlive, sBalance = search_for_commands(note)

        if len(wExpenses) + len(wSignature) + len(dStop) + len(sStatus) + len(sAlive) + len(sBalance) == 0:
            log('None found')
        else:
            log('Executing commands')

        if len(wExpenses) != 0:
            try:
                sheet.add_expenses(wExpenses)
                keep.delete_content()
            except (InvalidElementStateException, NoSuchElementException):
                log('Couldn\'t update expenses, will try on next run')

        if len(wSignature) != 0:
            try:
                sheet.add_signature(wSignature)
                keep.delete_content()
            except (InvalidElementStateException, NoSuchElementException):
                log('Couldn\'t update signature, will try on next run')

        if len(sBalance) != 0:
            try:
                keep.send_message(sheet.get_balance(sBalance))
            except (InvalidElementStateException, NoSuchElementException):
                log('Couldn\'t send status, will try on next run')

        if len(sStatus) != 0:
            try:
                keep.send_message('{} runs so far. That\'s {} days, {} hours or {} minutes.'
                                  .format(runs, (runs*2 + totTime)//1440, (runs*2 + totTime)//60, runs*2 + totTime))
            except (InvalidElementStateException, NoSuchElementException):
                log('Couldn\'t send status, will try on next run')

        if len(sAlive) != 0:
            try:
                keep.send_message('Yes, I\'m alive! :)')
            except (InvalidElementStateException, NoSuchElementException):
                log('Couldn\'t speak, will try on next run')

        if len(dStop) != 0:
            break
            
        totTime += time.time()-start

        log('All done! Run {} took {} seconds, next scan in 120s'.format(runs, time.time()-start))
        time.sleep(120)

    log('Goodbye!')
