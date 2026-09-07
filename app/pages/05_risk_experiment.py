import streamlit as st
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OSSurvive — Risk Experiment",
    page_icon="🧪",
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
        "model_feature_importance.csv",
        "prediction_results.csv",
        "repository_modeling_dataset.csv",
    ]

    for directory in possible_dirs:
        if all((directory / f).exists() for f in required):
            return directory

    st.error("Risk Experiment data files could not be found.")
    st.stop()


DATA_DIR = find_data_dir()


def load_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        st.error(f"Required research file not found: {filename}")
        st.stop()

    return pd.read_csv(path)


importance = load_csv("model_feature_importance.csv")
predictions = load_csv("prediction_results.csv")
modeling = load_csv("repository_modeling_dataset.csv")


# ============================================================
# DATA PREPARATION
# ============================================================

importance = importance.sort_values(
    "absolute_importance",
    ascending=False
).reset_index(drop=True)

predictions["predicted_probability"] = pd.to_numeric(
    predictions["predicted_probability"],
    errors="coerce"
)

predictions["inactive_within_12m"] = pd.to_numeric(
    predictions["inactive_within_12m"],
    errors="coerce"
)

predictions["predicted_inactive"] = pd.to_numeric(
    predictions["predicted_inactive"],
    errors="coerce"
)

prediction_count = len(predictions)

actual_events = int(
    predictions["inactive_within_12m"].sum()
)

predicted_events = int(
    predictions["predicted_inactive"].sum()
)

mean_probability = (
    predictions["predicted_probability"].mean()
)

top_feature = importance.iloc[0]

risk_features = importance[
    importance["direction"].str.lower().str.contains(
        "risk|increase|positive",
        na=False
    )
]

protective_features = importance[
    importance["direction"].str.lower().str.contains(
        "protect|decrease|negative",
        na=False
    )
]


# ============================================================
# CSS
# ============================================================

st.html(
    """
    <style>

        .risk-section {
            margin-top: 2.2rem;
            margin-bottom: .9rem;
        }

        .risk-label {
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .14em;
            color: #65724e;
            margin-bottom: .3rem;
        }

        .risk-title {
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 750;
            color: #20392d;
            margin: 0;
        }

        .risk-copy {
            color: #667067;
            font-size: .96rem;
            line-height: 1.65;
            max-width: 820px;
            margin-top: .55rem;
        }

        .risk-card {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.045);
        }

        .risk-kicker {
            color: #7a865f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }

        .risk-value {
            color: #20392d;
            font-size: 1.8rem;
            line-height: 1;
            font-weight: 750;
            margin-bottom: .4rem;
        }

        .risk-text {
            color: #697169;
            font-size: .82rem;
            line-height: 1.5;
        }

        .risk-chart {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 20px;
            padding: 1.25rem 1.35rem .5rem 1.35rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.045);
        }

        .risk-chart-title {
            color: #20392d;
            font-size: 1.2rem;
            font-weight: 750;
            margin-bottom: .2rem;
        }

        .risk-chart-copy {
            color: #727a73;
            font-size: .82rem;
            line-height: 1.5;
            margin-bottom: .5rem;
        }

        .risk-dark {
            background: #20392d;
            color: #f6f3ec;
            border-radius: 20px;
            padding: 1.55rem 1.65rem;
            margin-top: 1.3rem;
        }

        .risk-dark-label {
            color: #b8c28f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            margin-bottom: .4rem;
        }

        .risk-dark-title {
            font-size: 1.25rem;
            font-weight: 750;
            line-height: 1.3;
            margin-bottom: .45rem;
        }

        .risk-dark-copy {
            color: rgba(246,243,236,.76);
            font-size: .86rem;
            line-height: 1.6;
        }

        .risk-footer {
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
    <section class="risk-section" style="margin-top:.5rem;">

        <div class="risk-label">
            RISK EXPERIMENT
        </div>

        <h1 class="risk-title">
            Which signals are associated with inactivity risk?
        </h1>

        <div class="risk-copy">
            OSSurvive combines project activity, community participation,
            lifecycle, and collaboration signals to estimate the likelihood
            of inactivity within the prediction horizon. This page exposes
            the model's learned feature signals and prediction behaviour.
        </div>

    </section>
    """
)


