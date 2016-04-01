import os
import sys

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

Please d to meet you. My name is Clerk Kent, I am an AI that
works for Wild Tree Tech.

You contacted us on our website, so we are reaching out to you
to learn about what it is that made you contact us? We look
forward to helping you.

In our experience scheduling a short phone or skype call is
the best way to kick start the conversation.

What time suits you best?

Clerk
ps. We like getting to know people, so the first meeting is on the house.
--
http://www.wildtreetech.com
"""
MSGTEXT = os.getenv("MSGTEXT", MSGTEXT)

def send_connection_message(connectee):
    r = requests.post(
        "https://api.mailgun.net/v3/mg.wildtreetech.com/messages",
        auth=("api", MG_API_KEY),
        data={"from": "Tim Head <tim@mg.wildtreetech.com>",
              "sender": "Clerk Kent <clerk@mg.wildtreetech.com>",
              "to": [connectee],
              "subject": "Hello from Wild Tree Tech",
              "text": MSGTEXT})
    return r.status_code


class EmailBoss(BaseHTTPRequestHandler):
    server_version = "ClerkKent/0.1"
    previous = deque([], 5)

    def finish_up(self, code):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', 'http://example.com')
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

        connectee = form.getvalue('connectee')
        if connectee is None:
            self.finish_up(500)
            return

        # only connect people we have not recently connected
        # silently swallow requests for reconnections
        status_code = 200
        if connectee not in self.previous:
            self.previous.append(connectee)
            status_code = send_connection_message(connectee)

        self.finish_up(status_code)


def run(server_class=HTTPServer, handler_class=EmailBoss):
    server_address = ('', 5555)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
