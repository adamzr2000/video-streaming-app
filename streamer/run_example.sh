#!/bin/bash

# Set environment variables
# WIDTH="1280"
# HEIGHT="720"

WIDTH="640"
HEIGHT="480"

# WIDTH="1920"
# HEIGHT="1080"


FRAMERATE="30"
RECEIVER_IP="127.0.0.1"
RECEIVER_PORT="5554"
DEVICE="/dev/video0"

# Run the Docker container
docker run --rm -it \
  --privileged \
  --network=host \
  --name video-streamer \
  -v ./app:/app/ \
  --group-add video \
  -e WIDTH="$WIDTH" \
  -e HEIGHT="$HEIGHT" \
  -e FRAMERATE="$FRAMERATE" \
  -e RECEIVER_IP="$RECEIVER_IP" \
  -e RECEIVER_PORT="$RECEIVER_PORT" \
  -e DEVICE="$DEVICE" \
  video-streamer \
  python3 video_streamer.py 
