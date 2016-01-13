# ------------------------------------- Expense Management Mad Assistant --------------------------------------------- #
import json
import gspread
import calendar
from datetime import date
from time import strftime, localtime
from oauth2client.client import SignedJwtAssertionCredentials


class Expenses:

    def __init__(self, sheet, json_auth, **kwargs):
        """
            Args:
                sheet (str): Google Sheet key to access.
                json (str): Json downloaded with credentials from Google Sheet API.
                verbose (optional 'yes'): If set verbose='yes' it will display step by step in the log.
        """
        self.key = sheet
        self.json_auth = json_auth
        self.verbose = kwargs.get('verbose', 'NO')

    def __log(self, message):
        """Message to print on log.
            Args:
                message (str): Message to print in log.
        """
        if self.verbose.upper() == 'YES':
            print('[{}] AccessKeep.{}'.format(strftime("%H:%M:%S", localtime()), message))

    def __log_in_sheets(self):
        """ Google Sheet API authentication process."""

        self.__log('Authenticating Google Sheet')

        json_key = json.load(open(self.json_auth.strip()))
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
        gc = gspread.authorize(credentials)
        sht = gc.open_by_key(self.key)

        return sht

# Make it need another variable corresponding to a list of the columns to update.
    def add_expenses(self, expenses, columns):
        """Adds found expenses to the corresponding month
            Args:
                expenses (list): List of expenses found. expenses[e][1] Will always be skipped but can be used as month
                                 for sheet name.
                columns (list): Columns to update.
        """

        self.__log('Adding expenses')

        sheet = self.__log_in_sheets()

        for data in expenses:
                temp = list(data)

                msheet = calendar.month_name[int(data[1])]
                temp.pop(1)

                if temp[0].upper() == 'SIG':
                    temp.pop(0)
                    lastrow = len(sheet.worksheet(msheet).col_values(9)) + 1
                else:
                    lastrow = len(sheet.worksheet(msheet).col_values(2)) + 1

                for j in range(len(temp)):
                        sheet.worksheet(msheet).update_acell(columns[j] + str(lastrow), temp[j])

    def get_balance(self, balance):
        """Returns the balance of the month asked
            Args:
                balance (list): Month (in number)
        """

        self.__log('Retrieving requested balance')

        sheet = self.__log_in_sheets()

        balances = []
        ws = sheet.worksheet('{}'.format(date.today().year))

        for i in range(len(balance)):
            bmonth = int(balance[i]) + 1
            value = ws.cell(40, bmonth).value
            balances.append(value)

        return balances
