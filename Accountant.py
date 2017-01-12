# ------------------------------------ Extended Multi Management Assistant ------------------------------------------- #
# ------------------------------------             Accountant              ------------------------------------------- #
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

    def log_in_sheets(self, categ_col):
        """
        Google Sheet API authentication process.
        :param categ_col: Column where the categories to load are in integer.
        :return Returns a worksheet.
        """

        self.__log('Authenticating Google Sheet')

        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_auth, scope)
        gc = gspread.authorize(credentials)
        sht = gc.open_by_key(self.key)

        self.__log("Authorized")

        self.__log("Loading categories")

        wsheet = sht.worksheet(calendar.month_name[datetime.now().month])

        self.categories = wsheet.col_values(categ_col)

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

            month = int(data[2])
            temp.pop(2)

            categ = difflib.get_close_matches(temp[2], self.categories)

            temp[2] = categ[0] if categ else temp[2]

            payments = int(temp[7]) if temp[7] else 1
            temp.pop(7)

            for i in range(payments):
                msheet = calendar.month_name[month + i]
                lastrow = sheet.worksheet(msheet).col_values(2)[1:].index('') + 2

                for j in range(len(temp)):
                    sheet.worksheet(msheet).update_acell(columns[j] + str(lastrow),
                                                         temp[j].title() if j < 4 else temp[j].upper())

    def get_balance(self, balance, sheet, row_no):
        """
        Returns the balance of a month.
        :param balance: Months (in number).
        :param sheet: Spreadsheet to gather data from.
        :param row_no: Int, row number where the balance is.
        :return: Returns the values to be informed.
        """

        self.__log('Retrieving requested balance')

        balances = []
        ws = sheet.worksheet('{}'.format(date.today().year))

        for month in balance:
            value = ws.cell(row_no, int(month) + 1).value
            balances.append(value)

        return balances

    def get_currency(self, curr, sheet, usd_pos, eur_pos):
        """
        Returns the current value of the asked currency.
        :param curr: Currency name (USD or EUR).
        :param sheet: Sheet to get the value from.
        :param usd_pos: Tuple with the position of the USD currency value.
        :param eur_pos: Tuple with the position of the EUR currency value.
        :return: Returns the value to be informed.
        """

        self.__log('Retrieving requested currency values')

        values = []
        ws = sheet.worksheet('{}'.format(date.today().year))

        for i in curr:
            if i.lower() == '<usd>':
                value = ws.cell(usd_pos[1], usd_pos[0]).value
                values.append(value)
            elif i.lower() == '<eur>':
                value = ws.cell(eur_pos[1], eur_pos[0]).value
                values.append(value)

        return values

    def lock_cur_value(self, entities, cur_col, value_col, entity_col, sheet):
        """
        Locks the foreign currency value for the whole month in the spreadsheet.
        :param entities: Entities that have been paid.
        :param cur_col: Column where the currency data is.
        :param value_col: Column where the values to update are.
        :param entity_col: Column where the entity data is.
        :param sheet: Spreadsheet to update.
        """

        dt = datetime.now()
        msheet = calendar.month_name[dt.month]

        usd = requests.get("https://currency-api.appspot.com/api/USD/ARS.json").json()['rate']
        eur = requests.get("https://currency-api.appspot.com/api/EUR/ARS.json").json()['rate']

        ws = sheet.worksheet(msheet)

        for entity in entities:

            self.__log('Locking Spreadsheet foreign currency value for {} in {}'.format(entity, msheet))

            for row, value in enumerate(ws.col_values(value_col)):
                row += 1
                if ws.cell(row, entity_col).value == entity.upper():
                    if ws.cell(row, cur_col).value == 'USD':
                        ws.update_cell(row, value_col, str(usd).replace('.', ','))
                    if ws.cell(row, cur_col).value == 'EUR':
                        ws.update_cell(row, value_col, str(eur).replace('.', ','))

        return True

    def get_last_id(self, qty, spreadsheet, worksheet, cell):
        """
        Returns the highest transaction id value.
        :param qty: Number of transactions to fetch.
        :param spreadsheet: Spreadsheet to get the IDs from.
        :param worksheet: Worksheet where the max ID is placed.
        :param cell: Cell where the max ID is written.
        :return max_id: Returns the highest ID in the spreadsheet.
        :return transactions: Returns a list of the number of transactions needed.
        """

        self.__log("Retrieving last transaction")

        ws = spreadsheet.worksheet(worksheet)

        max_id = ws.cell(cell[0], cell[1]).value

        ids_to_fetch = [max_id - i for i in range(qty)]

        transaction = []
        transactions = []

        # TODO Find a way to fetch all the necessary rows that might be spread across the whole spreadsheet.
        # The worksheet would probably have to change for each ID too.

        for i in range(12):

            msheet = calendar.month_name[i + 1]

            ws = spreadsheet.worksheet(msheet)

            # get list of IDs from spreadsheet

            if 'Cell with ID' in ids_to_fetch:
                transaction = ['Values from each individual transaction']
                ids_to_fetch.remove('ID')

            transactions.append(transaction)

        return max_id, transactions


