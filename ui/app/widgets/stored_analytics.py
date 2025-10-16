import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

@st.cache_data
def load_data():
    df = pd.read_csv("app/data/detection-example.csv")
    # Convert datetime columns
    df['detection_time'] = pd.to_datetime(df['detection_time'])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    # Convert confidence to float
    df['confidence'] = df['confidence'].astype(float)
    # Calculate bounding box area
    df['bbox_area'] = (df['bbox_x2'] - df['bbox_x1']) * (df['bbox_y2'] - df['bbox_y1'])
    # Calculate bounding box center
    df['bbox_center_x'] = (df['bbox_x1'] + df['bbox_x2']) / 2
    df['bbox_center_y'] = (df['bbox_y1'] + df['bbox_y2']) / 2
    return df


def stored_analytics():
    st.title("📊 Detection Analytics Dashboard")
    st.write("Comprehensive analysis of person detection data")
    
    # Load data
    df = load_data()
        
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Person filter
    unique_persons = sorted(df['person_id'].unique())
    selected_persons = st.sidebar.multiselect(
        "Select Persons", 
        unique_persons, 
        default=unique_persons[:5]  # Show first 5 by default
    )
    
    # Confidence filter
    min_confidence = st.sidebar.slider(
        "Minimum Confidence", 
        0.0, 1.0, 
        value=0.0, 
        step=0.01
    )
    
    # Time range filter
    time_range = st.sidebar.selectbox(
        "Time Range",
        ["All", "Last 5 minutes", "Last 10 minutes", "Last 30 minutes", "Custom"]
    )
    
    # Apply filters
    filtered_df = df[df['person_id'].isin(selected_persons)]
    filtered_df = filtered_df[filtered_df['confidence'] >= min_confidence]
    
    if time_range != "All":
        if time_range == "Last 5 minutes":
            time_threshold = filtered_df['detection_time'].max() - timedelta(minutes=5)
        elif time_range == "Last 10 minutes":
            time_threshold = filtered_df['detection_time'].max() - timedelta(minutes=10)
        elif time_range == "Last 30 minutes":
            time_threshold = filtered_df['detection_time'].max() - timedelta(minutes=30)
        
        filtered_df = filtered_df[filtered_df['detection_time'] >= time_threshold]
    
    # KPI Metrics
    st.header("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_detections = len(filtered_df)
        st.metric("Total Detections", f"{total_detections:,}")
    
    with col2:
        unique_persons_count = filtered_df['person_id'].nunique()
        st.metric("Unique Persons", f"{unique_persons_count:,}")
    
    with col3:
        avg_confidence = filtered_df['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.3f}")
    
    with col4:
        time_span = (filtered_df['detection_time'].max() - filtered_df['detection_time'].min()).total_seconds() / 60
        st.metric("Time Span (min)", f"{time_span:.1f}")
    
    # Additional metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        detections_per_minute = total_detections / max(time_span, 1)
        st.metric("Detections/min", f"{detections_per_minute:.1f}")
    
    with col6:
        avg_bbox_area = filtered_df['bbox_area'].mean()
        st.metric("Avg Bbox Area", f"{avg_bbox_area:.0f} px²")
    
    with col7:
        high_confidence = len(filtered_df[filtered_df['confidence'] >= 0.8])
        st.metric("High Conf (≥0.8)", f"{high_confidence:,}")
    
    with col8:
        most_active_person = filtered_df['person_id'].value_counts().index[0] if len(filtered_df) > 0 else "N/A"
        st.metric("Most Active", most_active_person)
    
    st.divider()
    
    # Charts Section
    st.header("📊 Visualizations")
    
    # Create tabs for different chart types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Time Series", "👥 Person Analysis", "🎯 Confidence", "📐 Bounding Boxes", "📋 Raw Data"
    ])
    
    with tab1:
        st.subheader("Detection Trends Over Time")
        
        # Time series of detections
        detections_by_time = filtered_df.groupby(filtered_df['detection_time'].dt.floor('30S')).size().reset_index()
        detections_by_time.columns = ['time', 'count']
        
        fig_time = px.line(
            detections_by_time, 
            x='time', 
            y='count',
            title="Detections per 30 seconds",
            labels={'count': 'Number of Detections', 'time': 'Time'}
        )
        fig_time.update_layout(height=400)
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Person activity over time
        person_activity = filtered_df.groupby([
            filtered_df['detection_time'].dt.floor('1min'), 
            'person_id'
        ]).size().reset_index()
        person_activity.columns = ['time', 'person_id', 'count']
        
        fig_person_time = px.line(
            person_activity, 
            x='time', 
            y='count',
            color='person_id',
            title="Person Activity Over Time (1-minute intervals)",
            labels={'count': 'Detections', 'time': 'Time'}
        )
        fig_person_time.update_layout(height=400)
        st.plotly_chart(fig_person_time, use_container_width=True)
    
    with tab2:
        st.subheader("Person Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Person detection counts
            person_counts = filtered_df['person_id'].value_counts().head(20)
            
            fig_person_counts = px.bar(
                x=person_counts.values,
                y=person_counts.index,
                orientation='h',
                title="Top 20 Most Detected Persons",
                labels={'x': 'Number of Detections', 'y': 'Person ID'}
            )
            fig_person_counts.update_layout(height=500)
            st.plotly_chart(fig_person_counts, use_container_width=True)
        
        with col2:
            # Person confidence distribution
            person_confidence = filtered_df.groupby('person_id')['confidence'].agg(['mean', 'std', 'count']).reset_index()
            person_confidence = person_confidence[person_confidence['count'] >= 5]  # Only persons with 5+ detections
            
            fig_confidence = px.scatter(
                person_confidence,
                x='count',
                y='mean',
                size='std',
                hover_data=['person_id'],
                title="Person Confidence vs Detection Count",
                labels={'count': 'Detection Count', 'mean': 'Average Confidence'}
            )
            fig_confidence.update_layout(height=500)
            st.plotly_chart(fig_confidence, use_container_width=True)
    
    with tab3:
        st.subheader("Confidence Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Confidence distribution histogram
            fig_hist = px.histogram(
                filtered_df,
                x='confidence',
                nbins=30,
                title="Confidence Score Distribution",
                labels={'confidence': 'Confidence Score', 'count': 'Frequency'}
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Confidence box plot by person
            top_persons = filtered_df['person_id'].value_counts().head(10).index
            top_persons_df = filtered_df[filtered_df['person_id'].isin(top_persons)]
            
            fig_box = px.box(
                top_persons_df,
                x='person_id',
                y='confidence',
                title="Confidence Distribution by Person (Top 10)",
                labels={'person_id': 'Person ID', 'confidence': 'Confidence Score'}
            )
            fig_box.update_layout(height=400)
            fig_box.update_xaxes(tickangle=45)
            st.plotly_chart(fig_box, use_container_width=True)
    
    with tab4:
        st.subheader("Bounding Box Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bounding box area distribution
            fig_area = px.histogram(
                filtered_df,
                x='bbox_area',
                nbins=30,
                title="Bounding Box Area Distribution",
                labels={'bbox_area': 'Area (pixels²)', 'count': 'Frequency'}
            )
            fig_area.update_layout(height=400)
            st.plotly_chart(fig_area, use_container_width=True)
        
        with col2:
            # Scatter plot of bounding box positions
            sample_df = filtered_df.sample(min(1000, len(filtered_df)))  # Sample for performance
            
            fig_scatter = px.scatter(
                sample_df,
                x='bbox_center_x',
                y='bbox_center_y',
                color='confidence',
                size='bbox_area',
                hover_data=['person_id'],
                title="Bounding Box Positions (Sampled)",
                labels={'bbox_center_x': 'Center X', 'bbox_center_y': 'Center Y'}
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Bounding box size vs confidence
        fig_size_conf = px.scatter(
            filtered_df,
            x='bbox_area',
            y='confidence',
            color='person_id',
            title="Bounding Box Area vs Confidence",
            labels={'bbox_area': 'Area (pixels²)', 'confidence': 'Confidence Score'}
        )
        fig_size_conf.update_layout(height=400)
        st.plotly_chart(fig_size_conf, use_container_width=True)
    
    with tab5:
        st.subheader("Raw Data")
        
        # Data summary
        st.write(f"**Dataset Summary:** {len(filtered_df):,} records from {filtered_df['person_id'].nunique()} unique persons")
        
        # Show filtered data
        st.dataframe(
            filtered_df[['person_id', 'confidence', 'bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2', 'detection_time']],
            use_container_width=True,
            height=400
        )
        
        # Export options
        st.subheader("📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download filtered data as CSV",
                    data=csv,
                    file_name=f"detection_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Download Summary"):
                summary_data = {
                    'Metric': [
                        'Total Detections', 'Unique Persons', 'Average Confidence',
                        'Time Span (minutes)', 'Detections per minute', 'High Confidence Count'
                    ],
                    'Value': [
                        len(filtered_df),
                        filtered_df['person_id'].nunique(),
                        f"{filtered_df['confidence'].mean():.3f}",
                        f"{time_span:.1f}",
                        f"{detections_per_minute:.1f}",
                        high_confidence
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="Download summary as CSV",
                    data=csv,
                    file_name=f"detection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )