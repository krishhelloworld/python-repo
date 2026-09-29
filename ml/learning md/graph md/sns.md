This is an excellent reference to keep while doing EDA and machine learning. Below is a practical Seaborn cheat sheet with the **most-used functions**, their **important arguments**, **one-line code examples**, and **where they're used**.

---

# Seaborn (`sns`) Cheat Sheet

| Function            | Important Arguments                          | One-line Example                                 | Used In        | Purpose                          |
| ------------------- | -------------------------------------------- | ------------------------------------------------ | -------------- | -------------------------------- |
| `sns.histplot()`    | `x`, `data`, `bins`, `kde`, `hue`            | `sns.histplot(data=df,x='Age',bins=20,kde=True)` | EDA            | Distribution of numeric data     |
| `sns.countplot()`   | `x`, `y`, `data`, `hue`, `order`             | `sns.countplot(data=df,x='Gender')`              | EDA            | Frequency of categories          |
| `sns.boxplot()`     | `x`, `y`, `data`, `hue`, `palette`           | `sns.boxplot(data=df,y='Salary')`                | EDA            | Detect outliers                  |
| `sns.violinplot()`  | `x`, `y`, `data`, `hue`, `split`             | `sns.violinplot(data=df,y='Salary')`             | EDA            | Distribution + Outliers          |
| `sns.scatterplot()` | `x`, `y`, `data`, `hue`, `style`, `size`     | `sns.scatterplot(data=df,x='Age',y='Salary')`    | Correlation    | Relationship between variables   |
| `sns.lineplot()`    | `x`, `y`, `data`, `hue`, `style`             | `sns.lineplot(data=df,x='Year',y='Sales')`       | Time Series    | Trend analysis                   |
| `sns.barplot()`     | `x`, `y`, `data`, `estimator`, `ci`, `hue`   | `sns.barplot(data=df,x='City',y='Sales')`        | EDA            | Average/Sum by category          |
| `sns.pointplot()`   | `x`, `y`, `data`, `hue`                      | `sns.pointplot(data=df,x='Month',y='Profit')`    | Statistics     | Mean with confidence interval    |
| `sns.stripplot()`   | `x`, `y`, `data`, `jitter`, `hue`            | `sns.stripplot(data=df,x='Gender',y='Salary')`   | EDA            | Individual observations          |
| `sns.swarmplot()`   | `x`, `y`, `data`, `hue`                      | `sns.swarmplot(data=df,x='Gender',y='Salary')`   | EDA            | Non-overlapping observations     |
| `sns.regplot()`     | `x`, `y`, `data`, `order`, `ci`              | `sns.regplot(data=df,x='Age',y='Salary')`        | Regression     | Scatter + Regression line        |
| `sns.lmplot()`      | `x`, `y`, `data`, `hue`                      | `sns.lmplot(data=df,x='Age',y='Salary')`         | Regression     | Regression by category           |
| `sns.residplot()`   | `x`, `y`, `data`                             | `sns.residplot(data=df,x='Age',y='Salary')`      | Error Analysis | Residual plot                    |
| `sns.heatmap()`     | `data`, `annot`, `cmap`, `fmt`, `linewidths` | `sns.heatmap(df.corr(),annot=True)`              | Correlation    | Correlation matrix               |
| `sns.pairplot()`    | `data`, `hue`, `diag_kind`                   | `sns.pairplot(df)`                               | EDA            | Relationship among all variables |
| `sns.jointplot()`   | `x`, `y`, `data`, `kind`                     | `sns.jointplot(data=df,x='Age',y='Salary')`      | Correlation    | Scatter + Distribution           |
| `sns.kdeplot()`     | `x`, `data`, `fill`, `hue`                   | `sns.kdeplot(data=df,x='Age',fill=True)`         | Statistics     | Density estimation               |
| `sns.ecdfplot()`    | `x`, `data`, `hue`                           | `sns.ecdfplot(data=df,x='Age')`                  | Statistics     | Cumulative distribution          |
| `sns.clustermap()`  | `data`, `cmap`, `annot`                      | `sns.clustermap(df.corr())`                      | Clustering     | Clustered heatmap                |
| `sns.rugplot()`     | `x`, `data`                                  | `sns.rugplot(data=df,x='Age')`                   | Distribution   | Tick marks for observations      |

