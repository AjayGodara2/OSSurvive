import streamlit as st
from pathlib import Path
import pandas as pd


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OSSurvive — Methodology",
    page_icon="🔬",
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
        "repository_survival_dataset.csv",
        "repository_monthly_features.csv",
        "repository_modeling_dataset.csv",
        "repository_engineered_features.csv",
        "model_feature_importance.csv",
        "prediction_results.csv",
    ]

    for directory in possible_dirs:
        if all((directory / f).exists() for f in required):
            return directory

    st.error("Methodology data files could not be found.")
    st.stop()


DATA_DIR = find_data_dir()


# ============================================================
# LOAD DATA
# ============================================================

def load_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        st.error(f"Required research file not found: {filename}")
        st.stop()

    return pd.read_csv(path)


survival = load_csv(
    "repository_survival_dataset.csv"
)

monthly = load_csv(
    "repository_monthly_features.csv"
)

modeling = load_csv(
    "repository_modeling_dataset.csv"
)

engineered = load_csv(
    "repository_engineered_features.csv"
)

importance = load_csv(
    "model_feature_importance.csv"
)

predictions = load_csv(
    "prediction_results.csv"
)


# ============================================================
# DATASET METRICS
# ============================================================

project_count = survival["repo_id"].nunique()

survival_rows = len(survival)

monthly_rows = len(monthly)

modeling_rows = len(modeling)

engineered_rows = len(engineered)

prediction_rows = len(predictions)

feature_count = len(importance)


# ============================================================
# CSS
# ============================================================

st.html(
    """
    <style>

        .meth-section {
            margin-top: 2.2rem;
            margin-bottom: .9rem;
        }

        .meth-label {
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .14em;
            color: #65724e;
            margin-bottom: .3rem;
        }

        .meth-title {
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 750;
            color: #20392d;
            margin: 0;
        }

        .meth-copy {
            color: #667067;
            font-size: .96rem;
            line-height: 1.65;
            max-width: 820px;
            margin-top: .55rem;
        }

        .meth-card {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.045);
            height: 100%;
        }

        .meth-kicker {
            color: #7a865f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }

        .meth-value {
            color: #20392d;
            font-size: 1.65rem;
            line-height: 1;
            font-weight: 750;
            margin-bottom: .4rem;
        }

        .meth-text {
            color: #697169;
            font-size: .82rem;
            line-height: 1.5;
        }

        .meth-step {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 18px;
            padding: 1.3rem 1.4rem;
            margin-bottom: .8rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.035);
        }

        .meth-number {
            color: #7a865f;
            font-size: .72rem;
            font-weight: 850;
            letter-spacing: .12em;
            margin-bottom: .35rem;
        }

        .meth-step-title {
            color: #20392d;
            font-size: 1.08rem;
            font-weight: 750;
            margin-bottom: .35rem;
        }

        .meth-step-copy {
            color: #697169;
            font-size: .84rem;
            line-height: 1.6;
        }

        .meth-dark {
            background: #20392d;
            color: #f6f3ec;
            border-radius: 20px;
            padding: 1.55rem 1.65rem;
            margin-top: 1.3rem;
        }

        .meth-dark-label {
            color: #b8c28f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            margin-bottom: .4rem;
        }

        .meth-dark-title {
            font-size: 1.25rem;
            font-weight: 750;
            line-height: 1.3;
            margin-bottom: .45rem;
        }

        .meth-dark-copy {
            color: rgba(246,243,236,.76);
            font-size: .86rem;
            line-height: 1.65;
        }

        .meth-footer {
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
    <section class="meth-section" style="margin-top:.5rem;">

        <div class="meth-label">
            METHODOLOGY
        </div>

        <h1 class="meth-title">
            How was OSSurvive built?
        </h1>

        <div class="meth-copy">
            OSSurvive combines longitudinal repository activity,
            community participation, collaboration signals, survival
            analysis, feature engineering, and predictive modelling
            into a single research workflow.
        </div>

    </section>
    """
)


# ============================================================
# DATASET SNAPSHOT
# ============================================================

st.html(
    """
    <section class="meth-section">

        <div class="meth-label">
            DATASET SNAPSHOT
        </div>

        <h2 class="meth-title">
            The research pipeline in numbers
        </h2>

    </section>
    """
)


c1, c2, c3, c4 = st.columns(
    4,
    gap="medium"
)

with c1:
    st.html(
        f"""
        <div class="meth-card">
            <div class="meth-kicker">
                Projects
            </div>

            <div class="meth-value">
                {project_count}
            </div>

            <div class="meth-text">
                Repository projects included in the study cohort.
            </div>
        </div>
        """
    )

