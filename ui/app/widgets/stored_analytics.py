import streamlit as st
import pandas as pd

def stored_analytics():
    st.write("Stored analytics")
    st.write("This is a stored analytics - based in data stored in a csv file")
    
    df = pd.read_csv("data/detection-example.csv")
    st.dataframe(df)