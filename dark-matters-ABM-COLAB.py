"""Colab-ready analysis script for Dark Patterns ABM CSV exports.

Usage in Google Colab:
1. Upload this file to Colab.
2. Run: `!python dark-matters-ABM-COLAB.py`
3. When prompted, upload a CSV exported from the web app.

You can also import this file in a Colab cell and call:
    analyze_simulation_csv("simulation-<id>.csv")
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Iterable

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
except ModuleNotFoundError as exc:  # pragma: no cover - environment-specific guard
    raise SystemExit(
        "This analysis script requires pandas, matplotlib, and seaborn. "
        "In Google Colab you can install missing packages with: "
        "!pip install pandas matplotlib seaborn"
    ) from exc

try:
    from IPython.display import Markdown, display
except Exception:  # pragma: no cover - safe fallback outside notebook contexts
    Markdown = None
    display = None


THEORY_OVERVIEW = dedent(
    """
    # Dark Matters ABM: Colab Analysis Workbook

    ## What this script is for
    This analysis script is designed for the exported CSV files produced by the
    Dark Patterns ABM dashboard. It turns one simulation run into a structured
    analytical report with:

    - model framing and theory notes
    - parameter summaries
    - descriptive statistics
    - simulation charts
    - interpretation of the observed trajectory
    - publication-friendly figures you can save from Colab

    ## Theoretical framing
    The model studies how dark patterns can generate a gap between short-term
    platform gains and long-term user trust. The central theoretical idea is
    that manipulative interface choices may increase immediate revenue, but they
    also create cumulative harm, negative word-of-mouth, and churn. Over time,
    those effects can reduce platform reputation and weaken long-run value.

    ## Agents in the model
    The current simulation contains two main agent types:

    - User agents:
      They differ in digital literacy, manipulation sensitivity, social
      activity, complaint propensity, switching cost, and baseline trust.
    - Platform agent:
      It controls dark pattern intensity, customer support quality, and may
      optionally adapt its strategy if outcomes worsen.

    ## Mechanisms represented in the run
    Each step of the simulation roughly follows this logic:

    1. Users may be exposed to dark patterns.
    2. Exposure decreases trust and increases harm.
    3. Negative experience can diffuse socially as word-of-mouth.
    4. Support quality can produce partial recovery.
    5. Users may churn depending on trust, harm, social pressure, and switching cost.
    6. Platform reputation and revenue are updated.
    7. If adaptive behavior is enabled, the platform may react to worsening outcomes.

    ## What the exported CSV represents
    Each row in the exported CSV corresponds to one simulation step.
    The file repeats the simulation parameters in every row so that the
    timeseries can always be interpreted together with the scenario settings.

    ## Formalized tipping-point detection
    The simulation now includes explicit tipping-point rules. A tipping point is
    only recorded when a threshold is sustained for three consecutive steps.
    This avoids treating a single noisy fluctuation as a systemic transition.

    The current rules are:

    - Trust Collapse:
      mean trust is at or below 0.50 for three consecutive steps.
    - Social Contagion:
      negative WOM is at or above 0.22 for three consecutive steps.
    - Churn Cascade:
      cumulative churn is at or above 0.35 for three consecutive steps.
    - Extractive Divergence:
      the revenue gap exceeds 20% of short-term revenue while cumulative churn
      is at or above 0.15 for three consecutive steps.
    """
).strip()


METRIC_GUIDE = dedent(
    """
    ## Metric guide

    - `active_users`: number of users still active in the platform.
    - `mean_trust`: average trust among active users.
    - `mean_harm`: average accumulated harm among active users.
    - `churn_rate`: step-level increase in cumulative churn.
    - `cumulative_churn`: share of users who have already left the platform.
    - `negative_wom_rate`: average negative word-of-mouth among active users.
    - `reputation`: platform reputation proxy.
    - `short_term_revenue`: accumulated short-run revenue proxy.
    - `long_term_revenue`: revenue proxy discounted by churn.
    - `trust_collapse_triggered`, `social_contagion_triggered`,
      `churn_cascade_triggered`, `extractive_divergence_triggered`:
      binary indicators for whether each formal tipping point has been triggered.
    - `*_step` columns:
      the first step at which the corresponding tipping point was confirmed.

    ## Interpretation logic
    A "good" run is not just one with high revenue. A more balanced run is one
    where short-term revenue does not come at the cost of a steep collapse in
    trust, reputation, and retention. When cumulative churn rises while
    long-term revenue flattens or falls, the model is showing the long-run cost
    of dark-pattern-heavy strategies.
    """
).strip()


CHART_EXPLANATIONS = dedent(
    """
    ## Reading the charts

    - Trust and reputation:
      Shows whether users continue to believe the platform is fair and whether
      the platform's aggregate standing remains stable over time.

    - Churn and negative WOM:
      Helps identify social tipping points. If churn and negative WOM rise
      together, social diffusion may be accelerating system decline.

    - Revenue trajectories:
      Shows the difference between immediate extraction and durable value.
      Divergence between short-term and long-term revenue is especially important.

    - Active users and harm:
      Shows whether the system is sustaining engagement while accumulating harm,
      or whether harm is converting into visible user loss.

    - Correlation heatmap:
      Useful for exploratory interpretation. It does not prove causation, but it
      shows which metrics move together inside a single run.

    - Tipping-point overlay:
      Vertical markers show when the model judged the system to have crossed a
      persistent qualitative threshold rather than a one-step fluctuation.
    """
).strip()


PARAMETER_COLUMNS = [
    "adaptive_platform",
    "alpha_exposure_to_trust",
    "avg_degree",
    "beta_support_recovery",
    "complaint_propensity_mean",
    "complaint_propensity_sd",
    "customer_support_quality",
    "dark_pattern_intensity",
    "delta_exposure_to_harm",
    "digital_literacy_mean",
    "digital_literacy_sd",
    "drip_pricing_exposure_prob",
    "drip_pricing_severity",
    "forced_trial_exposure_prob",
    "forced_trial_severity",
    "gamma_social_trust_loss",
    "hard_cancel_exposure_prob",
    "hard_cancel_severity",
    "manipulation_sensitivity_mean",
    "manipulation_sensitivity_sd",
    "max_steps",
    "network_type",
    "num_users",
    "pattern_drip_pricing",
    "pattern_forced_trial",
    "pattern_hard_cancel",
    "review_visibility",
    "rewire_prob",
    "seed",
    "social_activity_mean",
    "social_activity_sd",
    "social_influence_strength",
    "switching_cost_mean",
    "switching_cost_sd",
    "theta0",
    "theta_harm",
    "theta_social",
    "theta_switching_cost",
    "theta_trust",
    "trust_baseline_mean",
    "trust_baseline_sd",
]


METRIC_COLUMNS = [
    "active_users",
    "any_tipping_point_triggered",
    "churn_rate",
    "cumulative_churn",
    "extractive_divergence_step",
    "extractive_divergence_triggered",
    "first_tipping_point_step",
    "long_term_revenue",
    "mean_harm",
    "mean_trust",
    "negative_wom_rate",
    "reputation",
    "short_term_revenue",
    "social_contagion_step",
    "social_contagion_triggered",
    "step",
    "tipping_points_triggered_count",
    "trust_collapse_step",
    "trust_collapse_triggered",
    "churn_cascade_step",
    "churn_cascade_triggered",
]


TIPPING_POINT_SPECS = {
    "trust_collapse": {
        "trigger_column": "trust_collapse_triggered",
        "step_column": "trust_collapse_step",
        "label": "Trust Collapse",
        "color": "#2563eb",
    },
    "social_contagion": {
        "trigger_column": "social_contagion_triggered",
        "step_column": "social_contagion_step",
        "label": "Social Contagion",
        "color": "#059669",
    },
    "churn_cascade": {
        "trigger_column": "churn_cascade_triggered",
        "step_column": "churn_cascade_step",
        "label": "Churn Cascade",
        "color": "#dc2626",
    },
    "extractive_divergence": {
        "trigger_column": "extractive_divergence_triggered",
        "step_column": "extractive_divergence_step",
        "label": "Extractive Divergence",
        "color": "#d97706",
    },
}


CORRELATION_COLUMNS = [
    "active_users",
    "active_share",
    "churn_rate",
    "cumulative_churn",
    "long_term_revenue",
    "mean_harm",
    "mean_trust",
    "negative_wom_rate",
    "reputation",
    "revenue_gap",
    "short_term_revenue",
    "trust_loss_from_baseline",
]


def _show_markdown(text: str) -> None:
    if display is not None and Markdown is not None:
        display(Markdown(text))
    else:
        print(text)
        print()


def _show_dataframe(df: pd.DataFrame) -> None:
    if display is not None:
        display(df)
    else:
        print(df.to_string(index=False))
        print()


def _in_colab() -> bool:
    try:
        import google.colab  # noqa: F401

        return True
    except Exception:
        return False


def _load_csv_from_colab_upload() -> pd.DataFrame:
    from google.colab import files

    uploaded = files.upload()
    if not uploaded:
        raise ValueError("No file was uploaded.")
    first_name = next(iter(uploaded))
    return pd.read_csv(first_name)


def _load_dataframe(csv_path: str | Path | None) -> pd.DataFrame:
    if csv_path is None:
        if _in_colab():
            return _load_csv_from_colab_upload()
        raise ValueError("Provide a csv_path when running outside Google Colab.")
    return pd.read_csv(csv_path)


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.columns:
        if cleaned[column].dtype == object:
            lowered = cleaned[column].astype(str).str.lower()
            if lowered.isin({"true", "false"}).all():
                cleaned[column] = lowered.map({"true": True, "false": False})

    for column in METRIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    if "step" in cleaned.columns:
        cleaned = cleaned.sort_values("step").reset_index(drop=True)

    if "num_users" in cleaned.columns and "active_users" in cleaned.columns:
        cleaned["active_share"] = cleaned["active_users"] / cleaned["num_users"]

    if "mean_trust" in cleaned.columns:
        baseline = float(cleaned["mean_trust"].iloc[0])
        cleaned["trust_loss_from_baseline"] = baseline - cleaned["mean_trust"]

    if "short_term_revenue" in cleaned.columns and "long_term_revenue" in cleaned.columns:
        cleaned["revenue_gap"] = cleaned["short_term_revenue"] - cleaned["long_term_revenue"]

    return cleaned


def _tipping_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for spec in TIPPING_POINT_SPECS.values():
        trigger_column = spec["trigger_column"]
        step_column = spec["step_column"]
        if trigger_column not in df.columns or step_column not in df.columns:
            continue

        triggered = bool(df[trigger_column].fillna(0).max() >= 1)
        raw_step = df.loc[df[step_column] >= 0, step_column]
        trigger_step = None if raw_step.empty else int(raw_step.iloc[0])
        rows.append(
            {
                "tipping_point": spec["label"],
                "triggered": triggered,
                "trigger_step": trigger_step,
            }
        )
    return pd.DataFrame(rows)


def _parameter_summary(df: pd.DataFrame) -> pd.DataFrame:
    available = [column for column in PARAMETER_COLUMNS if column in df.columns]
    if not available:
        return pd.DataFrame(columns=["parameter", "value"])
    row = df.iloc[0][available]
    return pd.DataFrame({"parameter": available, "value": row.values})


def _metric_summary(df: pd.DataFrame) -> pd.DataFrame:
    available = [column for column in METRIC_COLUMNS if column in df.columns]
    if not available:
        return pd.DataFrame()
    summary = pd.DataFrame(
        {
            "start": df[available].iloc[0],
            "end": df[available].iloc[-1],
            "min": df[available].min(),
            "max": df[available].max(),
            "mean": df[available].mean(),
        }
    )
    return summary.round(4)


def _triggered_tipping_labels(df: pd.DataFrame) -> list[str]:
    summary = _tipping_summary(df)
    if summary.empty:
        return []
    return summary.loc[summary["triggered"], "tipping_point"].astype(str).tolist()


def _narrative_summary(df: pd.DataFrame) -> str:
    final = df.iloc[-1]
    start = df.iloc[0]

    trust_change = (
        float(final["mean_trust"] - start["mean_trust"])
        if "mean_trust" in df.columns
        else 0.0
    )
    churn_end = float(final["cumulative_churn"]) if "cumulative_churn" in df.columns else 0.0
    wom_peak = float(df["negative_wom_rate"].max()) if "negative_wom_rate" in df.columns else 0.0
    harm_end = float(final["mean_harm"]) if "mean_harm" in df.columns else 0.0
    revenue_gap_end = float(final["revenue_gap"]) if "revenue_gap" in df.columns else 0.0
    triggered_tipping_points = _triggered_tipping_labels(df)

    if trust_change <= -0.15:
        trust_read = "The run shows a substantial erosion of trust."
    elif trust_change <= -0.05:
        trust_read = "The run shows a moderate decline in trust."
    else:
        trust_read = "Trust remains comparatively stable over the run."

    if churn_end >= 0.5:
        churn_read = "Cumulative churn ends at a high level, suggesting deep long-run user loss."
    elif churn_end >= 0.2:
        churn_read = "Cumulative churn is meaningful and should be treated as a warning signal."
    else:
        churn_read = "Cumulative churn remains comparatively contained."

    if revenue_gap_end > 0:
        revenue_read = (
            "Short-term revenue exceeds long-term revenue at the end of the run, "
            "which is consistent with extraction outpacing durable value."
        )
    else:
        revenue_read = (
            "Short-term and long-term revenue remain relatively aligned, "
            "which suggests less divergence between extraction and sustainability."
        )

    if triggered_tipping_points:
        tipping_read = (
            "The formal tipping detector was activated for: "
            + ", ".join(f"**{name}**" for name in triggered_tipping_points)
            + "."
        )
    else:
        tipping_read = "No formal tipping point is triggered under the current detection rules."

    return dedent(
        f"""
        ## Automated interpretation

        {trust_read}

        {churn_read}

        End-of-run mean harm is **{harm_end:.3f}** and the peak negative WOM rate is **{wom_peak:.3f}**.

        {revenue_read}

        {tipping_read}
        """
    ).strip()


def _line_chart(
    df: pd.DataFrame,
    columns: Iterable[str],
    title: str,
    ylabel: str,
    colors: list[str] | None = None,
    ylim: tuple[float, float] | None = None,
) -> None:
    plt.figure(figsize=(12, 5))
    for idx, column in enumerate(columns):
        if column not in df.columns:
            continue
        color = None if colors is None else colors[idx]
        plt.plot(df["step"], df[column], linewidth=2.4, label=column, color=color)
    plt.title(title, fontsize=13)
    plt.xlabel("Step", fontsize=10)
    plt.ylabel(ylabel, fontsize=10)
    if ylim is not None:
        plt.ylim(*ylim)
    _add_tipping_markers(df)
    plt.grid(alpha=0.25)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.legend(fontsize=9)
    plt.tight_layout()
    plt.show()


def _add_tipping_markers(df: pd.DataFrame) -> None:
    used_labels: set[str] = set()
    for spec in TIPPING_POINT_SPECS.values():
        step_column = spec["step_column"]
        if step_column not in df.columns:
            continue
        valid_steps = df.loc[df[step_column] >= 0, step_column]
        if valid_steps.empty:
            continue
        trigger_step = int(valid_steps.iloc[0])
        label = spec["label"]
        plt.axvline(
            trigger_step,
            color=spec["color"],
            linestyle="--",
            linewidth=1.6,
            alpha=0.75,
            label=label if label not in used_labels else None,
        )
        used_labels.add(label)


def _plot_dashboard_charts(df: pd.DataFrame) -> None:
    _show_markdown("### Core simulation charts")

    _line_chart(
        df,
        ["mean_trust", "reputation"],
        "Trust and Reputation Over Time",
        "Value",
        colors=["#2563eb", "#9333ea"],
        ylim=(0, 1),
    )

    _line_chart(
        df,
        ["churn_rate", "cumulative_churn", "negative_wom_rate"],
        "Churn and Negative WOM Over Time",
        "Value",
        colors=["#ef4444", "#f97316", "#059669"],
        ylim=(0, 1),
    )

    _line_chart(
        df,
        ["short_term_revenue", "long_term_revenue", "revenue_gap"],
        "Revenue Dynamics",
        "Revenue proxy",
        colors=["#0f172a", "#0891b2", "#dc2626"],
    )

    _line_chart(
        df,
        ["active_users", "mean_harm"],
        "Active Users and Mean Harm",
        "Value",
        colors=["#16a34a", "#f59e0b"],
    )


def _plot_normalized_trajectories(df: pd.DataFrame) -> None:
    columns = [
        "mean_trust",
        "reputation",
        "cumulative_churn",
        "negative_wom_rate",
        "mean_harm",
        "active_share",
    ]
    available = [column for column in columns if column in df.columns]
    if not available:
        return

    normalized = df[available].copy()
    for column in available:
        col_min = normalized[column].min()
        col_max = normalized[column].max()
        if col_max == col_min:
            normalized[column] = 0.0
        else:
            normalized[column] = (normalized[column] - col_min) / (col_max - col_min)
    normalized["step"] = df["step"]

    plt.figure(figsize=(12, 6))
    for column in available:
        plt.plot(normalized["step"], normalized[column], linewidth=2.0, label=column)
    _add_tipping_markers(df)
    plt.title("Normalized System Trajectories", fontsize=13)
    plt.xlabel("Step", fontsize=10)
    plt.ylabel("Normalized value", fontsize=10)
    plt.grid(alpha=0.25)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.legend(ncol=2, fontsize=9)
    plt.tight_layout()
    plt.show()


def _plot_correlation_heatmap(df: pd.DataFrame) -> None:
    columns = [column for column in CORRELATION_COLUMNS if column in df.columns]
    columns = [column for column in columns if df[column].nunique(dropna=True) > 1]
    if len(columns) < 2:
        return

    corr = df[columns].corr(numeric_only=True)
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr,
        annot=True,
        annot_kws={"size": 8},
        cmap="coolwarm",
        center=0,
        fmt=".2f",
        square=True,
        cbar_kws={"shrink": 0.8},
    )
    plt.title("Correlation Heatmap for Time-Series Metrics", fontsize=13)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.show()


def _plot_incremental_change(df: pd.DataFrame) -> None:
    if "step" not in df.columns:
        return

    delta_columns = [column for column in ["mean_trust", "reputation", "cumulative_churn", "short_term_revenue", "long_term_revenue"] if column in df.columns]
    if not delta_columns:
        return

    delta_df = df[["step", *delta_columns]].copy()
    for column in delta_columns:
        delta_df[column] = delta_df[column].diff().fillna(0.0)

    plt.figure(figsize=(12, 6))
    for column in delta_columns:
        plt.plot(delta_df["step"], delta_df[column], linewidth=2.0, label=f"d({column})")
    plt.axhline(0, color="#64748b", linewidth=1, alpha=0.7)
    _add_tipping_markers(df)
    plt.title("Step-to-Step Change in Key Metrics", fontsize=13)
    plt.xlabel("Step", fontsize=10)
    plt.ylabel("Delta", fontsize=10)
    plt.grid(alpha=0.25)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.legend(ncol=2, fontsize=9)
    plt.tight_layout()
    plt.show()


def analyze_simulation_csv(csv_path: str | Path | None = None) -> pd.DataFrame:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["xtick.labelsize"] = 9
    plt.rcParams["ytick.labelsize"] = 9
    plt.rcParams["legend.fontsize"] = 9

    _show_markdown(THEORY_OVERVIEW)

    df = _clean_dataframe(_load_dataframe(csv_path))

    if "simulation_id" in df.columns:
        simulation_ids = df["simulation_id"].dropna().astype(str).unique().tolist()
        _show_markdown(
            f"## Loaded simulation data\n\n"
            f"- Rows: **{len(df)}**\n"
            f"- Simulation IDs found: **{len(simulation_ids)}**\n"
            f"- Selected run for analysis: **{simulation_ids[0]}**"
        )

    _show_markdown("## Scenario parameters")
    _show_dataframe(_parameter_summary(df))

    _show_markdown(METRIC_GUIDE)

    _show_markdown("## Descriptive summary of the run")
    _show_dataframe(_metric_summary(df))

    _show_markdown("## Formal tipping-point summary")
    _show_dataframe(_tipping_summary(df))

    _show_markdown(_narrative_summary(df))
    _show_markdown(CHART_EXPLANATIONS)

    _plot_dashboard_charts(df)

    _show_markdown("### Comparative trajectory view")
    _plot_normalized_trajectories(df)

    _show_markdown("### Correlation structure")
    _plot_correlation_heatmap(df)

    _show_markdown("### Step-to-step change diagnostics")
    _plot_incremental_change(df)

    _show_markdown(
        """
        ## Suggested discussion prompts

        - At what point does trust begin to break down more quickly?
        - Does negative WOM appear before churn accelerates, or at the same time?
        - How large is the final gap between short-term and long-term revenue?
        - Does the parameter combination look extractive, sustainable, or mixed?
        - If adaptive behavior was enabled, did the platform stabilize outcomes?
        """
    )

    return df


if __name__ == "__main__":
    analyze_simulation_csv(csv_path=None)
