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

    def __init__(self, acc, pw, nt, bkacc, **kwargs):
        """
            Args:
                acc (str): Account to access the Google Keep Note.
                pw (str): Password of said account.
                nt (str): Link of the note to access.
                bkacc (str): Verification email (alternative email asked by Google to verify who's logging in).
                verbose (optional 'yes'): If set verbose='yes' it will display step by step in the log.
        """
        self.passw = pw
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
            print('[{}] Messenger.{}'.format(strftime("%H:%M:%S", localtime()), message))

    def log_in_goog(self):
        """Logs into the Google Account capable to read and edit the Google Keep Note to be used."""

        self.__log('Logging into Google Account')

        try:
            drive = webdriver.Chrome()
        except AttributeError:
            pass

        wait()

        try:
            drive.get("http://keep.google.com/")
        except (InvalidElementStateException, NoSuchElementException, TimeoutException,
                UnexpectedAlertPresentException):
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

    def read_note(self):
        """"Retrieves text from the Google Keep Note."""

        driver = self.log_in_goog()
        wait()

        self.__log('Getting text')

        try:
            text = driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[1]/div[6]').text
            self.__log('Got Text')
            wait()
            driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[2]/div[1]').click()
            self.__log('Clicked Done')

        except (InvalidElementStateException, NoSuchElementException, TimeoutException,
                UnexpectedAlertPresentException):
            driver.save_screenshot('element_error.png')
            self.__log('Can\'t find element, will relog and try on next run')
            raise ElementNotFound

        self.__log('Closing driver')
        try:
            driver.quit()
        except AttributeError:
            pass

        return text

    def send_message(self, message):
        """ Message to print on the Google Keep Note
            Args:
                message (list): Messages to send. One line per element in list.
        """

        driver = self.delete_content(cont='yes')

        self.__log('Sending message')

        driver.get(self.note)
        wait()

        for line in message:
            driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[1]/div[6]').send_keys(line)
            wait()
            driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[1]/div[6]').send_keys(Keys.RETURN)
            driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[1]/div[6]').send_keys(Keys.SHIFT + Keys.HOME)

        driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[2]/div[1]').click()

        wait()
        self.__log('Closing driver')
        try:
            driver.quit()
        except AttributeError:
            pass

    def delete_content(self, **kwargs):
        """Deletes contents of the Google Keep Note.
            Args:
                kwargs = can add cont='yes' to avoid closing the driver after deleting the contents.
        """

        self.__log('Deleting contents')

        cont = kwargs.get('cont', 'NO')

        driver = self.log_in_goog()

        driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[1]/div[6]').clear()
        wait()
        driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div[2]/div[1]').click()
        wait()

        if cont.upper() == 'NO':
            self.__log('Closing driver')
            try:
                driver.quit()
            except AttributeError:
                pass
        elif cont.upper() == 'YES':
            self.__log('Keeping driver open for further use')
            return driver


# This type of error is really not that good.
class ElementNotFound(Exception):
    pass
