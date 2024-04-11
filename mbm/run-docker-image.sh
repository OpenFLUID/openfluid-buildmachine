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