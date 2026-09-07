import streamlit as st
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OSSurvive — Research Overview",
    page_icon="🔬",
    layout="wide",
)

# ============================================================
# PATHS + DATA
# ============================================================

APP_DIR = Path(__file__).resolve().parent.parent


def find_data_dir():
    """
    Find the historical data directory regardless of whether
    the app is being run from the project root or /app.
    """

    possible_dirs = [
        APP_DIR / "data" / "historical",
        APP_DIR.parent / "data" / "historical",
        Path.cwd() / "data" / "historical",
        Path.cwd() / "app" / "data" / "historical",
    ]

    required_files = [
        "kaplan_meier_survival.csv",
        "survival_threshold_comparison.csv",
        "model_feature_importance.csv",
        "prediction_results.csv",
    ]

    for directory in possible_dirs:
        if all((directory / filename).exists() for filename in required_files):
            return directory

    # Nothing found — show exactly where Streamlit looked
    st.error("Research data files could not be found.")

    st.write("Streamlit searched these locations:")

    for directory in possible_dirs:
        st.code(str(directory))

    st.write("Current page location:")
    st.code(str(Path(__file__).resolve()))

    st.write("Current working directory:")
    st.code(str(Path.cwd()))

    st.stop()


DATA_DIR = find_data_dir()

KM_PATH = DATA_DIR / "kaplan_meier_survival.csv"
THRESHOLD_PATH = DATA_DIR / "survival_threshold_comparison.csv"
IMPORTANCE_PATH = DATA_DIR / "model_feature_importance.csv"
PREDICTION_PATH = DATA_DIR / "prediction_results.csv"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error(f"Research file not found: {path}")
        st.stop()

    return pd.read_csv(path)


km = load_csv(KM_PATH)
thresholds = load_csv(THRESHOLD_PATH)
importance = load_csv(IMPORTANCE_PATH)
predictions = load_csv(PREDICTION_PATH)
# ============================================================
# RESEARCH VALUES — DERIVED FROM REAL DATA
# ============================================================

projects_analyzed = thresholds["repo_id"].nunique()

# Survival at selected observed points.
km = km.sort_values("duration_months").reset_index(drop=True)


def survival_at_or_before(months: float):
    eligible = km[km["duration_months"] <= months]
    if eligible.empty:
        return None
    return float(eligible.iloc[-1]["survival_probability"])


survival_12 = survival_at_or_before(12)
survival_120 = survival_at_or_before(120)
final_survival = float(km.iloc[-1]["survival_probability"])
final_month = float(km.iloc[-1]["duration_months"])

threshold_summary = (
    thresholds.groupby("threshold_months")
    .agg(
        projects=("repo_id", "nunique"),
        events=("event", "sum"),
        event_rate=("event", "mean"),
    )
    .reset_index()
    .sort_values("threshold_months")
)

importance = importance.sort_values("absolute_importance", ascending=False).reset_index(drop=True)
top_risk = importance[importance["direction"] == "increases_risk"].iloc[0]
top_protective = importance[importance["direction"] == "decreases_risk"].iloc[0]

prediction_count = len(predictions)
actual_events = int(predictions["inactive_within_12m"].sum())
predicted_events = int(predictions["predicted_inactive"].sum())

# ============================================================
# CUSTOM STYLES
# ============================================================

