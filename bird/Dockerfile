FROM debian:buster

ARG RELEASE=1.6.8

RUN apt -y update && \
    apt -y install git wget curl vim gcc binutils m4 make flex bison libncurses5-dev libreadline-dev python3.7-dev python3-pip pkg-config libcairo2-dev procps

RUN ln -s /usr/bin/python3.7 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip

RUN cd /root && \
    wget ftp://bird.network.cz/pub/bird/bird-${RELEASE}.tar.gz && \
    tar -xzvf bird-${RELEASE}.tar.gz && \
    cd bird-${RELEASE} && \
    ./configure && \
    make && \
    make install

ADD . /opt/bird

RUN pip install --upgrade pip && \
    pip install -r /opt/bird/requirements.txt

RUN mkdir /etc/bird

WORKDIR /opt/bird

EXPOSE 179

ENTRYPOINT ["/opt/bird/entrypoint.sh"]
