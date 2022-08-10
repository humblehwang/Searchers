#!/bin/bash
sudo docker image build -t mongodb . --no-cache

sudo docker run -d -it --privileged --mount type=bind,source="/home/Humble/Code/PhD/mongodb_data",target=/home -p 27018:27017 mongodb bash start_mongodb.sh
#mongodb need to start in container, that is we need to go into container and run command
