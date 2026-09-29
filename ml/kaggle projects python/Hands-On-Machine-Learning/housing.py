import pandas as pd
import streamlit as st
import os as os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
import io as io
df = pd.read_csv("housing.csv")

st.dataframe(df.describe(include='all'))
st.dataframe(df)
buffer = io.StringIO()
df.info(buf=buffer)
info_txt= buffer.getvalue()
st.text(info_txt)


figOfOp,axOfOp= plt.subplots()
sns.countplot(x='total_rooms',data=df)
st.pyplot(figOfOp)