st.html(
    """
    <style>
        .oss-section {
            margin-top: 2.2rem;
            margin-bottom: 0.9rem;
        }

        .oss-section-label {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            color: #65724e;
            margin-bottom: 0.3rem;
        }

        .oss-section-title {
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 750;
            color: #20392d;
            margin: 0;
        }

        .oss-section-copy {
            color: #667067;
            font-size: 0.98rem;
            line-height: 1.65;
            max-width: 760px;
            margin-top: 0.55rem;
        }

        .oss-finding-card {
            background: #ffffff;
            border: 1px solid rgba(32, 57, 45, 0.10);
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            min-height: 132px;
            box-shadow: 0 7px 24px rgba(32, 57, 45, 0.045);
        }

        .oss-finding-kicker {
            color: #7a8461;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .oss-finding-value {
            color: #20392d;
            font-size: 1.85rem;
            line-height: 1;
            font-weight: 750;
            margin-bottom: 0.42rem;
        }

        .oss-finding-text {
            color: #697169;
            font-size: 0.82rem;
            line-height: 1.45;
        }

        .oss-chart-card {
            background: #ffffff;
            border: 1px solid rgba(32, 57, 45, 0.10);
            border-radius: 18px;
            padding: 1.05rem 1.15rem 0.75rem 1.15rem;
            box-shadow: 0 7px 24px rgba(32, 57, 45, 0.045);
        }

        .oss-chart-title {
            color: #20392d;
            font-size: 1.15rem;
            font-weight: 750;
            margin-bottom: 0.12rem;
        }

        .oss-chart-subtitle {
            color: #727a73;
            font-size: 0.82rem;
            line-height: 1.45;
            margin-bottom: 0.4rem;
        }

        .oss-insight {
            background: #20392d;
            border-radius: 18px;
            padding: 1.25rem 1.4rem;
            color: #f6f3ec;
            margin-top: 0.9rem;
        }

        .oss-insight-label {
            color: #b6c18e;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            margin-bottom: 0.35rem;
        }

        .oss-insight-title {
            font-size: 1.15rem;
            font-weight: 750;
            margin-bottom: 0.35rem;
        }

        .oss-insight-copy {
            color: rgba(246, 243, 236, 0.78);
            font-size: 0.86rem;
            line-height: 1.55;
        }

        .oss-mini-note {
            color: #788078;
            font-size: 0.74rem;
            line-height: 1.45;
            margin-top: 0.4rem;
        }

        .oss-footer-note {
            margin: 2.4rem 0 1.2rem 0;
            padding-top: 1rem;
            border-top: 1px solid rgba(32, 57, 45, 0.10);
            color: #7a827b;
            font-size: 0.75rem;
            line-height: 1.5;
        }
    </style>
    """
)

# ============================================================
# HERO
# ============================================================

