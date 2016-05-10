# ------------------------------------- Expense Management Mad Assistant --------------------------------------------- #
import gspread
import calendar
from datetime import date
from time import strftime, localtime
from oauth2client.service_account import ServiceAccountCredentials


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
            print('[{}] Emma.Accountant: {}'.format(strftime("%H:%M:%S", localtime()), message))

    def __log_in_sheets(self):
        """ Google Sheet API authentication process."""

        self.__log('Authenticating Google Sheet')

        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_auth, scope)
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

        self.__log('Authorized')

        for data in expenses:
            temp = list(data)

            msheet = calendar.month_name[int(data[1])]
            temp.pop(1)

            if temp[0].upper() == 'SIG':
                temp.pop(0)
                lastrow = sheet.worksheet(msheet).col_values(9)[1:].index('') + 2
            else:
                lastrow = sheet.worksheet(msheet).col_values(2)[1:].index('') + 2

            for j in range(len(temp)):
                sheet.worksheet(msheet).update_acell(columns[j] + str(lastrow), temp[j].title())

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
            value = ws.cell(41, bmonth).value
            balances.append(value)

        return balances

    def get_currency(self, curr):
        """Returns the value of the asked currency
            Args:
                curr (list): Currency name (strings)
        """

        self.__log('Retrieving requested currency values')

        sheet = self.__log_in_sheets()

        values = []
        ws = sheet.worksheet('{}'.format(date.today().year))

        for i in curr:
            if i.lower() == '<usd>':
                value = ws.cell(5, 17).value
                values.append(value)
            elif i.lower() == '<eur>':
                value = ws.cell(6, 17).value
                values.append(value)

        return values
