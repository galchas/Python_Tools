import imaplib
import email
import re
from datetime import datetime


class ReadMails:

    def __init__(self, username="YOUREMAIL@gmail.com", password='YOURPASSWORD'):
        self.mails = dict()
        self.imap = None
        self.username = username
        self.password = password
        self.is_connected = False
        self._has_mails = False

    def connect(self):
        try:
            # create an IMAP4 class with SSL
            self.imap = imaplib.IMAP4_SSL('smtp.gmail.com', port=993)
            # authenticate
            self.imap.login(self.username, self.password)
            self.is_connected = True
        except Exception as ex:
            print(ex)
            return None
        return self.imap

    def disconnect(self):
        try:
            self.imap.close()
        finally:
            self.imap.logout()
        self.is_connected = False

    def get_mails(self, from_date=''):
        date_format = "%d-%b-%Y"  # DD-Mon-YYYY e.g., 3-Mar-2014
        since_date = datetime.strptime(from_date, date_format)

        self.connect()
        try:
            self._get_mailbox()
            # https://gist.github.com/martinrusev/6121028
            if from_date != '':
                _, data = self.imap.uid('SEARCH', '(SENTSINCE {})'.format(from_date))
            else:
                _, data = self.imap.uid('SEARCH', 'ALL')
            msgs = data[0].split()
            print("Found {0} msgs".format(len(msgs)))

            for uid in msgs:
                typ, s = self.imap.uid('FETCH', uid, '(RFC822)')
                if s is None or s[0] is None:
                    continue
                mail = email.message_from_string(s[0][1].decode('utf-8'))

                print("From: {0}, Subject: {1}, Date: {2}\n".format(mail["From"], mail["Subject"], mail["Date"]))
                _datetime = datetime.strptime(mail["Date"][0:mail["Date"].rfind(' ')], "%a, %d %b %Y %H:%M:%S -%f")
                self.mails[_datetime] = mail
        finally:
            self.disconnect()
        if len(self.mails) != 0:
            self._has_mails = True

    def save_attachment(self, path=''):
        if self._has_mails is False:
            print(" No mails found! run first get_mails()")
            exit(-1)
        mail = self.mails[max(self.mails.keys())]
        print("Add subject contenct to search and remove this")
        if '<SUBJECT CONTENT>' in mail['Subject']:
            print(mail['Subject']+"   -  "+mail['Date'])
            self.connect()
            self._get_mailbox()

            try:
                if mail.is_multipart():
                    for part in mail.walk():
                        ctype = part.get_content_type()
                        print(ctype)
                        if ctype in ['image/jpeg', 'image/png', 'application/octet-stream']:
                            open(part.get_filename().replace('/', ''), 'wb').write(part.get_payload(decode=True))
            finally:
                self.disconnect()

    def save_all_attachments(self, path=''):
        if self._has_mails is False:
            print(" No mails found! run first get_mails()")
            exit(-1)
        self.connect()
        self._get_mailbox()

        try:
            for key, mail in self.mails.items():
                if mail.is_multipart():
                    for part in mail.walk():
                        ctype = part.get_content_type()
                        print(ctype)
                        if ctype in ['image/jpeg', 'image/png', 'application/octet-stream']:
                            open(part.get_filename().replace('/', ''), 'wb').write(part.get_payload(decode=True))
        finally:
            self.disconnect()


    def _get_mailbox(self, mailbox_name='[Gmail]/Sent'):
        if not self.is_connected: return ''
        # total number of emails
        try:
            _typ, _data = self.imap.list(directory=mailbox_name)
        except imaplib.IMAP4.error as ex:
            print(ex)
            self.imap.logout()
        print('Response code:', _typ)

        for line in _data:
            _res_dict = ReadMails.parse_list_respond(line)
            print('Server response:', _res_dict['mailbox_name'])
        status, messages = self.imap.select(_res_dict['mailbox_name'])
        print(status)

        return messages[0].decode('utf-8')

    @staticmethod
    def parse_list_respond(line):
        list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
        flags, delimiter, mailbox_name = list_response_pattern.match(bytes(line).decode('utf-8')).groups()
        return {'flags': flags, "delimiter": delimiter, "mailbox_name": mailbox_name}


if __name__ == '__main__':
    r = ReadMails()
    r.get_mails('13-Dec-2020')
    r.save_all_attachments()
