def active_users(model) -> int:
    return sum(1 for a in model.user_agents if a.active)


def mean_trust(model) -> float:
    active = [a.trust for a in model.user_agents if a.active]
    return sum(active) / len(active) if active else 0.0


def mean_harm(model) -> float:
    active = [a.harm for a in model.user_agents if a.active]
    return sum(active) / len(active) if active else 0.0


def churn_rate(model) -> float:
    return model.churn_rate


def cumulative_churn(model) -> float:
    return model.cumulative_churn


def reputation(model) -> float:
    return model.platform.reputation


def short_term_revenue(model) -> float:
    return model.platform.short_term_revenue


def long_term_revenue(model) -> float:
    return model.platform.long_term_revenue


def negative_wom_rate(model) -> float:
    active = [a.negative_wom for a in model.user_agents if a.active]
    return sum(active) / len(active) if active else 0.0


def trust_collapse_triggered(model) -> float:
    return float(model.tipping_points["trust_collapse"]["triggered"])


def trust_collapse_step(model) -> int:
    step = model.tipping_points["trust_collapse"]["step"]
    return -1 if step is None else step


def social_contagion_triggered(model) -> float:
    return float(model.tipping_points["social_contagion"]["triggered"])


def social_contagion_step(model) -> int:
    step = model.tipping_points["social_contagion"]["step"]
    return -1 if step is None else step


def churn_cascade_triggered(model) -> float:
    return float(model.tipping_points["churn_cascade"]["triggered"])


def churn_cascade_step(model) -> int:
    step = model.tipping_points["churn_cascade"]["step"]
    return -1 if step is None else step


def extractive_divergence_triggered(model) -> float:
    return float(model.tipping_points["extractive_divergence"]["triggered"])


def extractive_divergence_step(model) -> int:
    step = model.tipping_points["extractive_divergence"]["step"]
    return -1 if step is None else step


def tipping_points_triggered_count(model) -> int:
    return sum(1 for point in model.tipping_points.values() if point["triggered"])


def any_tipping_point_triggered(model) -> float:
    return float(tipping_points_triggered_count(model) > 0)


def first_tipping_point_step(model) -> int:
    steps = [point["step"] for point in model.tipping_points.values() if point["step"] is not None]
    return -1 if not steps else min(steps)
