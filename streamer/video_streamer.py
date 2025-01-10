import os
import pyrealsense2 as rs
import subprocess

# Retrieve configuration from environment variables
STREAM_WIDTH = int(os.getenv("STREAM_WIDTH", "640"))
STREAM_HEIGHT = int(os.getenv("STREAM_HEIGHT", "480"))
FRAME_RATE = int(os.getenv("FRAME_RATE", "30"))
BITRATE = int(os.getenv("BITRATE", "500"))
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))

# Debug information
print("Configuration:")
print(f"  STREAM_WIDTH: {STREAM_WIDTH}")
print(f"  STREAM_HEIGHT: {STREAM_HEIGHT}")
print(f"  FRAME_RATE: {FRAME_RATE}")
print(f"  BITRATE: {BITRATE}")
print(f"  SERVER_IP: {SERVER_IP}")
print(f"  SERVER_PORT: {SERVER_PORT}")

# Configure the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, STREAM_WIDTH, STREAM_HEIGHT, rs.format.bgr8, FRAME_RATE)

print("Starting RealSense pipeline...")
pipeline.start(config)

# GStreamer command for UDP streaming
gst_command = (
    f"gst-launch-1.0 -v appsrc ! videoconvert ! "
    f"x264enc tune=zerolatency bitrate={BITRATE} speed-preset=superfast ! "
    f"rtph264pay ! udpsink host={SERVER_IP} port={SERVER_PORT}"
)

print(f"Starting GStreamer pipeline with command:\n{gst_command}")
gst_process = subprocess.Popen(gst_command, shell=True, stdin=subprocess.PIPE)

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        # Send raw frame data to GStreamer
        color_image = color_frame.get_data()
        gst_process.stdin.write(color_image)
except KeyboardInterrupt:
    print("Stopping pipeline...")
finally:
    print("Shutting down RealSense pipeline and GStreamer process.")
    pipeline.stop()
    gst_process.terminate()
