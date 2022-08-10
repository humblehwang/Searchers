#!/bin/bash
#utility: 建立以及啟動container

# build docker image by Dockerfile without cache
sudo docker image build -t redis . --no-cache

#run container by docker image(上一步驟建立的docker image)
#-p 為要bind的port
#-v 為將資料夾/var/lib/redi(redis儲存的資料夾)寫入到實體機器上
sudo docker run -d -it --privileged --log-opt max-size=1g -p 6379:6379  -v /var/lib/redis redis bash start_redis.sh
