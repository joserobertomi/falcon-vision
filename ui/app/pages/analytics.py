import streamlit as st
import pandas as pd

def real_demo():
    st.write("Real demo")
    st.write("This is a real demo of the analytics - based in data requested and api responses")

def stored_analytics():
    st.write("Stored analytics")
    st.write("This is a stored analytics - based in data stored in a csv file")
    
    df = pd.read_csv("data/detection-example.csv")
    st.dataframe(df)
    
def main():
    st.title("🚀 FastCV Beta Frontend - Analytics")
    st.write("Welcome to the FastCV application - Analytics!")
    st.divider()
    metric = st.sidebar.selectbox("Select a format for analytics", ["Real demo", "Stored analytics"])
    if metric == "Real demo":
        real_demo()
    elif metric == "Stored analytics":
        stored_analytics()
    
if __name__ == "__main__":
    main()