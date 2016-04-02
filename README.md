# Clerk Kent

:wave:

Hi, I'm Clerk Kent. My superpower is introducing people by email.


# Setup

You will need a [Mailgun](//mailgun.com) account.

To deploy Clerk Kent in a docker container:
```
docker build -t clerk-kent .
docker run -d -p 5555:5555 -e MG_API_KEY=$MG_API_KEY clerk-kent
```

Clerk is now ready to introduce you by POST'ing to `http://host:5555/connect`
using the `them` parameter to pass the email address of the person you want
to get contacted.
