# ------------------------------------- Expense Management Mad Assistant --------------------------------------------- #
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from datetime import date
import calendar
from time import strftime, localtime


class Expenses:

    def __init__(self, sheet, json, **kwargs):
        """
            Args:
                sheet (str): Google Sheet key to access.
                json (str): Json downloaded with credentials from Google Sheet API.
                verbose (optional 'yes'): If set verbose='yes' it will display step by step in the log.
        """
        self.key = sheet
        self.json_key = json
        self.verbose = kwargs.get('verbose', 'NO')

    def __log(self, message):
        """Message to print on log.
            Args:
                message (str): Message to print in log.
        """
        if self.verbose.upper() == 'YES':
            print('[{}] AccessKeep.{}'.format(strftime("%H:%M:%S", localtime()), message))

    def log_in_sheets(self):
        """ Google Sheet API authentication process."""

        self.__log('Authenticating Google Sheet')

        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SignedJwtAssertionCredentials(self.json_key['client_email'], self.json_key['private_key'].encode(), scope)
        gc = gspread.authorize(credentials)
        sht = gc.open_by_key(self.key)

        return sht

    def add_expenses(self, expenses):
        """Adds found expenses to the corresponding month
            Args:
                expenses (list): List of expenses found.
        """

        self.__log('Adding expenses')

        sheet = self.log_in_sheets()

        for data in expenses:
                day = data[0]
                msheet = calendar.month_name[int(data[1])]
                detail = data[2]
                category = data[3]
                amount = data[4]
                currency = data[5]

                lastrow = len(sheet.worksheet(msheet).col_values(2)) + 1

                col = ['B', 'C', 'D', 'E', 'F']
                colnm = [day, detail.title(), category.title(), amount, currency.upper()]

                for j in range(len(col)):
                        sheet.worksheet(msheet).update_acell(col[j] + str(lastrow), colnm[j])

    def add_signature(self, signature):
        """Adds Visa Signature expenses to the corresponding month
            Args:
                signature (list): List of expenses found.
        """

        self.__log('Adding Visa Signature expenses')

        sheet = self.log_in_sheets()

        for e in signature:
                msheet = calendar.month_name[int(e[1])]
                detail = e[2]
                amount = e[3]
                currency = e[4]

                lastrow = len(sheet.worksheet(msheet).col_values(9)) + 1

                col = ['I', 'J', 'K']
                colnm = [detail.title(), amount, currency.upper()]

                for j in range(len(col)):
                        sheet.worksheet(msheet).update_acell(col[j] + str(lastrow), colnm[j])

    def get_balance(self, balance):
        """Returns the balance of the month asked
            Args:
                balance (list): Month (in number)
        """

        self.__log('Retrieving requested balance')

        sheet = self.log_in_sheets()

        bmonth = int(balance[0]) + 1
        ws = sheet.worksheet('{}'.format(date.today().year))
        value = ws.cell(40, bmonth).value

        return value
