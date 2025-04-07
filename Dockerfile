FROM python:3-11.bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN set -eux; \
  apt-get update -y; \
  apt-get upgrade -y; \
  apt-get install -y \
    git \
    nano \
  ;

WORKDIR /app
RUN git clone --branch master https://github.com/riazmey/fuel_cards.git

WORKDIR /app/fuel_cards
RUN pip3 install -r requirements.txt

#CMD ["python", "./fuel_cards/manage.py", "runserver", "0.0.0.0:8000"]
CMD ["bash"]
