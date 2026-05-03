Good—this is the right direction. You already know basics like `df.isna().sum()`. Now I’ll show you **advanced reusable patterns** in pandas that people actually use in real data analysis workflows.

These are not “one-liners”, but **reusable building blocks for serious cleaning + exploration**.

---

# 🔥 1. Full Data Quality Report (very powerful)

Instead of manually checking everything:

```python id="dq1"
def data_quality_report(df):
    return {
        "shape": df.shape,
        "missing_values": df.isna().sum(),
        "missing_percent": (df.isna().mean() * 100).round(2),
        "duplicate_rows": df.duplicated().sum(),
        "dtypes": df.dtypes,
        "unique_counts": df.nunique()
    }
```

👉 Use:

```python id="dq2"
report = data_quality_report(df)
```

---

# 🔥 2. Column profiling (advanced EDA tool)

```python id="cp1"
def profile_column(df, col):
    return {
        "dtype": df[col].dtype,
        "missing": df[col].isna().sum(),
        "unique": df[col].nunique(),
        "top_values": df[col].value_counts().head(5),
        "mean": df[col].mean() if df[col].dtype != "object" else None
    }
```

👉 Helps detect:

* categorical imbalance
* numeric anomalies
* missing patterns

---

# 🔥 3. Automatic outlier detection (IQR method)

```python id="out1"
def detect_outliers(df, col):
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return df[(df[col] < lower) | (df[col] > upper)]
```

---

# 🔥 4. Smart missing value handler

```python id="mv1"
def fill_missing(df):
    df = df.copy()

    for col in df.columns:
        if df[col].dtype == "object":
            df[col].fillna(df[col].mode()[0], inplace=True)
        else:
            df[col].fillna(df[col].median(), inplace=True)

    return df
```

👉 Automatically chooses strategy based on type.

---

# 🔥 5. Correlation scanner (feature selection helper)

```python id="corr1"
def high_correlation_pairs(df, threshold=0.8):
    corr = df.corr(numeric_only=True)
    pairs = []

    for i in corr.columns:
        for j in corr.columns:
            if i != j and abs(corr.loc[i, j]) > threshold:
                pairs.append((i, j, corr.loc[i, j]))

    return sorted(pairs, key=lambda x: -abs(x[2]))
```

👉 Finds redundant features.

---

# 🔥 6. Automated summary stats (better than describe)

```python id="sum1"
def full_summary(df):
    return {
        "mean": df.mean(numeric_only=True),
        "median": df.median(numeric_only=True),
        "skew": df.skew(numeric_only=True),
        "kurtosis": df.kurtosis(numeric_only=True)
    }
```

---

# 🔥 7. Column drift checker (important in ML pipelines)

```python id="dr1"
def column_drift(df1, df2):
    return {
        "missing_in_new": set(df1.columns) - set(df2.columns),
        "new_columns": set(df2.columns) - set(df1.columns)
    }
```

👉 Used in production ML systems.

---

# 🔥 8. Quick EDA pipeline (real-world style)

```python id="eda1"
def quick_eda(df):
    print("SHAPE:", df.shape)
    print("\nMISSING %:\n", df.isna().mean().sort_values(ascending=False))
    print("\nDUPLICATES:", df.duplicated().sum())
    print("\nNUMERIC SUMMARY:\n", df.describe())
```

---

# 🧠 What makes these “advanced”

These go beyond simple commands because they:

* automate repeated analysis
* scale to multiple datasets
* combine multiple checks in one function
* are used in real-world data pipelines

---

# 🚀 If you want next level (pro tier)

I can also show you:

* full **AutoEDA system (like Pandas Profiling replacement)**
* feature engineering pipeline functions
* memory optimization tricks (important for big data)
* fast groupby optimization patterns
* production-grade cleaning pipelines used in ML systems

Just tell me 👍
