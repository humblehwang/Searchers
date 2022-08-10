FROM ubuntu:20.04
MAINTAINER Samuel Hwang <z8630076@yahoo.com.tw>

#安裝redis server
RUN apt-get update -y
RUN apt install redis-server -y

#設定container時區
RUN apt-get update \
    &&  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 

#複製redis設定檔到container
COPY redis.conf redis.conf

#複製redis啟動bash script到container
COPY start_redis.sh start_redis.sh

