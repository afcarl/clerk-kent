import os
import sys
import random

from cgi import FieldStorage
from collections import deque
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

import requests


MG_API_KEY = os.getenv("MG_API_KEY", None)
if MG_API_KEY is None:
    print("Set the MG_API_KEY environment variable.")
    sys.exit(1)

MSGTEXT = """Hello!

Pleased to meet you. My name is Clerk Kent, I am an artificial
intelligence bot that works for Wild Tree Tech.

We look forward to helping you. You contacted us on our
website, so we are reaching out to you schedule a short
phone or skype call to kick start the conversation.

What time suits you best? Wild Tree Tech's calendar is
setup to show when we are free/busy:

http://bit.ly/wtt-calendar

Pick a time that suits you and reply to this email
to schedule the meeting.

If you have any further questions or comments, simply reply
to this email.

Clerk
ps. We like getting to know people, so the first meeting is on the house.
--
http://www.wildtreetech.com
"""
MSGTEXT = os.getenv("MSGTEXT", MSGTEXT)

SUBJECTS = ["Hello from Wild Tree Tech",
            "Scheduling a free meeting with Wild Tree Tech",
            "Wild Tree Tech wanted to say hello!",
            "Can Wild Tree Tech buy you a (virtual) coffee?",
            "A note from Wild Tree Tech"]

def send_connection_message(them):
    r = requests.post(
        "https://api.mailgun.net/v3/mg.wildtreetech.com/messages",
        auth=("api", MG_API_KEY),
        data={"from": "Tim Head <tim@wildtreetech.com>",
              "bcc": "Tim Head <tim@wildtreetech.com>",
              "sender": "Clerk Kent <clerk@mg.wildtreetech.com>",
              "to": [them],
              "subject": random.choice(SUBJECTS),
              "text": MSGTEXT})
    return r.status_code


class EmailBoss(BaseHTTPRequestHandler):
    server_version = "ClerkKent/0.1"
    previous = deque([], 1)

    def finish_up(self, code):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', 'http://www.wildtreetech.com')
        self.send_header('Connection', 'close')
        self.end_headers()

    def do_POST(self):
        if self.path != '/connect':
            self.finish_up(404)
            return

        form = FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type']}
            )

        them = form.getvalue('them')
        if them is None:
            self.finish_up(500)
            return

        # only connect people we have not recently connected
        # silently swallow requests for reconnections
        status_code = 200
        if them not in self.previous:
            self.previous.append(them)
            status_code = send_connection_message(them)
            print("Emailed %s. MG code: %i", them, status_code)

        else:
            print("We recently emailed %s so skipping them.", them)

        self.finish_up(status_code)


def run(server_class=HTTPServer, handler_class=EmailBoss):
    print("starting up")
    server_address = ('', int(os.getenv('PORT', 5555)))
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
