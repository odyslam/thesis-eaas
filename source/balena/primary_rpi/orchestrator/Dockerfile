FROM balenalib/raspberrypi3-64-alpine-python:3.7-3.7-run
#FROM balenalib/raspberrypi3-64-python:3.7-latest-build

# Install all dependencies
COPY requirements.txt requirements.txt
RUN apk add --no-cache openssh
RUN pip install -U pip
RUN pip install -U --no-cache-dir -r requirements.txt


COPY . /usr/src/app
WORKDIR /usr/src/app

CMD ["python", "app2.py"]