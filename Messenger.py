import time
from selenium import webdriver
from time import strftime, localtime
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import UnexpectedAlertPresentException


def wait():
    """Time to wait between actions. Applies to all."""
    time.sleep(1)


class GoogleKeep:
    """Access a Google Keep note to send or read message."""

    def __init__(self, acc, pw, nt, bkacc, loc, **kwargs):
        """
            Args:
                acc (str): Account to access the Google Keep Note.
                pw (str): Password of said account.
                nt (str): Link of the note to access.
                bkacc (str): Verification email (alternative email asked by Google to verify who's logging in).
                nt (str): Path to Chromedriver.exe
                verbose (optional 'yes'): If set verbose='yes' it will display step by step in the log.
        """
        self.passw = pw
        self.location = loc
        self.mail = acc
        self.note = nt
        self.backaccount = bkacc
        self.verbose = kwargs.get('verbose', 'NO')

    def __log(self, message):
        """Message to print on log.
            Args:
                message (str): Message to print in log.
        """
        if self.verbose.upper() == 'YES':
            print('[{}] Emma.Messenger: {}'.format(strftime("%H:%M:%S", localtime()), message))

    def close_driver(self, driver):
        self.__log('Closing driver')
        try:
            driver.quit()
        except AttributeError:
            self.__log('Error while closing')
            pass

    def log_in_goog(self):
        """Logs into the Google Account capable to read and edit the Google Keep Note to be used."""

        self.__log('Logging into Google Account')

        try:
            drive = webdriver.Chrome(self.location)
        except AttributeError:
            pass

        wait()

        try:
            drive.get("http://keep.google.com/")
        except (InvalidElementStateException, NoSuchElementException, TimeoutException,
                UnexpectedAlertPresentException):
            self.close_driver(drive)
            raise ElementNotFound
        wait()
        drive.find_element_by_id('Email').send_keys(self.mail)
        wait()
        drive.find_element_by_id('next').click()
        wait()

        drive.find_element_by_xpath('//*[@id="Passwd"]').send_keys(self.passw)
        wait()
        drive.find_element_by_id('signIn').click()
        wait()

        try:
            drive.find_element_by_xpath('//*[@id="emailAnswer"]').send_keys(self.backaccount)
            wait()
            drive.find_element_by_xpath('//*[@id="submitChallenge"]').click()
            wait()
            drive.find_element_by_xpath('//*[@id="Passwd"]').send_keys(self.passw)
            wait()
            drive.find_element_by_id('signIn').click()
        except(InvalidElementStateException, NoSuchElementException, TimeoutException,
               UnexpectedAlertPresentException):
            pass

        self.__log('Opening note')

        drive.get(self.note)
        wait()

        return drive

    def read_note(self, **kwargs):
        """"Retrieves text from the Google Keep Note.
         Args:
                kwargs = can add cont='yes' to avoid closing the driver after deleting the contents.
        """

        cont = kwargs.get('cont', 'NO')

        driver = self.log_in_goog()
        wait()

        self.__log('Getting text')

        try:
            text = driver.find_element_by_xpath('/html/body/div[9]/div/div[2]').text
            self.__log('Got Text')
            wait()
            driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()
            self.__log('Clicked Done')

        except (InvalidElementStateException, NoSuchElementException, TimeoutException,
                UnexpectedAlertPresentException):
            driver.save_screenshot('element_error.png')
            self.__log('Can\'t find element, will relog and try on next run')
            self.close_driver(driver)
            raise ElementNotFound

        if cont.upper() == 'NO':
            self.close_driver(driver)
        else:
            self.__log('Keeping open for further use')

        return text, driver

    def send_message(self, message, **kwargs):
        """ Message to print on the Google Keep Note
            Args:
                message (list): Messages to send. One line per element in list.
        """

        logged = kwargs.get('logged', 'NO')
        window = kwargs.get('driver', '')

        self.__log('Prepearing note for message')

        if window:
            driver = self.delete_content(cont='YES', logged=logged, driver=window)
        else:
            driver = self.delete_content(cont='YES', logged=logged)

        self.__log('Sending message')

        driver.get(self.note)
        wait()

        for line in message:

            for i in range(4, 11):
                try:
                    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[{}]'.format(i)).send_keys(
                        line)
                    break
                except:
                    pass

            wait()

            for i in range(4, 11):
                try:
                    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[{}]'.format(i)).send_keys(
                        Keys.RETURN)
                    driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[{}]'.format(i)).send_keys(
                        Keys.SHIFT + Keys.HOME)
                except:
                    pass

        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()

        wait()
        self.close_driver(driver)

    def delete_content(self, **kwargs):
        """Deletes contents of the Google Keep Note.
            Args:
                kwargs = can add cont='yes' to avoid closing the driver after deleting the contents.
        """

        self.__log('Deleting contents')

        cont = kwargs.get('cont', 'NO')
        logged = kwargs.get('logged', 'NO')
        window = kwargs.get('driver', '')

        if logged == 'NO':
            driver = self.log_in_goog()
        elif window:
            driver = window

        for i in range(4, 11):
            try:
                driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[{}]'.format(i)).clear()
                break
            except:
                pass

        wait()
        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()
        wait()

        if cont.upper() == 'NO':
            self.close_driver(driver)
        elif cont.upper() == 'YES':
            self.__log('Keeping driver open for further use')
            return driver


# This type of error is really not that good.
class ElementNotFound(Exception):
    pass
