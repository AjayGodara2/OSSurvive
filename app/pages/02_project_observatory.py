import streamlit as st
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OSSurvive — Project Observatory",
    page_icon="🔭",
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
    ]

    for directory in possible_dirs:
        if all((directory / file).exists() for file in required):
            return directory

    st.error("Project Observatory data files could not be found.")
    st.write("Current page:")
    st.code(str(Path(__file__).resolve()))
    st.write("Current working directory:")
    st.code(str(Path.cwd()))
    st.stop()


DATA_DIR = find_data_dir()

SURVIVAL_PATH = DATA_DIR / "repository_survival_dataset.csv"
MONTHLY_PATH = DATA_DIR / "repository_monthly_features.csv"


def load_csv(path):
    if not path.exists():
        st.error(f"Required research file not found: {path.name}")
        st.stop()

    return pd.read_csv(path)


survival = load_csv(SURVIVAL_PATH)
monthly = load_csv(MONTHLY_PATH)


# ============================================================
# DATA PREPARATION
# ============================================================

survival["event"] = survival["event"].astype(int)
monthly["month"] = pd.to_datetime(monthly["month"])

projects = (
    survival[["repo_id", "full_name", "language", "start_month",
              "end_month", "event_month", "duration_months", "event"]]
    .drop_duplicates()
    .sort_values("full_name")
    .reset_index(drop=True)
)

project_names = projects["full_name"].tolist()


# ============================================================
# CUSTOM CSS
# ============================================================

