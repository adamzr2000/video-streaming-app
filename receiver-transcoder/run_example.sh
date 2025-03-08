#!/bin/bash

# Set environment variables
RECEIVER_PORT="5554"
WIDTH="1280"
HEIGHT="720"
BITRATE="2000"
SPEED_PRESET="ultrafast"
SRT_IP="10.5.1.21"
SRT_PORT="8890"
STREAM_NAME="test_stream"
ENABLE_MONITORING="true"

# Run the Docker container
docker run --rm -it \
  --name video-receiver-transcoder \
  -p 5554:5554/udp \
  -e RECEIVER_PORT="$RECEIVER_PORT" \
  -e WIDTH="$WIDTH" \
  -e HEIGHT="$HEIGHT" \
  -e BITRATE="$BITRATE" \
  -e SPEED_PRESET="$SPEED_PRESET" \
  -e SRT_IP="$SRT_IP" \
  -e SRT_PORT="$SRT_PORT" \
  -e STREAM_NAME="$STREAM_NAME" \
  -e ENABLE_MONITORING="$ENABLE_MONITORING" \
  -v ./app:/app/ \
  video-receiver-transcoder
