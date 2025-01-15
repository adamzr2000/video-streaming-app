#!/bin/bash

# Set environment variables
RECEIVER_PORT="5554"
WIDTH="1280"
HEIGHT="720"
BITRATE="2000"
SPEED_PRESET="ultrafast"
SRT_IP="127.0.0.1"
SRT_PORT="8890"
STREAM_NAME="test_stream"


# Run the Docker container
docker run --rm -it \
  --privileged \
  --network=host \
  --name video-receiver-transcoder \
  -e RECEIVER_PORT="$RECEIVER_PORT" \
  -e WIDTH="$WIDTH" \
  -e HEIGHT="$HEIGHT" \
  -e BITRATE="$BITRATE" \
  -e SPEED_PRESET="$SPEED_PRESET" \
  -e SRT_IP="$SRT_IP" \
  -e SRT_PORT="$SRT_PORT" \
  -e STREAM_NAME="$STREAM_NAME" \
  video-receiver-transcoder 