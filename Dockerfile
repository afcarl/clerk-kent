FROM python:3.5.1-alpine
MAINTAINER Tim Head <betatim@gmail.com>

RUN pip install requests

ADD app.py /tmp/app.py
EXPOSE 5555

ENTRYPOINT ["python", "/tmp/app.py"]
