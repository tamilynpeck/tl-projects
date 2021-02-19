FROM python:3.7-slim-buster
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y \
  g++ \
  unixodbc \
  unixodbc-bin \
  unixodbc-dev \
  tdsodbc \
  freetds-common \
  freetds-bin \
  freetds-dev
RUN pip install -U pip
RUN pip install pyodbc==4.0.30
RUN pip install -U pandas
RUN pip install -U pyyaml

ENV PYTHONPATH "${PYTHONPATH}:/"

# WORKDIR /work

COPY ./src/practice /practice

ENTRYPOINT ["python", "practice/practice.py"]
