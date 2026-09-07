import streamlit as st
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OSSurvive — Lifecycle Analysis",
    page_icon="🔄",
    layout="wide",
)


# ============================================================
# DATA PATH
# ============================================================

APP_DIR = Path(__file__).resolve().parent.parent


def find_data_dir():
    possible_dirs = [
        APP_DIR / "data" / "historical",
        APP_DIR.parent / "data" / "historical",
        Path.cwd() / "data" / "historical",
        Path.cwd() / "app" / "data" / "historical",
    ]

    required = [
        "repository_modeling_dataset.csv",
        "repository_engineered_features.csv",
    ]

    for directory in possible_dirs:
        if all((directory / f).exists() for f in required):
            return directory

    st.error("Lifecycle Analysis data files could not be found.")
    st.stop()


DATA_DIR = find_data_dir()


def load_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        st.error(f"Required research file not found: {filename}")
        st.stop()

    return pd.read_csv(path)


modeling = load_csv("repository_modeling_dataset.csv")
engineered = load_csv("repository_engineered_features.csv")


# ============================================================
# DATA PREPARATION
# ============================================================

modeling["month"] = pd.to_datetime(
    modeling["month"],
    errors="coerce"
)

engineered["month"] = pd.to_datetime(
    engineered["month"],
    errors="coerce"
)

projects = modeling["repo_id"].nunique()

total_observations = len(modeling)

active_observations = int(
    modeling["meaningful_activity"].sum()
)

activity_rate = (
    active_observations / total_observations
    if total_observations
    else 0
)

# Monthly activity across the entire cohort
monthly_activity = (
    modeling
    .groupby("month")
    .agg(
        commits=("commits", "sum"),
        contributors=("contributors", "sum"),
        activity=("meaningful_activity", "sum"),
    )
    .reset_index()
    .sort_values("month")
)

# Project-level lifecycle summary
project_summary = (
    modeling
    .groupby(["repo_id", "full_name"])
    .agg(
        observations=("month", "count"),
        total_commits=("commits", "sum"),
        avg_monthly_commits=("commits", "mean"),
        avg_contributors=("contributors", "mean"),
        active_month_ratio=("meaningful_activity", "mean"),
        max_age_months=("project_age_months", "max"),
    )
    .reset_index()
)

project_summary["active_month_ratio"] = (
    project_summary["active_month_ratio"]
    .fillna(0)
)

# Lifecycle age buckets
bins = [0, 6, 12, 24, 36, 60, float("inf")]
labels = [
    "0–6",
    "7–12",
    "13–24",
    "25–36",
    "37–60",
    "60+",
]

modeling["lifecycle_stage"] = pd.cut(
    modeling["project_age_months"],
    bins=bins,
    labels=labels,
    include_lowest=True,
)

stage_summary = (
    modeling
    .groupby("lifecycle_stage", observed=False)
    .agg(
        observations=("repo_id", "count"),
        commits=("commits", "mean"),
        contributors=("contributors", "mean"),
        active_ratio=("meaningful_activity", "mean"),
    )
    .reset_index()
)

# Activity change distribution
activity_change = modeling[
    "activity_change_3m"
].dropna()


# ============================================================
# CSS
# ============================================================

