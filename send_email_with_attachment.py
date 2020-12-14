#! /usr/bin/python
import logging
import os
import ssl
import zipfile
from datetime import datetime
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def get_config():
    # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_config.json"), "r") as f:
    #     return json.load(f)
    return json.load('{  "mail_list": [<MAIL LIST>], "subject": "<MAIL-SUBJECT>", "from": "<YOUR_EMAIL>"}')
        

class Postman:
    def __init__(self, log_path=logger):
        self._config = get_config() # create 'config.json' file and reader for all setting needed
        self.zipped_path = r'c:\\temp\\'
        self.s = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        self.logger = logging.getLogger(log_path)
        self.logger.name = self.__class__.__name__
        self.password = "<PASSWORD>"

    def send_mail(self, html_report, test_name='', attachment_dir=''):
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = self._config['subject']+test_name
        msg_root['From'] = self._config['from']
        msg_root['To'] = ', '.join(self._config['mail_list'])
        msg_root.preamble = 'This is a multi-part message in MIME format.'
        msg_alternative = MIMEMultipart('alternative')
        msg_root.attach(msg_alternative)

        msg_text = MIMEText('This is the alternative plain text message.')
        msg_alternative.attach(msg_text)
        self.logger.info("Iterating results for each test...")
        html_code = html_report
        if attachment_dir != '':
            part = self.attachment(attachment_dir)
            msg_root.attach(part)

        msg_text = MIMEText(html_code, 'html')
        msg_alternative.attach(msg_text)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(r"smtp.gmail.com", 465, context=context) as server:
            server.login(self._config['from'], self.password)
            server.sendmail(
                self._config['from'], self._config['mail_list'], msg_root.as_string()
            )
        return True

    def attachment(self, logs_path):
        date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        zip_file_path = os.path.join(self.zipped_path, 'app_logs_{}.zip'.format(date))
        zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
        if not logs_path.endswith('/'):
            logs_path += '/'
        self._zip_dir(logs_path, zipf)
        zipf.close()
        fp = open(zip_file_path, "rb")
        part = MIMEApplication(fp.read())
        fp.close()
        encoders.encode_base64(part)
        # the miracle
        part.set_payload(part.get_payload())

        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % 'app_logs_{}.zip'.format(logs_path.split('\\')[-1]))
        return part

    def _zip_dir(self, path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))
