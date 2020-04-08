FROM debian:buster

ARG RELEASE=1.6.8

RUN apt -y update && \
    apt -y install git wget curl vim gcc binutils m4 make flex bison libncurses5-dev libreadline-dev python3.7-dev python3-pip pkg-config libcairo2-dev procps supervisor

RUN cd /root && \
    wget ftp://bird.network.cz/pub/bird/bird-${RELEASE}.tar.gz && \
    tar -xzvf bird-${RELEASE}.tar.gz && \
    cd bird-${RELEASE} && \
    ./configure && \
    make && \
    make install

RUN cd /root/bird-${RELEASE} && \
    ./configure --enable-ipv6 && \
    make && \
    make install

ADD ./bird /opt/routers/bird
ADD ./helpers /opt/routers/helpers
ADD ./configure.py /opt/routers/configure.py
ADD ./bird/supervisord.conf /opt/routers/supervisord.conf
ADD ./bird/entrypoint.sh /opt/routers/entrypoint.sh

RUN pip3 install --upgrade pip && \
    pip3 install -r /opt/routers/bird/requirements.txt

RUN mkdir /etc/bird

WORKDIR /opt/routers

EXPOSE 179

ENTRYPOINT ["/opt/routers/entrypoint.sh"]