st.html(
    """
    <style>

        .life-section {
            margin-top: 2.2rem;
            margin-bottom: .9rem;
        }

        .life-label {
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .14em;
            color: #65724e;
            margin-bottom: .3rem;
        }

        .life-title {
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 750;
            color: #20392d;
            margin: 0;
        }

        .life-copy {
            color: #667067;
            font-size: .96rem;
            line-height: 1.65;
            max-width: 800px;
            margin-top: .55rem;
        }

        .life-card {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.045);
        }

        .life-kicker {
            color: #7a865f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }

        .life-value {
            color: #20392d;
            font-size: 1.8rem;
            line-height: 1;
            font-weight: 750;
            margin-bottom: .4rem;
        }

        .life-text {
            color: #697169;
            font-size: .82rem;
            line-height: 1.5;
        }

        .life-chart {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 20px;
            padding: 1.25rem 1.35rem .5rem 1.35rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.045);
        }

        .life-chart-title {
            color: #20392d;
            font-size: 1.2rem;
            font-weight: 750;
            margin-bottom: .2rem;
        }

        .life-chart-copy {
            color: #727a73;
            font-size: .82rem;
            line-height: 1.5;
        }

        .life-dark {
            background: #20392d;
            color: #f6f3ec;
            border-radius: 20px;
            padding: 1.55rem 1.65rem;
            margin-top: 1.3rem;
        }

        .life-dark-label {
            color: #b8c28f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            margin-bottom: .4rem;
        }

        .life-dark-title {
            font-size: 1.25rem;
            font-weight: 750;
            line-height: 1.3;
            margin-bottom: .45rem;
        }

        .life-dark-copy {
            color: rgba(246,243,236,.76);
            font-size: .86rem;
            line-height: 1.6;
        }

        .life-footer {
            margin: 2.4rem 0 1.2rem 0;
            padding-top: 1rem;
            border-top: 1px solid rgba(32,57,45,.10);
            color: #7a827b;
            font-size: .75rem;
            line-height: 1.5;
        }

    </style>
    """
)


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <section class="life-section" style="margin-top:.5rem;">

        <div class="life-label">
            LIFECYCLE ANALYSIS
        </div>

        <h1 class="life-title">
            How does project activity change with age?
        </h1>

        <div class="life-copy">
            Open-source projects do not behave the same way throughout
            their lifetime. OSSurvive follows project activity across
            different stages of project age to examine changes in
            commits, contributors, and overall activity.
        </div>

    </section>
    """
)


# ============================================================
# OVERVIEW CARDS
# ============================================================

c1, c2, c3, c4 = st.columns(
    4,
    gap="medium"
)

with c1:
    st.html(
        f"""
        <div class="life-card">
            <div class="life-kicker">
                Projects
            </div>

            <div class="life-value">
                {projects}
            </div>

            <div class="life-text">
                Projects represented in the lifecycle dataset.
            </div>
        </div>
        """
    )

with c2:
    st.html(
        f"""
        <div class="life-card">
            <div class="life-kicker">
                Observations
            </div>

            <div class="life-value">
                {total_observations:,}
            </div>

            <div class="life-text">
                Project-month observations used for lifecycle analysis.
            </div>
        </div>
        """
    )

with c3:
    st.html(
        f"""
        <div class="life-card">
            <div class="life-kicker">
                Active observations
            </div>

            <div class="life-value">
                {activity_rate:.1%}
            </div>

            <div class="life-text">
                Share of observations classified as meaningful activity.
            </div>
        </div>
        """
    )

with c4:
    st.html(
        f"""
        <div class="life-card">
            <div class="life-kicker">
                Longest project age
            </div>

            <div class="life-value">
                {project_summary["max_age_months"].max():.0f}
            </div>

            <div class="life-text">
                Maximum observed project age in months.
            </div>
        </div>
        """
    )


# ============================================================
# COHORT ACTIVITY
# ============================================================

st.html(
    """
    <section class="life-section">

        <div class="life-label">
            COHORT ACTIVITY
        </div>

        <h2 class="life-title">
            Activity across the observed timeline
        </h2>

    </section>

    <div class="life-chart">

        <div class="life-chart-title">
            Monthly commits across the study cohort
        </div>

        <div class="life-chart-copy">
            Aggregate commit activity provides a view of how the
            observed cohort behaves across calendar time.
        </div>

    </div>
    """
)


fig, ax = plt.subplots(
    figsize=(12, 5)
)

fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

ax.plot(
    monthly_activity["month"],
    monthly_activity["commits"],
    linewidth=2.2,
    color="#365b48",
)

ax.fill_between(
    monthly_activity["month"],
    monthly_activity["commits"],
    alpha=.10,
    color="#6f8059",
)

ax.set_xlabel(
    "Month",
    fontsize=10
)

ax.set_ylabel(
    "Commits",
    fontsize=10
)

ax.grid(
    axis="y",
    alpha=.17
)

ax.grid(
    axis="x",
    visible=False
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_alpha(.22)
ax.spines["bottom"].set_alpha(.22)

ax.tick_params(
    labelsize=9
)

fig.autofmt_xdate()

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# ============================================================
# ACTIVITY BY PROJECT AGE
# ============================================================

st.html(
    """
    <section class="life-section">

        <div class="life-label">
            PROJECT AGE
        </div>

        <h2 class="life-title">
            Activity profile across lifecycle stages
        </h2>

        <div class="life-copy">
            Instead of treating all observations equally, this view
            groups project-month observations according to project age.
            This helps reveal how activity characteristics differ
            between early and later stages.
        </div>

    </section>
    """
)


left, right = st.columns(
    2,
    gap="medium"
)


# ------------------------------------------------------------
# COMMITS BY AGE
# ------------------------------------------------------------

with left:

    st.html(
        """
        <div class="life-chart">

            <div class="life-chart-title">
                Average commits by project age
            </div>

            <div class="life-chart-copy">
                Mean monthly commits within each lifecycle stage.
            </div>

        </div>
        """
    )

    fig, ax = plt.subplots(
        figsize=(7, 4.5)
    )

    fig.patch.set_alpha(0)
    ax.set_facecolor("#ffffff")

    ax.bar(
        stage_summary["lifecycle_stage"].astype(str),
        stage_summary["commits"],
        color="#6f8059",
        alpha=.88,
    )

    ax.set_xlabel(
        "Project age (months)",
        fontsize=9
    )

    ax.set_ylabel(
        "Average commits",
        fontsize=9
    )

    ax.grid(
        axis="y",
        alpha=.17
    )

    ax.grid(
        axis="x",
        visible=False
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_alpha(.22)
    ax.spines["bottom"].set_alpha(.22)

    ax.tick_params(
        labelsize=8
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


# ------------------------------------------------------------
# ACTIVE RATIO BY AGE
# ------------------------------------------------------------

with right:

    st.html(
        """
        <div class="life-chart">

            <div class="life-chart-title">
                Meaningful activity by project age
            </div>

            <div class="life-chart-copy">
                Share of project-month observations classified as active.
            </div>

        </div>
        """
    )

    fig, ax = plt.subplots(
        figsize=(7, 4.5)
    )

    fig.patch.set_alpha(0)
    ax.set_facecolor("#ffffff")

    ax.plot(
        stage_summary["lifecycle_stage"].astype(str),
        stage_summary["active_ratio"] * 100,
        marker="o",
        linewidth=2.4,
        color="#365b48",
    )

    ax.set_xlabel(
        "Project age (months)",
        fontsize=9
    )

    ax.set_ylabel(
        "Meaningful activity (%)",
        fontsize=9
    )

    ax.set_ylim(
        0,
        105
    )

    ax.grid(
        axis="y",
        alpha=.17
    )

    ax.grid(
        axis="x",
        visible=False
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_alpha(.22)
    ax.spines["bottom"].set_alpha(.22)

    ax.tick_params(
        labelsize=8
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


# ============================================================
# CONTRIBUTOR ACTIVITY
# ============================================================

st.html(
    """
    <section class="life-section">

        <div class="life-label">
            COMMUNITY PARTICIPATION
        </div>

        <h2 class="life-title">
            Contributor activity through the lifecycle
        </h2>

        <div class="life-copy">
            Community participation is another dimension of project
            activity. Contributor counts are examined alongside code
            activity to capture the human side of project maintenance.
        </div>

    </section>

    <div class="life-chart">

        <div class="life-chart-title">
            Average contributors by project age
        </div>

        <div class="life-chart-copy">
            Mean monthly contributor count across lifecycle stages.
        </div>

    </div>
    """
)


fig, ax = plt.subplots(
    figsize=(12, 4.8)
)

fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

ax.plot(
    stage_summary["lifecycle_stage"].astype(str),
    stage_summary["contributors"],
    marker="o",
    linewidth=2.4,
    color="#365b48",
)

ax.set_xlabel(
    "Project age (months)",
    fontsize=10
)

ax.set_ylabel(
    "Average contributors",
    fontsize=10
)

ax.grid(
    axis="y",
    alpha=.17
)

ax.grid(
    axis="x",
    visible=False
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_alpha(.22)
ax.spines["bottom"].set_alpha(.22)

ax.tick_params(
    labelsize=9
)

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# ============================================================
# ACTIVITY CHANGE
# ============================================================

st.html(
    """
    <section class="life-section">

        <div class="life-label">
            MOMENTUM
        </div>

        <h2 class="life-title">
            Short-term activity change
        </h2>

        <div class="life-copy">
            OSSurvive also derives short-term activity-change measures.
            These capture whether recent activity is increasing or
            decreasing relative to the preceding period.
        </div>

    </section>
    """
)


fig, ax = plt.subplots(
    figsize=(12, 4.5)
)

fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

ax.hist(
    activity_change,
    bins=30,
    color="#7a865f",
    alpha=.82,
)

ax.axvline(
    0,
    linewidth=1.4,
    color="#20392d",
    linestyle="--",
)

ax.set_xlabel(
    "Activity change over recent months",
    fontsize=10
)

ax.set_ylabel(
    "Observations",
    fontsize=10
)

ax.grid(
    axis="y",
    alpha=.17
)

ax.grid(
    axis="x",
    visible=False
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_alpha(.22)
ax.spines["bottom"].set_alpha(.22)

ax.tick_params(
    labelsize=9
)

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# ============================================================
# INTERPRETATION
# ============================================================

st.html(
    """
    <div class="life-dark">

        <div class="life-dark-label">
            RESEARCH INTERPRETATION
        </div>

        <div class="life-dark-title">
            Project lifecycle is multidimensional.
        </div>

        <div class="life-dark-copy">
            Code activity, contributor participation, and short-term
            momentum provide different views of project health.
            A project can therefore experience changes in one dimension
            without an identical change in another. OSSurvive uses these
            complementary signals as inputs to its broader survival-risk
            analysis.
        </div>

    </div>
    """
)


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="life-footer">

        <b>Interpretation note:</b>
        Lifecycle patterns describe the observed project-month dataset.
        They should be interpreted as descriptive patterns rather than
        causal evidence about why a project changes over time.

    </div>
    """
)