import pandas as pd
import streamlit as st
st.header('Analysis')
df= pd.read_csv('Automobile.csv')
st.dataframe(df)