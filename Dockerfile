FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y mc nano apt-utils

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./src ./src

CMD ["python", "./fuel_cards/manage.py", "runserver", "0.0.0.0:8000"]
