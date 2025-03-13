#!/bin/bash

# Default values
MTX_WEBRTCADDITIONALHOSTS="192.168.1.166"
RECEIVER_PORT="5554"
WIDTH="1920"
HEIGHT="1080"
BITRATE="10000"
SPEED_PRESET="ultrafast"
SRT_IP="mediamtx"
SRT_PORT="8890"
STREAM_NAME="go1_camera"
ENABLE_MONITORING="true"
USE_H264="false"

# Parse optional arguments
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --webrtc-additional-hosts)
      MTX_WEBRTCADDITIONALHOSTS="$2"
      shift 2;;
    --receiver-port)
      RECEIVER_PORT="$2"
      shift 2;;
    --width)
      WIDTH="$2"
      shift 2;;
    --height)
      HEIGHT="$2"
      shift 2;;
    --bitrate)
      BITRATE="$2"
      shift 2;;
    --speed-preset)
      SPEED_PRESET="$2"
      shift 2;;
    --srt-ip)
      SRT_IP="$2"
      shift 2;;
    --srt-port)
      SRT_PORT="$2"
      shift 2;;
    --stream-name)
      STREAM_NAME="$2"
      shift 2;;
    --enable-monitoring)
      ENABLE_MONITORING="true"
      shift 2;;
    --use-h264)
      USE_H264="true"
      shift 2;;     
    --)
      shift
      break;;
    *)
      echo "Unknown option: $1"
      exit 1;;
  esac
done

# Overwrite .env file with updated values
cat << EOF > .env
MTX_WEBRTCADDITIONALHOSTS=$MTX_WEBRTCADDITIONALHOSTS
RECEIVER_PORT=$RECEIVER_PORT
WIDTH=$WIDTH
HEIGHT=$HEIGHT
BITRATE=$BITRATE
SPEED_PRESET=$SPEED_PRESET
SRT_IP=$SRT_IP
SRT_PORT=$SRT_PORT
STREAM_NAME=$STREAM_NAME
ENABLE_MONITORING=$ENABLE_MONITORING
USE_H264=$USE_H264
EOF

# Run docker-compose with updated environment
docker compose -f docker-compose-edge.yml up -d