class PostgreDBManager:
    def __init__(self, db, tbl_name, **kwargs):
        """
        Class to handle the connection with the PostgreSQL database.
        :param db: String with DB connection data.
        :param tbl_name: Transactions table name.
        :param kwargs: If set verbose='yes' it will display step by step in the log.
        """

        self.connection = db
        self.trans_table = tbl_name
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

        exp_w_id = []

        self.__log('Adding expenses to Database')

        currencies = ['USD', 'usd', 'EUR', 'eur']

        for currency in currencies:
            transaction = chain.from_iterable(expenses)
            if currency in transaction:
                usd = requests.get("https://currency-api.appspot.com/api/USD/ARS.json").json()['rate']
                eur = requests.get("https://currency-api.appspot.com/api/EUR/ARS.json").json()['rate']
                break
        else:
            usd = None
            eur = None

        cursor.execute("""SELECT MAX(trans_id) FROM {};""".format(self.trans_table))
        tid = cursor.fetchone()
        trans_id = tid[0]

        for data in expenses:

            dt = datetime.now()

            if data[5].upper() == 'ARS':
                currency_value = 1
            elif data[5].upper() == 'USD':
                currency_value = usd
            elif data[5].upper() == 'EUR':
                currency_value = eur
            else:
                self.__log('Currency not expected')
                return False
            
            amt = data[4].replace(',', '.')

            total = float(amt) * currency_value if currency_value \
                else float(amt)

            trans_id += 1

            payments = int(data[7]) if data[7] else 1

            for i in range(payments):
                month = int(data[1]) + i

            cursor.execute(
                """INSERT INTO  {} (TRANS_ID,
                                        TRANS_DATE,
                                        DETAIL,
                                        EXP_CATEGORY,
                                        PRICE,
                                        PYMNT_METHOD,
                                        CURRENCY,
                                        CURRENCY_VALUE,
                                        TOTAL,
                                        INSERT_TIMESTAMP,
                                        INSERT_USER_ID)
                                VALUES ({}
                                        ,to_date('{}','DDMMYYYY')
                                        ,'{}'
                                        ,'{}'
                                        ,{}
                                        ,'{}'
                                        ,'{}'
                                        ,{}
                                        ,{}
                                        ,{}
                                        ,'{}');""".format(self.trans_table, trans_id,
                                                          data[0] + '{0:0=2d}'.format(month) + str(datetime.now().year),
                                                          data[2].title(), data[3].title(), amt, data[6].upper(),
                                                          data[5].upper(), currency_value, total,
                                                          dt.strftime("%Y%d%m%H%M%S"), 'Emma'))

            data = (str(trans_id), *data)
            exp_w_id.append(data)

            connection.commit()

        return True, exp_w_id

    def lock_cur_value(self, entities):
        """
        Locks the foreign currency value for the whole month in the DB.
        :param entities: Entities that have been paid.
        """

        # TODO Fix payed command

        connection = self.connect_db()
        cursor = connection.cursor()

        dt = datetime.now()
        year = dt.year
        month = int(dt.month)

        usd = requests.get("https://currency-api.appspot.com/api/USD/ARS.json").json()['rate']
        eur = requests.get("https://currency-api.appspot.com/api/EUR/ARS.json").json()['rate']

        for entity in entities:
            self.__log('Locking DB foreign currency value for {} in {}.'.format(entity, calendar.month_name[month]))

            cursor.execute("""UPDATE {}
                                     SET currency_value = {},
                                         close_date = to_date('{}','DDMMYYYY'),
                                         edit_timestamp = {},
                                         edit_user_id = 'Emma'
                                   WHERE EXTRACT(MONTH FROM trans_date) = {}
                                     AND EXTRACT(YEAR FROM trans_date) = {}
                                     AND pymnt_method = '{}'
                                     AND currency = 'USD';""".format(self.trans_table, usd, dt.strftime("%d%m%y"),
                                                                     dt.strftime("%Y%d%m%H%M%S"), month, year,
                                                                     entity.upper()))

            cursor.execute("""UPDATE {}
                                     SET currency_value = {},
                                         close_date = to_date('{}','DDMMYYYY'),
                                         edit_timestamp = {},
                                         edit_user_id = 'Emma'
                                   WHERE EXTRACT(MONTH FROM trans_date) = {}
                                     AND EXTRACT(YEAR FROM trans_date) = {}
                                     AND pymnt_method = '{}'
                                     AND currency = 'EUR';""".format(self.trans_table, eur, dt.strftime("%d%m%y"),
                                                                     dt.strftime("%Y%d%m%H%M%S"), month, year,
                                                                     entity.upper()))

        connection.commit()

    def get_last_id(self, qty):
        """
        Returns the highest transaction id value
        :param qty: Number of expenses to fetch.
        :return max_id: the highest ID in the DB.
        :return transactions: Last X transactions in DB.
        """

        self.__log("Retrieving last {} transactions".format(qty))

        conn = self.connect_db()

        cursor = conn.cursor()
        cursor.execute("""SELECT MAX(trans_id) FROM {};""".format(self.trans_table))
        max_id = cursor.fetchone()

        cursor.execute("""SELECT TRANS_ID, TRANS_DATE, DETAIL, EXP_CATEGORY, PRICE, PYMNT_METHOD, CURRENCY
                                FROM {}
                               WHERE TRANS_ID >= {}""".format(self.trans_table, max_id[0] - qty))

        transactions = cursor.fetchone

        return max_id[0], transactions
