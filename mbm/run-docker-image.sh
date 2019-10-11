#!/bin/sh

xhost +

DOCKER_OPTIONS="\
-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
-e DISPLAY=unix$DISPLAY \
"

docker run -i --rm -v $1:/shared $DOCKER_OPTIONS -t $2 $3
#docker run -i --rm $DOCKER_OPTIONS -t $1 python3 /shared/openfluid-buildmachine/dummyLaunch.py
#docker run -i --rm $DOCKER_OPTIONS -t $1 "ls /shared/"

# -v /home/thoniarm/Documents/PROJEKTS/OF_FACTORY/GitRepositories/development:/home/openfluid/development \
# -v /home/thoniarm/Documents/PROJEKTS/OF_FACTORY/GitRepositories/integration:/home/openfluid/integration \