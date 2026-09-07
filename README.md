````markdown
# OSSurvive — Open-Source Project Survival Analytics

> **From repository activity to survival risk.**

OSSurvive is an open-source project survival analytics platform designed to study how repository activity, inactivity, collaboration, contributors, and project lifecycle signals relate to the long-term survival of open-source software projects.

The project combines historical GitHub repository data, exploratory analysis, survival analysis, feature engineering, and machine-learning-based risk experimentation into an interactive Streamlit research dashboard.

---

## Live Demo

**Streamlit App:**  
https://ossurvive.streamlit.app/

---

## Research Question

> **Can repository activity and collaboration patterns provide useful signals about the survival risk of open-source projects?**

OSSurvive approaches this question by analyzing repository behavior over time rather than relying only on current repository statistics.

The analysis focuses on signals such as:

- Commit activity
- Inactivity periods
- Contributors
- Collaboration patterns
- Issues
- Project age
- Active-month ratios
- Changes in repository activity
- Longest inactivity gaps
- Zero-commit streaks

---

## What OSSurvive Does

OSSurvive follows a research-oriented analytics pipeline:

```text
GitHub Repository Data
        ↓
Historical Activity Collection
        ↓
Activity & Collaboration Features
        ↓
Feature Engineering
        ↓
Survival Dataset
        ↓
Kaplan–Meier Survival Analysis
        ↓
Risk Modeling Experiment
        ↓
Interactive Research Dashboard
````

The goal is not simply to predict whether a repository will become inactive.

Instead, the project attempts to understand:

1. How inactivity can be defined.
2. How survival changes under different inactivity thresholds.
3. What repository signals are associated with survival risk.
4. How project activity changes across its lifecycle.
5. Whether historical repository features can provide useful risk signals.

---

# Research Scope

The current study analyzes:

* **18 open-source projects**
* Historical repository activity
* Monthly repository behavior
* Contributor activity
* Collaboration signals
* Inactivity periods
* Survival duration
* Risk-related features

Three inactivity thresholds are examined:

| Threshold | Inactivity Events | Event Rate |
| --------- | ----------------: | ---------: |
| 6 months  |            8 / 18 |      44.4% |
| 12 months |            6 / 18 |      33.3% |
| 18 months |            4 / 18 |      22.2% |

The threshold comparison demonstrates that the definition of "project inactivity" has a substantial effect on the observed survival outcomes.

---

# Key Findings

## 1. Survival depends strongly on the inactivity definition

Using increasingly strict inactivity thresholds reduces the number of projects classified as inactive:

* 6-month threshold → **44.4%**
* 12-month threshold → **33.3%**
* 18-month threshold → **22.2%**

This highlights an important methodological issue in open-source survival research: there is no single universally correct inactivity threshold.

---

## 2. Long-term survival declines over project age

The Kaplan–Meier analysis estimates approximately:

* **94.1% survival at 12 months**
* **51.3% survival at 120 months**
* Approximately **51.3% at the final observed duration of 163 months**

The survival curve illustrates how the probability of remaining active changes as project age increases.

---

## 3. Inactivity streaks are important risk signals

The risk experiment identifies several features associated with the predicted risk of inactivity.

One of the strongest signals is:

**`zero_commit_streak`**

Its positive model coefficient indicates that longer periods without commits are associated with increased inactivity risk within the modeling setup.

---

## 4. Consistent activity is associated with lower risk

The feature:

**`active_month_ratio_12m`**

has a negative model coefficient.

This suggests that projects active across a larger proportion of the previous 12 months tend to exhibit lower modeled inactivity risk.

---

## 5. Project age also matters

**`project_age_months`** has a positive coefficient in the current model.

This indicates that project age is associated with the modeled risk outcome.

Importantly, this should not be interpreted as saying that older projects are inherently unhealthy. Project age can interact with many other lifecycle and activity characteristics.

---

# Application

OSSurvive provides six interactive sections.

### 1. Research Overview

Introduces the research problem, dataset, analytical approach, and major findings.

### 2. Project Observatory

Provides a repository-level view of the projects included in the study and their activity characteristics.

### 3. Survival Study

Explores project survival using Kaplan–Meier analysis and compares survival behavior over time.

### 4. Lifecycle Analysis

Examines how repository activity, contributors, collaboration, and other signals change throughout a project's lifecycle.

### 5. Risk Experiment

Explores modeled inactivity risk and feature importance using historical repository features.

### 6. Methodology

Documents the analytical definitions, data pipeline, feature engineering, survival methodology, and modeling approach.

---

# Methodology

## Historical Data

Repository information is collected and transformed into historical monthly observations.

The historical pipeline includes:

* Repository activity
* Contributors
* Collaboration
* Issues
* Monthly repository features

These datasets are then integrated into modeling and survival-analysis datasets.

---

## Feature Engineering

Repository-level and monthly features are engineered to capture different dimensions of project health.

Examples include:

* `project_age_months`
* `active_month_ratio_12m`
* `zero_commit_streak`
* `inactivity_streak`
* `activity_change_3m`
* `longest_inactivity_gap`
* `issue_net_flow_6m`

These features attempt to capture both recent activity and longer-term project behavior.

---

# Survival Analysis

OSSurvive uses **Kaplan–Meier survival analysis** to estimate the probability that a project remains active over time.

The analysis treats repository inactivity as the event of interest.

A major part of the study is threshold sensitivity.

Instead of assuming that a project becomes inactive after one fixed period, the analysis evaluates:

```text
6-month inactivity threshold
12-month inactivity threshold
18-month inactivity threshold
```

This allows the effect of the inactivity definition to be examined directly.

---

# Risk Modeling Experiment

The project also includes a machine-learning-based risk experiment.

The current modeling pipeline uses:

* Feature imputation
* Feature scaling
* Logistic Regression
* Historical repository features

The model is used primarily as an **analytical experiment** to investigate relationships between repository characteristics and inactivity risk.

Feature coefficients are used to understand which signals contribute positively or negatively to the modeled risk.

This is intended as an exploratory research component rather than a production prediction system.

---

# Data Pipeline

The project is organized around a reproducible analytical pipeline:

```text
Repository Selection
        ↓
