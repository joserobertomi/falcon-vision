import streamlit as st
import streamlit.components.v1 as components

def main():
    st.title("🎥 WebSocket Video Streaming Test Client")
    
    # Connection Settings
    st.header("Connection Settings")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ws_url = st.text_input(
            "WebSocket URL:",
            value="ws://localhost:8000/api/v1/ws/video/client123",
            placeholder="ws://localhost:8000/api/v1/ws/video/your-client-id"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
    
    # Streaming Settings
    st.subheader("Streaming Settings")
    fps = st.slider("Streaming FPS:", min_value=1, max_value=60, value=10)
    
    st.divider()
    
    # Embed the WebSocket client
    websocket_client_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: transparent;
            }}

            .status {{
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 10px;
                text-align: center;
                font-weight: bold;
            }}

            .status.connected {{
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}

            .status.disconnected {{
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}

            .status.connecting {{
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }}

            .controls {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
                margin-bottom: 20px;
            }}

            button {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s;
            }}

            button:hover {{
                background-color: #45a049;
            }}

            button:disabled {{
                background-color: #cccccc;
                cursor: not-allowed;
            }}

            button.disconnect {{
                background-color: #f44336;
            }}

            button.disconnect:hover {{
                background-color: #da190b;
            }}

            .video-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }}

            .video-section {{
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 4px;
            }}

            video, img {{
                width: 100%;
                max-width: 100%;
                border: 2px solid #ddd;
                border-radius: 4px;
                background-color: #000;
                min-height: 300px;
            }}

            .stats {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin-bottom: 20px;
            }}

            .stat-card {{
                background-color: #f0f0f0;
                padding: 15px;
                border-radius: 4px;
                text-align: center;
            }}

            .stat-value {{
                font-size: 32px;
                font-weight: bold;
                color: #4CAF50;
            }}

            .stat-label {{
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }}

            #log {{
                background-color: #1e1e1e;
                color: #d4d4d4;
                padding: 15px;
                border-radius: 4px;
                height: 250px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}

            h3 {{
                color: #333;
                margin-top: 0;
            }}
        </style>
    </head>
    <body>
        <div id="status" class="status disconnected">
            Disconnected
        </div>

        <div class="controls">
            <button id="connectBtn" onclick="connect()">Connect</button>
            <button id="disconnectBtn" class="disconnect" onclick="disconnect()" disabled>Disconnect</button>
            <button onclick="sendPing()">Send Ping</button>
            <button onclick="requestStatus()">Request Status</button>
            <button onclick="clearLog()">Clear Log</button>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="framesSent">0</div>
                <div class="stat-label">Frames Sent</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="framesReceived">0</div>
                <div class="stat-label">Frames Received</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="fps">0</div>
                <div class="stat-label">FPS</div>
            </div>
        </div>

        <div class="video-container">
            <div class="video-section">
                <h3>Local Camera</h3>
                <video id="localVideo" autoplay playsinline muted></video>
                <div class="controls" style="margin-top: 10px;">
                    <button onclick="startCamera()">Start Camera</button>
                    <button onclick="stopCamera()">Stop Camera</button>
                    <button onclick="startStreaming()">Start Streaming</button>
                    <button onclick="stopStreaming()">Stop Streaming</button>
                </div>
            </div>

            <div class="video-section">
                <h3>Received Frames</h3>
                <img id="receivedFrame" src="" alt="Received video frame will appear here">
            </div>
        </div>

        <h3>Console Log</h3>
        <div id="log"></div>

        <script>
            let ws = null;
            let localStream = null;
            let streamingInterval = null;
            let framesSent = 0;
            let framesReceived = 0;
            let fpsCounter = 0;
            let lastFpsUpdate = Date.now();

            const WS_URL = "{ws_url}";
            const TARGET_FPS = {fps};

            function log(message, type = 'info') {{
                const logDiv = document.getElementById('log');
                const timestamp = new Date().toLocaleTimeString();
                const colors = {{
                    info: '#4CAF50',
                    error: '#f44336',
                    warning: '#ff9800',
                    success: '#2196F3'
                }};
                const color = colors[type] || colors.info;
                logDiv.innerHTML += `<span style="color: ${{color}}">[[${{timestamp}}]]</span> ${{message}}\\n`;
                logDiv.scrollTop = logDiv.scrollHeight;
            }}

            function clearLog() {{
                document.getElementById('log').innerHTML = '';
            }}

            function updateStatus(status, className) {{
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = status;
                statusDiv.className = 'status ' + className;
            }}

            function updateStats() {{
                document.getElementById('framesSent').textContent = framesSent;
                document.getElementById('framesReceived').textContent = framesReceived;

                const now = Date.now();
                if (now - lastFpsUpdate >= 1000) {{
                    document.getElementById('fps').textContent = fpsCounter;
                    fpsCounter = 0;
                    lastFpsUpdate = now;
                }}
            }}

            function connect() {{
                if (ws && ws.readyState === WebSocket.OPEN) {{
                    log('Already connected', 'warning');
                    return;
                }}

                log(`Connecting to ${{WS_URL}}...`, 'info');
                updateStatus('Connecting...', 'connecting');

                try {{
                    ws = new WebSocket(WS_URL);

                    ws.onopen = () => {{
                        log('WebSocket connection established', 'success');
                        updateStatus('Connected', 'connected');
                        document.getElementById('connectBtn').disabled = true;
                        document.getElementById('disconnectBtn').disabled = false;
                    }};

                    ws.onmessage = async (event) => {{
                        if (event.data instanceof Blob) {{
                            framesReceived++;
                            fpsCounter++;
                            updateStats();

                            const url = URL.createObjectURL(event.data);
                            const img = document.getElementById('receivedFrame');
                            if (img.src) {{
                                URL.revokeObjectURL(img.src);
                            }}
                            img.src = url;

                            log(`Received video frame (${{event.data.size}} bytes)`, 'info');
                        }} else {{
                            try {{
                                const data = JSON.parse(event.data);
                                log(`Received: ${{JSON.stringify(data, null, 2)}}`, 'success');
                            }} catch (e) {{
                                log(`Received text: ${{event.data}}`, 'info');
                            }}
                        }}
                    }};

                    ws.onerror = (error) => {{
                        log(`WebSocket error: ${{error}}`, 'error');
                    }};

                    ws.onclose = () => {{
                        log('WebSocket connection closed', 'warning');
                        updateStatus('Disconnected', 'disconnected');
                        document.getElementById('connectBtn').disabled = false;
                        document.getElementById('disconnectBtn').disabled = true;
                        ws = null;
                    }};
                }} catch (error) {{
                    log(`Connection error: ${{error.message}}`, 'error');
                    updateStatus('Error', 'disconnected');
                }}
            }}

            function disconnect() {{
                if (ws) {{
                    stopStreaming();
                    ws.close();
                    log('Disconnecting...', 'info');
                }}
            }}

            function sendPing() {{
                if (!ws || ws.readyState !== WebSocket.OPEN) {{
                    log('Not connected', 'error');
                    return;
                }}
                ws.send(JSON.stringify({{ action: 'ping' }}));
                log('Sent ping', 'info');
            }}

            function requestStatus() {{
                if (!ws || ws.readyState !== WebSocket.OPEN) {{
                    log('Not connected', 'error');
                    return;
                }}
                ws.send(JSON.stringify({{ action: 'status' }}));
                log('Requested status', 'info');
            }}

            async function startCamera() {{
                try {{
                    localStream = await navigator.mediaDevices.getUserMedia({{
                        video: {{
                            width: {{ ideal: 640 }},
                            height: {{ ideal: 480 }}
                        }},
                        audio: false
                    }});
                    document.getElementById('localVideo').srcObject = localStream;
                    log('Camera started', 'success');
                }} catch (error) {{
                    log(`Camera error: ${{error.message}}`, 'error');
                }}
            }}

            function stopCamera() {{
                if (localStream) {{
                    localStream.getTracks().forEach(track => track.stop());
                    document.getElementById('localVideo').srcObject = null;
                    localStream = null;
                    log('Camera stopped', 'info');
                }}
            }}

            async function captureFrame() {{
                const video = document.getElementById('localVideo');
                if (!video.srcObject) {{
                    log('No camera stream available', 'error');
                    return null;
                }}

                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0);

                return new Promise((resolve) => {{
                    canvas.toBlob((blob) => {{
                        resolve(blob);
                    }}, 'image/jpeg', 0.8);
                }});
            }}

            async function startStreaming() {{
                if (!ws || ws.readyState !== WebSocket.OPEN) {{
                    log('Not connected', 'error');
                    return;
                }}

                if (!localStream) {{
                    log('Camera not started', 'error');
                    return;
                }}

                if (streamingInterval) {{
                    log('Already streaming', 'warning');
                    return;
                }}

                const interval = 1000 / TARGET_FPS;

                log(`Started streaming at ${{TARGET_FPS}} FPS`, 'success');

                streamingInterval = setInterval(async () => {{
                    const frame = await captureFrame();
                    if (frame && ws && ws.readyState === WebSocket.OPEN) {{
                        ws.send(frame);
                        framesSent++;
                        fpsCounter++;
                        updateStats();
                    }}
                }}, interval);
            }}

            function stopStreaming() {{
                if (streamingInterval) {{
                    clearInterval(streamingInterval);
                    streamingInterval = null;
                    log('Stopped streaming', 'info');
                }}
            }}

            // Update FPS display
            setInterval(updateStats, 100);

            // Clean up on page unload
            window.addEventListener('beforeunload', () => {{
                stopStreaming();
                stopCamera();
                if (ws) ws.close();
            }});

            log('WebSocket Video Streaming Test Client loaded', 'success');
            log('Instructions:', 'info');
            log('1. Click "Connect" to establish WebSocket connection', 'info');
            log('2. Click "Start Camera" to access your webcam', 'info');
            log('3. Click "Start Streaming" to send video frames to the server', 'info');
            log('4. The server will echo frames back for testing', 'info');
        </script>
    </body>
    </html>
    """
    
    # Render the WebSocket client
    components.html(websocket_client_html, height=1200, scrolling=True)
    
    # Instructions
    st.divider()
    st.subheader("📋 Instructions")
    st.markdown("""
    1. **Connect**: Click the "Connect" button to establish a WebSocket connection to the server
    2. **Start Camera**: Click "Start Camera" to access your webcam (you'll need to grant permission)
    3. **Start Streaming**: Once connected and camera is active, click "Start Streaming" to send video frames
    4. **View Results**: The server will process and echo frames back, displayed in the "Received Frames" section
    5. **Monitor**: Check the stats for frames sent/received and current FPS
    6. **Test Actions**: Use "Send Ping" and "Request Status" to test JSON message communication
    
    **Note**: Make sure your backend server is running at the specified WebSocket URL.
    """)
    
    # Additional Information
    with st.expander("ℹ️ Technical Details"):
        st.markdown("""
        ### WebSocket Protocol
        - **Binary Messages**: Video frames are sent as JPEG blobs
        - **Text Messages**: Control messages (ping, status) are sent as JSON
        - **Bidirectional**: Server can send frames back to the client
        
        ### Performance Tips
        - Lower FPS for slower networks
        - Ensure good lighting for better video quality
        - Check console log for detailed connection info
        
        ### Troubleshooting
        - **Connection Failed**: Verify the backend server is running
        - **Camera Not Working**: Check browser permissions
        - **No Frames Received**: Check server logs for errors
        """)

if __name__ == "__main__":
    main()