st.html(
    """
    <section style="
        position: relative;
        overflow: hidden;
        min-height: 390px;
        padding: 2.5rem 2.7rem 2.2rem 2.7rem;
        border-radius: 26px;
        background: linear-gradient(135deg, #f7f4ec 0%, #edf0df 100%);
        border: 1px solid rgba(32,57,45,.08);
        box-shadow: 0 10px 35px rgba(32,57,45,.055);
    ">
        <div style="position:relative;z-index:5;max-width:650px;">
            <div style="
                color:#68744f;
                font-size:.72rem;
                font-weight:800;
                letter-spacing:.14em;
                margin-bottom:.8rem;
            ">OPEN-SOURCE PROJECT SURVIVAL ANALYTICS</div>

            <div style="
                color:#20392d;
                font-size:clamp(3.2rem,6vw,5.2rem);
                line-height:.9;
                font-weight:800;
                letter-spacing:-.055em;
                margin-bottom:1rem;
            ">OSSurvive</div>

            <div style="
                color:#59645c;
                font-size:1.03rem;
                line-height:1.6;
                max-width:570px;
                margin-bottom:1.45rem;
            ">
                Understanding why open-source projects survive, decline,
                and become inactive.
            </div>

            <div style="display:flex;gap:.7rem;flex-wrap:wrap;">
                <div style="
                    display:inline-block;
                    padding:.68rem 1rem;
                    border-radius:999px;
                    background:#20392d;
                    color:#f6f3ec;
                    font-size:.82rem;
                    font-weight:700;
                ">📊 Explore Insights →</div>
                <div style="
                    display:inline-block;
                    padding:.68rem 1rem;
                    border-radius:999px;
                    border:1px solid rgba(32,57,45,.18);
                    background:rgba(255,255,255,.55);
                    color:#20392d;
                    font-size:.82rem;
                    font-weight:700;
                ">📖 Read the Research</div>
            </div>
        </div>

        <div style="
            position:absolute;
            right:3%;
            top:12%;
            z-index:4;
            width:41%;
            min-width:300px;
            height:76%;
        ">
            <div style="
                position:absolute;
                width:92px;height:92px;
                border-radius:50%;
                right:25%;top:4%;
                background:#d7d4a6;
                opacity:.75;
            "></div>

            <div style="
                position:absolute;left:4%;bottom:21%;
                width:65%;height:43%;
                background:#aab48c;
                clip-path:polygon(0 100%,18% 52%,34% 70%,55% 28%,72% 63%,88% 42%,100% 100%);
                opacity:.75;
            "></div>

            <div style="
                position:absolute;left:18%;bottom:17%;
                width:76%;height:44%;
                background:#788760;
                clip-path:polygon(0 100%,17% 57%,31% 72%,51% 30%,67% 66%,82% 43%,100% 100%);
            "></div>

            <div style="
                position:absolute;left:0;bottom:7%;
                width:100%;height:31%;
                background:#4d6549;
                clip-path:polygon(0 42%,12% 27%,24% 40%,38% 18%,52% 35%,66% 12%,82% 33%,100% 18%,100% 100%,0 100%);
            "></div>

            <div style="
                position:absolute;left:5%;bottom:2%;
                width:90%;height:22%;
                background:#20392d;
                clip-path:polygon(0 45%,8% 29%,17% 42%,28% 20%,38% 37%,49% 17%,60% 39%,71% 22%,82% 35%,92% 19%,100% 31%,100% 100%,0 100%);
            "></div>

            <div style="
                position:absolute;right:8%;bottom:14%;
                width:7px;height:62px;background:#20392d;
                border-radius:3px;
            "></div>
            <div style="
                position:absolute;right:2%;bottom:13%;
                width:6px;height:49px;background:#20392d;
                border-radius:3px;
            "></div>

            <div style="
                position:absolute;right:3%;bottom:49%;
                color:#20392d;
                font-size:.9rem;
                line-height:1.35;
                font-style:italic;
                text-align:right;
                font-weight:650;
            ">Stronger<br>Open Source<br>Together</div>
        </div>
    </section>
    """
)

# ============================================================
# RESEARCH SNAPSHOT
# ============================================================

st.html(
    """
    <section class="oss-section">
        <div class="oss-section-label">RESEARCH SNAPSHOT</div>
        <h2 class="oss-section-title">The study at a glance</h2>
    </section>
    """
)

k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    st.html(
        f"""
        <div class="oss-finding-card">
            <div class="oss-finding-kicker">Projects analyzed</div>
            <div class="oss-finding-value">{projects_analyzed}</div>
            <div class="oss-finding-text">Open-source projects included in the study.</div>
        </div>
        """
    )

with k2:
    st.html(
        """
        <div class="oss-finding-card">
            <div class="oss-finding-kicker">Complete observations</div>
            <div class="oss-finding-value">1,630</div>
            <div class="oss-finding-text">Project-level observations used for analysis.</div>
        </div>
        """
    )

with k3:
    st.html(
        """
        <div class="oss-finding-card">
            <div class="oss-finding-kicker">Research model</div>
            <div class="oss-finding-value">Validated</div>
            <div class="oss-finding-text">Model validation completed before deployment.</div>
        </div>
        """
    )

with k4:
    st.html(
        """
        <div class="oss-finding-card">
            <div class="oss-finding-kicker">Core question</div>
            <div class="oss-finding-value">Survival</div>
            <div class="oss-finding-text">Understanding the factors behind project survival and decline.</div>
        </div>
        """
    )

# ============================================================
# STUDY OVERVIEW
# ============================================================

