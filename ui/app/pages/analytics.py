import streamlit as st
import pandas as pd
from widgets.stored_analytics import stored_analytics
from widgets.real_demo_analytics import real_demo_analytics
    
def main():
    st.title("🚀 FastCV Beta Frontend - Analytics")
    st.write("Welcome to the FastCV application - Analytics!")
    st.divider()
    
    metric = st.sidebar.selectbox("Select a format for analytics", ["Real demo", "Stored analytics"])
    
    if metric == "Real demo":
        real_demo_analytics()
    elif metric == "Stored analytics":
        stored_analytics()
    
if __name__ == "__main__":
    main()