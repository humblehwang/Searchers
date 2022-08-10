#!/bin/bash
#utility: 啟動redis server

#透過conf檔啟動redis server
redis-server redis.conf

#無限迴圈，為了防止container被停止
while [ 1 ]
do
    ping localhost
done