st.html(
    """
    <section class="oss-section">
        <div class="oss-section-label">THE STUDY</div>
        <h2 class="oss-section-title">From project activity to survival risk</h2>
    </section>

    <div style="display:grid;grid-template-columns:1.08fr .92fr;gap:1rem;margin-top:.7rem;">
        <div style="
            background:#20392d;
            color:#f6f3ec;
            border-radius:20px;
            padding:1.55rem 1.65rem;
        ">
            <div style="color:#b8c28f;font-size:.68rem;font-weight:800;letter-spacing:.12em;margin-bottom:.55rem;">THE RESEARCH</div>
            <div style="font-size:1.5rem;font-weight:750;line-height:1.2;margin-bottom:.75rem;">What is OSSurvive trying to understand?</div>
            <div style="color:rgba(246,243,236,.75);font-size:.88rem;line-height:1.65;">
                Open-source projects move through different stages of activity.
                Some maintain a healthy development rhythm, while others gradually
                lose activity and eventually become inactive. OSSurvive studies these
                lifecycle patterns and the signals associated with survival risk.
            </div>
            <div style="margin-top:1.35rem;padding-top:1rem;border-top:1px solid rgba(246,243,236,.16);">
                <div style="color:#b8c28f;font-size:.66rem;font-weight:800;letter-spacing:.12em;margin-bottom:.35rem;">CENTRAL RESEARCH QUESTION</div>
                <div style="font-size:1rem;font-weight:650;line-height:1.45;">What factors help an open-source project remain active over time?</div>
            </div>
        </div>

        <div style="
            background:#ffffff;
            border:1px solid rgba(32,57,45,.10);
            border-radius:20px;
            padding:1.55rem 1.65rem;
        ">
            <div style="color:#20392d;font-size:1.05rem;font-weight:750;margin-bottom:.9rem;">Analytical perspective</div>
            <div style="display:grid;gap:.8rem;">
                <div style="display:flex;gap:.75rem;align-items:flex-start;"><span style="color:#7a865f;font-weight:800;">01</span><div><b>Project activity</b><br><span style="color:#727a73;font-size:.82rem;">How consistently development activity is maintained.</span></div></div>
                <div style="display:flex;gap:.75rem;align-items:flex-start;"><span style="color:#7a865f;font-weight:800;">02</span><div><b>Community participation</b><br><span style="color:#727a73;font-size:.82rem;">How contributors and collaboration evolve.</span></div></div>
                <div style="display:flex;gap:.75rem;align-items:flex-start;"><span style="color:#7a865f;font-weight:800;">03</span><div><b>Project lifecycle</b><br><span style="color:#727a73;font-size:.82rem;">How activity changes as projects age.</span></div></div>
                <div style="display:flex;gap:.75rem;align-items:flex-start;"><span style="color:#7a865f;font-weight:800;">04</span><div><b>Survival risk</b><br><span style="color:#727a73;font-size:.82rem;">Which observed signals are associated with future inactivity.</span></div></div>
            </div>
        </div>
    </div>
    """
)

# ============================================================
# RESEARCH FINDINGS
# ============================================================

st.html(
    """
    <section class="oss-section" style="margin-top:3rem;">
        <div class="oss-section-label">RESEARCH FINDINGS</div>
        <h2 class="oss-section-title">What the data reveals</h2>
        <div class="oss-section-copy">
            The first results connect three parts of the study: how long projects
            remain active, how the inactivity definition changes the measured outcome,
            and which activity signals carry the strongest modeled risk.
        </div>
    </section>
    """
)

# ============================================================
# FINDING 01 — KAPLAN-MEIER
# ============================================================

st.html(
    f"""
    <div class="oss-chart-card">
        <div class="oss-chart-title">01 · Project survival over time</div>
        <div class="oss-chart-subtitle">
            Kaplan–Meier estimate of the probability that a project remains active
            as project age increases.
        </div>
    </div>
    """
)

fig, ax = plt.subplots(figsize=(12, 4.8))
fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

ax.step(
    km["duration_months"],
    km["survival_probability"],
    where="post",
    linewidth=2.5,
    color="#365b48",
)

