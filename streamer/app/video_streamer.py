import gi
import os
import traceback

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

def on_message(bus, message, loop):
    """Callback for GStreamer bus messages."""
    msg_type = message.type

    if msg_type == Gst.MessageType.EOS:
        print("[INFO] End of stream")
        loop.quit()
    elif msg_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"[ERROR] {err.message} ({debug})")
        loop.quit()
    elif msg_type == Gst.MessageType.WARNING:
        warn, debug = message.parse_warning()
        print(f"[WARNING] {warn.message} ({debug})")
    elif msg_type == Gst.MessageType.STATE_CHANGED:
        old, new, _ = message.parse_state_changed()
        print(f"[STATE] '{message.src.get_name()}' changed from {old.value_name} to {new.value_name}")
    elif msg_type == Gst.MessageType.BUFFERING:
        percent = message.parse_buffering()
        print(f"[BUFFERING] {percent}%")
    else:
        print(f"[INFO] Message: {Gst.MessageType.get_name(msg_type)}")


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

    print(f"[PIPELINE] {pipeline_desc}")
    pipeline = Gst.parse_launch(pipeline_desc)

    # Set up bus to handle messages
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    loop = GLib.MainLoop()
    bus.connect("message", on_message, loop)

    try:
        # Start the pipeline
        pipeline.set_state(Gst.State.PLAYING)
        print(f"[INFO] Streaming to {host}:{port} ... Press Ctrl+C to stop.")
        loop.run()
    except KeyboardInterrupt:
        print("\n[INFO] Streaming interrupted. Shutting down...")
    except Exception as e:
        print(f"[EXCEPTION] An error occurred: {e}")
        traceback.print_exc()
    finally:
        pipeline.set_state(Gst.State.NULL)
        loop.quit()
        print("[INFO] Pipeline shut down.")

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
