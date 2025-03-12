import gi
import os
import traceback
import logging

import subprocess
import re

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def find_realsense_color_camera():
    """Automatically identify the RealSense color camera device."""
    try:
        result = subprocess.run(["v4l2-ctl", "--list-devices"], text=True, capture_output=True, check=True)
        devices_output = result.stdout

        realsense_devices = []
        current_device = None
        for line in devices_output.splitlines():
            if "RealSense" in line:
                current_device = []
            elif current_device is not None:
                match = re.search(r"/dev/video\d+", line)
                if match:
                    current_device.append(match.group(0))
                if not line.strip():  # End of device section
                    realsense_devices.extend(current_device)
                    current_device = None

        for device in realsense_devices:
            try:
                result = subprocess.run(
                    ["v4l2-ctl", f"--device={device}", "--list-formats-ext"],
                    text=True, capture_output=True, check=True,
                )
                if "YUYV" in result.stdout or "MJPEG" in result.stdout:
                    logger.info(f"Color camera found: {device}")
                    return device
            except subprocess.CalledProcessError:
                pass

        logger.error("No RealSense color camera with YUYV format found.")
        return None
    except Exception as e:
        logger.error(f"An error occurred during detection: {e}")
        return None
    
def on_message(bus, message, loop):
    """Callback for GStreamer bus messages."""
    msg_type = message.type

    if msg_type == Gst.MessageType.EOS:
        logger.info("End of stream")
        loop.quit()
    elif msg_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        logger.error(f"{err.message} ({debug})")
        loop.quit()
    elif msg_type == Gst.MessageType.WARNING:
        warn, debug = message.parse_warning()
        logger.warning(f"{warn.message} ({debug})")
    elif msg_type == Gst.MessageType.STATE_CHANGED:
        old, new, _ = message.parse_state_changed()
        logger.info(f"'{message.src.get_name()}' changed from {old.value_name} to {new.value_name}")
    elif msg_type == Gst.MessageType.BUFFERING:
        percent = message.parse_buffering()
        logger.info(f"{percent}%")
    else:
        logger.info(f"Message: {Gst.MessageType.get_name(msg_type)}")


def start_streaming(device, width, height, framerate, host, port, use_d435i):
    """Start streaming video over UDP."""
    Gst.init(None)

    if use_d435i:
        pipeline_desc = (
            f"v4l2src device={device} ! "
            f"video/x-raw, format=YUY2, width={width}, height={height}, framerate={framerate}/1 ! "
            "jpegenc ! "
            "queue ! "
            "rtpjpegpay ! "
            f"udpsink host={host} port={port} sync=false"
        )
        # pipeline_desc = (
        #     f"v4l2src device={device} ! "
        #     f"video/x-raw, format=YUY2, width={width}, height={height}, framerate={framerate}/1 ! "
        #     "videoconvert ! "
        #     "x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! "
        #     "rtph264pay ! "
        #     f"udpsink host={host} port={port} sync=false"
        # )
    else:
        pipeline_desc = (
            f"v4l2src device={device} ! "
            f"image/jpeg, width={width}, height={height}, framerate={framerate}/1 ! "
            "queue ! "
            "rtpjpegpay ! "
            f"udpsink host={host} port={port} sync=false"
        )

    logger.info("Pipeline description:")
    print(pipeline_desc)
    pipeline = Gst.parse_launch(pipeline_desc)

    # Set up bus to handle messages
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    loop = GLib.MainLoop()
    bus.connect("message", on_message, loop)

    try:
        # Start the pipeline
        pipeline.set_state(Gst.State.PLAYING)
        logger.info(f"Streaming to {host}:{port} ... Press Ctrl+C to stop.")
        loop.run()
    except KeyboardInterrupt:
        logger.info("\n[INFO] Streaming interrupted. Shutting down...")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        pipeline.set_state(Gst.State.NULL)
        loop.quit()
        logger.info("Pipeline shut down.")

if __name__ == "__main__":
    use_d435i = os.getenv("USE_D435I", "False").lower() == "true"
    device = None
    if use_d435i:
        device = find_realsense_color_camera()
        if not device:
            logger.error("No suitable RealSense color camera found. Exiting.")
            exit(1)
    else:
        device = os.getenv("DEVICE", "/dev/video0")

    # Read environment variables
    width = int(os.getenv("WIDTH", 640))
    height = int(os.getenv("HEIGHT", 480))
    framerate = int(os.getenv("FRAMERATE", 30))
    host = os.getenv("RECEIVER_IP", "127.0.0.1")
    port = int(os.getenv("RECEIVER_PORT", 5554))

    logger.info("Starting MJPG video stream with the following properties:")
    print(f"  Device:     {device}")
    print(f"  Resolution: {width}x{height}")
    print(f"  Framerate:  {framerate}")
    print(f"  Receiver:   {host}:{port}")
    print(f"  Use D435i:  {use_d435i}")

    # Pass parameters to the streaming function
    start_streaming(device, width, height, framerate, host, port, use_d435i)