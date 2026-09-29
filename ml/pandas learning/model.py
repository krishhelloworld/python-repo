# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: base
#     language: python
#     name: python3
# ---

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
df1 = pd.read_csv("train.csv",index_col=0)#index_col to remove the default indexing and giving the new one
df2 = pd.read_csv("test.csv",index_col=0)
# print(f'df1.shape=>{df1.head()}')
# print(f'df2.shape=>{df2.head()}')
# print(df1.info())
print(df1.describe(include='all'))

if "SalePrice" not in df2.columns:
    df2['SalePrice']=0
df = pd.concat(
    [df1,df2],
    axis=0,
 )
print(f'df.shape=> {df.shape}')
df.head()


# %%
df_null =df[df.isnull().sum()[df.isnull().sum()>0].index]
df_null.head()
# for i in df_null.columns:
#     print(f'"{i}"        =>{df[f"{i}"].isnull().sum()}')
# null_cols = df.columns[df.isnull().sum() > 0]
# df_null = df[null_cols]
#df[df['MSZoning'].isnull()==True] to get the specific column with containing null
# for i in range(len(df)):
#     print(f'{df.iloc[[i],0:3]}\t ......=> {df.iloc[i].isnull().sum()}')
# for i in df.index:
#     print(f'{df.iloc[i]}        =>{df.loc[i].isnull().sum()}')


# %%
print(df_null.shape)
sns.heatmap(df_null.loc[:,df_null.columns[0:20]].isnull())
sns.histplot(df['SalePrice'], kde=True)

# %%
df_objects = df[df.select_dtypes(include='object').columns]
# print(df_objects.shape)#(2919, 43)
df_objects_nan_arr=df_objects.isna().sum()[df_objects.isna().sum()>1100].index
# print(df[df_objects_nan_arr].isna().sum())
# print(df[df_objects_nan_arr])
# df_objects[df_objects_nan_arr]
# df_objects.drop(columns=df_objects_nan_arr).shape
# print(df_objects.shape)#includes all the object ones 
# print(df_objects[df_objects_nan_arr].shape)#arr of columns having more than 1100 nan sum
# print(df_objects.drop(columns=df_objects_nan_arr).shape)#removing these columns 
df= df.drop(columns=df_objects_nan_arr)#6 columns removed from the original
# df

corr = df.corr(numeric_only=True,method="spearman")
mask = np.triu(np.ones_like(corr, dtype=bool))
# plt.figure(figsize=(16, 12))
# sns.heatmap(corr, mask=mask, cmap="coolwarm", annot=True, fmt=".2f")
# plt.show()

"""CORELATION IN THIS HELP ME TO FIND NAN VALUES ,when two columns ARE CONNECTED TOGETHER SUCH THAT WHEN I REPLACING NAN VALUES I WILL TAKE THESE HELPS TO FILL THEIR VALUE 
like here garage cars and garageArea are together close 
"""
target_corr = corr["GarageCars"].sort_values(ascending=False)
print(target_corr[target_corr>=0])

# %%
df_objects_new = df_objects.drop(columns=df_objects_nan_arr)
print(df_objects.shape)
print(df_objects_new.shape)
df_objects_new = df_objects_new.fillna('null')
df_objects_encoded= pd.get_dummies(df_objects_new,dtype=int)
print(df_objects_encoded.shape)
# df_objects_new['MSZoning'].value_counts()
df_encoded_col_value_check =0
for cols in df_objects_new.columns:
    print(f'\033[35m{df_objects_new[cols].nunique()}\033[0m\t\n\033[33m{df_objects_new[cols].value_counts()}\033[0m\n\n')
    df_encoded_col_value_check +=df_objects_new[cols].nunique()
print(df_encoded_col_value_check)

# %%
df_objects_encoded.head()

# %%
# sns.heatmap(df_objects.loc[:, df_objects.columns[:20]].isnull())
# plt.title("df_objects (old ones)", fontsize=16)
# sns.heatmap(df_objects_new.loc[:, df_objects_new.columns[:20]].isnull())
# plt.title("df_objects_new",fontdict={"color":"darkblue"}, fontsize=16)

# %%
drop_null_cols = [cols for cols in df_objects_encoded if 'null' in cols]
df_objects_encoded = df_objects_encoded.drop(columns=drop_null_cols)
df_objects_encoded.columns

# %%
new_df = pd.concat([df,df_objects_encoded],axis=1)
print(len(new_df.columns))
new_df.head()

# %%
new_df = new_df.drop(df.select_dtypes(include=['object']),axis=1)
check = new_df.isna().sum()[new_df.isna().sum()>0].index
# sns.heatmap(new_df.loc[:, new_df.columns[:10]].isna())
print(new_df.info())


# %%
for dfs in check:
    if new_df[dfs].skew()>1 or new_df[dfs].skew()<-1:
        print(f'\033[33m{dfs}\033[0m  =>  \033[32m{new_df[dfs].skew()}\033[0m')
    else:
        print(f'{dfs}\033[0m  =>  {new_df[dfs].skew()}')
