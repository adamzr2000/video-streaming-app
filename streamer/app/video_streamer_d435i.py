import gi
import os
import subprocess
import traceback
import re

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib


def find_realsense_color_camera():
    """Automatically identify the RealSense color camera device."""
    try:
        # Step 1: Get list of video devices
        result = subprocess.run(["v4l2-ctl", "--list-devices"], text=True, capture_output=True, check=True)
        devices_output = result.stdout

        # Step 2: Find RealSense-related devices
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

        # Step 3: Check each RealSense device for YUYV format
        for device in realsense_devices:
            try:
                result = subprocess.run(
                    ["v4l2-ctl", f"--device={device}", "--list-formats-ext"],
                    text=True, capture_output=True, check=True,
                )
                if "YUYV" in result.stdout:
                    print(f"[INFO] Color camera found: {device}")
                    return device
            except subprocess.CalledProcessError:
                pass

        print("[ERROR] No RealSense color camera with YUYV format found.")
        return None
    except Exception as e:
        print(f"[ERROR] An error occurred during detection: {e}")
        return None


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
    """Start streaming YUYV video over UDP using Video4Linux2."""
    Gst.init(None)

    pipeline_desc = (
        f"v4l2src device={device} ! "
        f"video/x-raw, format=YUY2, width={width}, height={height}, framerate={framerate}/1 ! "
        "jpegenc ! "  # Convert YUYV to MJPG
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
    # Detect the RealSense color camera device
    device = find_realsense_color_camera()
    if not device:
        print("[ERROR] No suitable color camera found. Exiting.")
        exit(1)

    # Read other environment variables
    width = int(os.getenv("WIDTH", 1280))
    height = int(os.getenv("HEIGHT", 720))
    framerate = int(os.getenv("FRAMERATE", 30))
    host = os.getenv("RECEIVER_IP", "127.0.0.1")
    port = int(os.getenv("RECEIVER_PORT", 5554))

    print("[CONFIG] Starting video stream with the following properties:")
    print(f"  Device:     {device}")
    print(f"  Resolution: {width}x{height}")
    print(f"  Framerate:  {framerate}")
    print(f"  Receiver:   {host}:{port}")

    # Pass parameters to the streaming function
    start_streaming(device, width, height, framerate, host, port)
