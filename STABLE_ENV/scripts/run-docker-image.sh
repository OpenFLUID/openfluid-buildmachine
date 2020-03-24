#!/bin/sh

xhost +

DOCKER_OPTIONS="\
-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
-v $1:/shared/scripts \
-v $2:/shared/build:rw \
-v $3:/shared/src \
-e DISPLAY=unix$DISPLAY \
"

docker run -i --rm $DOCKER_OPTIONS -t $4 $5
#docker run -i --rm $DOCKER_OPTIONS -t $1 python3 /shared/openfluid-buildmachine/dummyLaunch.py
#docker run -i --rm $DOCKER_OPTIONS -t $1 "ls /shared/"

# -v /home/thoniarm/Documents/PROJEKTS/OF_FACTORY/GitRepositories/development:/home/openfluid/development \
# -v /home/thoniarm/Documents/PROJEKTS/OF_FACTORY/GitRepositories/integration:/home/openfluid/integration \