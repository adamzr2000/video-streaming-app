# Video Streaming System

1. **Streamer**: Captures video from a webcam, encodes it as MJPG, and streams it over UDP to `receiver-transcoder` component.
2. **Receiver-Transcoder**: Receives the MJPG stream, decodes it, encodes it as H.264, and streams it via SRT to `mediamtx` component.
3. **MediaMTX**: Acts as the media server, handling and redistributing the SRT stream.

```bash
docker compose up -d
```

```bash
[http://127.0.0.1:8889/test_stream](http://127.0.0.1:8889/test_stream)
```

```bash
docker compose down
```