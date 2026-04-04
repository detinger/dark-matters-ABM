from __future__ import annotations

import os
import sys
import time
from math import sqrt
from pathlib import Path

import networkx as nx
import numpy as np

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
CACHE_DIR = BACKEND_DIR / ".cache"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("IPYTHONDIR", str(CACHE_DIR / "ipython"))
os.environ.setdefault("MPLCONFIGDIR", str(CACHE_DIR / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(CACHE_DIR / "xdg"))

for cache_subdir in ("ipython", "matplotlib", "xdg", "xdg/fontconfig"):
    (CACHE_DIR / cache_subdir).mkdir(parents=True, exist_ok=True)

import solara
import solara.lab
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from mesa.visualization.utils import force_update, update_counter

from app.simulation.config import DEFAULTS
from app.simulation.model import DarkPatternTrustModel


def trust_to_color(trust: float, active: bool) -> str:
    if not active:
        return "#475569"
    if trust > 0.85:
        return "#16a34a"
    if trust > 0.65:
        return "#0ea5e9"
    if trust > 0.45:
        return "#7c3aed"
    if trust > 0.25:
        return "#f97316"
    return "#dc2626"


def format_metric(value: float | int | bool | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, int):
        return f"{value}"
    return f"{value:.3f}"


def build_initial_model_parameters() -> dict:
    parameters = {}
    for name, options in MODEL_PARAMS.items():
        if isinstance(options, dict) and "type" in options:
            parameters[name] = options.get("value")
        else:
            parameters[name] = options
    return parameters


SERIES_COLORS = {
    "mean_trust": "#0ea5e9",
    "mean_harm": "#f97316",
    "negative_wom_rate": "#dc2626",
    "cumulative_churn": "#7c3aed",
    "reputation": "#16a34a",
    "short_term_revenue": "#f59e0b",
    "long_term_revenue": "#2563eb",
}


def get_layout(model: DarkPatternTrustModel) -> dict[int | str, np.ndarray]:
    cached_layout = getattr(model, "_solara_layout", None)
    expected_nodes = len(model.graph.nodes()) + 1
    if cached_layout and len(cached_layout) == expected_nodes:
        return cached_layout

    user_layout = nx.spring_layout(model.graph, seed=13)
    scale = 1.35
    layout = {int(node_id): np.asarray(coords) * scale for node_id, coords in user_layout.items()}
    layout["platform"] = np.asarray((0.0, 0.0))
    model._solara_layout = layout
    return layout


@solara.component
def NetworkOverview(model: DarkPatternTrustModel, version: int = 0):
    _ = version
    update_counter.get()

    total_users = len(model.user_agents)
    if total_users > 1200:
        solara.Markdown(
            "> The Solara network panel is intentionally disabled above 1,200 users to keep the Mesa UI responsive. "
            "You can still step the model and inspect the plots below."
        )
        return

    layout = get_layout(model)
    fig = Figure(figsize=(9.8, 9.8))
    ax = fig.subplots()
    ax.set_facecolor("#f8fafc")

    social_edges = [(int(src), int(dst)) for src, dst in model.graph.edges()]
    platform_edges = [("platform", int(node_id)) for node_id in model.graph.nodes()]

    nx.draw_networkx_edges(
        model.graph,
        pos=layout,
        ax=ax,
        edgelist=social_edges,
        edge_color="#cbd5e1",
        width=0.55,
        alpha=0.28,
    )

    platform_graph = nx.Graph()
    platform_graph.add_node("platform")
    platform_graph.add_nodes_from(int(node_id) for node_id in model.graph.nodes())
    platform_graph.add_edges_from(platform_edges)
    nx.draw_networkx_edges(
        platform_graph,
        pos=layout,
        ax=ax,
        edgelist=platform_edges,
        edge_color="#facc15",
        width=0.6,
        alpha=0.08,
    )

    user_positions = [layout[int(node_id)] for node_id in model.graph.nodes()]
    user_colors = [
        trust_to_color(agent.trust, agent.active)
        for node_id in model.graph.nodes()
        for agent in [model.graph.nodes[node_id]["agent"]]
    ]
    user_sizes = [
        28 + (18 * model.graph.nodes[node_id]["agent"].negative_wom)
        for node_id in model.graph.nodes()
    ]

    if user_positions:
        xy = np.vstack(user_positions)
        ax.scatter(
            xy[:, 0],
            xy[:, 1],
            s=user_sizes,
            c=user_colors,
            edgecolors="#f8fafc",
            linewidths=0.45,
            zorder=3,
        )

    platform_x, platform_y = layout["platform"]
    ax.scatter(
        [platform_x],
        [platform_y],
        s=220,
        c=["#facc15"],
        edgecolors="#78350f",
        linewidths=1.4,
        zorder=4,
    )
    ax.annotate(
        "Platform",
        xy=(platform_x, platform_y),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=10,
        color="#78350f",
        weight="bold",
    )

    radius = max(
        sqrt(total_users) * 0.08,
        max(np.abs(coords).max() for coords in layout.values()) + 0.2,
        1.2,
    )
    ax.set_xlim(-radius, radius)
    ax.set_ylim(-radius, radius)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Network Overview", fontsize=13, pad=12)
    for spine in ax.spines.values():
        spine.set_visible(False)

    solara.FigureMatplotlib(fig)


@solara.component
def RunSummary(model: DarkPatternTrustModel, version: int = 0):
    _ = version
    update_counter.get()

    metrics = model.get_latest_metrics()
    tipping_points = model.get_tipping_points()
    recent_events = model.get_recent_events()
    summary_rows = [
        ("Step", model.steps),
        ("Active users", metrics.get("active_users")),
        ("Mean trust", metrics.get("mean_trust")),
        ("Mean harm", metrics.get("mean_harm")),
        ("Cumulative churn", metrics.get("cumulative_churn")),
        ("Platform reputation", metrics.get("reputation")),
        ("Short-term revenue", metrics.get("short_term_revenue")),
        ("Long-term revenue", metrics.get("long_term_revenue")),
        ("Direct exposures (last step)", len(recent_events["direct_exposures"])),
        ("Social signals (last step)", len(recent_events["social_edges"])),
        ("Churn events (last step)", len(recent_events["churned_nodes"])),
    ]
    tipping_rows = [
        (
            point["label"],
            "Triggered" if point["triggered"] else "Not triggered",
            point["step"] if point["step"] is not None else "-",
        )
        for point in tipping_points.values()
    ]

    summary_table = "\n".join(
        f"| {label} | {format_metric(value)} |"
        for label, value in summary_rows
    )
    tipping_table = "\n".join(
        f"| {label} | {status} | {step} |"
        for label, status, step in tipping_rows
    )

    with solara.Column():
        solara.Markdown(
            "\n".join(
                [
                    "### Run Summary",
                    "",
                    "| Metric | Value |",
                    "| --- | --- |",
                    summary_table,
                ]
            )
        )
        solara.Markdown(
            "\n".join(
                [
                    "### Tipping Points",
                    "",
                    "| Tipping point | Status | Step |",
                    "| --- | --- | --- |",
                    tipping_table,
                ]
            )
        )


@solara.component
def TimeSeriesPlot(model: DarkPatternTrustModel, measures: list[str], version: int = 0):
    _ = version
    update_counter.get()

    df = model.datacollector.get_model_vars_dataframe()
    fig = Figure(figsize=(4.6, 3.8))
    ax = fig.subplots()
    ax.set_facecolor("#f8fafc")

    if df.empty:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center", transform=ax.transAxes)
    else:
        for measure in measures:
            if measure not in df.columns:
                continue
            ax.plot(
                df.index,
                df[measure],
                label=measure,
                color=SERIES_COLORS.get(measure),
                linewidth=2.0,
                marker="o",
                markersize=3.0,
            )
        ax.legend(loc="best", fontsize=8)

    ax.set_xlabel("Step")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(alpha=0.18, linewidth=0.6)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.94, bottom=0.22)
    for spine in ax.spines.values():
        spine.set_alpha(0.35)

    solara.FigureMatplotlib(fig)


