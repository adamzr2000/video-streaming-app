#!/bin/bash

# Set the default UDP port if not provided
UDP_PORT=${UDP_PORT:-5000}

# Print the configuration
echo "Starting the container with the following configuration:"
echo "  UDP_PORT: $UDP_PORT"


# Run the Docker container
docker run --rm \
  --privileged \
  --network=host \
  --name video-reciever \
  -e UDP_PORT="$UDP_PORT" \
  video-reciever