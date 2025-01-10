import os
import subprocess
from flask import Flask, Response

app = Flask(__name__)

# Retrieve configuration from environment variable
UDP_PORT = int(os.getenv("UDP_PORT", "5000"))

# Debug information
print("Configuration:")
print(f"  UDP_PORT: {UDP_PORT}")

# GStreamer command to receive and forward the stream
gst_command = (
    f"gst-launch-1.0 -v udpsrc port={UDP_PORT} caps='application/x-rtp, media=video, encoding-name=H264, payload=96' "
    f"! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink"
)

gst_process = None


@app.route('/start_stream')
def start_stream():
    """Starts the GStreamer pipeline."""
    global gst_process
    if gst_process is None:
        print("Starting GStreamer pipeline...")
        gst_process = subprocess.Popen(gst_command, shell=True)
        return "Stream started"
    print("Stream already running.")
    return "Stream already running"


@app.route('/stop_stream')
def stop_stream():
    """Stops the GStreamer pipeline."""
    global gst_process
    if gst_process:
        print("Stopping GStreamer pipeline...")
        gst_process.terminate()
        gst_process = None
        return "Stream stopped"
    print("No stream to stop.")
    return "No stream to stop"


@app.route('/')
def home():
    """Home endpoint providing basic instructions."""
    return Response(
        "Edge Server running. Use /start_stream to start and /stop_stream to stop."
    )


if __name__ == '__main__':
    # Retrieve Flask server configuration
    HOST = "0.0.0.0"
    PORT = 8000

    print(f"Starting Flask server on {HOST}:{PORT}...")
    app.run(host=HOST, port=PORT)