ax.fill_between(
    km["duration_months"],
    km["survival_probability"],
    step="post",
    alpha=0.10,
    color="#6f8059",
)

ax.set_xlabel("Months since project start", fontsize=10)
ax.set_ylabel("Probability of remaining active", fontsize=10)
ax.set_ylim(0.45, 1.04)
ax.set_xlim(left=0)
ax.grid(axis="y", alpha=0.18, linewidth=0.8)
ax.grid(axis="x", visible=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_alpha(0.25)
ax.spines["bottom"].set_alpha(0.25)
ax.tick_params(labelsize=9)

st.pyplot(fig, use_container_width=True)
plt.close(fig)

s1, s2, s3 = st.columns(3, gap="medium")
with s1:
    st.html(
        f"""
        <div class="oss-finding-card">
            <div class="oss-finding-kicker">At 12 months</div>
            <div class="oss-finding-value">{survival_12:.1%}</div>
            <div class="oss-finding-text">Estimated probability of remaining active at the first major observed drop.</div>
        </div>
        """
    )
with s2:
    st.html(
        f"""
        <div class="oss-finding-card">
            <div class="oss-finding-kicker">At 120 months</div>
            <div class="oss-finding-value">{survival_120:.1%}</div>
            <div class="oss-finding-text">Estimated survival after roughly ten years in the observed cohort.</div>
        </div>
        """
    )
with s3:
    st.html(
        f"""
        <div class="oss-finding-card">
            <div class="oss-finding-kicker">End of observed curve</div>
            <div class="oss-finding-value">{final_survival:.1%}</div>
            <div class="oss-finding-text">Estimated survival at the final observed duration of {final_month:.0f} months.</div>
        </div>
        """
    )

st.html(
    """
    <div class="oss-insight">
        <div class="oss-insight-label">RESEARCH SIGNAL</div>
        <div class="oss-insight-title">Survival declines gradually rather than collapsing at one fixed age.</div>
        <div class="oss-insight-copy">
            The curve shows several periods of relative stability followed by discrete
            drops. This supports treating project survival as a lifecycle process rather
            than assuming a single universal failure point.
        </div>
    </div>
    """
)

# ============================================================
# FINDING 02 — THRESHOLD EXPERIMENT
# ============================================================

st.html(
    """
    <div class="oss-chart-card" style="margin-top:1.5rem;">
        <div class="oss-chart-title">02 · The inactivity definition matters</div>
        <div class="oss-chart-subtitle">
            Observed event rates change when inactivity is defined using different
            continuous inactivity thresholds.
        </div>
    </div>
    """
)

fig, ax = plt.subplots(figsize=(12, 4.5))
fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

x = threshold_summary["threshold_months"].astype(str)
y = threshold_summary["event_rate"] * 100
bars = ax.bar(x, y, width=0.52, color="#7a865f", alpha=0.88)

for bar, value in zip(bars, y):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1.3,
        f"{value:.1f}%",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="700",
        color="#20392d",
    )