---

# Most Important Arguments

| Argument          | Used In               | Purpose                   |
| ----------------- | --------------------- | ------------------------- |
| `data=`           | Almost every function | DataFrame                 |
| `x=`              | All plots             | X-axis column             |
| `y=`              | Most plots            | Y-axis column             |
| `hue=`            | Most plots            | Group by another column   |
| `style=`          | Scatter, Line         | Different marker styles   |
| `size=`           | Scatter               | Marker size               |
| `palette=`        | Most plots            | Color theme               |
| `bins=`           | Histplot              | Number of histogram bins  |
| `kde=True`        | Histplot              | Add density curve         |
| `fill=True`       | KDE                   | Fill density curve        |
| `annot=True`      | Heatmap               | Show numbers              |
| `fmt='.2f'`       | Heatmap               | Decimal formatting        |
| `cmap='coolwarm'` | Heatmap               | Color map                 |
| `linewidths=1`    | Heatmap               | Cell borders              |
| `order=`          | Countplot, Barplot    | Custom category order     |
| `estimator=`      | Barplot               | Mean, Sum, Median, etc.   |
| `ci=`             | Barplot               | Confidence interval       |
| `split=True`      | Violinplot            | Split by hue              |
| `jitter=True`     | Stripplot             | Spread overlapping points |
| `kind='hex'`      | Jointplot             | Hexbin plot               |
| `kind='kde'`      | Jointplot             | Density plot              |
| `diag_kind='kde'` | Pairplot              | KDE on diagonal           |

---

# Which Plot for Which Problem?

| Problem                      | Best Seaborn Function |
| ---------------------------- | --------------------- |
| Distribution                 | `histplot()`          |
| Density                      | `kdeplot()`           |
| Outliers                     | `boxplot()`           |
| Distribution + Outliers      | `violinplot()`        |
| Category Frequency           | `countplot()`         |
| Compare Means                | `barplot()`           |
| Scatter Relationship         | `scatterplot()`       |
| Regression                   | `regplot()`           |
| Time Series                  | `lineplot()`          |
| Correlation Matrix           | `heatmap()`           |
| Pairwise Relationships       | `pairplot()`          |
| Two Variables + Distribution | `jointplot()`         |
| Residual Analysis            | `residplot()`         |
| Cluster Correlation          | `clustermap()`        |
| Cumulative Distribution      | `ecdfplot()`          |

---

# Most Used Plots in Machine Learning

| Stage                | Plot                        |
| -------------------- | --------------------------- |
| Missing Values       | `sns.heatmap(df.isnull())`  |
| Distribution         | `sns.histplot()`            |
| Outlier Detection    | `sns.boxplot()`             |
| Correlation          | `sns.heatmap(df.corr())`    |
| Feature Relationship | `sns.scatterplot()`         |
| Feature vs Target    | `sns.regplot()`             |
| Category Counts      | `sns.countplot()`           |
| Pairwise EDA         | `sns.pairplot()`            |
| Residual Analysis    | `sns.residplot()`           |
| Class Imbalance      | `sns.countplot(x='Target')` |

### Learning order

If you're focusing on data science and machine learning, these are the **10 Seaborn functions to master first**:

1. `sns.histplot()`
2. `sns.countplot()`
3. `sns.boxplot()`
4. `sns.scatterplot()`
5. `sns.lineplot()`
6. `sns.barplot()`
7. `sns.heatmap()`
8. `sns.pairplot()`
9. `sns.regplot()`
10. `sns.violinplot()`

Together, these cover the majority of EDA tasks you'll perform in real-world ML projects.
