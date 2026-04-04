from __future__ import annotations

import math
import mesa


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


class UserAgent(mesa.Agent):
    def __init__(
        self,
        model,
        digital_literacy: float,
        manipulation_sensitivity: float,
        social_activity: float,
        complaint_propensity: float,
        switching_cost: float,
        trust_baseline: float,
    ):
        super().__init__(model)
        self.digital_literacy = clamp(digital_literacy)
        self.manipulation_sensitivity = clamp(manipulation_sensitivity)
        self.social_activity = clamp(social_activity)
        self.complaint_propensity = clamp(complaint_propensity)
        self.switching_cost = clamp(switching_cost)
        self.trust_baseline = clamp(trust_baseline)

        self.trust = clamp(trust_baseline)
        self.perceived_fairness = clamp(trust_baseline)
        self.harm = 0.0
        self.exposure_count = 0
        self.received_negative_signal = 0.0
        self.negative_wom = 0.0
        self.active = True

        self.last_exposure = 0.0
        self.last_churn_probability = 0.0
        self.last_review_valence = 0.0

    def apply_direct_exposure(self, exposure_severity: float) -> None:
        if not self.active:
            return

        self.exposure_count += 1
        self.last_exposure = exposure_severity

        alpha = self.model.alpha_exposure_to_trust
        delta = self.model.delta_exposure_to_harm
        detection_multiplier = 0.6 + 0.8 * self.digital_literacy

        trust_loss = alpha * exposure_severity * self.manipulation_sensitivity * detection_multiplier
        harm_gain = delta * exposure_severity * (0.7 + 0.6 * self.manipulation_sensitivity)

        self.trust = clamp(self.trust - trust_loss)
        self.perceived_fairness = clamp(self.perceived_fairness - 0.8 * trust_loss)
        self.harm += harm_gain
        self.last_review_valence = -min(1.0, exposure_severity)

    def apply_social_signal(self) -> None:
        if not self.active:
            return
        social_loss = self.model.gamma_social_trust_loss * self.received_negative_signal
        self.trust = clamp(self.trust - social_loss)
        self.perceived_fairness = clamp(self.perceived_fairness - 0.8 * social_loss)
        self.received_negative_signal = 0.0

    def apply_recovery(self) -> None:
        if not self.active:
            return
        recovery = self.model.beta_support_recovery * self.model.platform.customer_support_quality * (1.0 - self.harm * 0.15)
        recovery = max(0.0, recovery)
        self.trust = clamp(self.trust + recovery)
        self.perceived_fairness = clamp(self.perceived_fairness + 0.7 * recovery)

    def decide_word_of_mouth(self) -> float:
        if not self.active:
            self.negative_wom = 0.0
            return 0.0
        base = (
            0.20 * self.social_activity
            + 0.35 * self.complaint_propensity
            + 0.30 * min(1.0, self.harm)
            + 0.15 * (1.0 - self.trust)
        )
        self.negative_wom = clamp(base)
        return self.negative_wom

    def compute_churn_probability(self) -> float:
        if not self.active:
            self.last_churn_probability = 1.0
            return 1.0
        m = self.model
        z = (
            m.theta0
            + m.theta_trust * (1.0 - self.trust)
            + m.theta_harm * self.harm
            + m.theta_social * self.negative_wom
            - m.theta_switching_cost * self.switching_cost
        )
        p = 1.0 / (1.0 + math.exp(-z))
        self.last_churn_probability = clamp(p)
        return self.last_churn_probability

    def maybe_churn(self) -> None:
        if self.active and self.random.random() < self.compute_churn_probability():
            self.active = False

    def to_snapshot(self) -> dict:
        return {
            "id": self.unique_id,
            "trust": round(self.trust, 4),
            "perceived_fairness": round(self.perceived_fairness, 4),
            "harm": round(self.harm, 4),
            "negative_wom": round(self.negative_wom, 4),
            "active": self.active,
            "last_exposure": round(self.last_exposure, 4),
            "last_churn_probability": round(self.last_churn_probability, 4),
        }

    def step(self) -> None:
        pass


class PlatformAgent(mesa.Agent):
    def __init__(self, model, dark_pattern_intensity: float, customer_support_quality: float, adaptive_platform: bool):
        super().__init__(model)
        self.dark_pattern_intensity = clamp(dark_pattern_intensity)
        self.customer_support_quality = clamp(customer_support_quality)
        self.adaptive_platform = adaptive_platform
        self.reputation = 1.0
        self.short_term_revenue = 0.0
        self.long_term_revenue = 0.0

    def adapt_strategy(self) -> None:
        if not self.adaptive_platform:
            return
        if self.model.churn_rate > 0.08 or self.reputation < 0.45:
            self.dark_pattern_intensity = clamp(self.dark_pattern_intensity - 0.04)
            self.customer_support_quality = clamp(self.customer_support_quality + 0.03)
        elif self.model.churn_rate < 0.03 and self.reputation > 0.70:
            self.dark_pattern_intensity = clamp(self.dark_pattern_intensity + 0.01)
