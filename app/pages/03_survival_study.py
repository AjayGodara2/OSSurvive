import streamlit as st
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OSSurvive — Survival Study",
    page_icon="📈",
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
        "kaplan_meier_survival.csv",
        "survival_threshold_comparison.csv",
    ]

    for directory in possible_dirs:
        if all((directory / f).exists() for f in required):
            return directory

    st.error("Survival Study data files could not be found.")
    st.code(str(Path(__file__).resolve()))
    st.code(str(Path.cwd()))
    st.stop()


DATA_DIR = find_data_dir()


def load_csv(path):
    if not path.exists():
        st.error(f"Required research file not found: {path.name}")
        st.stop()

    return pd.read_csv(path)


survival = load_csv(
    DATA_DIR / "repository_survival_dataset.csv"
)

km = load_csv(
    DATA_DIR / "kaplan_meier_survival.csv"
)

thresholds = load_csv(
    DATA_DIR / "survival_threshold_comparison.csv"
)


# ============================================================
# DATA PREPARATION
# ============================================================

survival["event"] = survival["event"].astype(int)

km = (
    km.sort_values("duration_months")
    .reset_index(drop=True)
)

threshold_summary = (
    thresholds
    .groupby("threshold_months")
    .agg(
        projects=("repo_id", "nunique"),
        events=("event", "sum"),
        event_rate=("event", "mean"),
    )
    .reset_index()
    .sort_values("threshold_months")
)

total_projects = len(
    survival["repo_id"].unique()
)

events = int(
    survival.groupby("repo_id")["event"].max().sum()
)

censored = total_projects - events

median_duration = survival[
    "duration_months"
].median()

maximum_duration = survival[
    "duration_months"
].max()

final_survival = float(
    km.iloc[-1]["survival_probability"]
)

final_month = float(
    km.iloc[-1]["duration_months"]
)


def survival_at(months):

    eligible = km[
        km["duration_months"] <= months
    ]

    if eligible.empty:
        return None

    return float(
        eligible.iloc[-1]["survival_probability"]
    )


survival_12 = survival_at(12)
survival_60 = survival_at(60)
survival_120 = survival_at(120)


# ============================================================
# CSS
# ============================================================

st.html(
    """
    <style>

        .surv-section {
            margin-top: 2.2rem;
            margin-bottom: .9rem;
        }

        .surv-label {
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .14em;
            color: #65724e;
            margin-bottom: .3rem;
        }

        .surv-title {
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 750;
            color: #20392d;
            margin: 0;
        }

        .surv-copy {
            color: #667067;
            font-size: .96rem;
            line-height: 1.65;
            max-width: 780px;
            margin-top: .55rem;
        }

        .surv-card {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.045);
        }

        .surv-kicker {
            color: #7a865f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }

        .surv-value {
            color: #20392d;
            font-size: 1.8rem;
            line-height: 1;
            font-weight: 750;
            margin-bottom: .4rem;
        }

        .surv-text {
            color: #697169;
            font-size: .82rem;
            line-height: 1.5;
        }

        .surv-chart {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 20px;
            padding: 1.25rem 1.35rem .5rem 1.35rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.045);
        }

        .surv-chart-title {
            color: #20392d;
            font-size: 1.2rem;
            font-weight: 750;
            margin-bottom: .2rem;
        }

        .surv-chart-copy {
            color: #727a73;
            font-size: .82rem;
            line-height: 1.5;
            margin-bottom: .5rem;
        }

        .surv-dark {
            background: #20392d;
            color: #f6f3ec;
            border-radius: 20px;
            padding: 1.55rem 1.65rem;
            margin-top: 1.3rem;
        }

        .surv-dark-label {
            color: #b8c28f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            margin-bottom: .4rem;
        }

        .surv-dark-title {
            font-size: 1.25rem;
            font-weight: 750;
            line-height: 1.3;
            margin-bottom: .45rem;
        }

        .surv-dark-copy {
            color: rgba(246,243,236,.76);
            font-size: .86rem;
            line-height: 1.6;
        }

        .surv-footer {
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
    <section class="surv-section" style="margin-top:.5rem;">

        <div class="surv-label">
            SURVIVAL STUDY
        </div>

        <h1 class="surv-title">
            How long do open-source projects remain active?
        </h1>

        <div class="surv-copy">
            OSSurvive treats project activity as a time-to-event process.
            This page examines how the probability of remaining active changes
            as projects age and how the definition of inactivity affects the
            observed survival outcome.
        </div>

    </section>
    """
)


