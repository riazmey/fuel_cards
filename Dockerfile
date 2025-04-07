FROM alpine:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y git python3 python3-pip mc nano apt-utils

WORKDIR /app
RUN git clone --branch master https://github.com/riazmey/fuel_cards.git

WORKDIR /app/fuel_cards
RUN pip3 install -r requirements.txt

#CMD ["python", "./fuel_cards/manage.py", "runserver", "0.0.0.0:8000"]
CMD ["bash"]
