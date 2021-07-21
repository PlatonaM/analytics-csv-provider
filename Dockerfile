FROM python:3-alpine

RUN apk --no-cache add git build-base leveldb-dev

RUN mkdir /storage && mkdir /storage/db && mkdir /storage/data && mkdir /storage/tmp

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["gunicorn", "-b", "0.0.0.0:80", "--workers", "1", "--log-level", "warning", "app:app"]

#CMD ["gunicorn", "-b", "0.0.0.0:80", "--workers", "1", "--threads", "4", "--worker-class", "gthread", "--log-level", "debug", "app:app"]