# Dockerfile for running go_webserver.py as a web service

FROM python:2.7.15-alpine

# Add dependencies for building psycopg2,
# if using a Python repo that does not have the binary version
RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# run as non-root
RUN adduser -D myuser
USER myuser

CMD ["python", "./go_webserver.py"]

# default port is 8000, but can be over-ridden with $PORT env variable
EXPOSE 8000