# ============================================================
# COHORT SUMMARY
# ============================================================

c1, c2, c3, c4 = st.columns(
    4,
    gap="medium"
)

with c1:
    st.html(
        f"""
        <div class="surv-card">
            <div class="surv-kicker">
                Survival cohort
            </div>

            <div class="surv-value">
                {total_projects}
            </div>

            <div class="surv-text">
                Projects included in the survival analysis.
            </div>
        </div>
        """
    )

with c2:
    st.html(
        f"""
        <div class="surv-card">
            <div class="surv-kicker">
                Observed events
            </div>

            <div class="surv-value">
                {events}
            </div>

            <div class="surv-text">
                Projects reaching the study's inactivity event definition.
            </div>
        </div>
        """
    )

with c3:
    st.html(
        f"""
        <div class="surv-card">
            <div class="surv-kicker">
                Censored projects
            </div>

            <div class="surv-value">
                {censored}
            </div>

            <div class="surv-text">
                Projects without an observed inactivity event during follow-up.
            </div>
        </div>
        """
    )

with c4:
    st.html(
        f"""
        <div class="surv-card">
            <div class="surv-kicker">
                Median observation
            </div>

            <div class="surv-value">
                {median_duration:.0f}
            </div>

            <div class="surv-text">
                Median observed duration in months.
            </div>
        </div>
        """
    )


# ============================================================
# KAPLAN-MEIER
# ============================================================

st.html(
    """
    <section class="surv-section">

        <div class="surv-label">
            KAPLAN–MEIER ANALYSIS
        </div>

        <h2 class="surv-title">
            Project survival over time
        </h2>

    </section>

    <div class="surv-chart">

        <div class="surv-chart-title">
            Survival probability
        </div>

        <div class="surv-chart-copy">
            Estimated probability that a project remains active
            as project age increases.
        </div>

    </div>
    """
)


fig, ax = plt.subplots(
    figsize=(12, 5.2)
)

fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

ax.step(
    km["duration_months"],
    km["survival_probability"],
    where="post",
    linewidth=2.6,
    color="#365b48",
)

ax.fill_between(
    km["duration_months"],
    km["survival_probability"],
    step="post",
    alpha=.10,
    color="#6f8059",
)

ax.scatter(
    km["duration_months"],
    km["survival_probability"],
    s=18,
    color="#20392d",
    zorder=4,
)

ax.set_xlabel(
    "Months since project start",
    fontsize=10
)

ax.set_ylabel(
    "Probability of remaining active",
    fontsize=10
)

ax.set_xlim(
    left=0
)

ax.set_ylim(
    max(.45, km["survival_probability"].min() - .04),
    1.04
)