# ============================================================
# MODEL SNAPSHOT
# ============================================================

c1, c2, c3, c4 = st.columns(
    4,
    gap="medium"
)

with c1:
    st.html(
        f"""
        <div class="risk-card">
            <div class="risk-kicker">
                Prediction observations
            </div>

            <div class="risk-value">
                {prediction_count:,}
            </div>

            <div class="risk-text">
                Project-month observations evaluated by the prediction model.
            </div>
        </div>
        """
    )

with c2:
    st.html(
        f"""
        <div class="risk-card">
            <div class="risk-kicker">
                Actual events
            </div>

            <div class="risk-value">
                {actual_events}
            </div>

            <div class="risk-text">
                Observed inactivity events in the prediction set.
            </div>
        </div>
        """
    )

with c3:
    st.html(
        f"""
        <div class="risk-card">
            <div class="risk-kicker">
                Predicted high risk
            </div>

            <div class="risk-value">
                {predicted_events}
            </div>

            <div class="risk-text">
                Observations classified as predicted inactive.
            </div>
        </div>
        """
    )

with c4:
    st.html(
        f"""
        <div class="risk-card">
            <div class="risk-kicker">
                Mean predicted probability
            </div>

            <div class="risk-value">
                {mean_probability:.1%}
            </div>

            <div class="risk-text">
                Average predicted probability across the prediction set.
            </div>
        </div>
        """
    )


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

st.html(
    """
    <section class="risk-section">

        <div class="risk-label">
            FEATURE IMPORTANCE
        </div>

        <h2 class="risk-title">
            What does the model pay attention to?
        </h2>

        <div class="risk-copy">
            Feature coefficients indicate the direction and relative
            strength of the learned relationship with the model's
            inactivity outcome. Larger absolute coefficients represent
            stronger model signals within this fitted specification.
        </div>

    </section>

    <div class="risk-chart">

        <div class="risk-chart-title">
            Model feature importance
        </div>

        <div class="risk-chart-copy">
            Top features ranked by absolute coefficient magnitude.
        </div>

    </div>
    """
)


top_n = importance.head(12).copy()

top_n = top_n.sort_values(
    "absolute_importance",
    ascending=True
)

fig, ax = plt.subplots(
    figsize=(12, 6)
)

fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

ax.barh(
    top_n["feature"],
    top_n["coefficient"],
    color="#6f8059",
    alpha=.88,
)

ax.axvline(
    0,
    color="#20392d",
    linewidth=1.2
)

ax.set_xlabel(
    "Model coefficient",
    fontsize=10
)

ax.set_ylabel(
    "",
    fontsize=10
)

ax.grid(
    axis="x",
    alpha=.17
)

