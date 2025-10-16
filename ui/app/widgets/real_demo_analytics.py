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
    
    # Create tabs for different analytics sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Summary Stats", 
        "👥 Person Analytics", 
        "📈 Timeline", 
        "🎯 Active Persons", 
        "📊 Confidence Distribution",
        "🔍 Detailed Queries"
    ])
    
    with tab1:
        st.header("📊 Detection Summary Statistics")
        
        # Get summary stats
        summary_data = make_api_call("/detections/stats/summary")
        
        if summary_data:
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
            
            # Display raw data
            st.subheader("Raw Summary Data")
            st.json(summary_data)
    
    with tab2:
        st.header("👥 Person Detection Analytics")
        
        # Get person stats
        person_stats = make_api_call("/detections/stats/by-person", {"limit": 20})
        
        if person_stats:
            # Create DataFrame for better visualization
            df_persons = pd.DataFrame(person_stats)
            
            if not df_persons.empty:
                # Top persons by detection count
                st.subheader("Top Persons by Detection Count")
                fig = px.bar(
                    df_persons.head(10), 
                    x='person_id', 
                    y='detection_count',
                    title="Detection Count by Person",
                    labels={'person_id': 'Person ID', 'detection_count': 'Detection Count'}
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Average confidence by person
                st.subheader("Average Confidence by Person")
                fig2 = px.scatter(
                    df_persons.head(10),
                    x='person_id',
                    y='avg_confidence',
                    size='detection_count',
                    title="Confidence vs Detection Count",
                    labels={'person_id': 'Person ID', 'avg_confidence': 'Average Confidence'}
                )
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(fig2, use_container_width=True)
                
                # Display table
                st.subheader("Detailed Person Statistics")
                st.dataframe(df_persons, use_container_width=True)
            else:
                st.info("No person data available")
    
    with tab3:
        st.header("📈 Detection Timeline")
        
        # Timeline controls
        col1, col2 = st.columns(2)
        with col1:
            hours = st.slider("Hours to look back", 1, 168, 24)
        with col2:
            interval_minutes = st.slider("Interval (minutes)", 5, 1440, 60)
        
        # Get timeline data
        timeline_data = make_api_call("/detections/stats/timeline", {
            "hours": hours,
            "interval_minutes": interval_minutes
        })
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            
            if not df_timeline.empty:
                # Convert timestamp to datetime
                df_timeline['timestamp'] = pd.to_datetime(df_timeline['timestamp'])
                
                # Detection count over time
                st.subheader("Detection Count Over Time")
                fig = px.line(
                    df_timeline, 
                    x='timestamp', 
                    y='detection_count',
                    title=f"Detections Over Last {hours} Hours"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Unique persons over time
                st.subheader("Unique Persons Over Time")
                fig2 = px.line(
                    df_timeline, 
                    x='timestamp', 
                    y='unique_persons',
                    title=f"Unique Persons Over Last {hours} Hours"
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Combined chart
                st.subheader("Combined Timeline View")
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=df_timeline['timestamp'], 
                    y=df_timeline['detection_count'],
                    mode='lines+markers',
                    name='Detection Count',
                    yaxis='y'
                ))
                fig3.add_trace(go.Scatter(
                    x=df_timeline['timestamp'], 
                    y=df_timeline['unique_persons'],
                    mode='lines+markers',
                    name='Unique Persons',
                    yaxis='y2'
                ))
                
                fig3.update_layout(
                    title=f"Detection Activity Over Last {hours} Hours",
                    xaxis_title="Time",
                    yaxis=dict(title="Detection Count", side="left"),
                    yaxis2=dict(title="Unique Persons", side="right", overlaying="y"),
                    hovermode='x unified'
                )
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No timeline data available for the selected period")
    
    with tab4:
        st.header("🎯 Currently Active Persons")
        
        # Active persons controls
        minutes = st.slider("Activity window (minutes)", 1, 1440, 5)
        
        # Get active persons
        active_persons = make_api_call("/detections/stats/active-persons", {"minutes": minutes})
        
        if active_persons:
            if active_persons:
                st.subheader(f"Persons Active in Last {minutes} Minutes")
                
                # Create DataFrame
                df_active = pd.DataFrame(active_persons)
                
                if not df_active.empty:
                    # Convert last_seen to datetime
                    df_active['last_seen'] = pd.to_datetime(df_active['last_seen'])
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Active Persons", len(df_active))
                    with col2:
                        avg_confidence = df_active['confidence'].mean()
                        st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                    with col3:
                        total_time = df_active['elapsed_time'].sum()
                        st.metric("Total Time Tracked", f"{total_time:.1f}s")
                    
                    # Display table
                    st.subheader("Active Person Details")
                    st.dataframe(df_active, use_container_width=True)
                    
                    # Confidence distribution of active persons
                    st.subheader("Confidence Distribution of Active Persons")
                    fig = px.histogram(
                        df_active, 
                        x='confidence',
                        title="Confidence Score Distribution",
                        nbins=20
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No persons active in the last {minutes} minutes")
            else:
                st.info("No active person data available")
    
    with tab5:
        st.header("📊 Confidence Score Distribution")
        
        # Get confidence distribution
        confidence_dist = make_api_call("/detections/stats/confidence-distribution")
        
        if confidence_dist:
            # Prepare data for visualization
            ranges = []
            counts = []
            labels = []
            
            for range_label, data in confidence_dist.items():
                ranges.append(data['range'])
                counts.append(data['count'])
                labels.append(f"{range_label.title()}\n({data['range']})")
            
            # Create pie chart
            st.subheader("Confidence Score Distribution")
            fig = px.pie(
                values=counts,
                names=labels,
                title="Distribution of Detection Confidence Scores"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Create bar chart
            st.subheader("Confidence Ranges - Bar Chart")
            fig2 = px.bar(
                x=labels,
                y=counts,
                title="Detection Count by Confidence Range",
                labels={'x': 'Confidence Range', 'y': 'Detection Count'}
            )
            fig2.update_xaxes(tickangle=45)
            st.plotly_chart(fig2, use_container_width=True)
            
            # Display raw data
            st.subheader("Raw Distribution Data")
            st.json(confidence_dist)
    
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
