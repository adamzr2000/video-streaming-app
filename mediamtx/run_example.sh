#!/bin/bash

docker run --rm -it \
  -p 8890:8890/udp \
  -p 8889:8889 \
  -p 8189:8189 \
  --name mediamtx \
  -e MTX_WEBRTCADDITIONALHOSTS="10.5.1.21" \
  bluenviron/mediamtx:latest