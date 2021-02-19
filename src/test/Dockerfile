FROM practice:local

RUN pip install -U pytest

COPY ./src/connection /connection
COPY ./src/practice /practice
COPY ./src/test /test

ENTRYPOINT ["pytest", "-p", "no:cacheprovider", "/test"]
