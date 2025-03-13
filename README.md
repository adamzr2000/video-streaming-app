# Video Streaming System

**Author:** Adam Zahir Rodriguez

1. **Streamer**: Captures video from a webcam, encodes it as MJPG, and streams it over UDP to `receiver-transcoder` component.
2. **Receiver-Transcoder**: Receives the MJPG stream, decodes it, encodes it as H.264, and streams it via SRT to `mediamtx` component.
3. **MediaMTX**: Acts as the media server, handling and redistributing the SRT stream.


## Usage
```bash
docker compose up -d
```

[http://127.0.0.1:8889/test_stream](http://127.0.0.1:8889/test_stream)


```bash
docker compose down
```

## Usage (5TONIC)


### Edge
```bash
./run_example_edge.sh --stream-name go1_camera --enable-monitoring true --webrtc-additional-hosts 10.5.1.21
```

```bash
./stop_example_edge.sh
```

### Robot
```bash
cd streamer
./run_example.sh --width 1920 --height 1080 --framerate 30 --receiver-ip 10.5.1.21 --receiver-port 5554 --device /dev/video0
```

```bash
docker kill video-streamer
```