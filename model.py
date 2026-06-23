# %% [markdown]
# # TRAIN THIS DATA
# ---
# 

# %%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as  plt
import os 
import streamlit as st
import io
def data_quality_report(df):
    return {
        "shape": df.shape,
        "missing_values": df.isna().sum(),
        "missing_percent": (df.isna().mean() * 100).round(2),
        "duplicate_rows": df.duplicated().sum(),
        "dtypes": df.dtypes,
        "unique_counts": df.nunique()
    }
def md(text):
    st.markdown(f"{text}", unsafe_allow_html=True)
md("<h1> merging the data </h1>")

#--------------------------------------------------------------------------------------------------------
            #----------------------------- CODE BEGINS ------------------------------
#--------------------------------------------------------------------------------------------------------
df1 = pd.read_csv("train.csv",index_col=0)#index_col to remove the default indexing and giving the new one
df2 = pd.read_csv("test.csv",index_col=0)
# st.write(df1.info())
md("<h1 style = 'color : red;'>  TRAIN CSV</h1>")
st.write(df1.shape)
st.dataframe(df1.head())
st.write(df1.describe(include='all'))
buffer = io.StringIO()
df1.info(buf= buffer)
# st.text(buffer.getvalue())
st.write(df1.isna().sum()[df1.isna().sum()>0])
md("<h1 style = 'color : red;'>  TEST CSV</h1>")
st.write(df2.shape)
st.dataframe(df2.head())
st.write(df2.describe(include='all'))
st.write(df2.isna().sum()[df1.isna().sum()>0])

#checking the target column is present in df2 or not if not then add with 0  values 
if "SalePrice" not in df2.columns:
    df2['SalePrice']=0  
df = pd.concat(
    [df1,df2],
    axis=0,
 )
md("<h1 style= 'color : purple; background : white; font-size:130px; text-align:center;'>{ DF }</h1>")
st.write(f'df.shape=> {df.shape}')
st.dataframe(df.head())
options = st.selectbox("Choose Columns",df.columns)
figOfOp,axOfOp= plt.subplots()
try:
    sns.heatmap(df[[f'{options}']],ax=axOfOp) 
except ValueError:

    counts = df[options].fillna("NULL").value_counts()
    print(f"\033[32m{counts}[0m")   
    sns.barplot(x=counts.index, y=counts.values, ax=axOfOp)

    axOfOp.set_title("Value Count (Including NULL)")
    axOfOp.set_xlabel(f'{options}')
    axOfOp.set_ylabel("Count")
    for containers in axOfOp.containers:
        axOfOp.bar_label(containers) 
#--------------- OR -----------// because there is only one container
    axOfOp.bar_label(axOfOp.containers[0])

st.pyplot(figOfOp)



# %%
md("<h1> fitlerted the first df_null</h1>")
df_null =df[df.isnull().sum()[df.isnull().sum()>0].index]
st.dataframe(df_null.head())
# for i in df_null.columns:
#     st.write(f'"{i}"        =>{df[f"{i}"].isnull().sum()}')
# null_cols = df.columns[df.isnull().sum() > 0]
# df_null = df[null_cols]
#df[df['MSZoning'].isnull()==True] to get the specific column with containing null
# for i in range(len(df)):
#     st.write(f'{df.iloc[[i],0:3]}\t ......=> {df.iloc[i].isnull().sum()}')
# for i in df.index:
#     st.write(f'{df.iloc[i]}        =>{df.loc[i].isnull().sum()}')


# %%
st.write(df_null.shape)
p1,ax1 = plt.subplots()
sns.heatmap(df_null.loc[:,df_null.columns[0:20]].isnull(),ax=ax1)
st.pyplot(p1)
p2,ax2 = plt.subplots()
sns.histplot(df['SalePrice'], kde=True,ax=ax2)
st.pyplot(p2)
# %%
df_objects = df[df.select_dtypes(include='object').columns]
# st.write(df_objects.shape)#(2919, 43)
df_objects_nan_arr=df_objects.isna().sum()[df_objects.isna().sum()>1100].index
# st.write(df[df_objects_nan_arr].isna().sum())
# st.write(df[df_objects_nan_arr])
# df_objects[df_objects_nan_arr]
# df_objects.drop(columns=df_objects_nan_arr).shape
# st.write(df_objects.shape)#includes all the object ones 
# st.write(df_objects[df_objects_nan_arr].shape)#arr of columns having more than 1100 nan sum
# st.write(df_objects.drop(columns=df_objects_nan_arr).shape)#removing these columns 
df= df.drop(columns=df_objects_nan_arr)#6 columns removed from the original
st.dataframe(df)