@solara.component
def OverviewPage(model, version: int = 0):
    _ = version
    reactive_model = model.value
    update_counter.get()

    with solara.Column(gap="16px", style={"padding": "8px 4px 20px 4px"}):
        with solara.Row(
            gap="16px",
            style={"alignItems": "stretch", "flexWrap": "wrap"},
        ):
            with solara.Card(
                title="Network Overview",
                style={"flex": "3 1 840px", "minWidth": "640px"},
            ):
                NetworkOverview(reactive_model, version=version)
            with solara.Card(
                title="Simulation Summary",
                style={"flex": "1 1 320px", "minWidth": "300px"},
            ):
                RunSummary(reactive_model, version=version)

        with solara.Row(
            gap="16px",
            style={"alignItems": "stretch", "flexWrap": "wrap"},
        ):
            with solara.Card(
                title="Trust, Harm, and WOM",
                style={"flex": "1 1 320px", "minWidth": "280px", "minHeight": "360px"},
            ):
                TimeSeriesPlot(
                    reactive_model,
                    ["mean_trust", "mean_harm", "negative_wom_rate"],
                    version=version,
                )
            with solara.Card(
                title="Churn and Reputation",
                style={"flex": "1 1 320px", "minWidth": "280px", "minHeight": "360px"},
            ):
                TimeSeriesPlot(
                    reactive_model,
                    ["cumulative_churn", "reputation"],
                    version=version,
                )
            with solara.Card(
                title="Revenue",
                style={"flex": "1 1 320px", "minWidth": "280px", "minHeight": "360px"},
            ):
                TimeSeriesPlot(
                    reactive_model,
                    ["short_term_revenue", "long_term_revenue"],
                    version=version,
                )


