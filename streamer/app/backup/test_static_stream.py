import gi
import os
import time
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
        logger.info(f"[STATE] '{message.src.get_name()}' changed from {old.value_name} to {new.value_name}")

def start_streaming(image_folder, host, port, interval):
    """Start streaming static images over UDP."""
    Gst.init(None)
    images = ["image1.jpg", "image2.jpg", "image3.jpg", "image4.jpg"]
    image_index = 0
    
    while True:
        image_path = os.path.join(image_folder, images[image_index])
        pipeline_desc = (
            f"filesrc location={image_path} ! "
            "jpegparse ! jpegdec ! videoconvert ! "
            "jpegenc ! rtpjpegpay ! "
            f"udpsink host={host} port={port} sync=false"
        )

        logger.info(f"Streaming image: {image_path} to {host}:{port}")
        pipeline = Gst.parse_launch(pipeline_desc)

        bus = pipeline.get_bus()
        bus.add_signal_watch()
        loop = GLib.MainLoop()
        bus.connect("message", on_message, loop)

        try:
            pipeline.set_state(Gst.State.PLAYING)
            time.sleep(interval)  # Stream each image for 'interval' seconds
        except KeyboardInterrupt:
            logger.info("\nStreaming interrupted. Shutting down...")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            pipeline.set_state(Gst.State.NULL)
            loop.quit()

        image_index = (image_index + 1) % len(images)  # Rotate images

if __name__ == "__main__":
    image_folder = os.getenv("IMAGE_FOLDER", ".")
    host = os.getenv("RECEIVER_IP", "127.0.0.1")
    port = int(os.getenv("RECEIVER_PORT", 5554))
    interval = int(os.getenv("IMAGE_INTERVAL", 2))  # Default: 2 seconds per image

    print("[CONFIG] Starting image stream with the following properties:")
    print(f"  Image Folder: {image_folder}")
    print(f"  Receiver:     {host}:{port}")
    print(f"  Interval:     {interval} sec per image")

    start_streaming(image_folder, host, port, interval)
