That's a great idea. Below is a practical cheat sheet of the most commonly used **Matplotlib (`plt`) functions** for **EDA, visualization, model evaluation, and ML**.

| Function             | Important Arguments          | One-line Example              | Used In                 | Purpose                                |
| -------------------- | ---------------------------- | ----------------------------- | ----------------------- | -------------------------------------- |
| `plt.figure()`       | `figsize`, `dpi`             | `plt.figure(figsize=(8,5))`   | EDA                     | Create a new figure                    |
| `plt.subplot()`      | `nrows,ncols,index`          | `plt.subplot(1,2,1)`          | EDA                     | Multiple plots in one figure           |
| `plt.subplots()`     | `nrows`, `ncols`, `figsize`  | `fig,ax=plt.subplots(2,2)`    | EDA                     | Preferred way to create multiple plots |
| `plt.plot()`         | `x,y,color,linestyle,marker` | `plt.plot(x,y)`               | Trends, Time Series     | Draw line graph                        |
| `plt.scatter()`      | `x,y,c,s`                    | `plt.scatter(x,y)`            | Correlation, Regression | Relationship between two variables     |
| `plt.bar()`          | `x,height`                   | `plt.bar(cat,val)`            | Categorical EDA         | Compare categories                     |
| `plt.barh()`         | `y,width`                    | `plt.barh(cat,val)`           | Feature Importance      | Horizontal bar chart                   |
| `plt.hist()`         | `x,bins`                     | `plt.hist(df['Age'],bins=20)` | Distribution            | Histogram                              |
| `plt.boxplot()`      | `x`                          | `plt.boxplot(df['Age'])`      | Outlier Detection       | Detect outliers                        |
| `plt.pie()`          | `x,labels,autopct`           | `plt.pie(val,labels=lab)`     | Composition             | Percentage distribution                |
| `plt.imshow()`       | `image,cmap`                 | `plt.imshow(img)`             | Computer Vision         | Display image                          |
| `plt.errorbar()`     | `x,y,yerr`                   | `plt.errorbar(x,y,yerr=e)`    | Error Analysis          | Error bars                             |
| `plt.stem()`         | `x,y`                        | `plt.stem(x,y)`               | Signal Processing       | Stem plot                              |
| `plt.step()`         | `x,y`                        | `plt.step(x,y)`               | Time Series             | Step graph                             |
| `plt.fill_between()` | `x,y1,y2`                    | `plt.fill_between(x,y)`       | Confidence Interval     | Fill area                              |
| `plt.contour()`      | `X,Y,Z`                      | `plt.contour(X,Y,Z)`          | ML Decision Boundary    | Contour plot                           |
| `plt.contourf()`     | `X,Y,Z`                      | `plt.contourf(X,Y,Z)`         | Classification          | Filled contour                         |
| `plt.hexbin()`       | `x,y`                        | `plt.hexbin(x,y)`             | Large Data              | Dense scatter replacement              |
| `plt.violinplot()`   | `dataset`                    | `plt.violinplot(df['Age'])`   | Distribution            | Shape + Outliers                       |
| `plt.eventplot()`    | `data`                       | `plt.eventplot(data)`         | Time Events             | Event visualization                    |

---

# Axis Functions

| Function             | Example                   | Purpose                 |
| -------------------- | ------------------------- | ----------------------- |
| `plt.title()`        | `plt.title("Sales")`      | Plot title              |
| `plt.xlabel()`       | `plt.xlabel("Age")`       | X-axis label            |
| `plt.ylabel()`       | `plt.ylabel("Salary")`    | Y-axis label            |
| `plt.xlim()`         | `plt.xlim(0,100)`         | X-axis range            |
| `plt.ylim()`         | `plt.ylim(0,50)`          | Y-axis range            |
| `plt.xticks()`       | `plt.xticks(rotation=45)` | Rotate/change x-ticks   |
| `plt.yticks()`       | `plt.yticks(fontsize=12)` | Modify y-ticks          |
| `plt.grid()`         | `plt.grid(True)`          | Grid lines              |
| `plt.legend()`       | `plt.legend()`            | Show legend             |
| `plt.tight_layout()` | `plt.tight_layout()`      | Avoid overlapping plots |
| `plt.show()`         | `plt.show()`              | Display plot            |
| `plt.savefig()`      | `plt.savefig("fig.png")`  | Save figure             |

---

# Common Plot Styling

| Function          | Example                        | Purpose                   |
| ----------------- | ------------------------------ | ------------------------- |
| `plt.style.use()` | `plt.style.use('ggplot')`      | Plot style                |
| `plt.rcParams`    | `plt.rcParams['font.size']=14` | Global settings           |
| `plt.annotate()`  | `plt.annotate('Peak',(3,5))`   | Add annotation            |
| `plt.text()`      | `plt.text(2,5,'Hello')`        | Add text                  |
| `plt.axhline()`   | `plt.axhline(y=0)`             | Horizontal reference line |
| `plt.axvline()`   | `plt.axvline(x=5)`             | Vertical reference line   |
| `plt.axline()`    | `plt.axline((0,0),(1,1))`      | Infinite line             |
| `plt.colorbar()`  | `plt.colorbar()`               | Add color scale           |

---

# Which plot to use in EDA?

| Problem                                    | Plot                                       |
| ------------------------------------------ | ------------------------------------------ |
| Distribution                               | `hist()`, `boxplot()`, `violinplot()`      |
| Outliers                                   | `boxplot()`                                |
| Relationship between two numeric variables | `scatter()`                                |
| Trend over time                            | `plot()`                                   |
| Compare categories                         | `bar()`                                    |
| Percentage share                           | `pie()`                                    |
| Multiple plots                             | `subplot()`, `subplots()`                  |
| Correlation Heatmap                        | *(Use Seaborn `sns.heatmap()`, not `plt`)* |
| Missing values                             | *(Use Seaborn heatmap or Pandas methods)*  |
| Decision boundary                          | `contourf()`                               |
| Confidence interval                        | `fill_between()`                           |

---

# Which library is preferred?

| Library                | Best For                                             |
| ---------------------- | ---------------------------------------------------- |
| **Matplotlib (`plt`)** | Basic plotting and customization                     |
| **Seaborn (`sns`)**    | EDA, statistical visualizations, attractive defaults |
| **Plotly**             | Interactive dashboards                               |
| **Pandas `.plot()`**   | Quick exploratory plots                              |

For most **machine learning EDA**, you'll primarily use:

* `plt.figure()`
* `plt.subplot()` / `plt.subplots()`
* `plt.scatter()`
* `plt.hist()`
* `plt.bar()`
* `plt.boxplot()`
* `plt.title()`
* `plt.xlabel()`
* `plt.ylabel()`
* `plt.legend()`
* `plt.grid()`
* `plt.tight_layout()`
* `plt.show()`

These cover the vast majority of plotting tasks you'll encounter before training and evaluating models.