with c2:
    st.html(
        f"""
        <div class="meth-card">
            <div class="meth-kicker">
                Monthly observations
            </div>

            <div class="meth-value">
                {monthly_rows:,}
            </div>

            <div class="meth-text">
                Raw project-month activity observations.
            </div>
        </div>
        """
    )

with c3:
    st.html(
        f"""
        <div class="meth-card">
            <div class="meth-kicker">
                Modeling observations
            </div>

            <div class="meth-value">
                {modeling_rows:,}
            </div>

            <div class="meth-text">
                Observations containing engineered modelling features.
            </div>
        </div>
        """
    )

with c4:
    st.html(
        f"""
        <div class="meth-card">
            <div class="meth-kicker">
                Model signals
            </div>

            <div class="meth-value">
                {feature_count}
            </div>

            <div class="meth-text">
                Features represented in the model importance results.
            </div>
        </div>
        """
    )


# ============================================================
# PIPELINE
# ============================================================

st.html(
    """
    <section class="meth-section">

        <div class="meth-label">
            ANALYTICAL PIPELINE
        </div>

        <h2 class="meth-title">
            From repository activity to survival risk
        </h2>

        <div class="meth-copy">
            The OSSurvive workflow is structured as a sequence of
            transformations. Each stage produces data used by the
            following stage.
        </div>

    </section>
    """
)


pipeline = [
    (
        "01",
        "Repository activity collection",
        "Project activity is represented at monthly resolution, including commits, contributors, pull requests, and issues."
    ),
    (
        "02",
        "Monthly activity construction",
        "Repository-level activity is organized into longitudinal project-month observations while preserving project age and observation timing."
    ),
    (
        "03",
        "Survival definition",
        "Projects are represented as time-to-event observations, with inactivity treated as the event and projects without an observed event treated as censored."
    ),
    (
        "04",
        "Feature engineering",
        "Rolling activity, contributor, collaboration, inactivity, trend, and lifecycle measures are derived from the longitudinal observations."
    ),
    (
        "05",
        "Model development",
        "Engineered project-month features are used to estimate inactivity risk within the prediction horizon."
    ),
    (
        "06",
        "Validation and analysis",
        "Survival analysis, threshold sensitivity, feature importance, and prediction results are examined before presenting the research through the application."
    ),
]


for number, title, copy in pipeline:

    st.html(
        f"""
        <div class="meth-step">

            <div class="meth-number">
                {number}
            </div>

            <div class="meth-step-title">
                {title}
            </div>

            <div class="meth-step-copy">
                {copy}
            </div>

        </div>
        """
    )


# ============================================================
# DATA LAYERS
# ============================================================

st.html(
    """
    <section class="meth-section">

        <div class="meth-label">
            DATA LAYERS
        </div>

        <h2 class="meth-title">
            What each dataset contributes
        </h2>

    </section>
    """
)


d1, d2 = st.columns(
    2,
    gap="medium"
)


with d1:

    st.html(
        f"""
        <div class="meth-card">

            <div class="meth-kicker">
                Survival dataset
            </div>

            <div class="meth-value">
                {survival_rows} rows
            </div>

            <div class="meth-text">
                Contains project-level start, end, event, and duration
                information used for time-to-event analysis.
            </div>

        </div>
        """
    )

    st.html(
        f"""
        <div class="meth-card" style="margin-top:.8rem;">

            <div class="meth-kicker">
                Monthly features
            </div>

            <div class="meth-value">
                {monthly_rows:,} rows
            </div>

            <div class="meth-text">
                Contains monthly commits, contributors, pull requests,
                issues, and related repository activity measures.
            </div>

        </div>
        """
    )


with d2:

    st.html(
        f"""
        <div class="meth-card">

            <div class="meth-kicker">
                Modeling dataset
            </div>

            <div class="meth-value">
                {modeling_rows:,} rows
            </div>

            <div class="meth-text">
                Contains project-month observations together with
                engineered rolling-window, lifecycle, inactivity,
                trend, and collaboration features.
            </div>

        </div>
        """
    )

    st.html(
        f"""
        <div class="meth-card" style="margin-top:.8rem;">

            <div class="meth-kicker">
                Engineered feature layer
            </div>

            <div class="meth-value">
                {engineered_rows:,} rows
            </div>

            <div class="meth-text">
                Provides the engineered feature representation used
                throughout the analytical workflow.
            </div>

        </div>
        """
    )


# ============================================================
# SURVIVAL METHODOLOGY
# ============================================================

st.html(
    """
    <section class="meth-section">

        <div class="meth-label">
            SURVIVAL ANALYSIS
        </div>

        <h2 class="meth-title">
            Why use time-to-event analysis?
        </h2>

        <div class="meth-copy">
            A project may remain active for different lengths of time,
            and some projects may not experience the defined event during
            the available observation period. Survival analysis allows
            these different observation histories to be represented
            explicitly.
        </div>

    </section>
    """
)


