#!/bin/bash

docker run --rm -it \
  -p 8890:8890/udp \
  -p 8889:8889 \
  -p 8189:8189 \
  --name mediamtx \
  bluenviron/mediamtx:latest