import streamlit as st
import streamlit.components.v1 as components
import requests
import json

def login(base_url: str, email: str, password: str) -> dict:
    """
    Login to the API and get access token.
    
    Args:
        base_url: Base URL of the API (e.g., http://localhost:8000)
        email: User email
        password: User password
        
    Returns:
        dict: Response containing access_token or error
    """
    try:
        response = requests.post(
            f"{base_url}/api/v1/login/access-token",
            data={
                "username": email,
                "password": password
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {
                "success": False, 
                "error": f"Login failed: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}

def get_user_info(base_url: str, token: str) -> dict:
    """
    Get current user information.
    
    Args:
        base_url: Base URL of the API
        token: JWT access token
        
    Returns:
        dict: User information or error
    """
    try:
        response = requests.get(
            f"{base_url}/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to get user info"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    st.title("🎥 WebSocket Video Streaming Test Client")
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # API Settings
    st.header("API Settings")
    # Get API URL from environment variable or use default
    import os
    default_api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    base_url = st.text_input(
        "API Base URL:",
        value=default_api_url,
        placeholder=default_api_url,
        help="Base URL of your FastAPI backend"
    )
    
    # Remove trailing slash if present
    base_url = base_url.rstrip('/')
    
    # WebSocket URL (derived from base_url)
    ws_url = base_url.replace('http://', 'ws://').replace('https://', 'wss://').replace('backend', 'localhost') + '/api/v1/ws/video'
    
    st.divider()
    
    # Authentication Section
    if not st.session_state.logged_in:
        st.header("🔐 Login")
        st.info("Please login to access the video streaming service.")
        
        with st.form("login_form"):
            email = st.text_input(
                "Email:",
                placeholder="user@example.com"
            )
            password = st.text_input(
                "Password:",
                type="password",
                placeholder="Enter your password"
            )
            
            col1, col2 = st.columns([1, 3])
            with col1:
                submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    with st.spinner("Logging in..."):
                        result = login(base_url, email, password)
                        
                        if result["success"]:
                            token = result["data"]["access_token"]
                            st.session_state.token = token
                            
                            # Get user info
                            user_result = get_user_info(base_url, token)
                            if user_result["success"]:
                                st.session_state.user_info = user_result["data"]
                                st.session_state.logged_in = True
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Failed to retrieve user information")
                        else:
                            st.error(result["error"])
    
    else:
        # User is logged in
        st.header("👤 User Info")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user = st.session_state.user_info
            st.success(f"✅ Logged in as: **{user.get('email')}**")
            if user.get('full_name'):
                st.write(f"Name: {user.get('full_name')}")
        
        with col2:
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.token = None
                st.session_state.user_info = None
                st.rerun()
        
        st.divider()
        
        # Connection Settings
        st.header("Connection Settings")
        
        # Streaming Settings
        st.subheader("Streaming Settings")
        fps = st.slider("Streaming FPS:", min_value=1, max_value=10, value=5)
        
        st.divider()
        
        # Get the token for WebSocket connection
        token = st.session_state.token
        
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

                const WS_BASE_URL = "{ws_url}";
                const TOKEN = "{token}";
                const TARGET_FPS = {fps};
                const WS_URL = TOKEN ? `${{WS_BASE_URL}}?token=${{encodeURIComponent(TOKEN)}}` : WS_BASE_URL;

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

                    if (!TOKEN) {{
                        log('ERROR: No authentication token available', 'error');
                        updateStatus('Authentication Required', 'disconnected');
                        return;
                    }}

                    log(`Connecting to WebSocket with authentication...`, 'info');
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
                log('Authenticated and ready to connect!', 'success');
                log('Click "Connect" to establish WebSocket connection', 'info');
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
        ### Getting Started
        
        1. ✅ **Logged In**: You're already authenticated and ready to stream!
        
        2. **Connect**: Click the "Connect" button to establish the WebSocket connection
        
        3. **Start Camera**: Click "Start Camera" to access your webcam (you'll need to grant browser permission)
        
        4. **Start Streaming**: Once connected and camera is active, click "Start Streaming" to send video frames
        
        5. **View Results**: The server will process and echo frames back, displayed in the "Received Frames" section
        
        6. **Monitor**: Check the stats for frames sent/received and current FPS
        
        7. **Test Actions**: Use "Send Ping" and "Request Status" to test JSON message communication
        
        **Note**: Your session will remain active until you logout or the token expires.
        """)
        
        # Additional Information
        with st.expander("ℹ️ Technical Details"):
            st.markdown("""
            ### Authentication
            - ✅ **Authenticated**: Your JWT token is automatically included in the WebSocket connection
            - **Auto-Login**: No need to manually enter tokens
            - **User Identification**: Your user ID is automatically used as the client identifier
            - **Security**: Your connection is secure with JWT authentication
            
            ### WebSocket Protocol
            - **Binary Messages**: Video frames are sent as JPEG blobs
            - **Text Messages**: Control messages (ping, status) are sent as JSON
            - **Bidirectional**: Server can send frames back to the client
            - **Heartbeat**: Server sends periodic heartbeat messages to keep connection alive
            
            ### Performance Tips
            - Lower FPS for slower networks
            - Ensure good lighting for better video quality
            - Check console log for detailed connection info
            - Monitor the stats panel for performance metrics
            
            ### Troubleshooting
            - **Token Expired**: Logout and login again to get a fresh token
            - **Connection Failed**: Verify the backend server is running
            - **Camera Not Working**: Check browser permissions for camera access
            - **No Frames Received**: Check server logs for errors
            """)

if __name__ == "__main__":
    main()