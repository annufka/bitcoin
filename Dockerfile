FROM python:3.8

RUN mkdir /src
WORKDIR /src
COPY . /src
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
