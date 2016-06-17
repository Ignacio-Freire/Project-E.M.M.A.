import time
from selenium import webdriver
from time import strftime, localtime
from evernote.api.client import EvernoteClient
from selenium.webdriver.common.keys import Keys
import evernote.edam.notestore.ttypes as NoteStore
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import UnexpectedAlertPresentException


def wait():
    """Time to wait between actions. Applies to all."""
    time.sleep(1)


class Evernote:
    def __init__(self, token, title, **kwargs):
        """ Access an Evernote note by title
            Args:
                token (str): Authentification token for Evernote.
                title (str): String to filter the notes by.
                verbose (optional 'yes'): If set verbose='yes' it will display step by step in the log.
        """

        self.filter = title
        self.auth_token = token
        self.verbose = kwargs.get('verbose', 'NO')

    def __log(self, message):
        """Message to print on log.
            Args:
                message (str): Message to print in log.
        """
        if self.verbose.upper() == 'YES':
            print('[{}] Emma.Messenger.Evernote: {}'.format(strftime("%H:%M:%S", localtime()), message))

    def auth(self):

        self.__log('Authentificating client')

        client = EvernoteClient(token=self.auth_token, sandbox=False)
        return client

    def get_content(self):

        self.__log('Accesing note')

        client = self.auth()

        note_store = client.get_note_store()

        note_filter = NoteStore.NoteFilter()
        note_filter.words = 'intitle:"{}"'.format(self.filter)

        notes_metadata_result_spec = NoteStore.NotesMetadataResultSpec()
        notes_metadata_list = note_store.findNotesMetadata(note_filter, 0, 1, notes_metadata_result_spec)

        note_guid = notes_metadata_list.notes[0].guid
        note = note_store.getNote(note_guid, True, False, False, False)

        return note_store, note, note.content

    def send_message(self, message, note_store, note):

        self.__log('Sending message')

        base = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM ' \
               '"http://xml.evernote.com/pub/enml2.dtd"><en-note>{}</en-note>'
        add = ''
        for msg in message:
            add += '<br>{}</br>'.format(msg)
        note.content = base.format(add)

        note_store.updateNote(note)

    def delete_content(self, note_store, note):

        self.__log('Deleting content')

        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM ' \
                       '"http://xml.evernote.com/pub/enml2.dtd"><en-note></en-note>'

        note_store.updateNote(note)


# Discontinued until Google Keep gets a public API. It got too unstable after a lot of updates from their part.
class GoogleKeep:
    """Access a Google Keep note to send or read message."""

    def __init__(self, acc, pw, nt, bkacc, **kwargs):
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
        self.location = kwargs.get('location', '')
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
            print('[{}] Emma.Messenger.Keep: {}'.format(strftime("%H:%M:%S", localtime()), message))

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
            if self.location:
                if 'chromedriver' in self.location:
                    drive = webdriver.Chrome(self.location)
                elif 'phantomjs' in self.location:
                    drive = webdriver.PhantomJS(self.location)
            else:
                drive = webdriver.Chrome()

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

        return text, driver

    def send_message(self, message, **kwargs):
        """ Message to print on the Google Keep Note
            Args:
                message (list): Messages to send. One line per element in list.
        """

        logged = kwargs.get('logged', 'NO')
        window = kwargs.get('driver', '')

        self.__log('Prepearing note for message')

        wait()

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
            driver.get(self.note)

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