ax.grid(
    axis="y",
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
# STRONGEST SIGNALS
# ============================================================

st.html(
    """
    <section class="risk-section">

        <div class="risk-label">
            STRONGEST SIGNALS
        </div>

        <h2 class="risk-title">
            The model highlights different sides of project health
        </h2>

    </section>
    """
)


s1, s2 = st.columns(
    2,
    gap="medium"
)


with s1:

    strongest_risk = importance[
        importance["coefficient"] > 0
    ].sort_values(
        "absolute_importance",
        ascending=False
    ).head(1)

    if not strongest_risk.empty:

        row = strongest_risk.iloc[0]

        st.html(
            f"""
            <div class="risk-dark">

                <div class="risk-dark-label">
                    STRONGEST RISK SIGNAL
                </div>

                <div class="risk-dark-title">
                    {row["feature"]}
                </div>

                <div class="risk-dark-copy">
                    Coefficient:
                    <b>{row["coefficient"]:.3f}</b>.
                    Within this model specification, higher values of this
                    feature are associated with higher predicted inactivity
                    risk.
                </div>

            </div>
            """
        )


with s2:

    strongest_protective = importance[
        importance["coefficient"] < 0
    ].sort_values(
        "absolute_importance",
        ascending=False
    ).head(1)

    if not strongest_protective.empty:

        row = strongest_protective.iloc[0]

        st.html(
            f"""
            <div class="risk-dark">

                <div class="risk-dark-label">
                    STRONGEST PROTECTIVE SIGNAL
                </div>

                <div class="risk-dark-title">
                    {row["feature"]}
                </div>

                <div class="risk-dark-copy">
                    Coefficient:
                    <b>{row["coefficient"]:.3f}</b>.
                    Within this model specification, higher values of this
                    feature are associated with lower predicted inactivity
                    risk.
                </div>

            </div>
            """
        )


# ============================================================
# COEFFICIENT TABLE
# ============================================================

st.html(
    """
    <section class="risk-section">

        <div class="risk-label">
            MODEL SIGNALS
        </div>

        <h2 class="risk-title">
            Feature-level model results
        </h2>

    </section>
    """
)


display_importance = importance[
    [
        "feature",
        "coefficient",
        "absolute_importance",
        "direction",
    ]
].copy()

display_importance["coefficient"] = (
    display_importance["coefficient"]
    .round(4)
)

display_importance["absolute_importance"] = (
    display_importance["absolute_importance"]
    .round(4)
)

display_importance.columns = [
    "Feature",
    "Coefficient",
    "Absolute importance",
    "Direction",
]

st.dataframe(
    display_importance,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# PREDICTION DISTRIBUTION
# ============================================================

st.html(
    """
    <section class="risk-section">

        <div class="risk-label">
            PREDICTION DISTRIBUTION
        </div>

        <h2 class="risk-title">
            How are risk probabilities distributed?
        </h2>

        <div class="risk-copy">
            The prediction distribution shows how the model assigns
            inactivity probabilities across the evaluated observations.
        </div>

    </section>

    <div class="risk-chart">

        <div class="risk-chart-title">
            Predicted inactivity probability
        </div>

        <div class="risk-chart-copy">
            Distribution of model-generated probabilities.
        </div>

    </div>
    """
)


fig, ax = plt.subplots(
    figsize=(12, 4.7)
)

fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

ax.hist(
    predictions["predicted_probability"].dropna(),
    bins=25,
    color="#7a865f",
    alpha=.84,
)

ax.set_xlabel(
    "Predicted probability of inactivity",
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
# ACTUAL VS PREDICTED
# ============================================================

st.html(
    """
    <section class="risk-section">

        <div class="risk-label">
            PREDICTION OUTCOME
        </div>

        <h2 class="risk-title">
            Actual events versus model classifications
        </h2>

    </section>
    """
)


outcome_df = pd.DataFrame(
    {
        "Category": [
            "Actual inactive",
            "Predicted inactive",
        ],
        "Count": [
            actual_events,
            predicted_events,
        ],
    }
)


fig, ax = plt.subplots(
    figsize=(9, 4.5)
)

fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

bars = ax.bar(
    outcome_df["Category"],
    outcome_df["Count"],
    width=.45,
    color="#6f8059",
    alpha=.88,
)

for bar in bars:

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,
        bar.get_height() + max(1, bar.get_height() * .04),
        f"{int(bar.get_height())}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="700",
        color="#20392d",
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
# RESEARCH INTERPRETATION
# ============================================================

st.html(
    """
    <div class="risk-dark">

        <div class="risk-dark-label">
            RESEARCH INTERPRETATION
        </div>

        <div class="risk-dark-title">
            Risk is driven by a combination of activity and lifecycle signals.
        </div>

        <div class="risk-dark-copy">
            The model does not rely on a single measure of project health.
            Its learned coefficients combine inactivity patterns, sustained
            activity, project age, collaboration, and other engineered
            features. These coefficients describe associations learned by
            the fitted model; they should not be interpreted as causal
            effects.
        </div>

    </div>
    """
)


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="risk-footer">

        <b>Interpretation note:</b>
        Model coefficients and predictions are specific to the OSSurvive
        dataset, feature engineering process, and fitted model. They
        represent predictive signals rather than proof that changing
        a feature will directly change project survival.

    </div>
    """
)