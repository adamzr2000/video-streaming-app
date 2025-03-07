import gi
import os
import traceback
import logging

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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


def start_streaming(device, width, height, framerate, host, port):
    """Start streaming MJPG video over UDP."""
    Gst.init(None)

    pipeline_desc = (
        f"v4l2src device={device} ! "
        f"image/jpeg, width={width}, height={height}, framerate={framerate}/1 ! "
        "queue ! "
        "rtpjpegpay ! "
        f"udpsink host={host} port={port} sync=false"
    )

    print(f"{pipeline_desc}")
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
    # Read environment variables
    device = os.getenv("DEVICE", "/dev/video0")
    width = int(os.getenv("WIDTH", 640))
    height = int(os.getenv("HEIGHT", 480))
    framerate = int(os.getenv("FRAMERATE", 30))
    host = os.getenv("RECEIVER_IP", "127.0.0.1")
    port = int(os.getenv("RECEIVER_PORT", 5554))

    print("[CONFIG] Starting MJPG video stream with the following properties:")
    print(f"  Device:     {device}")
    print(f"  Resolution: {width}x{height}")
    print(f"  Framerate:  {framerate}")
    print(f"  Receiver:   {host}:{port}")

    # Pass parameters to the streaming function
    start_streaming(device, width, height, framerate, host, port)