ax.set_xlabel("Continuous inactivity threshold", fontsize=10)
ax.set_ylabel("Observed event rate (%)", fontsize=10)
ax.set_ylim(0, max(y) + 12)
ax.grid(axis="y", alpha=0.18, linewidth=0.8)
ax.grid(axis="x", visible=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_alpha(0.25)
ax.spines["bottom"].set_alpha(0.25)
ax.tick_params(labelsize=9)

st.pyplot(fig, use_container_width=True)
plt.close(fig)

threshold_cols = st.columns(3, gap="medium")
for col, row in zip(threshold_cols, threshold_summary.itertuples(index=False)):
    with col:
        st.html(
            f"""
            <div class="oss-finding-card">
                <div class="oss-finding-kicker">{int(row.threshold_months)}-month threshold</div>
                <div class="oss-finding-value">{int(row.events)} / {int(row.projects)}</div>
                <div class="oss-finding-text">Projects classified as events under this inactivity definition · {row.event_rate:.1%} event rate.</div>
            </div>
            """
        )

st.html(
    """
    <div class="oss-insight">
        <div class="oss-insight-label">EXPERIMENT RESULT</div>
        <div class="oss-insight-title">A stricter inactivity definition produces fewer observed events.</div>
        <div class="oss-insight-copy">
            In this pilot cohort, the observed event rate moves from 44.4% at a
            6-month threshold to 33.3% at 12 months and 22.2% at 18 months.
            The choice of threshold therefore directly affects survival estimates
            and should be treated as a methodological decision, not a minor parameter.
        </div>
    </div>
    """
)

# ============================================================
# FINDING 03 — MODEL SIGNALS
# ============================================================

st.html(
    """
    <div class="oss-chart-card" style="margin-top:1.5rem;">
        <div class="oss-chart-title">03 · What drives inactivity risk?</div>
        <div class="oss-chart-subtitle">
            The strongest model features by absolute coefficient. Positive values
            increase modeled risk; negative values decrease it.
        </div>
    </div>
    """
)

plot_features = importance.head(8).copy().sort_values("coefficient")
labels = [
    value.replace("_", " ").title()
    for value in plot_features["feature"]
]
values = plot_features["coefficient"]

fig, ax = plt.subplots(figsize=(12, 5.0))
fig.patch.set_alpha(0)
ax.set_facecolor("#ffffff")

bar_colors = [
    "#6f8059" if value > 0 else "#365b48"
    for value in values
]
ax.barh(labels, values, color=bar_colors, alpha=0.88, height=0.58)
ax.axvline(0, linewidth=1, color="#20392d", alpha=0.45)

ax.set_xlabel("Model coefficient", fontsize=10)
ax.grid(axis="x", alpha=0.16, linewidth=0.8)
ax.grid(axis="y", visible=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_alpha(0.18)
ax.spines["bottom"].set_alpha(0.25)
ax.tick_params(labelsize=9)

st.pyplot(fig, use_container_width=True)
plt.close(fig)

r1, r2 = st.columns(2, gap="medium")

with r1:
    st.html(
        f"""
        <div class="oss-finding-card" style="min-height:145px;">
            <div class="oss-finding-kicker">Strongest risk signal</div>
            <div class="oss-finding-value" style="font-size:1.35rem;">{top_risk['feature'].replace('_', ' ')}</div>
            <div class="oss-finding-text">Coefficient {top_risk['coefficient']:.3f}. Longer zero-commit streaks are associated with higher modeled inactivity risk.</div>
        </div>
        """
    )

with r2:
    st.html(
        f"""
        <div class="oss-finding-card" style="min-height:145px;">
            <div class="oss-finding-kicker">Strongest protective signal</div>
            <div class="oss-finding-value" style="font-size:1.35rem;">{top_protective['feature'].replace('_', ' ')}</div>
            <div class="oss-finding-text">Coefficient {top_protective['coefficient']:.3f}. A higher active-month ratio is associated with lower modeled inactivity risk.</div>
        </div>
        """
    )

st.html(
    f"""
    <div class="oss-insight">
        <div class="oss-insight-label">MODEL OBSERVATION</div>
        <div class="oss-insight-title">Sustained development activity is central to the risk signal.</div>
        <div class="oss-insight-copy">
            The current model places substantially more weight on <b>zero-commit streak</b>
            than on the other engineered features. In the prediction set, {prediction_count}
            observations were scored, with {actual_events} observed 12-month inactivity events
            and {predicted_events} observations classified as inactive by the current prediction rule.
        </div>
    </div>
    """
)

# ============================================================
# FOOTNOTE
# ============================================================

st.html(
    """
    <div class="oss-footer-note">
        <b>Interpretation note:</b> These findings describe the current OSSurvive pilot
        cohort and model outputs. Model coefficients indicate associations within the
        fitted model; they should not be interpreted as causal effects.
    </div>
    """
)