# %%
df_objects_new = df_objects.drop(columns=df_objects_nan_arr)
st.write(df_objects.shape)
st.write(df_objects_new.shape)
df_objects_new = df_objects_new.fillna('null')
df_objects_encoded= pd.get_dummies(df_objects_new,dtype=int)
st.write(df_objects_encoded.shape)
st.markdown(f"<h1>hello buddy check from here</h1>",unsafe_allow_html=True)
# df_objects_new['MSZoning'].value_counts()
df_encoded_col_value_check =0
for cols in df_objects_new.columns:
    st.markdown("### 🟣 Unique Values Count")
    value = df_objects_new[cols].nunique()
    st.dataframe(pd.DataFrame({"Unique Counts":[value]}))
    st.markdown("### 🟡 Value Counts")
    values=df_objects_new[cols].value_counts()
    st.dataframe(pd.DataFrame({"Unique Counts":[values]}))
    df_encoded_col_value_check +=df_objects_new[cols].nunique()
st.write(df_encoded_col_value_check)

# %%
st.dataframe(df_objects_encoded.head())

# %%
# sns.heatmap(df_objects.loc[:, df_objects.columns[:20]].isnull())
# plt.title("df_objects (old ones)", fontsize=16)
# sns.heatmap(df_objects_new.loc[:, df_objects_new.columns[:20]].isnull())
# plt.title("df_objects_new",fontdict={"color":"darkblue"}, fontsize=16)

# %%

drop_null_cols = [cols for cols in df_objects_encoded if 'null' in cols]
df_objects_encoded = df_objects_encoded.drop(columns=drop_null_cols)
st.dataframe(df_objects_encoded.columns)

# %%
new_df = pd.concat([df,df_objects_encoded],axis=1)
st.write(len(new_df.columns))
st.dataframe(new_df.head())

# %%
new_df = new_df.drop(df.select_dtypes(include=['object']),axis=1)
check = new_df.isna().sum()[new_df.isna().sum()>0].index
# sns.heatmap(new_df.loc[:, new_df.columns[:10]].isna())
st.write(new_df.info())


# %%
for dfs in check:
    if new_df[dfs].skew()>1 or new_df[dfs].skew()<-1:
        st.write(f'{dfs}  =>  {new_df[dfs].skew()}')
    else:
        st.write(f'{dfs}  =>  {new_df[dfs].skew()}')
# st.write(new_df['3SsnPorch'].isnull().sum())
grouptby_median = [ dfs for dfs in check if new_df[dfs].skew()>1]

# %%
# """Representation of right big skew,deviated the mean from zero to 0.6 because of 4 value out of 2742"""
# st.write(new_df['BsmtHalfBath'].mean())
# st.write(new_df['BsmtHalfBath'].median())
# st.write("this is lenght of value bigger than one =>",len(new_df[new_df['BsmtHalfBath']>1.0].index))
# st.write("this is exactly equal to zero =>",len(new_df[new_df['BsmtHalfBath']==0.0].index))
# st.write(new_df['BsmtHalfBath'].mode()[0])
# # st.write(new_df['BsmtHalfBath'].count())
# sns.histplot(df['LotFrontage'], kde=True)
# sns.boxplot(x='MSZoning', y='LotFrontage', data=df)
"""Categorical and Numerical DATA"""
st.write(len(new_df.columns))
for col in new_df.columns:
    if (null_val:=int(new_df[col].isna().sum())) >0 :
        st.write(null_val,col)
        # sns.heatmap(new_df[col].isna())
    new_df[col] = new_df[col].fillna(new_df[col].median())
skewed_cols = new_df[new_df.columns].skew()
skewed_cols = skewed_cols[skewed_cols > 1].index
for col in skewed_cols:
    new_df[col] = np.log1p(new_df[col])

# sns.heatmap(new_df.isnull())

# %%
train_df = new_df[new_df['SalePrice'] > 0]
test_df = new_df[new_df['SalePrice'] == 0]

# %%

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
# from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor

# %%

# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error
# from sklearn.linear_model import LinearRegression
# # from xgboost import XGBRegressor
# from sklearn.ensemble import RandomForestRegressor

# data=[
#     {'Apple':'30','Bananas':'40'},
#     {'Apple':'30','Bananas':'40'}
# ]
# cols=['2104 sales price','2104 sales price']
# fruits= pd.DataFrame(data,index=cols)
# fruits


# %% [markdown]
# 

# %%
# ages = pd.Series([25, 30, 35])
# st.write(ages)
# # Creating a DataFrame using Series
# names = pd.Series(['John', 'Alice', 'Bob'])
# cities = pd.Series(["New York", 'Los Angeles', 'Chicago'])
# st.write(names)
# st.write(cities)
# df = pd.DataFrame({
# 'Age': ages,
# 'Name': names,
# 'City': cities,
# })

# df.sort_values('Age')

# df['City'] = ['Delhi', 'Mumbai', 'Lucknow']
# df.insert(0,'Cities',['Delhi', 'Mumbai', 'Lucknow'])
# df['country']='null'

# new_row = pd.DataFrame([{'Name': 'Aman', 'Age': 22, 'City': 'Delhi'}])
# st.write("\n\n")
# df=pd.concat([new_row,df],ignore_index=False)
# df['Age'] = df['Age'].replace(30, 99)
# df

# %%



