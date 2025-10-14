import streamlit as st

def main():
    
    home_page = st.Page("pages/home.py", url_path="/", title="Home")
    camera_page = st.Page("pages/camera.py", url_path="/camera", title="Camera")
    analytics_page = st.Page("pages/analytics.py", url_path="/analytics", title="Analytics")
    
    pg = st.navigation([home_page, camera_page, analytics_page])
    st.set_page_config(
        page_title="FastCV Beta Frontend",
        page_icon="🚀",
        layout="wide"
    )
    pg.run()

if __name__ == "__main__":
    main()