MODEL_PARAMS = {
    **DEFAULTS,
    "num_users": {
        "type": "SliderInt",
        "value": DEFAULTS["num_users"],
        "label": "Users",
        "min": 50,
        "max": 2000,
        "step": 50,
    },
    "network_type": {
        "type": "Select",
        "value": DEFAULTS["network_type"],
        "label": "Network type",
        "values": ["small_world", "scale_free", "random"],
    },
    "avg_degree": {
        "type": "SliderInt",
        "value": DEFAULTS["avg_degree"],
        "label": "Average degree",
        "min": 2,
        "max": 50,
        "step": 1,
    },
    "rewire_prob": {
        "type": "SliderFloat",
        "value": DEFAULTS["rewire_prob"],
        "label": "Rewire probability",
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
    },
    "max_steps": {
        "type": "SliderInt",
        "value": DEFAULTS["max_steps"],
        "label": "Max steps",
        "min": 1,
        "max": 500,
        "step": 1,
    },
    "seed": {
        "type": "SliderInt",
        "value": DEFAULTS["seed"],
        "label": "Seed",
        "min": 0,
        "max": 9999,
        "step": 1,
    },
    "dark_pattern_intensity": {
        "type": "SliderFloat",
        "value": DEFAULTS["dark_pattern_intensity"],
        "label": "Dark pattern intensity",
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
    },
    "pattern_forced_trial": {
        "type": "Checkbox",
        "value": DEFAULTS["pattern_forced_trial"],
        "label": "Enable forced trial",
    },
    "pattern_hard_cancel": {
        "type": "Checkbox",
        "value": DEFAULTS["pattern_hard_cancel"],
        "label": "Enable hard cancel",
    },
    "pattern_drip_pricing": {
        "type": "Checkbox",
        "value": DEFAULTS["pattern_drip_pricing"],
        "label": "Enable drip pricing",
    },
    "customer_support_quality": {
        "type": "SliderFloat",
        "value": DEFAULTS["customer_support_quality"],
        "label": "Support quality",
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
    },
    "adaptive_platform": {
        "type": "Checkbox",
        "value": DEFAULTS["adaptive_platform"],
        "label": "Adaptive platform",
    },
    "social_influence_strength": {
        "type": "SliderFloat",
        "value": DEFAULTS["social_influence_strength"],
        "label": "Social influence strength",
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
    },
    "review_visibility": {
        "type": "SliderFloat",
        "value": DEFAULTS["review_visibility"],
        "label": "Review visibility",
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
    },
}


