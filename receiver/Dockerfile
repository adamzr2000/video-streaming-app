# Edge Server Dockerfile (edge/Dockerfile)
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav && \
    apt-get clean

# Install Flask
RUN pip install flask

# Copy script
WORKDIR /app
COPY video_receiver.py .

CMD ["python", "video_receiver.py"]
