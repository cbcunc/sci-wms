FROM phusion/baseimage:0.9.18
# Use baseimage-docker's init system
CMD ["/sbin/my_init"]

MAINTAINER Kyle Wilcox <kyle@axiomdatascience.com>
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y \
    binutils \
    build-essential \
    bzip2 \
    ca-certificates \
    git \
    libglib2.0-0 \
    libkeyutils1 \
    libproj-dev \
    libsm6 \
    libxext6 \
    libxrender1 \
    pwgen \
    redis-server \
    wget \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Setup CONDA (https://hub.docker.com/r/continuumio/miniconda3/~/dockerfile/)
ENV MINICONDA_VERSION 3.16.0
ENV CONDA_VERSION 3.19.0

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-$MINICONDA_VERSION-Linux-x86_64.sh && \
    /bin/bash /Miniconda3-$MINICONDA_VERSION-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-$MINICONDA_VERSION-Linux-x86_64.sh && \
    /opt/conda/bin/conda install --yes conda==$CONDA_VERSION
ENV PATH /opt/conda/bin:$PATH

# Install requirements
COPY requirements*.txt /tmp/
RUN conda install -c ioos -c axiom-data-science --file /tmp/requirements.txt
RUN conda install -c ioos -c axiom-data-science --file /tmp/requirements-prod.txt
RUN conda install -c rustychris libspatialindex

#RUN mkdir -p /etc/cron.d/
#COPY docker/crontab/* /etc/cron.d/
#RUN chmod 644 /etc/cron.d/*

RUN mkdir -p /etc/my_init.d
COPY docker/init/* /etc/my_init.d/
RUN chmod +x /etc/my_init.d/*

#COPY docker/scripts/* /usr/local/bin/
#RUN chmod +x /usr/local/bin/*

# Redis
RUN mkdir -p /etc/service/redis
COPY docker/service/redis.sh /etc/service/redis/run
RUN chmod +x /etc/service/redis/run
RUN sed -i 's/daemonize yes/daemonize no/g' /etc/redis/redis.conf
#RUN sed -i 's/bind 127.0.0.1/# bind 127.0.0.1/g' /etc/redis/redis.conf

# Gunicorn
RUN mkdir -p /etc/service/gunicorn
COPY docker/service/gunicorn.sh /etc/service/gunicorn/run
RUN chmod +x /etc/service/gunicorn/run

# Flower
RUN mkdir -p /etc/service/flower
COPY docker/service/flower.sh /etc/service/flower/run
RUN chmod +x /etc/service/flower/run

# Worker
RUN mkdir -p /etc/service/worker
COPY docker/service/worker.sh /etc/service/worker/run
RUN chmod +x /etc/service/worker/run

ENV WEB_PORT 7002
ENV FLOWER_PORT 5555
EXPOSE $WEB_PORT $FLOWER_PORT

WORKDIR /sciwms
ENV SCIWMS_ROOT /sciwms
RUN mkdir -p "$SCIWMS_ROOT"
COPY . $SCIWMS_ROOT
RUN rm -f $SCIWMS_ROOT/sciwms/db/sci-wms.db

ENV DJANGO_SETTINGS_MODULE sciwms.settings.prod
VOLUME ["/data"]
VOLUME ["$SCIWMS_ROOT/sciwms/settings/local"]
VOLUME ["$SCIWMS_ROOT/wms/topology"]
VOLUME ["$SCIWMS_ROOT/sciwms/db"]
