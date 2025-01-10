# Robot Dockerfile (robot/Dockerfile)
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    librealsense2-utils \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    v4l-utils && \
    apt-get clean

# Install RealSense Python bindings
RUN pip install pyrealsense2

# Copy script
WORKDIR /app
COPY video_streamer.py .

CMD ["python", "video_streamer.py"]
