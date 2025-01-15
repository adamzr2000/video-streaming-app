import pyrealsense2 as rs
import numpy as np
import cv2
from flask import Flask, Response

app = Flask(__name__)

# Configure the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start the pipeline
pipeline_profile = pipeline.start(config)

# Get connected device information
device = pipeline_profile.get_device()
print(f"Connected to device: {device.get_info(rs.camera_info.name)}")
print(f"Serial number: {device.get_info(rs.camera_info.serial_number)}")
print(f"Firmware version: {device.get_info(rs.camera_info.firmware_version)}")

def generate_frames():
    """
    Generator function to yield frames from the RealSense camera as JPEGs.
    """
    try:
        while True:
            # Wait for a frame
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()

            if not color_frame:
                continue

            # Convert to NumPy array
            color_image = np.asanyarray(color_frame.get_data())

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', color_image)
            frame = buffer.tobytes()

            # Yield the frame in a format suitable for Flask streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    except Exception as e:
        print(f"An error occurred in the frame generator: {e}")
    finally:
        print("Stopping RealSense pipeline...")
        pipeline.stop()

@app.route('/video_feed')
def video_feed():
    """
    Flask route to stream video frames.
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
