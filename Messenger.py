from time import strftime, localtime
from evernote.api.client import EvernoteClient
import evernote.edam.notestore.ttypes as NoteStore


class EvernoteManager:
    def __init__(self, token, title, **kwargs):
        """
        Class to handle communication with the user via Evernote.
        :param token: Authentication token for Evernote.
        :param title: String to filter the notes by.
        :param kwargs: If set verbose='yes' it will display step by step in the log.
        """

        self.filter = title
        self.auth_token = token
        self.verbose = kwargs.get('verbose', 'NO')

    def __log(self, message):
        """
        Displays message on console providing some context.
        :param message: Message to print in log.
        """

        if self.verbose.upper() == 'YES':
            print('[{}] Emma.Messenger.EvernoteManager: {}'.format(strftime("%H:%M:%S", localtime()), message))

    def auth(self):
        """
        Authentication function for the Evernote note.
        :return client: Returns a Client object.
        """

        self.__log('Authenticating client')

        client = EvernoteClient(token=self.auth_token, sandbox=False)
        return client

    def get_content(self):
        """
        Retrieves the content of the specified note.
        :return note_store: Returns the location of the expenses note.
        :return note: Returns the note object.
        :return note.content: Returns the content of the note in a string.
        """

        self.__log('Accessing note')

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
        """
        Generates a message to be delivered to the user vía a note.
        :param message: Message to deliver.
        :param note_store: Location of the note.
        :param note: Note to be updated.
        """

        self.__log('Sending message')

        base = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM ' \
               '"http://xml.evernote.com/pub/enml2.dtd"><en-note>{}</en-note>'
        add = ''
        for msg in message:
            add += '<br>{}</br>'.format(msg)
        note.content = base.format(add)

        note_store.updateNote(note)

    def delete_content(self, note_store, note):
        """
        Deletes the content of a note.
        :param note_store: Location of the note.
        :param note: Note to be updated.
        :return:
        """

        self.__log('Deleting content')

        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM ' \
                       '"http://xml.evernote.com/pub/enml2.dtd"><en-note></en-note>'

        note_store.updateNote(note)
