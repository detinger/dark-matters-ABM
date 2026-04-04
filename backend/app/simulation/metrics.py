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
