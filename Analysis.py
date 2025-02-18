import pandas as pd
import streamlit as st
st.header('Analysis')
df= pd.read_csv('Automobile.csv')
st.dataframe(df)
st.bar_chart(data=df,x="length",y='mileage',x_label='Length',y_label='Mileage',color='#ffaa00')