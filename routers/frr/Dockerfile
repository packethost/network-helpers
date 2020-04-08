FROM debian:buster

RUN apt-get update && \
    apt-get install -y libpcre3-dev apt-transport-https ca-certificates curl wget logrotate libc-ares2 libjson-c3 vim systemd procps libreadline7 gnupg2 lsb-release apt-utils python3.7-dev python3-pip pkg-config libcairo2-dev procps supervisor

RUN curl -s https://deb.frrouting.org/frr/keys.asc | apt-key add - && \
    echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) frr-stable | tee -a /etc/apt/sources.list.d/frr.list

RUN apt-get update && \
    apt-get install -y frr frr-pythontools

ADD . /opt/bgp
ADD ./routers/frr/daemons /etc/frr/daemons

WORKDIR /opt/bgp

RUN pip3 install --upgrade pip setuptools && \
    pip3 install -e /opt/bgp/

EXPOSE 179

ENTRYPOINT ["/opt/bgp/routers/frr/entrypoint.sh"]