@solara.component
def SimulationControls(
    model,
    model_parameters,
    play_interval,
    render_interval,
    model_version,
):
    playing = solara.use_reactive(False)
    running = solara.use_reactive(bool(getattr(model.value, "running", True)))
    error_message = solara.use_reactive(None)

    def sync_running():
        running.value = bool(getattr(model.value, "running", True))

    solara.use_effect(sync_running, [model.value])

    def step_once():
        if not getattr(model.value, "running", True):
            running.value = False
            return
        model.value.step()
        running.value = bool(getattr(model.value, "running", True))

    def do_step():
        error_message.value = None
        try:
            for _ in range(render_interval.value):
                step_once()
                if not running.value:
                    break
            force_update()
        except Exception as exc:
            error_message.value = f"error in step: {exc}"

    def play_loop():
        while playing.value and running.value:
            time.sleep(play_interval.value / 1000)
            do_step()

    solara.lab.use_task(
        play_loop,
        dependencies=[playing.value, running.value, play_interval.value, render_interval.value],
        prefer_threaded=True,
    )

    def do_reset():
        error_message.value = None
        playing.value = False
        model.value = type(model.value)(**model_parameters.value)
        running.value = bool(getattr(model.value, "running", True))
        model_version.value = model_version.value + 1
        force_update()

    def toggle_play():
        if not running.value:
            return
        playing.value = not playing.value

    with solara.Row(justify="space-between"):
        solara.Button(label="Reset", color="primary", on_click=do_reset)
        solara.Button(
            label="▶" if not playing.value else "❚❚",
            color="primary",
            on_click=toggle_play,
            disabled=not running.value,
        )
        solara.Button(
            label="Step",
            color="primary",
            on_click=do_step,
            disabled=playing.value or not running.value,
        )

    if error_message.value:
        solara.Error(label=error_message.value)


@solara.component
def ParameterInputs(model_parameters):
    parameters = model_parameters.value

    for name, options in MODEL_PARAMS.items():
        if not isinstance(options, dict) or "type" not in options:
            continue

        label = options.get("label", name)
        current_value = parameters.get(name, options.get("value"))

        def on_change(value, name=name):
            model_parameters.value = {**model_parameters.value, name: value}

        input_type = options.get("type")
        if input_type == "SliderInt":
            solara.SliderInt(
                label,
                value=current_value,
                on_value=on_change,
                min=options.get("min"),
                max=options.get("max"),
                step=options.get("step"),
            )
        elif input_type == "SliderFloat":
            solara.SliderFloat(
                label,
                value=current_value,
                on_value=on_change,
                min=options.get("min"),
                max=options.get("max"),
                step=options.get("step"),
            )
        elif input_type == "Select":
            solara.Select(
                label,
                value=current_value,
                on_value=on_change,
                values=options.get("values"),
            )
        elif input_type == "Checkbox":
            solara.Checkbox(
                label=label,
                value=current_value,
                on_value=on_change,
            )


@solara.component
def Page():
    initial_model = solara.use_memo(lambda: DarkPatternTrustModel(**DEFAULTS), [])
    initial_model_parameters = solara.use_memo(build_initial_model_parameters, [])

    model = solara.use_reactive(initial_model)
    reactive_model_parameters = solara.use_reactive(initial_model_parameters)
    reactive_play_interval = solara.use_reactive(100)
    reactive_render_interval = solara.use_reactive(1)
    model_version = solara.use_reactive(0)

    with solara.AppBar():
        solara.AppBarTitle("Dark Patterns ABM (Mesa/Solara)")
        solara.lab.ThemeToggle()

    with solara.Sidebar(), solara.Column():
        with solara.Card("Controls"):
            solara.SliderInt(
                label="Play Interval (ms)",
                value=reactive_play_interval,
                on_value=reactive_play_interval.set,
                min=1,
                max=500,
                step=10,
            )
            solara.SliderInt(
                label="Render Interval (steps)",
                value=reactive_render_interval,
                on_value=reactive_render_interval.set,
                min=1,
                max=100,
                step=2,
            )
            SimulationControls(
                model,
                model_parameters=reactive_model_parameters,
                play_interval=reactive_play_interval,
                render_interval=reactive_render_interval,
                model_version=model_version,
            )

        with solara.Card("Model Parameters"):
            solara.Markdown("Changes apply when you click **Reset**.")
            ParameterInputs(reactive_model_parameters)

    OverviewPage(model, version=model_version.value)


page = Page