ax.grid(
    axis="y",
    alpha=.17,
    linewidth=.8
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
# SURVIVAL MILESTONES
# ============================================================

st.html(
    """
    <section class="surv-section">

        <div class="surv-label">
            SURVIVAL MILESTONES
        </div>

        <h2 class="surv-title">
            Survival probability at key project ages
        </h2>

    </section>
    """
)


m1, m2, m3 = st.columns(
    3,
    gap="medium"
)


with m1:
    value = (
        f"{survival_12:.1%}"
        if survival_12 is not None
        else "—"
    )

    st.html(
        f"""
        <div class="surv-card">
            <div class="surv-kicker">
                12 months
            </div>

            <div class="surv-value">
                {value}
            </div>

            <div class="surv-text">
                Estimated probability of remaining active
                at approximately one year.
            </div>
        </div>
        """
    )


with m2:
    value = (
        f"{survival_60:.1%}"
        if survival_60 is not None
        else "—"
    )

    st.html(
        f"""
        <div class="surv-card">
            <div class="surv-kicker">
                60 months
            </div>

            <div class="surv-value">
                {value}
            </div>

            <div class="surv-text">
                Estimated probability of remaining active
                after approximately five years.
            </div>
        </div>
        """
    )


with m3:
    value = (
        f"{survival_120:.1%}"
        if survival_120 is not None
        else "—"
    )

    st.html(
        f"""
        <div class="surv-card">
            <div class="surv-kicker">
                120 months
            </div>

            <div class="surv-value">
                {value}
            </div>

            <div class="surv-text">
                Estimated probability of remaining active
                after approximately ten years.
            </div>
        </div>
        """
    )


# ============================================================
# OBSERVATION WINDOW
# ============================================================

st.html(
    f"""
    <div class="surv-dark">

        <div class="surv-dark-label">
            OBSERVATION WINDOW
        </div>

        <div class="surv-dark-title">
            The cohort is observed across a wide range of project ages.
        </div>

        <div class="surv-dark-copy">
            The longest observed project duration is approximately
            <b>{maximum_duration:.0f} months</b>. At the final observed
            point of the Kaplan–Meier curve, estimated survival is
            <b>{final_survival:.1%}</b>.
        </div>

    </div>
    """
)


# ============================================================
# THRESHOLD SENSITIVITY
# ============================================================

st.html(
    """
    <section class="surv-section">

        <div class="surv-label">
            THRESHOLD SENSITIVITY
        </div>

        <h2 class="surv-title">
            What counts as inactivity changes the result
        </h2>

        <div class="surv-copy">
            The study tests alternative continuous-inactivity thresholds.
            A longer threshold requires a project to remain inactive for
            longer before an event is recorded.
        </div>

    </section>
    """
)


fig, ax = plt.subplots(
    figsize=(12, 4.5)
)

fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

x = threshold_summary[
    "threshold_months"
].astype(str)

y = (
    threshold_summary["event_rate"] * 100
)

bars = ax.bar(
    x,
    y,
    width=.52,
    color="#7a865f",
    alpha=.88,
)

for bar, value in zip(bars, y):

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,
        value + 1.2,
        f"{value:.1f}%",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="700",
        color="#20392d",
    )

ax.set_xlabel(
    "Continuous inactivity threshold",
    fontsize=10
)

ax.set_ylabel(
    "Observed event rate (%)",
    fontsize=10
)

ax.set_ylim(
    0,
    max(y) + 12
)

ax.grid(
    axis="y",
    alpha=.17,
    linewidth=.8
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
# THRESHOLD CARDS
# ============================================================

threshold_cards = st.columns(
    len(threshold_summary),
    gap="medium"
)

for column, row in zip(
    threshold_cards,
    threshold_summary.itertuples(index=False)
):

    with column:

        st.html(
            f"""
            <div class="surv-card">

                <div class="surv-kicker">
                    {int(row.threshold_months)}-month threshold
                </div>

                <div class="surv-value">
                    {int(row.events)} / {int(row.projects)}
                </div>

                <div class="surv-text">
                    Observed events ·
                    {row.event_rate:.1%} event rate.
                </div>

            </div>
            """
        )


# ============================================================
# RESEARCH INTERPRETATION
# ============================================================

st.html(
    """
    <div class="surv-dark">

        <div class="surv-dark-label">
            RESEARCH INTERPRETATION
        </div>

        <div class="surv-dark-title">
            Survival is a time-dependent outcome, not a simple active/inactive label.
        </div>

        <div class="surv-dark-copy">
            The Kaplan–Meier analysis accounts for the fact that projects
            are observed for different lengths of time. The threshold
            experiment also shows that methodological choices about
            inactivity directly influence the number of observed events.
            Together, these results support treating project survival as
            a lifecycle problem rather than a single static classification.
        </div>

    </div>
    """
)


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="surv-footer">

        <b>Interpretation note:</b>
        Survival estimates describe this OSSurvive pilot cohort.
        An observed event represents the operational inactivity definition
        used in the study and should not be interpreted as proof of permanent
        project failure.

    </div>
    """
)