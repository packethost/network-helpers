FROM python:3.7-stretch

RUN apt-get update && apt-get install -y make python-dev && \
    apt-get clean && \
    pip install --upgrade pip && \
    pip install black mypy pytest pylama pytest-cov jmespath

RUN mkdir /opt/tests

ADD . /opt/tests
WORKDIR /opt/tests

RUN pip install -e ./

CMD ["make", "all"]
