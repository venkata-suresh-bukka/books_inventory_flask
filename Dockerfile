FROM python:3.8-slim-buster

ADD . .

RUN python db_connect.py

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "app.py", "--host=0.0.0.0"]