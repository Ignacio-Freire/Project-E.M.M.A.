# ------------------------------------- Expense Management Mad Assistant --------------------------------------------- #
import gspread
import difflib
import calendar
import psycopg2
import requests
from itertools import chain
from datetime import date, datetime
from time import strftime, localtime
from oauth2client.service_account import ServiceAccountCredentials


class SpreadsheetManager:
    # TODO Change functions so that they need to be called with which cell they need to use instead of hardcoding them.

    def __init__(self, sheet, json_auth, **kwargs):
        """
        Class to handle the connection with the Spreadsheet.
        :param sheet: Google Sheet key to access.
        :param json_auth: Json downloaded with credentials from Google Sheet API.
        :param kwargs: If set verbose='yes' it will display step by step in the log.
        """

        self.key = sheet
        self.json_auth = json_auth
        self.verbose = kwargs.get('verbose', 'NO')
        self.categories = []

    def __log(self, message):
        """
        Displays message on console providing some context.
        :param message: Message to print in log.
        """

        if self.verbose.upper() == 'YES':
            print('[{}] Emma.Accountant.SpreadsheetManager: {}'.format(strftime("%H:%M:%S", localtime()), message))

    def log_in_sheets(self):
        """
        Google Sheet API authentication process.
        :return Returns a worksheet.
        """

        self.__log('Authenticating Google Sheet')

        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_auth, scope)
        gc = gspread.authorize(credentials)
        sht = gc.open_by_key(self.key)

        self.__log("Authorized")

        self.__log("Loading categories")

        wsheet = sht.worksheet(calendar.month_name[datetime.now().year])

        self.categories = wsheet.col_values('A')

        self.__log("Loaded")

        return sht

    def add_expenses(self, expenses, columns, sheet):
        """
        Adds found expenses to the corresponding month.
        :param expenses: List of expenses found. expenses[e][1] Will always be skipped but can be used as month
                         for sheet name.
        :param columns: List of columns to update.
        :param sheet: Spreadsheet to add data.
        """

        self.__log('Adding expenses')

        for data in expenses:
            temp = list(data)

            month = int(data[1])
            temp.pop(1)

            categ = difflib.get_close_matches(temp[2], self.categories)

            temp[2] = categ[0] if categ else temp[2]

            payments = int(temp[6]) if temp[6] else 1
            temp.pop(6)

            for i in range(payments):
                msheet = calendar.month_name[month + i]
                lastrow = sheet.worksheet(msheet).col_values(2)[1:].index('') + 2

                for j in range(len(temp)):
                    sheet.worksheet(msheet).update_acell(columns[j] + str(lastrow), temp[j].title())

    def get_balance(self, balance, sheet):
        """
        Returns the balance of a month.
        :param balance: Months (in number).
        :param sheet: Spreadsheet to gather data from.
        :return: Returns the values to be informed.
        """

        self.__log('Retrieving requested balance')

        balances = []
        ws = sheet.worksheet('{}'.format(date.today().year))

        for month in balance:
            value = ws.cell(45, int(month) + 1).value
            balances.append(value)

        return balances

    def get_currency(self, curr, sheet):
        """
        Returns the current value of the asked currency.
        :param curr: Currency name (USD or EUR).
        :param sheet: Sheet to get the value from.
        :return: Returns the value to be informed.
        """

        self.__log('Retrieving requested currency values')

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

    def get_last_id(self):
        """
        Returns the highest transaction id value.
        :return Returns the highest ID in the spreadsheet.
        """

        self.__log("Retrieving last transaction")

        sheet = self.log_in_sheets()

        # TODO Finish get las ID function from Spreadsheet

    def lock_cur_value(self, month, column, entity):
        """
        Locks the foreign currency value for the whole month in the spreadsheet.
        :param month: Month to lock currency value.
        :param column: Column on which the currency value resides.
        :param entity: Entity to lock the foreing currency value on. (Ex: Visa, Master, Cash, All).
        :return:
        """

        msheet = calendar.month_name[month]
        self.__log('Locking Spreadsheet foreign currency value for {}'.format(msheet))

        # TODO complete function to lock currency value at EoM in Sheet

        pass


class PostgreDBManager:
    def __init__(self, db, **kwargs):
        """
        Class to handle the connection with the PostgreSQL database.
        :param db: String with DB connection data.
        :param kwargs: If set verbose='yes' it will display step by step in the log.
        """

        self.connection = db
        self.verbose = kwargs.get('verbose', 'NO')

    def __log(self, message):
        """
        Prints a message on the console specifying the current module in use.
        :param message: Message to display.
        """
        if self.verbose.upper() == 'YES':
            print('[{}] Emma.Accountant.DBManager: {}'.format(strftime("%H:%M:%S", localtime()), message))

    def connect_db(self):
        """
        PostgreSQL Database Connection
        :return: Connection object.
        """

        self.__log('Connecting to Database')

        conn = psycopg2.connect(self.connection)

        return conn

    def add_expenses(self, expenses):
        """
        Adds expenses to Postgre DB.
        :param expenses: Lists of lists containing the expenses and their attributes.
        :return: True if the insert was successful
        """

        connection = self.connect_db()
        cursor = connection.cursor()

        self.__log('Adding expenses to Database')

        currencies = ['USD', 'EUR']

        for currency in currencies:
            if currency in chain.from_iterable(expenses.upper()):
                usd = requests.get("https://currency-api.appspot.com/api/USD/ARS.json").json()['rate']
                eur = requests.get("https://currency-api.appspot.com/api/EUR/ARS.json").json()['rate']
                break
        else:
            usd = None
            eur = None

        cursor.execute("""SELECT MAX(trans_id) FROM GASTOS;""")
        tid = cursor.fetchone()

        for data in expenses:

            dt = datetime.now()

            if data[5].upper() == 'ARS':
                currency_value = None
            elif data[5].upper() == 'USD':
                currency_value = usd
            elif data[5].upper() == 'EUR':
                currency_value = eur
            else:
                self.__log('Currency not expected')
                return False

            total = float(data[4]) * currency_value if currency_value else int(data[4])

            tid[0] += 1

            payments = int(data[7]) if data[7] else 1

            for i in range(payments):

                month = int(data[1]) + i

                cursor.execute(
                    """INSERT INTO GASTOS (TRANS_ID, TRANS_DATE, DETAIL, EXP_CATEGORY, PRICE, PYMNT_METHOD, CURRENCY,
                     CURRENCY_VALUE, TOTAL, INSERT_TIMESTAMP, INSERT_USER_ID) VALUES ({}, to_date('{}','DDMMYYYY'),
                      '{}', '{}', {}, '{}', '{}', {}, {}, {}, '{}');""".format(
                        tid[0], data[0] + str(month) + str(datetime.now().year), data[2].title(), data[3].title(),
                        data[4],
                        data[6].upper(), data[5].upper(), currency_value, total, dt.strftime("%Y%d%m%H%M%S"),
                        'Emma'))

        connection.commit()

        return True

    def get_last_id(self):
        """
        Returns the highest transaction id value
        :return the highest ID in the DB
        """

        self.__log("Retrieving last transaction")

        sheet = self.connect_db()

        # TODO Finish get las ID function from DB

    def lock_cur_value(self, month, entity):
        """
        Locks the foreign currency value for the whole month in the DB.
        :param month: Month to lock currency value.
        :param entity: Entity to lock the foreing currency value on. (Ex: Visa, Master, Cash, All)
        :return:
        """

        self.connect_db()

        self.__log('Locking DB foreign currency value for {}'.format(calendar.month_name[month]))

        # TODO complete function to lock currency value at EoM in DB

        pass