# print(new_df['3SsnPorch'].isnull().sum())
grouptby_median = [ dfs for dfs in check if new_df[dfs].skew()>1]

# %%
# """Representation of right big skew,deviated the mean from zero to 0.6 because of 4 value out of 2742"""
# print(new_df['BsmtHalfBath'].mean())
# print(new_df['BsmtHalfBath'].median())
# print("this is lenght of \033[33mvalue bigger than one =>\033[0m",len(new_df[new_df['BsmtHalfBath']>1.0].index))
# print("this is \033[33mexactly equal to zero =>\033[0m",len(new_df[new_df['BsmtHalfBath']==0.0].index))
# print(new_df['BsmtHalfBath'].mode()[0])
# # print(new_df['BsmtHalfBath'].count())
# sns.histplot(df['LotFrontage'], kde=True)
# sns.boxplot(x='MSZoning', y='LotFrontage', data=df)
"""Categorical and Numerical DATA"""
print(len(new_df.columns))
for col in new_df.columns:
    if (null_val:=int(new_df[col].isna().sum())) >0 :
        print(null_val,col)
        # sns.heatmap(new_df[col].isna())
    new_df[col] = new_df[col].fillna(new_df[col].median())
skewed_cols = new_df[new_df.columns].skew()
skewed_cols = skewed_cols[skewed_cols > 1].index
for col in skewed_cols:
    new_df[col] = np.log1p(new_df[col])


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
# print(ages)
# # Creating a DataFrame using Series
# names = pd.Series(['John', 'Alice', 'Bob'])
# cities = pd.Series(["New York", 'Los Angeles', 'Chicago'])
# print(names)
# print(cities)
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
# print("\n\n")
# df=pd.concat([new_row,df],ignore_index=False)
# df['Age'] = df['Age'].replace(30, 99)
# df

# %%
l = ['tc','maths']
l.append('python')

# print(l)
l= [0,1,2,3,4,5,6,7,8]
# (start):(end):(step)
print(l[-0::])

# %%
import string
print(ord('a'))
print(chr(97))

# %%
lst =[1,-2,0,5,-3]
k=0
def lessthan(lst,k):
    return [i for i in lst if i<k]
ans = lessthan(lst,k)
print(ans)

# %%
l = [1,2,3,4,5,6,7,8,9]
print(l[:-9:-1])
print(l[2:8:])
print(l[::2])
print(l[4::])#confirm it
print(l[:5:][::-1])#confirm it 
print([i%2 for i in l])

# %%
lst1 =[1,3,4,5]
lst2 =[2,3,4,9]
def makepair(lst1,lst2):
    ans_lst=[]
    x = len(lst1)
    for i in range(x):
        ans_lst.append((lst1[i],lst2[i]))
    return ans_lst
print(makepair(lst1,lst2))


# %%
def alternating(lst):
    for i in range(len(lst)):
        if i%2==0 and lst[i]%2==0 or i%2!=0 and lst[i]%2!=0:
            pass
        else:
            return False
    return True
print(alternating([10]))
print([("new world").split])
            

# %%
# | Rank | Number | Approx ownership |
# | ---- | ------ | ---------------- |
# | 🥇 2 | 2      | 50,000           |
# | 🥈 3 | 3      | 16,666           |
# | 🥉 5 | 5      | 13,333           |
# | 4    | 7      | 11,428           |
# | 5    | 11     | 9,090            |
# | 6    | 13     | 7,692            |
# | 7    | 17     | 5,882            |
# | 8    | 19     | 5,263            |
# | 9    | 23     | 4,347            |
# | 10   | 29     | 3,448            |

def isprime(n):
    if n<=1:
        return False
    if n==2 or n==3 or n==5:
        return True
    elif  n%2==0 or n%3==0 or n%5==0 :
        return False
    i=5
    while i*i <=n:
        if n%i==0 or n%(i+2)==0:
            return False
        i+=6
    return True
print(isprime(342384109283490239))
    

# %%
import sys

sys.set_int_max_str_digits(10000)
def fibo(n):
    fibonacc=[0]*(n+2)
    fibonacc[1]=0
    fibonacc[2]=1
    for i in range(3,n+1):
        fibonacc[i]= fibonacc[i-1]+fibonacc[i-2]
    return fibonacc[n]
print(fibo(111000))

# %%

# %%
import matplotlib.pyplot as  plt
foods= ['Meat', 'Banana', 'Avocados', 'Sweet Potatoes', 'Spinach','Watermelon', 'Coconut water', 'Beans', 'Legumes', 'Tomato']
calories = [250, 130, 140, 120, 20, 20, 10, 50, 40, 19]
potassium = [40, 55, 20, 30, 40, 32, 10, 26, 25, 201]
fat= [8, 5, 3, 6, 1, 1.5, 0, 2, 1.5, 2.51]
plt.figure(figsize=(4,6))
plt.barh(foods,calories)
plt.show()
#########################

plt.barh(foods,potassium)
plt.show()
#####################
plt.barh(foods,fat)
plt.show()

# %%
print('krish')
print(10+40)

# %%