GitHub Data Collection
        ↓
Historical Activity
        ↓
Contributor History
        ↓
Collaboration History
        ↓
Feature Engineering
        ↓
Target Construction
        ↓
Modeling Dataset
        ↓
Survival Analysis
        ↓
Risk Modeling
        ↓
Dashboard
```

---

# Project Structure

```text
OSSurvive/
│
├── analysis/
│   ├── notebooks/
│   └── reports/
│
├── app/
│   ├── main.py
│   ├── assets/
│   ├── components/
│   ├── data/
│   ├── pages/
│   └── styles/
│
├── data/
│   ├── historical/
│   ├── processed/
│   ├── raw/
│   └── repositories/
│
├── src/
│   ├── build_modeling_dataset.py
│   ├── build_targets.py
│   ├── collaboration_history.py
│   ├── contributor_history.py
│   ├── feature_engineering.py
│   ├── github_client.py
│   ├── historical_activity.py
│   ├── integrate_historical_data.py
│   ├── model_interpretation.py
│   ├── repository_selection.py
│   ├── survival_analysis.py
│   ├── threshold_sensitivity.py
│   └── train_prediction_model.py
│
├── tests/
│   ├── test_collaboration_history.py
│   ├── test_contributor_history.py
│   ├── test_feature_engineering.py
│   ├── test_github_client.py
│   ├── test_github_collaboration_api.py
│   └── test_historical_activity.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Technology Stack

### Programming

* Python

### Data Analysis

* Pandas
* NumPy

### Visualization

* Matplotlib

### Statistical Analysis

* Lifelines
* Kaplan–Meier survival analysis

### Machine Learning

* Scikit-learn
* Logistic Regression
* Feature preprocessing and imputation

### Data Collection

* GitHub API
* Requests

### Application

* Streamlit

### Configuration

* Python-dotenv

---

# Repository Data

The repository contains processed historical datasets used by the application, including:

```text
data/historical/
├── collection_state.csv
├── kaplan_meier_survival.csv
├── model_feature_importance.csv
├── prediction_results.csv
├── repository_activity_monthly.csv
├── repository_collaboration_monthly.csv
├── repository_contributors_monthly.csv
├── repository_engineered_features.csv
├── repository_modeling_dataset.csv
├── repository_monthly_features.csv
├── repository_prediction_targets.csv
├── repository_survival_dataset.csv
└── survival_threshold_comparison.csv
```

Raw repository metadata is stored under:

```text
data/raw/
```

Local repository clones are intentionally excluded from version control.

---

# Important Limitations

OSSurvive is a research and portfolio project, and the current results should be interpreted within its limitations.

### Small project sample

The current survival study contains **18 projects**.

Therefore, the results should not be treated as representative of the entire open-source ecosystem.

### Definition of inactivity

Project inactivity is dependent on the selected threshold.

Changing the threshold changes the observed event rate and survival estimates.

### Observational data

The analysis identifies associations in repository behavior. It does not establish that a particular feature directly causes a project to survive or fail.

### Model scope

The risk model is an exploratory experiment and should not be interpreted as a production-grade prediction service.

### Historical data limitations

GitHub activity does not capture every aspect of project health.

Factors such as:

* Funding
* Organizational support
* Private development
* Community discussions outside GitHub
* Commercial adoption
* Maintainer intentions

may influence project survival but are not fully represented in the current dataset.

---

# Future Work

Potential extensions include:

* Expanding the repository sample substantially.
* Incorporating more historical GitHub data.
* Testing additional survival-analysis techniques.
* Comparing multiple machine-learning models.
* Adding time-to-event modeling approaches.
* Improving calibration of risk predictions.
* Incorporating release activity and pull-request behavior.
* Adding community and ecosystem signals.
* Performing cross-validation across larger project samples.
* Studying different open-source ecosystems separately.

---

# Why This Project?

OSSurvive was built to explore a practical data-analysis question using real-world software-engineering data.

Rather than treating a repository as a static collection of stars, forks, and commits, the project looks at **how project behavior changes over time**.

This makes it possible to combine:

```text
Data Collection
+
Data Cleaning
+
Feature Engineering
+
Exploratory Analysis
+
Statistical Analysis
+
Machine Learning
+
Data Visualization
+
Interactive Analytics
```

into a single end-to-end project.

---

# Project Status

**Current status: Research prototype / portfolio project**

The analytical pipeline and interactive dashboard are functional, with historical datasets, survival analysis, lifecycle analysis, and a risk-modeling experiment implemented.

The project is still open to further research and validation with a larger dataset.

---

# Author

**Gourav Godara**

Data Analytics | Python | Machine Learning | Open-Source Analytics

---

## License

This project is intended for research, educational, and portfolio purposes.

See the repository for the applicable project license and data-source considerations.

````

### One important correction

I intentionally wrote **"research prototype / portfolio project"** rather than claiming OSSurvive is a production prediction system. With only 18 projects in the survival study, that's the honest and defensible framing.

After saving `README.md`, run:

```powershell
git status
````