import streamlit as st
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OSSurvive",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# LOAD THEME
# ============================================================

CSS_PATH = Path(__file__).parent / "styles" / "theme.css"

with open(CSS_PATH, "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True,
    )


# ============================================================
# DEFINE PAGES
# ============================================================

research_overview = st.Page(
    "pages/01_research_overview.py",
    title="Research Overview",
    icon="🔬",
    url_path="",
    default=True,
)

project_observatory = st.Page(
    "pages/02_project_observatory.py",
    title="Project Observatory",
    icon="🔭",
    url_path="project-observatory",
)

survival_study = st.Page(
    "pages/03_survival_study.py",
    title="Survival Study",
    icon="📈",
    url_path="survival-study",
)

lifecycle_analysis = st.Page(
    "pages/04_lifecycle_analysis.py",
    title="Lifecycle Analysis",
    icon="🔄",
    url_path="lifecycle-analysis",
)

risk_experiment = st.Page(
    "pages/05_risk_experiment.py",
    title="Risk Experiment",
    icon="🧪",
    url_path="risk-experiment",
)

methodology = st.Page(
    "pages/06_methodology.py",
    title="Methodology",
    icon="🔬",
    url_path="methodology",
)


# ============================================================
# NAVIGATION
# ============================================================

pg = st.navigation(
    [
        research_overview,
        project_observatory,
        survival_study,
        lifecycle_analysis,
        risk_experiment,
        methodology,
    ],
    position="hidden",
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🧬 OSSurvive")

    st.write(
        "Open-Source Project  \n"
        "Survival Analytics"
    )

    st.divider()

    st.caption("RESEARCH")

    st.page_link(
        research_overview,
        label="01  Research Overview",
        icon="🔬",
    )

    st.page_link(
        project_observatory,
        label="02  Project Observatory",
        icon="🔭",
    )

    st.page_link(
        survival_study,
        label="03  Survival Study",
        icon="📈",
    )

    st.page_link(
        lifecycle_analysis,
        label="04  Lifecycle Analysis",
        icon="🔄",
    )

    st.page_link(
        risk_experiment,
        label="05  Risk Experiment",
        icon="🧪",
    )

    st.page_link(
        methodology,
        label="06  Methodology",
        icon="🔬",
    )


# ============================================================
# RUN SELECTED PAGE
# ============================================================

pg.run()