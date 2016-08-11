# ------------------------------------- Expense Management Mad Assistant --------------------------------------------- #
import gspread
import calendar
import psycopg2
import requests
from itertools import chain
from datetime import date, datetime
from time import strftime, localtime
from oauth2client.service_account import ServiceAccountCredentials


class Expenses:
    def __init__(self, sheet, json_auth, db, **kwargs):
        """
            Args:
                sheet (str): Google Sheet key to access.
                json (str): Json downloaded with credentials from Google Sheet API.
                verbose (optional 'yes'): If set verbose='yes' it will display step by step in the log.
        """
        self.key = sheet
        self.json_auth = json_auth
        self.connection = db
        self.verbose = kwargs.get('verbose', 'NO')

    def __log(self, message):
        """Message to print on log.
            Args:
                message (str): Message to print in log.
        """
        if self.verbose.upper() == 'YES':
            print('[{}] Emma.Accountant: {}'.format(strftime("%H:%M:%S", localtime()), message))

    def log_in_sheets(self):
        """ Google Sheet API authentication process."""

        self.__log('Authenticating Google Sheet')

        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_auth, scope)
        gc = gspread.authorize(credentials)
        sht = gc.open_by_key(self.key)

        return sht

    def connect_db(self):

        self.__log('Connecting to Database')

        conn = psycopg2.connect(self.connection)

        return conn

    def add_db(self, expenses):

        connection = self.connect_db()
        cursor = connection.cursor()

        self.__log('Adding expenses to Database')

        currencies = ['ars', 'ARS', 'usd', 'USD', 'eur', 'EUR']

        for currency in currencies:
            if currency in chain.from_iterable(expenses):
                usd = requests.get("https://currency-api.appspot.com/api/USD/ARS.json").json()['rate']
                eur = requests.get("https://currency-api.appspot.com/api/EUR/ARS.json").json()['rate']
                break

        for data in expenses:
            cursor.execute("""select max(trans_id) from gastos;""")
            tid = cursor.fetchone()

            dt = datetime.now()

            if data[5].upper() == 'ARS':
                currency_value = 'null'
                total = int(data[4])
            elif data[5].upper() == 'USD':
                currency_value = usd
                total = int(data[4]) * usd
            elif data[5].upper() == 'EUR':
                currency_value = eur
                total = int(data[4]) * eur

            cursor.execute(
                """INSERT INTO GASTOS (TRANS_ID, TRANS_DATE, DETAIL, EXP_CATEGORY, PRICE, PYMNT_METHOD, CURRENCY,
                 CURRENCY_VALUE, TOTAL, INSERT_TIMESTAMP, INSERT_USER_ID) VALUES ({}, to_date('{}','DDMMYYYY'),
                  '{}', '{}', {}, '{}', '{}', {}, {}, {}, '{}');""".format(
                    tid[0] + 1, data[0] + data[1] + str(datetime.now().year), data[2], data[3], data[4],
                    data[6].upper(), data[5].upper(), currency_value, total, dt.strftime("%Y%d%m%H%M%S"), 'Emma'))

        connection.commit()

    def add_expenses(self, expenses, columns):
        """Adds found expenses to the corresponding month
            Args:
                expenses (list): List of expenses found. expenses[e][1] Will always be skipped but can be used as month
                                 for sheet name.
                columns (list): Columns to update.
        """

        self.__log('Adding expenses')

        sheet = self.log_in_sheets()

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
                balance (list): Months (in number)
        """

        self.__log('Retrieving requested balance')

        sheet = self.log_in_sheets()

        balances = []
        ws = sheet.worksheet('{}'.format(date.today().year))

        '''for i in range(len(balance)):
            bmonth = int(balance[i]) + 1
            value = ws.cell(41, bmonth).value
            balances.append(value)'''

        for month in balance:
            value = ws.cell(42, int(month) + 1).value
            balances.append(value)

        return balances

    def get_currency(self, curr):
        """Returns the value of the asked currency
            Args:
                curr (list): Currency name (strings)
        """

        self.__log('Retrieving requested currency values')

        sheet = self.log_in_sheets()

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

    def get_sig_remaining(self, remaining):
        """Returns the balance of the month asked
            Args:
                remaining (list): Months (in number)
        """

        self.__log('Retrieving requested remaining')

        sheet = self.log_in_sheets()

        remainings = []

        for month in remaining:
            ws = sheet.worksheet(calendar.month_name[int(month)])
            value = ws.cell(20, 11).value
            remainings.append(value)

        return remainings
