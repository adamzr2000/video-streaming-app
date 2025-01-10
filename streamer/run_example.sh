#!/bin/bash

# Set environment variables
STREAM_WIDTH=${STREAM_WIDTH:-640}
STREAM_HEIGHT=${STREAM_HEIGHT:-480}
FRAME_RATE=${FRAME_RATE:-30}
BITRATE=${BITRATE:-500}
SERVER_IP=${SERVER_IP:-127.0.0.1}
SERVER_PORT=${SERVER_PORT:-5000}

# Print the configuration
echo "Starting the container with the following configuration:"
echo "  STREAM_WIDTH: $STREAM_WIDTH"
echo "  STREAM_HEIGHT: $STREAM_HEIGHT"
echo "  FRAME_RATE: $FRAME_RATE"
echo "  BITRATE: $BITRATE"
echo "  SERVER_IP: $SERVER_IP"
echo "  SERVER_PORT: $SERVER_PORT"

# Run the Docker container
docker run --rm \
  --privileged \
  --network=host \
  --name video-streamer \
  -e STREAM_WIDTH="$STREAM_WIDTH" \
  -e STREAM_HEIGHT="$STREAM_HEIGHT" \
  -e FRAME_RATE="$FRAME_RATE" \
  -e BITRATE="$BITRATE" \
  -e SERVER_IP="$SERVER_IP" \
  -e SERVER_PORT="$SERVER_PORT" \
  video-streamer