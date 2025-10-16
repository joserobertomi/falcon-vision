import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
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

def real_demo_analytics():
    # Initialize session state for authentication FIRST
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # API Configuration
    import os
    default_api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    base_url = st.sidebar.text_input(
        "API Base URL:",
        value=default_api_url,
        placeholder=default_api_url,
        help="Base URL of your FastAPI backend"
    )
    
    # Remove trailing slash if present
    base_url = base_url.rstrip('/')
    
    # Authentication Setup - ALWAYS show sidebar
    st.sidebar.header("🔐 Login Authentication")
    
    headers = {"Content-Type": "application/json"}
    
    # Authentication Section
    if not st.session_state.is_authenticated:
        st.sidebar.info("Please login to access the analytics.")
        
        with st.sidebar.form("login_form"):
            email = st.text_input(
                "Email:",
                placeholder="user@example.com",
                key="login_email"
            )
            password = st.text_input(
                "Password:",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            col1, col2 = st.columns([1, 1])
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
                            st.session_state.access_token = token
                            
                            # Get user info
                            user_result = get_user_info(base_url, token)
                            if user_result["success"]:
                                st.session_state.user_info = user_result["data"]
                                st.session_state.user_email = email
                                st.session_state.is_authenticated = True
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Failed to retrieve user information")
                        else:
                            st.error(result["error"])
    
    else:
        # User is logged in
        st.sidebar.header("👤 User Info")
        
        user = st.session_state.user_info
        st.sidebar.success(f"✅ Logged in as: **{user.get('email')}**")
        if user.get('full_name'):
            st.sidebar.write(f"Name: {user.get('full_name')}")
        
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.is_authenticated = False
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.session_state.user_email = None
            st.rerun()
        
        # Set headers for API calls
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    # Test connection button
    if st.sidebar.button("🔍 Test API Connection"):
        if st.session_state.is_authenticated:
            test_response = requests.get(f"{base_url}/api/v1/detections/stats/summary", headers=headers)
            if test_response.status_code == 200:
                st.sidebar.success("✅ API Connection Successful!")
            elif test_response.status_code == 403:
                st.sidebar.error("❌ Authentication Failed (403)")
                st.sidebar.write("**Troubleshooting:**")
                st.sidebar.write("- Token might be expired, try logging in again")
                st.sidebar.write("- Check if your credentials are correct")
            elif test_response.status_code == 404:
                st.sidebar.warning("⚠️ Endpoint not found (404)")
                st.sidebar.write("Check if the API is running and the URL is correct")
            else:
                st.sidebar.error(f"❌ API Error {test_response.status_code}")
                st.sidebar.write(f"Response: {test_response.text}")
        else:
            st.sidebar.error("❌ Please login first")
    
    # Display current headers (for debugging)
    if st.sidebar.checkbox("Show Headers (Debug)"):
        st.sidebar.json(headers)
    
    # Help section
    with st.sidebar.expander("❓ Help & Troubleshooting"):
        st.write("**How to use:**")
        st.write("1. Enter your email and password")
        st.write("2. Click 'Login' to authenticate")
        st.write("3. Use 'Test API Connection' to verify")
        st.write("4. Explore the analytics tabs")
        st.write("")
        st.write("**Common Issues:**")
        st.write("- **403 Error**: Invalid credentials")
        st.write("- **404 Error**: API not running")
        st.write("- **Connection Error**: Check API URL")
        st.write("")
        st.write("**Logout**: Click 'Logout' to end session")
    
    # Main content area
    st.title("🔍 Real Detection Analytics Demo")
    st.write("This demo showcases all the detection API endpoints with real data visualization")
    
    # Check if user is authenticated before showing content
    if not st.session_state.is_authenticated:
        st.warning("🔐 **Authentication Required**")
        st.write("Please login using the sidebar to access the detection analytics.")
        st.write("You can use your email and password to authenticate with the API.")
        return
    
    # Show authenticated user info
    st.success(f"✅ Authenticated as: **{st.session_state.user_email}**")
    
   
    
    # Helper function to make API calls
    def make_api_call(endpoint, params=None):
        try:
            response = requests.get(f"{base_url}/api/v1{endpoint}", headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                st.error("🔐 Authentication Error (403): Could not validate credentials")
                st.error("Please check your authentication settings in the sidebar")
                return None
            elif response.status_code == 401:
                st.error("🔐 Unauthorized (401): Invalid or missing authentication")
                st.error("Please verify your token or API key")
                return None
            elif response.status_code == 404:
                st.warning(f"⚠️ Endpoint not found (404): {endpoint}")
                st.warning("Check if the API is running and the endpoint exists")
                return None
            elif response.status_code == 500:
                st.error("🚨 Server Error (500): Internal server error")
                st.error("The API server encountered an error")
                return None
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            st.error("🌐 Connection Error: Could not connect to the API")
            st.error("Please check if the API server is running and the URL is correct")
            return None
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout Error: The request took too long")
            st.error("The API server might be slow or overloaded")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return None
    
    # Create tabs for different API demonstration sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Summary Stats API", 
        "👥 Person Analytics API", 
        "📈 Timeline API", 
        "🎯 Active Persons API", 
        "📊 Confidence Distribution API",
        "🔍 Detailed Queries API"
    ])
    
    with tab1:
        st.header("📊 Detection Summary Statistics API")
        st.write("This demonstrates the `/detections/stats/summary` endpoint")
        
        # Show API request details
        st.subheader("🔗 API Request Details")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Endpoint:**")
            st.code("GET /api/v1/detections/stats/summary")
            
            st.write("**Headers:**")
            st.json(headers)
            
            st.write("**Authentication:**")
            st.code("Bearer Token (JWT)")
        
        with col2:
            st.write("**Request URL:**")
            st.code(f"{base_url}/api/v1/detections/stats/summary")
            
            st.write("**Expected Response:**")
            st.code(
                """
                {
                "total_detections": int,
                "unique_persons": int,
                "average_confidence": float,
                "detections_last_24h": int,
                "detections_last_hour": int
                }
            """)
        
        # Make the API call and show the process
        st.subheader("🚀 Making API Call")
        
        if st.button("Execute API Call", key="summary_call"):
            with st.spinner("Calling API..."):
                st.write("**Step 1: Sending Request**")
                st.code(f"requests.get('{base_url}/api/v1/detections/stats/summary', headers={headers})")
                
                summary_data = make_api_call("/detections/stats/summary")
                
                if summary_data:
                    st.write("**Step 2: Response Received**")
                    st.success("✅ API call successful!")
                    
                    # Show response details
                    st.write("**Response Status:** 200 OK")
                    st.write("**Response Headers:**")
                    st.json({"Content-Type": "application/json", "Authorization": "Bearer ***"})
                    
                    st.write("**Response Body:**")
                    st.json(summary_data)
                    
                    # Show how the data is used
                    st.write("**Step 3: Data Processing**")
                    st.write("The response data can be used to create metrics:")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric(
                            label="Total Detections",
                            value=summary_data.get("total_detections", 0)
                        )
                    
                    with col2:
                        st.metric(
                            label="Unique Persons",
                            value=summary_data.get("unique_persons", 0)
                        )
                    
                    with col3:
                        st.metric(
                            label="Avg Confidence",
                            value=f"{summary_data.get('average_confidence', 0):.2f}"
                        )
                    
                    with col4:
                        st.metric(
                            label="Last 24h",
                            value=summary_data.get("detections_last_24h", 0)
                        )
                    
                    with col5:
                        st.metric(
                            label="Last Hour",
                            value=summary_data.get("detections_last_hour", 0)
                        )
                    
                    st.write("**Step 4: Backend Implementation**")
                    st.code("""
# Backend route implementation
@router.get("/stats/summary", response_model=dict)
def get_detection_summary(session: SessionDep, current_user: CurrentUser):
    # Total detections
    total_count = session.exec(select(func.count()).select_from(Detection)).one()
    
    # Unique persons
    unique_persons = session.exec(select(func.count(func.distinct(Detection.person_id)))).one()
    
    # Average confidence
    avg_confidence = session.exec(select(func.avg(Detection.confidence))).one()
    
    # Last 24h detections
    last_24h_time = datetime.now(timezone.utc) - timedelta(hours=24)
    last_24h_count = session.exec(
        select(func.count()).select_from(Detection)
        .where(Detection.detection_time >= last_24h_time)
    ).one()
    
    return {
        "total_detections": total_count,
        "unique_persons": unique_persons,
        "average_confidence": round(float(avg_confidence or 0), 2),
        "detections_last_24h": last_24h_count,
        "detections_last_hour": last_1h_count,
    }
                    """)
                else:
                    st.error("❌ API call failed")
        else:
            st.info("Click 'Execute API Call' to see the request/response flow")
    
    with tab2:
        st.header("👥 Person Detection Analytics API")
        st.write("This demonstrates the `/detections/stats/by-person` endpoint")
        
        # Show API request details
        st.subheader("🔗 API Request Details")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Endpoint:**")
            st.code("GET /api/v1/detections/stats/by-person")
            
            st.write("**Query Parameters:**")
            st.code("""
limit: int (default: 10)
- Maximum number of persons to return
- Range: 1-100
            """)
            
            st.write("**Headers:**")
            st.json(headers)
        
        with col2:
            st.write("**Request URL:**")
            st.code(f"{base_url}/api/v1/detections/stats/by-person?limit=20")
            
            st.write("**Expected Response:**")
            st.code("""
[
  {
    "person_id": "string",
    "detection_count": int,
    "avg_confidence": float,
    "first_seen": "ISO datetime",
    "last_seen": "ISO datetime",
    "total_time_tracked": float
  }
]
            """)
        
        # Parameter input
        st.subheader("⚙️ Request Parameters")
        limit = st.slider("Limit", min_value=1, max_value=100, value=20, help="Maximum number of persons to return")
        
        # Make the API call and show the process
        st.subheader("🚀 Making API Call")
        
        if st.button("Execute API Call", key="person_call"):
            with st.spinner("Calling API..."):
                st.write("**Step 1: Sending Request**")
                st.code(f"requests.get('{base_url}/api/v1/detections/stats/by-person?limit={limit}', headers={headers})")
                
                person_stats = make_api_call("/detections/stats/by-person", {"limit": limit})
                
                if person_stats:
                    st.write("**Step 2: Response Received**")
                    st.success("✅ API call successful!")
                    
                    # Show response details
                    st.write("**Response Status:** 200 OK")
                    st.write("**Response Body:**")
                    st.json(person_stats)
                    
                    # Show how the data is used
                    st.write("**Step 3: Data Processing**")
                    st.write(f"Received {len(person_stats)} person records")
                    
                    if person_stats:
                        # Create DataFrame for display
                        df_persons = pd.DataFrame(person_stats)
                        st.write("**DataFrame Creation:**")
                        st.code("df_persons = pd.DataFrame(person_stats)")
                        st.dataframe(df_persons, use_container_width=True)
                        
                        # Show metrics
                        st.write("**Step 4: Metrics Calculation**")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            total_persons = len(person_stats)
                            st.metric("Total Persons", total_persons)
                        
                        with col2:
                            total_detections = sum(p.get('detection_count', 0) for p in person_stats)
                            st.metric("Total Detections", total_detections)
                        
                        with col3:
                            avg_confidence = sum(p.get('avg_confidence', 0) for p in person_stats) / len(person_stats) if person_stats else 0
                            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                    
                    st.write("**Step 5: Backend Implementation**")
                    st.code("""
# Backend route implementation
@router.get("/stats/by-person", response_model=list[dict])
def get_detections_by_person_stats(session: SessionDep, current_user: CurrentUser, limit: int = 10):
    # Get all unique person IDs
    person_ids = session.exec(select(Detection.person_id).distinct()).all()
    
    results = []
    for person_id in person_ids:
        stats = get_person_detection_stats(session=session, person_id=person_id)
        
        # Get average confidence for this person
        avg_confidence = session.exec(
            select(func.avg(Detection.confidence))
            .where(Detection.person_id == person_id)
        ).one()
        
        results.append({
            "person_id": person_id,
            "detection_count": stats["detection_count"],
            "avg_confidence": round(float(avg_confidence or 0), 2),
            "first_seen": stats["first_detection_time"].isoformat(),
            "last_seen": stats["last_detection_time"].isoformat(),
            "total_time_tracked": round(stats["elapsed_time"], 2),
        })
    
    # Sort by detection count and limit
    results.sort(key=lambda x: x["detection_count"], reverse=True)
    return results[:limit]
                    """)
                else:
                    st.error("❌ API call failed")
        else:
            st.info("Click 'Execute API Call' to see the request/response flow")
    
    with tab3:
        st.header("📈 Detection Timeline API")
        st.write("This demonstrates the `/detections/stats/timeline` endpoint")
        
        # Show API request details
        st.subheader("🔗 API Request Details")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Endpoint:**")
            st.code("GET /api/v1/detections/stats/timeline")
            
            st.write("**Query Parameters:**")
            st.code("""
hours: int (default: 24)
- Number of hours to look back
- Range: 1-168

interval_minutes: int (default: 60)
- Interval in minutes for grouping
- Range: 5-1440
            """)
            
            st.write("**Headers:**")
            st.json(headers)
        
        with col2:
            st.write("**Request URL:**")
            st.code(f"{base_url}/api/v1/detections/stats/timeline?hours=24&interval_minutes=60")
            
            st.write("**Expected Response:**")
            st.code("""
[
  {
    "timestamp": "ISO datetime",
    "detection_count": int,
    "unique_persons": int,
    "avg_confidence": float
  }
]
            """)
        
        # Parameter inputs
        st.subheader("⚙️ Request Parameters")
        col1, col2 = st.columns(2)
        with col1:
            hours = st.slider("Hours to look back", 1, 168, 24, help="Number of hours to look back")
        with col2:
            interval_minutes = st.slider("Interval (minutes)", 5, 1440, 60, help="Interval in minutes for grouping")
        
        # Make the API call and show the process
        st.subheader("🚀 Making API Call")
        
        if st.button("Execute API Call", key="timeline_call"):
            with st.spinner("Calling API..."):
                st.write("**Step 1: Sending Request**")
                st.code(f"requests.get('{base_url}/api/v1/detections/stats/timeline?hours={hours}&interval_minutes={interval_minutes}', headers={headers})")
                
                timeline_data = make_api_call("/detections/stats/timeline", {
                    "hours": hours,
                    "interval_minutes": interval_minutes
                })
                
                if timeline_data:
                    st.write("**Step 2: Response Received**")
                    st.success("✅ API call successful!")
                    
                    # Show response details
                    st.write("**Response Status:** 200 OK")
                    st.write("**Response Body:**")
                    st.json(timeline_data)
                    
                    # Show how the data is used
                    st.write("**Step 3: Data Processing**")
                    st.write(f"Received {len(timeline_data)} time intervals")
                    
                    if timeline_data:
                        # Create DataFrame for display
                        df_timeline = pd.DataFrame(timeline_data)
                        st.write("**DataFrame Creation:**")
                        st.code("df_timeline = pd.DataFrame(timeline_data)")
                        st.dataframe(df_timeline, use_container_width=True)
                        
                        # Show metrics
                        st.write("**Step 4: Metrics Calculation**")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            total_detections = sum(d.get('detection_count', 0) for d in timeline_data)
                            st.metric("Total Detections", total_detections)
                        
                        with col2:
                            max_unique = max(d.get('unique_persons', 0) for d in timeline_data) if timeline_data else 0
                            st.metric("Max Unique Persons", max_unique)
                        
                        with col3:
                            avg_confidence = sum(d.get('avg_confidence', 0) for d in timeline_data) / len(timeline_data) if timeline_data else 0
                            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                    
                    st.write("**Step 5: Backend Implementation**")
                    st.code("""
# Backend route implementation
@router.get("/stats/timeline", response_model=list[dict])
def get_detection_timeline(session: SessionDep, current_user: CurrentUser, 
                          hours: int = 24, interval_minutes: int = 60):
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=hours)
    
    # Get all detections in the time range
    detections = get_detections_by_time_range(session=session, start_time=start_time, end_time=now)
    
    # Group by intervals
    timeline = {}
    interval_seconds = interval_minutes * 60
    
    for detection in detections:
        # Round datetime down to nearest interval
        detection_time = detection.detection_time
        if detection_time.tzinfo is None:
            detection_time = detection_time.replace(tzinfo=timezone.utc)
        
        # Calculate interval timestamp
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        seconds_since_epoch = int((detection_time - epoch).total_seconds())
        interval_timestamp = (seconds_since_epoch // interval_seconds) * interval_seconds
        interval_time = epoch + timedelta(seconds=interval_timestamp)
        interval_key = interval_time.isoformat()
        
        if interval_key not in timeline:
            timeline[interval_key] = {
                "timestamp": interval_key,
                "count": 0,
                "unique_persons": set(),
                "avg_confidence": [],
            }
        
        timeline[interval_key]["count"] += 1
        timeline[interval_key]["unique_persons"].add(detection.person_id)
        timeline[interval_key]["avg_confidence"].append(detection.confidence)
    
    # Convert to list and calculate averages
    result = []
    for timestamp in sorted(timeline.keys()):
        data = timeline[timestamp]
        result.append({
            "timestamp": timestamp,
            "detection_count": data["count"],
            "unique_persons": len(data["unique_persons"]),
            "avg_confidence": round(sum(data["avg_confidence"]) / len(data["avg_confidence"]), 2)
        })
    
    return result
                    """)
                else:
                    st.error("❌ API call failed")
        else:
            st.info("Click 'Execute API Call' to see the request/response flow")
    
    with tab4:
        st.header("🎯 Active Persons API")
        st.write("This demonstrates the `/detections/stats/active-persons` endpoint")
        
        # Show API request details
        st.subheader("🔗 API Request Details")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Endpoint:**")
            st.code("GET /api/v1/detections/stats/active-persons")
            
            st.write("**Query Parameters:**")
            st.code("""
minutes: int (default: 5)
- Time window in minutes to consider a person active
- Range: 1-1440
            """)
            
            st.write("**Headers:**")
            st.json(headers)
        
        with col2:
            st.write("**Request URL:**")
            st.code(f"{base_url}/api/v1/detections/stats/active-persons?minutes=5")
            
            st.write("**Expected Response:**")
            st.code("""
[
  {
    "person_id": "string",
    "last_seen": "ISO datetime",
    "confidence": float,
    "elapsed_time": float,
    "bbox": {
      "x1": float, "y1": float,
      "x2": float, "y2": float
    }
  }
]
            """)
        
        # Parameter input
        st.subheader("⚙️ Request Parameters")
        minutes = st.slider("Activity window (minutes)", 1, 1440, 5, help="Time window to consider a person active")
        
        # Make the API call and show the process
        st.subheader("🚀 Making API Call")
        
        if st.button("Execute API Call", key="active_call"):
            with st.spinner("Calling API..."):
                st.write("**Step 1: Sending Request**")
                st.code(f"requests.get('{base_url}/api/v1/detections/stats/active-persons?minutes={minutes}', headers={headers})")
                
                active_persons = make_api_call("/detections/stats/active-persons", {"minutes": minutes})
                
                if active_persons is not None:
                    st.write("**Step 2: Response Received**")
                    st.success("✅ API call successful!")
                    
                    # Show response details
                    st.write("**Response Status:** 200 OK")
                    st.write("**Response Body:**")
                    st.json(active_persons)
                    
                    # Show how the data is used
                    st.write("**Step 3: Data Processing**")
                    st.write(f"Received {len(active_persons)} active person records")
                    
                    if active_persons:
                        # Create DataFrame for display
                        df_active = pd.DataFrame(active_persons)
                        st.write("**DataFrame Creation:**")
                        st.code("df_active = pd.DataFrame(active_persons)")
                        st.dataframe(df_active, use_container_width=True)
                        
                        # Show metrics
                        st.write("**Step 4: Metrics Calculation**")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Active Persons", len(active_persons))
                        
                        with col2:
                            avg_confidence = sum(p.get('confidence', 0) for p in active_persons) / len(active_persons) if active_persons else 0
                            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                        
                        with col3:
                            total_time = sum(p.get('elapsed_time', 0) for p in active_persons)
                            st.metric("Total Time Tracked", f"{total_time:.1f}s")
                    else:
                        st.info(f"No persons active in the last {minutes} minutes")
                    
                    st.write("**Step 5: Backend Implementation**")
                    st.code("""
# Backend route implementation
@router.get("/stats/active-persons", response_model=list[dict])
def get_active_persons(session: SessionDep, current_user: CurrentUser, minutes: int = 5):
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    
    # Get all unique person IDs detected recently
    person_ids = session.exec(
        select(Detection.person_id)
        .where(Detection.detection_time >= cutoff_time)
        .distinct()
    ).all()
    
    # Get latest detection for each person
    active_persons = []
    for person_id in person_ids:
        latest_detection = get_latest_detection_by_person_id(session=session, person_id=person_id)
        if latest_detection:
            # Ensure timezone awareness
            last_seen = latest_detection.detection_time
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            
            # Get person stats to calculate elapsed time
            stats = get_person_detection_stats(session=session, person_id=latest_detection.person_id)
            
            active_persons.append({
                "person_id": latest_detection.person_id,
                "last_seen": last_seen.isoformat(),
                "confidence": round(latest_detection.confidence, 2),
                "elapsed_time": round(stats["elapsed_time"], 2),
                "bbox": {
                    "x1": latest_detection.bbox_x1,
                    "y1": latest_detection.bbox_y1,
                    "x2": latest_detection.bbox_x2,
                    "y2": latest_detection.bbox_y2,
                },
            })
    
    # Sort by last_seen descending
    active_persons.sort(key=lambda x: x["last_seen"], reverse=True)
    return active_persons
                    """)
                else:
                    st.error("❌ API call failed")
        else:
            st.info("Click 'Execute API Call' to see the request/response flow")
    
    with tab5:
        st.header("📊 Confidence Distribution API")
        st.write("This demonstrates the `/detections/stats/confidence-distribution` endpoint")
        
        # Show API request details
        st.subheader("🔗 API Request Details")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Endpoint:**")
            st.code("GET /api/v1/detections/stats/confidence-distribution")
            
            st.write("**Query Parameters:**")
            st.code("None - No parameters required")
            
            st.write("**Headers:**")
            st.json(headers)
        
        with col2:
            st.write("**Request URL:**")
            st.code(f"{base_url}/api/v1/detections/stats/confidence-distribution")
            
            st.write("**Expected Response:**")
            st.code("""
{
  "low": {
    "range": "0.0-0.5",
    "count": int
  },
  "medium": {
    "range": "0.5-0.7",
    "count": int
  },
  "high": {
    "range": "0.7-0.85",
    "count": int
  },
  "very_high": {
    "range": "0.85-1.0",
    "count": int
  }
}
            """)
        
        # Make the API call and show the process
        st.subheader("🚀 Making API Call")
        
        if st.button("Execute API Call", key="confidence_call"):
            with st.spinner("Calling API..."):
                st.write("**Step 1: Sending Request**")
                st.code(f"requests.get('{base_url}/api/v1/detections/stats/confidence-distribution', headers={headers})")
                
                confidence_dist = make_api_call("/detections/stats/confidence-distribution")
                
                if confidence_dist:
                    st.write("**Step 2: Response Received**")
                    st.success("✅ API call successful!")
                    
                    # Show response details
                    st.write("**Response Status:** 200 OK")
                    st.write("**Response Body:**")
                    st.json(confidence_dist)
                    
                    # Show how the data is used
                    st.write("**Step 3: Data Processing**")
                    st.write("Processing confidence distribution data...")
                    
                    # Prepare data for visualization
                    ranges = []
                    counts = []
                    labels = []
                    
                    for range_label, data in confidence_dist.items():
                        ranges.append(data['range'])
                        counts.append(data['count'])
                        labels.append(f"{range_label.title()}\n({data['range']})")
                    
                    st.write("**Data Processing Code:**")
                    st.code("""
# Process confidence distribution data
ranges = []
counts = []
labels = []

for range_label, data in confidence_dist.items():
    ranges.append(data['range'])
    counts.append(data['count'])
    labels.append(f"{range_label.title()}\\n({data['range']})")
                    """)
                    
                    # Show metrics
                    st.write("**Step 4: Metrics Calculation**")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Low (0.0-0.5)", confidence_dist.get('low', {}).get('count', 0))
                    
                    with col2:
                        st.metric("Medium (0.5-0.7)", confidence_dist.get('medium', {}).get('count', 0))
                    
                    with col3:
                        st.metric("High (0.7-0.85)", confidence_dist.get('high', {}).get('count', 0))
                    
                    with col4:
                        st.metric("Very High (0.85-1.0)", confidence_dist.get('very_high', {}).get('count', 0))
                    
                    # Show total
                    total_detections = sum(data.get('count', 0) for data in confidence_dist.values())
                    st.metric("Total Detections", total_detections)
                    
                    st.write("**Step 5: Backend Implementation**")
                    st.code("""
# Backend route implementation
@router.get("/stats/confidence-distribution", response_model=dict)
def get_confidence_distribution(session: SessionDep, current_user: CurrentUser):
    ranges = [
        (0.0, 0.5, "low"),
        (0.5, 0.7, "medium"),
        (0.7, 0.85, "high"),
        (0.85, 1.0, "very_high"),
    ]
    
    distribution = {}
    for min_conf, max_conf, label in ranges:
        count = session.exec(
            select(func.count())
            .select_from(Detection)
            .where(Detection.confidence >= min_conf, Detection.confidence < max_conf)
        ).one()
        distribution[label] = {
            "range": f"{min_conf}-{max_conf}",
            "count": count,
        }
    
    return distribution
                    """)
                else:
                    st.error("❌ API call failed")
        else:
            st.info("Click 'Execute API Call' to see the request/response flow")
    
    with tab6:
        st.header("🔍 Detailed Detection Queries")
        
        # Query options
        query_type = st.selectbox(
            "Select Query Type",
            ["All Detections", "By Person", "By Time Range", "By Confidence", "Specific Detection"]
        )
        
        if query_type == "All Detections":
            st.subheader("All Detections (Paginated)")
            
            col1, col2 = st.columns(2)
            with col1:
                skip = st.number_input("Skip", min_value=0, value=0)
            with col2:
                limit = st.number_input("Limit", min_value=1, max_value=1000, value=100)
            
            detections = make_api_call("/detections/", {"skip": skip, "limit": limit})
            
            if detections:
                st.metric("Total Count", detections.get("count", 0))
                if detections.get("data"):
                    df_detections = pd.DataFrame(detections["data"])
                    st.dataframe(df_detections, use_container_width=True)
                else:
                    st.info("No detection data available")
        
        elif query_type == "By Person":
            st.subheader("Detections by Person ID")
            
            person_id = st.text_input("Enter Person ID")
            if person_id:
                person_detections = make_api_call(f"/detections/person/{person_id}")
                
                if person_detections:
                    st.metric("Detection Count", person_detections.get("count", 0))
                    if person_detections.get("data"):
                        df_person_detections = pd.DataFrame(person_detections["data"])
                        st.dataframe(df_person_detections, use_container_width=True)
                    else:
                        st.info(f"No detections found for person {person_id}")
        
        elif query_type == "By Time Range":
            st.subheader("Detections by Time Range")
            
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.date_input("Start Date")
                start_hour = st.time_input("Start Time")
            with col2:
                end_time = st.date_input("End Date")
                end_hour = st.time_input("End Time")
            
            if st.button("Query Time Range"):
                # Combine date and time
                start_datetime = datetime.combine(start_time, start_hour)
                end_datetime = datetime.combine(end_time, end_hour)
                
                time_detections = make_api_call("/detections/time-range", {
                    "start_time": start_datetime.isoformat() + "Z",
                    "end_time": end_datetime.isoformat() + "Z"
                })
                
                if time_detections:
                    st.metric("Detection Count", time_detections.get("count", 0))
                    if time_detections.get("data"):
                        df_time_detections = pd.DataFrame(time_detections["data"])
                        st.dataframe(df_time_detections, use_container_width=True)
                    else:
                        st.info("No detections found in the specified time range")
        
        elif query_type == "By Confidence":
            st.subheader("Detections by Confidence Threshold")
            
            min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.05)
            
            confidence_detections = make_api_call("/detections/by-confidence", {
                "min_confidence": min_confidence
            })
            
            if confidence_detections:
                st.metric("Detection Count", confidence_detections.get("count", 0))
                if confidence_detections.get("data"):
                    df_confidence_detections = pd.DataFrame(confidence_detections["data"])
                    st.dataframe(df_confidence_detections, use_container_width=True)
                else:
                    st.info(f"No detections found with confidence >= {min_confidence}")
        
        elif query_type == "Specific Detection":
            st.subheader("Get Specific Detection by ID")
            
            detection_id = st.text_input("Enter Detection ID (UUID)")
            if detection_id:
                detection = make_api_call(f"/detections/{detection_id}")
                
                if detection:
                    st.subheader("Detection Details")
                    st.json(detection)
                else:
                    st.error("Detection not found or invalid ID")
    
    # Footer
    st.markdown("---")
    st.markdown("**Note:** This demo requires the Falcon Vision API to be running and accessible. Adjust the `API_BASE_URL` and authentication headers as needed for your setup.")
