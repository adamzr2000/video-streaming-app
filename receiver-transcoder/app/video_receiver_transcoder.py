import gi
import os
import time
import traceback
import logging
from functools import partial

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Bandwidth and FPS calculation variables
bw_start_time = time.perf_counter()
fps_start_time = time.perf_counter()
accumulated_bytes = 0
frame_count = 0  
MONITOR_INTERVAL = 1.0


# Initialize logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def on_message(bus, message, loop):
    """Handles GStreamer bus messages."""
    msg_type = message.type

    if msg_type == Gst.MessageType.EOS:
        logger.info("End of stream received.")
        loop.quit()
    elif msg_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        logger.error(f"{err.message}")
        logger.info(f"{debug}")
        loop.quit()
    elif msg_type == Gst.MessageType.WARNING:
        warn, debug = message.parse_warning()
        logger.warning(f"{warn.message}")
        logger.info(f"{debug}")

def monitoring_probe(pad, info, is_fps=False):
    global bw_start_time, fps_start_time, accumulated_bytes, frame_count

    buffer = info.get_buffer()
    if not buffer:
        return Gst.PadProbeReturn.OK

    current_time = time.perf_counter()

    if is_fps:
        frame_count += 1
        if current_time - fps_start_time >= MONITOR_INTERVAL:
            fps = frame_count / (current_time - fps_start_time)
            logger.info(f"FPS: {fps:.2f}")
            frame_count = 0
            fps_start_time = current_time
    else:
        accumulated_bytes += buffer.get_size()
        if current_time - bw_start_time >= MONITOR_INTERVAL:
            bandwidth_mbps = (accumulated_bytes * 8) / ((current_time - bw_start_time) * 1_000_000)
            logger.info(f"Bandwidth: {bandwidth_mbps:.2f} Mbps")
            accumulated_bytes = 0
            bw_start_time = current_time

    return Gst.PadProbeReturn.OK

def start_receiver(port, width, height, bitrate, speed_preset, srt_ip, srt_port, stream_name, enable_monitoring, use_h264):
    """Sets up the GStreamer pipeline for video reception and transcoding."""
    Gst.init(None)

    if use_h264:
        pipeline_desc = (
            f'udpsrc name=source port={port} ! '
            'application/x-rtp, encoding-name=H264, payload=96 ! '
            'rtph264depay ! '
            'h264parse ! '
            'avdec_h264 ! '  # H.264 decoder
            'videoconvert ! '
            'videoscale ! '
            f'video/x-raw, width={width}, height={height} ! '
            f'x264enc name=my_enc bitrate={bitrate} '
            f'speed-preset={speed_preset} key-int-max=10 '
            'bframes=0 tune=zerolatency ! '
            'h264parse ! '
            'mpegtsmux alignment=7 ! '
            f'srtsink uri="srt://{srt_ip}:{srt_port}?streamid=publish:{stream_name}" sync=false'
        )
    else:
        pipeline_desc = (
            f'udpsrc name=source port={port} ! '
            'application/x-rtp, encoding-name=JPEG, payload=26 ! '
            'rtpjpegdepay ! '
            'jpegdec name=jpeg_decoder ! '  # Named for FPS probe
            'videoconvert ! '
            'videoscale ! '
            f'video/x-raw, width={width}, height={height} ! '
            f'x264enc name=my_enc bitrate={bitrate} '
            f'speed-preset={speed_preset} key-int-max=10 '
            'bframes=0 tune=zerolatency ! '
            'h264parse ! '
            'mpegtsmux alignment=7 ! '
            f'srtsink uri="srt://{srt_ip}:{srt_port}?streamid=publish:{stream_name}" sync=false'
        )

    logger.info("Pipeline description:")
    print(pipeline_desc)

    pipeline = Gst.parse_launch(pipeline_desc)
    if not pipeline:
        logger.error("Failed to create GStreamer pipeline.")
        return

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    loop = GLib.MainLoop()
    bus.connect("message", on_message, loop)

    # Attach probes if monitoring is enabled
    if enable_monitoring:
        logger.info("Bandwidth and FPS monitoring is ENABLED.")

        # Bandwidth probe (before decoding)
        udpsrc = pipeline.get_by_name("source")
        if udpsrc:
            src_pad = udpsrc.get_static_pad("src")
            if src_pad:
                src_pad.add_probe(Gst.PadProbeType.BUFFER, partial(monitoring_probe, is_fps=False))

        # FPS probe (after decoding)
        jpegdec = pipeline.get_by_name("jpeg_decoder")
        if jpegdec:
            src_pad = jpegdec.get_static_pad("src")
            if src_pad:
                src_pad.add_probe(Gst.PadProbeType.BUFFER, partial(monitoring_probe, is_fps=True))

    else:
        logger.info("Monitoring is DISABLED.")

    try:
        logger.info("Starting video receiver and transcoder:")
        pipeline.set_state(Gst.State.PLAYING)
        loop.run()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user, stopping...")
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        traceback.print_exc()
    finally:
        pipeline.set_state(Gst.State.NULL)
        loop.quit()
        logger.info("Pipeline stopped.")

if __name__ == "__main__":
    # Read environment variables
    use_h264 = os.getenv("USE_H264", "False").lower() == "true"
    port = int(os.getenv("RECEIVER_PORT", 5554))
    width = int(os.getenv("WIDTH", 640))
    height = int(os.getenv("HEIGHT", 480))
    bitrate = int(os.getenv("BITRATE", 2000))
    speed_preset = os.getenv("SPEED_PRESET", "medium")
    srt_ip = os.getenv("SRT_IP", "127.0.0.1")
    srt_port = int(os.getenv("SRT_PORT", 8890))
    stream_name = os.getenv("STREAM_NAME", "my_stream")
    
    # Enable monitoring only if explicitly set to "true"
    enable_monitoring = os.getenv("ENABLE_MONITORING", "false").lower() == "true"

    logger.info("Video Receiver and Transcoder Configuration:")
    print(f"  Listening port: {port}")
    print(f"  Resolution: {width}x{height}")
    print(f"  Bitrate: {bitrate}")
    print(f"  Speed preset: {speed_preset}")
    print(f"  Mediamtx server: {srt_ip}:{srt_port}")
    print(f"  Stream name: {stream_name}")
    print(f"  Monitoring: {'Enabled' if enable_monitoring else 'Disabled'}")
    print(f"  Use H264:  {use_h264}")

    # Start the receiver
    start_receiver(port, width, height, bitrate, speed_preset, srt_ip, srt_port, stream_name, enable_monitoring, use_h264)