st.html(
    """
    <div class="meth-dark">

        <div class="meth-dark-label">
            KAPLAN–MEIER
        </div>

        <div class="meth-dark-title">
            Project survival is estimated as a function of project age.
        </div>

        <div class="meth-dark-copy">
            The Kaplan–Meier curve represents the estimated probability
            that a project remains active as time progresses. Projects
            without an observed event contribute information through
            their available follow-up rather than being treated as
            immediate failures.
        </div>

    </div>
    """
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

st.html(
    """
    <section class="meth-section">

        <div class="meth-label">
            FEATURE ENGINEERING
        </div>

        <h2 class="meth-title">
            Capturing project behaviour over time
        </h2>

        <div class="meth-copy">
            OSSurvive does not rely only on raw monthly counts.
            Rolling and longitudinal features are used to represent
            sustained activity, recent change, inactivity patterns,
            contributor behaviour, collaboration, and project age.
        </div>

    </section>
    """
)


features = [
    (
        "Activity",
        "Commit rate, activity totals, active-month ratio, activity change, and commit volatility."
    ),
    (
        "Community",
        "Contributor averages, new contributor rate, returning contributor rate, and contributor trends."
    ),
    (
        "Collaboration",
        "Pull-request activity, merge rate, issue flow, and collaboration trends."
    ),
    (
        "Inactivity",
        "Zero-commit streaks, inactivity streaks, and longest inactivity gaps."
    ),
    (
        "Lifecycle",
        "Project age and observation position within the project's timeline."
    ),
    (
        "Momentum",
        "Recent trends and changes designed to capture shifts in project activity."
    ),
]


feature_columns = st.columns(
    3,
    gap="medium"
)

for index, (title, copy) in enumerate(features):

    with feature_columns[index % 3]:

        st.html(
            f"""
            <div class="meth-card" style="margin-bottom:.8rem;">

                <div class="meth-kicker">
                    {title}
                </div>

                <div class="meth-text">
                    {copy}
                </div>

            </div>
            """
        )


# ============================================================
# MODEL OUTPUTS
# ============================================================

st.html(
    """
    <section class="meth-section">

        <div class="meth-label">
            MODEL OUTPUTS
        </div>

        <h2 class="meth-title">
            What does the final analytical layer produce?
        </h2>

    </section>
    """
)


o1, o2, o3 = st.columns(
    3,
    gap="medium"
)


with o1:
    st.html(
        """
        <div class="meth-card">

            <div class="meth-kicker">
                Feature importance
            </div>

            <div class="meth-text">
                Model coefficients are examined to understand which
                engineered features have stronger positive or negative
                associations with predicted inactivity risk.
            </div>

        </div>
        """
    )


with o2:
    st.html(
        """
        <div class="meth-card">

            <div class="meth-kicker">
                Risk probability
            </div>

            <div class="meth-text">
                The prediction layer produces an estimated probability
                of inactivity for evaluated project-month observations.
            </div>

        </div>
        """
    )


with o3:
    st.html(
        """
        <div class="meth-card">

            <div class="meth-kicker">
                Survival analysis
            </div>

            <div class="meth-text">
                Time-to-event analysis provides the complementary
                population-level view of project survival over time.
            </div>

        </div>
        """
    )


# ============================================================
# REPRODUCIBILITY
# ============================================================

st.html(
    """
    <section class="meth-section">

        <div class="meth-label">
            RESEARCH DESIGN
        </div>

        <h2 class="meth-title">
            A transparent analytical workflow
        </h2>

        <div class="meth-copy">
            The application separates raw longitudinal observations,
            engineered features, survival outcomes, model outputs,
            and visual interpretation. This makes it possible to inspect
            the analytical layers independently rather than treating
            the final dashboard as a black box.
        </div>

    </section>
    """
)


st.html(
    """
    <div class="meth-dark">

        <div class="meth-dark-label">
            IMPORTANT LIMITATION
        </div>

        <div class="meth-dark-title">
            Predictive association is not the same as causation.
        </div>

        <div class="meth-dark-copy">
            OSSurvive identifies patterns associated with project
            inactivity within the observed dataset. The results should
            therefore be interpreted as evidence from the study cohort
            and fitted model, not as proof that a particular behaviour
            directly causes a project to survive or fail.
        </div>

    </div>
    """
)


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="meth-footer">

        <b>OSSurvive — Open-Source Project Survival Analytics.</b><br>
        Research interface for exploring project survival,
        lifecycle behaviour, and inactivity-risk signals.

    </div>
    """
)