st.html(
    """
    <style>

        .obs-section {
            margin-top: 2.2rem;
            margin-bottom: .9rem;
        }

        .obs-label {
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .14em;
            color: #65724e;
            margin-bottom: .3rem;
        }

        .obs-title {
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 750;
            color: #20392d;
            margin: 0;
        }

        .obs-copy {
            color: #667067;
            font-size: .96rem;
            line-height: 1.65;
            max-width: 760px;
            margin-top: .55rem;
        }

        .obs-card {
            background: #ffffff;
            border: 1px solid rgba(32,57,45,.10);
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 7px 24px rgba(32,57,45,.045);
        }

        .obs-dark {
            background: #20392d;
            color: #f6f3ec;
            border-radius: 20px;
            padding: 1.55rem 1.65rem;
        }

        .obs-kicker {
            color: #7a865f;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }

        .obs-dark .obs-kicker {
            color: #b8c28f;
        }

        .obs-value {
            color: #20392d;
            font-size: 1.8rem;
            line-height: 1;
            font-weight: 750;
            margin-bottom: .35rem;
        }

        .obs-dark-value {
            color: #f6f3ec;
            font-size: 1.45rem;
            font-weight: 750;
            line-height: 1.15;
            margin-bottom: .55rem;
        }

        .obs-text {
            color: #697169;
            font-size: .82rem;
            line-height: 1.5;
        }

        .obs-dark-text {
            color: rgba(246,243,236,.74);
            font-size: .87rem;
            line-height: 1.6;
        }

        .obs-profile-title {
            color: #20392d;
            font-size: 1.35rem;
            font-weight: 750;
            margin-bottom: .2rem;
        }

        .obs-profile-subtitle {
            color: #727a73;
            font-size: .82rem;
            margin-bottom: 1rem;
        }

        .obs-status {
            display: inline-block;
            padding: .38rem .72rem;
            border-radius: 999px;
            font-size: .72rem;
            font-weight: 750;
            background: #edf0df;
            color: #526044;
        }

        .obs-status-event {
            background: #eee6dc;
            color: #745e48;
        }

        .obs-footer {
            margin: 2.5rem 0 1.2rem 0;
            padding-top: 1rem;
            border-top: 1px solid rgba(32,57,45,.10);
            color: #7a827b;
            font-size: .75rem;
        }

    </style>
    """
)


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <section class="obs-section" style="margin-top:.5rem;">
        <div class="obs-label">PROJECT OBSERVATORY</div>

        <h1 class="obs-title">
            Explore the projects behind the study
        </h1>

        <div class="obs-copy">
            Move from the cohort-level findings to individual repositories.
            Inspect project age, activity, collaboration and observed survival
            outcomes across the OSSurvive study population.
        </div>
    </section>
    """
)


# ============================================================
# COHORT SNAPSHOT
# ============================================================

total_projects = len(projects)
event_projects = int(projects["event"].sum())
surviving_projects = total_projects - event_projects
median_duration = projects["duration_months"].median()

c1, c2, c3, c4 = st.columns(4, gap="medium")

with c1:
    st.html(
        f"""
        <div class="obs-card">
            <div class="obs-kicker">Study cohort</div>
            <div class="obs-value">{total_projects}</div>
            <div class="obs-text">Repositories included in the survival cohort.</div>
        </div>
        """
    )

with c2:
    st.html(
        f"""
        <div class="obs-card">
            <div class="obs-kicker">Observed survivors</div>
            <div class="obs-value">{surviving_projects}</div>
            <div class="obs-text">Projects without an observed inactivity event.</div>
        </div>
        """
    )

with c3:
    st.html(
        f"""
        <div class="obs-card">
            <div class="obs-kicker">Observed events</div>
            <div class="obs-value">{event_projects}</div>
            <div class="obs-text">Projects reaching the study's inactivity event definition.</div>
        </div>
        """
    )

with c4:
    st.html(
        f"""
        <div class="obs-card">
            <div class="obs-kicker">Median duration</div>
            <div class="obs-value">{median_duration:.0f}</div>
            <div class="obs-text">Median observed project duration in months.</div>
        </div>
        """
    )


# ============================================================
# PROJECT SELECTOR
# ============================================================

st.html(
    """
    <section class="obs-section">
        <div class="obs-label">PROJECT EXPLORER</div>
        <h2 class="obs-title">Select a repository</h2>
    </section>
    """
)

selected_project = st.selectbox(
    "Repository",
    project_names,
    label_visibility="collapsed",
)

selected = projects[
    projects["full_name"] == selected_project
].iloc[0]

repo_id = selected["repo_id"]

project_monthly = (
    monthly[monthly["repo_id"] == repo_id]
    .sort_values("month")
    .copy()
)


# ============================================================
# PROJECT PROFILE
# ============================================================

status_text = (
    "Observed inactivity event"
    if selected["event"] == 1
    else "No observed inactivity event"
)

status_class = (
    "obs-status-event"
    if selected["event"] == 1
    else "obs-status"
)

st.html(
    f"""
    <div class="obs-card">

        <div class="obs-profile-title">
            {selected["full_name"]}
        </div>

        <div class="obs-profile-subtitle">
            Repository ID · {selected["repo_id"]}
        </div>

        <span class="{status_class}">
            {status_text}
        </span>

    </div>
    """
)


p1, p2, p3, p4 = st.columns(4, gap="medium")

with p1:
    st.html(
        f"""
        <div class="obs-card">
            <div class="obs-kicker">Language</div>
            <div class="obs-value" style="font-size:1.35rem;">
                {selected["language"]}
            </div>
            <div class="obs-text">Primary recorded repository language.</div>
        </div>
        """
    )

with p2:
    st.html(
        f"""
        <div class="obs-card">
            <div class="obs-kicker">Observed duration</div>
            <div class="obs-value">
                {selected["duration_months"]:.0f}
            </div>
            <div class="obs-text">Months represented in the survival record.</div>
        </div>
        """
    )

with p3:
    st.html(
        f"""
        <div class="obs-card">
            <div class="obs-kicker">Start month</div>
            <div class="obs-value" style="font-size:1.2rem;">
                {selected["start_month"]}
            </div>
            <div class="obs-text">Beginning of the observed project history.</div>
        </div>
        """
    )

with p4:
    end_value = selected["event_month"]

    if pd.isna(end_value):
        end_value = selected["end_month"]

    st.html(
        f"""
        <div class="obs-card">
            <div class="obs-kicker">End / event month</div>
            <div class="obs-value" style="font-size:1.2rem;">
                {end_value}
            </div>
            <div class="obs-text">End of observation or recorded event.</div>
        </div>
        """
    )


# ============================================================
# ACTIVITY PROFILE
# ============================================================

st.html(
    """
    <section class="obs-section">
        <div class="obs-label">ACTIVITY PROFILE</div>
        <h2 class="obs-title">How activity changed over time</h2>
    </section>
    """
)


if not project_monthly.empty:

    activity_cols = [
        c for c in [
            "commits",
            "contributors",
            "pr_opened",
            "pr_closed",
            "pr_merged",
            "issues_opened",
            "issues_closed",
        ]
        if c in project_monthly.columns
    ]

    # --------------------------------------------------------
    # Commit activity
    # --------------------------------------------------------

    st.html(
        """
        <div class="obs-card">
            <div class="obs-profile-title">
                Commit activity
            </div>
            <div class="obs-profile-subtitle">
                Monthly development activity recorded for the selected project.
            </div>
        </div>
        """
    )

    fig, ax = plt.subplots(figsize=(12, 4.4))
    fig.patch.set_alpha(0)
    ax.set_facecolor("#ffffff")

    ax.plot(
        project_monthly["month"],
        project_monthly["commits"],
        linewidth=2.2,
        color="#365b48",
    )

    ax.fill_between(
        project_monthly["month"],
        project_monthly["commits"],
        alpha=.10,
        color="#6f8059",
    )

    ax.set_xlabel("Month", fontsize=9)
    ax.set_ylabel("Commits", fontsize=9)

    ax.grid(axis="y", alpha=.16)
    ax.grid(axis="x", visible=False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_alpha(.20)
    ax.spines["bottom"].set_alpha(.20)

    ax.tick_params(labelsize=8)

    st.pyplot(fig, use_container_width=True)

    plt.close(fig)


    # --------------------------------------------------------
    # Contributors + collaboration
    # --------------------------------------------------------

    a1, a2 = st.columns(2, gap="medium")

    with a1:

        st.html(
            """
            <div class="obs-card">
                <div class="obs-profile-title">
                    Contributor activity
                </div>
                <div class="obs-profile-subtitle">
                    Number of contributors observed each month.
                </div>
            </div>
            """
        )

        if "contributors" in project_monthly.columns:

            fig, ax = plt.subplots(figsize=(6, 3.7))
            fig.patch.set_alpha(0)
            ax.set_facecolor("#ffffff")

            ax.plot(
                project_monthly["month"],
                project_monthly["contributors"],
                linewidth=2,
                color="#788760",
            )

            ax.set_ylabel("Contributors", fontsize=9)
            ax.grid(axis="y", alpha=.16)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            ax.tick_params(labelsize=8)

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    with a2:

        st.html(
            """
            <div class="obs-card">
                <div class="obs-profile-title">
                    Collaboration activity
                </div>
                <div class="obs-profile-subtitle">
                    Pull requests and issue activity over the project history.
                </div>
            </div>
            """
        )

        collaboration = project_monthly.copy()

        available = [
            c for c in [
                "pr_opened",
                "pr_closed",
                "issues_opened",
                "issues_closed",
            ]
            if c in collaboration.columns
        ]

        if available:

            collaboration["total"] = collaboration[available].sum(axis=1)

            fig, ax = plt.subplots(figsize=(6, 3.7))
            fig.patch.set_alpha(0)
            ax.set_facecolor("#ffffff")

            ax.plot(
                collaboration["month"],
                collaboration["total"],
                linewidth=2,
                color="#365b48",
            )

            ax.set_ylabel("Collaboration events", fontsize=9)
            ax.grid(axis="y", alpha=.16)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            ax.tick_params(labelsize=8)

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)


else:

    st.info("No monthly activity records were found for this repository.")


# ============================================================
# RESEARCH INTERPRETATION
# ============================================================

st.html(
    f"""
    <div class="obs-dark" style="margin-top:1.5rem;">

        <div class="obs-kicker">
            PROJECT-LEVEL INTERPRETATION
        </div>

        <div class="obs-dark-value">
            Individual project histories reveal the activity patterns
            behind the cohort-level survival curve.
        </div>

        <div class="obs-dark-text">
            The selected repository can be examined through its development
            activity, contributor participation and collaboration history.
            These project-level signals provide the observational foundation
            for the survival and risk analyses used elsewhere in OSSurvive.
        </div>

    </div>
    """
)


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="obs-footer">
        Project-level observations are descriptive. An observed inactivity
        event represents the operational definition used by the OSSurvive study
        and should not be interpreted as proof of project failure.
    </div>
    """
)