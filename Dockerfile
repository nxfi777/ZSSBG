FROM python:3.10-alpine

ENV OPENAI_API_KEY='< YOUR OPENAI API KEY HERE >'

# Controls the range of possible integers
ENV BYTE_LENGTH=8

# Number of integers to generate
ENV N_INDEX=256

WORKDIR /usr/src/app

COPY truerandom.py ./

RUN pip install --no-cache-dir openai statsmodels

CMD [ "python", "-u", "./truerandom.py" ]
