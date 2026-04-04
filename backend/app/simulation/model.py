from __future__ import annotations

import networkx as nx
import mesa

from app.simulation.agents import UserAgent, PlatformAgent, clamp
from app.simulation.metrics import (
    active_users,
    mean_trust,
    mean_harm,
    churn_rate,
    cumulative_churn,
    reputation,
    short_term_revenue,
    long_term_revenue,
    negative_wom_rate,
)


class DarkPatternTrustModel(mesa.Model):
    def __init__(
        self,
        num_users=500,
        network_type="small_world",
        avg_degree=8,
        rewire_prob=0.08,
        max_steps=104,
        seed=None,
        dark_pattern_intensity=0.40,
        pattern_forced_trial=True,
        pattern_hard_cancel=True,
        pattern_drip_pricing=True,
        customer_support_quality=0.30,
        adaptive_platform=False,
        social_influence_strength=0.18,
        review_visibility=0.35,
        trust_baseline_mean=0.75,
        trust_baseline_sd=0.10,
        digital_literacy_mean=0.55,
        digital_literacy_sd=0.18,
        manipulation_sensitivity_mean=0.60,
        manipulation_sensitivity_sd=0.15,
        social_activity_mean=0.40,
        social_activity_sd=0.18,
        complaint_propensity_mean=0.35,
        complaint_propensity_sd=0.18,
        switching_cost_mean=0.45,
        switching_cost_sd=0.20,
        alpha_exposure_to_trust=0.22,
        beta_support_recovery=0.10,
        delta_exposure_to_harm=0.18,
        gamma_social_trust_loss=0.12,
        theta0=-2.20,
        theta_trust=2.80,
        theta_harm=1.90,
        theta_social=1.20,
        theta_switching_cost=1.60,
        forced_trial_exposure_prob=0.12,
        forced_trial_severity=0.45,
        hard_cancel_exposure_prob=0.10,
        hard_cancel_severity=0.50,
        drip_pricing_exposure_prob=0.08,
        drip_pricing_severity=0.70,
    ):
        super().__init__(rng=seed)
        self.max_steps = max_steps
        self.network_type = network_type
        self.avg_degree = avg_degree
        self.rewire_prob = rewire_prob
        self.pattern_forced_trial = pattern_forced_trial
        self.pattern_hard_cancel = pattern_hard_cancel
        self.pattern_drip_pricing = pattern_drip_pricing
        self.social_influence_strength = social_influence_strength
        self.review_visibility = review_visibility
        self.alpha_exposure_to_trust = alpha_exposure_to_trust
        self.beta_support_recovery = beta_support_recovery
        self.delta_exposure_to_harm = delta_exposure_to_harm
        self.gamma_social_trust_loss = gamma_social_trust_loss
        self.theta0 = theta0
        self.theta_trust = theta_trust
        self.theta_harm = theta_harm
        self.theta_social = theta_social
        self.theta_switching_cost = theta_switching_cost
        self.forced_trial_exposure_prob = forced_trial_exposure_prob
        self.forced_trial_severity = forced_trial_severity
        self.hard_cancel_exposure_prob = hard_cancel_exposure_prob
        self.hard_cancel_severity = hard_cancel_severity
        self.drip_pricing_exposure_prob = drip_pricing_exposure_prob
        self.drip_pricing_severity = drip_pricing_severity
        self.churn_rate = 0.0
        self.cumulative_churn = 0.0

        self.platform = PlatformAgent(
            self,
            dark_pattern_intensity=dark_pattern_intensity,
            customer_support_quality=customer_support_quality,
            adaptive_platform=adaptive_platform,
        )

        self.graph = self._build_network(num_users, network_type, avg_degree, rewire_prob)
        self.user_agents: list[UserAgent] = []

        for _ in range(num_users):
            agent = UserAgent(
                self,
                digital_literacy=self._draw_bounded_normal(digital_literacy_mean, digital_literacy_sd),
                manipulation_sensitivity=self._draw_bounded_normal(manipulation_sensitivity_mean, manipulation_sensitivity_sd),
                social_activity=self._draw_bounded_normal(social_activity_mean, social_activity_sd),
                complaint_propensity=self._draw_bounded_normal(complaint_propensity_mean, complaint_propensity_sd),
                switching_cost=self._draw_bounded_normal(switching_cost_mean, switching_cost_sd),
                trust_baseline=self._draw_bounded_normal(trust_baseline_mean, trust_baseline_sd),
            )
            self.user_agents.append(agent)

        for node_id, agent in zip(self.graph.nodes(), self.user_agents):
            self.graph.nodes[node_id]["agent"] = agent

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "active_users": active_users,
                "mean_trust": mean_trust,
                "mean_harm": mean_harm,
                "churn_rate": churn_rate,
                "cumulative_churn": cumulative_churn,
                "reputation": reputation,
                "negative_wom_rate": negative_wom_rate,
                "short_term_revenue": short_term_revenue,
                "long_term_revenue": long_term_revenue,
            },
        )
        self.datacollector.collect(self)

    def _draw_bounded_normal(self, mean: float, sd: float) -> float:
        return clamp(self.random.gauss(mean, sd))

    def _build_network(self, num_users: int, network_type: str, avg_degree: int, rewire_prob: float):
        seed = self.random.randint(0, 1_000_000)
        if network_type == "small_world":
            return nx.watts_strogatz_graph(num_users, avg_degree, rewire_prob, seed=seed)
        if network_type == "scale_free":
            return nx.barabasi_albert_graph(num_users, max(1, avg_degree // 2), seed=seed)
        p = avg_degree / max(1, num_users - 1)
        return nx.erdos_renyi_graph(num_users, p, seed=seed)

    def _sample_direct_exposure(self) -> float:
        severity = 0.0
        intensity = self.platform.dark_pattern_intensity
        if self.pattern_forced_trial and self.random.random() < self.forced_trial_exposure_prob * intensity:
            severity += self.forced_trial_severity
        if self.pattern_hard_cancel and self.random.random() < self.hard_cancel_exposure_prob * intensity:
            severity += self.hard_cancel_severity
        if self.pattern_drip_pricing and self.random.random() < self.drip_pricing_exposure_prob * intensity:
            severity += self.drip_pricing_severity
        return clamp(severity)

    def _propagate_social_signals(self):
        for node_id in self.graph.nodes():
            sender = self.graph.nodes[node_id]["agent"]
            if not sender.active:
                continue
            wom = sender.decide_word_of_mouth()
            if wom <= 0:
                continue
            for nbr in self.graph.neighbors(node_id):
                receiver = self.graph.nodes[nbr]["agent"]
                if receiver.active and self.random.random() < self.review_visibility:
                    receiver.received_negative_signal += self.social_influence_strength * wom

    def _update_platform_outcomes(self):
        active = [a for a in self.user_agents if a.active]
        churned = [a for a in self.user_agents if not a.active]
        prev_cumulative = self.cumulative_churn
        self.cumulative_churn = len(churned) / len(self.user_agents)
        self.churn_rate = max(0.0, self.cumulative_churn - prev_cumulative)

        mean_tr = sum(a.trust for a in active) / len(active) if active else 0.0
        mean_wom = sum(a.negative_wom for a in active) / len(active) if active else 0.0
        self.platform.reputation = clamp(0.7 * mean_tr + 0.3 * (1.0 - mean_wom))

        short_gain = 0.0
        for a in active:
            short_gain += 1.0
            short_gain += 0.8 * a.last_exposure
        self.platform.short_term_revenue += short_gain
        self.platform.long_term_revenue = self.platform.short_term_revenue * (1.0 - self.cumulative_churn)

    def get_latest_metrics(self) -> dict:
        df = self.datacollector.get_model_vars_dataframe()
        if df.empty:
            return {}
        latest = df.iloc[-1].to_dict()
        return {k: float(v) if hasattr(v, "item") else v for k, v in latest.items()}

    def get_timeseries(self) -> list[dict]:
        df = self.datacollector.get_model_vars_dataframe().reset_index(names="step")
        records = df.to_dict(orient="records")
        normalized = []
        for row in records:
            normalized.append({k: (float(v) if hasattr(v, "item") else v) for k, v in row.items()})
        return normalized

    def get_network_snapshot(self) -> dict:
        selected_nodes = list(self.graph.nodes())
        nodes = []
        edges = []
        for node_id in selected_nodes:
            agent = self.graph.nodes[node_id]["agent"]
            nodes.append({"nodeId": int(node_id), **agent.to_snapshot()})
        for src, dst in self.graph.edges():
            edges.append({"source": int(src), "target": int(dst)})
        return {"nodes": nodes, "edges": edges}

    def step(self):
        if self.steps >= self.max_steps:
            self.running = False
            return

        for user in self.user_agents:
            if user.active:
                user.last_exposure = 0.0
                sev = self._sample_direct_exposure()
                if sev > 0:
                    user.apply_direct_exposure(sev)

        self._propagate_social_signals()

        for user in self.user_agents:
            user.apply_social_signal()
        for user in self.user_agents:
            user.apply_recovery()
        for user in self.user_agents:
            user.maybe_churn()

        self._update_platform_outcomes()
        self.platform.adapt_strategy()
        self.datacollector.collect(self)
