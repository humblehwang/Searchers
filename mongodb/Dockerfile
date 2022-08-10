FROM ubuntu:20.04
MAINTAINER Samuel Hwang <z8630076@yahoo.com.tw>

RUN apt-get update \
    &&  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
    
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 

RUN apt-get update -y
RUN apt-get install mongodb -y
RUN apt-get install vim -y
RUN apt-get install iputils-ping -y

COPY . .
EXPOSE 27017
EXPOSE 27018
