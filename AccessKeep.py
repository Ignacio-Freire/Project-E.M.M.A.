import time
from time import strftime, localtime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException

def wait():
    """Time to wait between actions. Applies to all."""
    time.sleep(3)


class Keep:
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
            print('[{}] AccessKeep.{}'.format(strftime("%H:%M:%S", localtime()), message))
    
    def log_in_goog(self):
        """Logs into the Google Account capable to read and edit the Google Keep Note to be used."""

        self.__log('Logging into Google Account')

        drive = webdriver.Chrome()
        drive.get("http://keep.google.com/")
        wait()
        drive.find_element_by_id('Email').send_keys(self.mail)
        wait()
        drive.find_element_by_id('next').click()
        wait()
        try:
            drive.find_element_by_xpath('//*[@id="Passwd"]').send_keys(self.passw)
            wait()
            drive.find_element_by_id('signIn').click()
        except (InvalidElementStateException, NoSuchElementException):
            drive.save_screenshot('auth_error.png')
            drive.find_element_by_id('Email').send_keys(self.backaccount)
            drive.find_element_by_id('next').click()
            drive.find_element_by_xpath('//*[@id="Passwd"]').send_keys(self.passw)
            drive.find_element_by_id('signIn').click()

        self.__log('Opening note')

        drive.get(self.note)
        wait()

        return drive

    def read_note(self):
        """"Retrieves text from the Google Keep Note."""

        driver = self.log_in_goog()
        wait()
        text = ''

        self.__log('Getting text')

        try:
            text = driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').text
            wait()
            driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()

        except NoSuchElementException:
            driver.save_screenshot('element_error.png')
            self.__log('Can\'t find element, will relog and try on next run')

        self.__log('Closing driver')
        driver.quit()

        return text

    def send_message(self, message):
        """ Message to print on the Google Keep Note
            Args:
                message (list): Messages to send.
        """

        driver = self.delete_content(cont='yes')

        self.__log('Sending message')

        driver.get(self.note)
        wait()

        for i in message:
            driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').send_keys(i)
            wait()
            driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').send_keys(Keys.RETURN)
            driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').send_keys(Keys.SHIFT + Keys.HOME)

        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()

        wait()
        self.__log('Closing driver')
        driver.quit()

    def delete_content(self, **kwargs):
        """Deletes contents of the Google Keep Note."""

        self.__log('Deleting contents')

        cont = kwargs.get('cont', 'NO')

        driver = self.log_in_goog()

        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[1]/div[5]').clear()
        wait()
        driver.find_element_by_xpath('/html/body/div[9]/div/div[2]/div[2]/div[1]').click()
        wait()

        if cont.upper() == 'NO':
            self.__log('Closing driver')
            driver.quit()
        elif cont.upper() == 'YES':
            self.__log('Keeping driver open for further use')
            return driver


