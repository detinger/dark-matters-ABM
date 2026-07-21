---
marp: true
theme: dpabm
paginate: true
size: 16:9
html: true
footer: '**Dark Patterns as a Value-Destroying Strategy** · Etinger & Pivac · Univ. of Pula'
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: '' -->

<div class="kicker">Agent-Based Modeling · Technology in Society</div>

# Dark Patterns as a<br/>Value-Destroying Strategy

## An Agent-Based Network Model of Trust, Social Contagion, and Platform Sustainability

<div class="authors"><strong>Darko Etinger</strong> &nbsp;·&nbsp; <strong>Dejana Pivac</strong></div>
<div class="affil">Faculty of Informatics, Juraj Dobrila University of Pula, Croatia</div>

---

## Agenda

1. **The problem** — dark patterns are everywhere, and they work
2. **The gap** — nobody has modeled the *long-run* systemic effect
3. **The model** — a network-based agent-based simulation
4. **The results** — six years of simulated trust erosion
5. **The takeaways** — tipping points, vulnerability, and policy

<div class="callout">
Central question: if dark patterns boost short-term conversions, do they actually pay off for a platform over years — or do they quietly destroy it?
</div>

---

<!-- _class: divider -->
<!-- _footer: '' -->

<div class="kicker">Part 1</div>

# The Problem

---

## Dark patterns are the norm, not the exception

<div class="stat-row">
<div class="stat-card alert">
<div class="num">1,818</div>
<div class="label">dark pattern instances found across 11,000 shopping sites (Mathur et al. 2019)</div>
</div>
<div class="stat-card alert">
<div class="num">~95%</div>
<div class="label">of 240 popular mobile apps contain at least one dark pattern (Di Geronimo et al. 2020)</div>
</div>
<div class="stat-card gold">
<div class="num">~2–4×</div>
<div class="label">increase in unwanted sign-ups from mild → aggressive dark patterns (Luguri &amp; Strahilevitz 2021)</div>
</div>
</div>

<p style="margin-top:0.9em;">Deceptive interfaces exploit framing effects, scarcity illusions, social proof, and anchoring — steering users into purchases, data disclosure, and subscriptions they would not otherwise choose.</p>

---

## The research gap

<div class="callout">
Existing research is <strong>predominantly static</strong>: cross-sectional detection and classification, or one-shot experiments measuring immediate response.
</div>

**What's missing:**
- How dark patterns interact with **social networks** over time
- How harm **accumulates** and **spreads** via word-of-mouth
- Whether "profitable" dark patterns are actually **sustainable**
- *At what intensity* systemic harm begins

No prior model couples a platform's strategic design choices, heterogeneous user behavior, **and** the resulting trust–economy feedback loop in one computational framework.

---

## This paper's contribution

<div class="columns">
<div>

**1. A network-based ABM**
Simulates 6 years of trust, harm, churn, word-of-mouth, reputation, and platform economics under dark-pattern deployment.

**2. Four formal tipping points**
Quantitative detectors for qualitative regime shifts in platform health.

</div>
<div>

**3. Systematic scenario analysis**
100 random seeds × 7 scenarios reveal a **non-linear, threshold-dependent** relationship between intensity and sustainability.

<div class="callout warn" style="margin-top:0.6em;">
Headline finding: <strong>no safe deployment level exists</strong> — even mild dark patterns cross regime boundaries.
</div>

</div>
</div>

---

<!-- _class: divider -->
<!-- _footer: '' -->

<div class="kicker">Part 2</div>

# The Model

---

## Model overview

<div class="columns">
<div>

- **500** heterogeneous user agents
- Connected via a **small-world social network** (Watts–Strogatz)
- **1** platform agent deploying up to 3 dark patterns
- **1 step = 1 week** → 312 steps ≈ **6 years**
- Built in **Mesa** (Python ABM framework)

</div>
<div>

**Each weekly step:**

<div class="flow" style="flex-direction:column; align-items:stretch;">
<div class="flow-box">Exposure → Detection → Harm</div>
<div class="flow-box">Negative word-of-mouth</div>
<div class="flow-box">Recovery (support + natural)</div>
<div class="flow-box">Churn decisions</div>
<div class="flow-box">Platform adapts, economics update</div>
</div>

</div>
</div>

---

## Three user archetypes

| Type | Share | Key traits |
|---|---|---|
| **Naive** | 50% | High baseline trust, low digital literacy, low manipulation sensitivity, **high switching cost**, elevated trust resilience |
| **Skeptic** | 30% | Moderate trust, high digital literacy, higher manipulation sensitivity, lower switching cost |
| **Activist** | 20% | Moderate trust, **highest** manipulation sensitivity, **lowest** switching cost, high social activity |

<div class="callout">
Traits are sampled from Beta(5,5) distributions scaled to type-specific ranges — bell-shaped variation around each type's midpoint, not a single universal distribution.
</div>

---

## Three dark patterns modeled

| Pattern | Models | Detectability | Base harm |
|---|---|---|---|
| **Forced Trial** | Forced conversions / upsells after a "free" trial | Moderate | Moderate |
| **Hard Cancellation** | Obstruction-based subscriber retention | **Highest** | Moderate |
| **Drip Pricing** | Hidden fees revealed late in checkout | Moderate | **Highest** |

<p>All three share a single global <strong>dark-pattern intensity</strong> dial (0–1). Trust loss and harm accumulate per exposure, with per-step caps and a 3-exposure "habituation" ramp so shocks build gradually rather than instantly.</p>

---

## Four formal tipping points

Each requires **5 consecutive steps** past threshold to trigger — filtering noise from genuine regime shifts.

| Tipping point | Trigger condition |
|---|---|
| **Trust Collapse** | Mean trust of active users ≤ 0.50 |
| **Social Contagion** | Negative word-of-mouth rate ≥ 0.22 |
| **Churn Cascade** | Cumulative churn ≥ 0.35 |
| **Extractive Divergence** | Revenue gap ≥ 20% of short-term revenue **and** churn ≥ 0.15 |

<div class="callout">These operationalize qualitative "platform health" shifts that are hard to observe empirically but emerge clearly in simulation.</div>

---

## Experimental setup

<div class="stat-row">
<div class="stat-card"><div class="num">500</div><div class="label">simulated users</div></div>
<div class="stat-card"><div class="num">312</div><div class="label">weekly steps (~6 years)</div></div>
<div class="stat-card"><div class="num">100</div><div class="label">random seeds per scenario</div></div>
<div class="stat-card"><div class="num">7</div><div class="label">scenarios compared</div></div>
</div>

**Scenarios:** Control (no dark patterns) · Low (0.20) · Medium (0.40) · High (0.80) — all three patterns active — plus three **single-pattern** scenarios at intensity 0.50 to isolate each pattern's individual effect.

<p class="source">All results regenerated end-to-end from an open replication package; unit-tested exposure–harm pipeline and tipping-point detectors.</p>

---

<!-- _class: divider -->
<!-- _footer: '' -->

<div class="kicker">Part 3</div>

# Results

---

## Outcomes across intensity levels

<div class="pill">Table 1 · 312 steps · N = 500 · 100 seeds · mean ± 95% CI</div>

| Metric | Control | Low (0.20) | Medium (0.40) | High (0.80) |
|---|---|---|---|---|
| Cumulative churn | 8.2 ± 0.2% | 17.6 ± 0.3% | 53.5 ± 0.5% | **88.0 ± 0.3%** |
| Mean trust (all) | 0.735 | 0.416 | 0.214 | **0.037** |
| Platform reputation | 74.3 | 46.8 | 18.4 | **2.0 (floor)** |
| Cumulative revenue | 654,255 | 624,184 | 452,232 | 281,916 |
| Opportunity cost | 29,079 | 59,151 | 231,103 | 401,419 |
| Tipping points (of 4) | 0.00 | 1.95 | **4.00** | **4.00** |

<div class="callout warn">Even <strong>low</strong> intensity (0.20) crosses Trust Collapse and Extractive Divergence — while revenue looks almost untouched.</div>

---

<!-- _class: figure -->

## Trust collapses well before revenue visibly suffers

![w:820](images/fig_trust_by_intensity.png)

<p class="fig-cap">Mean trust (all users) over time by dark-pattern intensity; shaded bands = 95% CI across 100 seeds.</p>

---

<!-- _class: figure -->

## Churn accelerates sharply with intensity

![w:820](images/fig_churn_by_intensity.png)

<p class="fig-cap">Cumulative churn over time by dark-pattern intensity (mean ± 95% CI).</p>

---

## Who leaves — and who stays trapped

<div class="pill teal">Table 2 · Churn by user type · 100 seeds</div>

| User type | Control | Low (0.20) | Medium (0.40) | High (0.80) |
|---|---|---|---|---|
| **Skeptic** (N=150) | 10 ± 1% | 24 ± 1% | **75 ± 1%** | 100% |
| **Naive** (N=250) | 7 ± 0% | 11 ± 0% | **29 ± 1%** | 76 ± 1% |
| **Activist** (N=100) | 9 ± 1% | 25 ± 1% | **84 ± 1%** | 100% |

<div class="callout warn">
Skeptics and activists exit fast. <strong>Naive users stay</strong> — high switching costs trap them on a deteriorating platform even as trust collapses around them.
</div>

---

<!-- _class: figure -->

## Churn by user type and intensity

![w:760](images/fig_churn_by_type.png)

<p class="fig-cap">Percent of each user type churned, by scenario (mean ± 95% CI).</p>

---

## Not all dark patterns are equally harmful

<div class="pill red">Table 3 · Single-pattern impact at intensity 0.50 · 100 seeds</div>

| Metric | Forced Trial | Drip Pricing | Hard Cancel |
|---|---|---|---|
| Cumulative churn | **43.5%** | 42.5% | 37.2% |
| Mean trust (all) | 0.171 | 0.176 | 0.174 |
| Tipping points (of 4) | **3.86** | 3.38 | 2.79 |

<div class="callout">
<strong>Counter-intuitive finding:</strong> Hard Cancellation is the most obstructive pattern but the <em>least</em> damaging overall — because it's the easiest to detect. Users notice fast and leave before harm accumulates. <strong>Higher detectability shortens the exposure window and limits systemic harm.</strong>
</div>

---

<!-- _class: figure -->

## Per-pattern churn and residual trust

![w:760](images/fig_per_pattern.png)

<p class="fig-cap">Single-pattern impact at intensity 0.50: cumulative churn and residual trust (mean ± 95% CI).</p>

---

<!-- _class: figure -->

## Revenue: early extraction, long-run losses

![w:820](images/fig_revenue_by_intensity.png)

<p class="fig-cap">Cumulative revenue over time by dark-pattern intensity (mean ± 95% CI). Dark-pattern extraction front-loads revenue; falling reputation and churn erode it over the long run.</p>

---

## Sensitivity analysis: what actually drives the outcome?

<div class="pill gold">Table 4 · Morris elementary-effects screening · 360 model runs</div>

| Parameter | μ\* churn | μ\* trust |
|---|---|---|
| **γ — dark pattern intensity** | **0.701** | **0.656** |
| θ_T — churn trust weight | 0.217 | 0.071 |
| δ — exposure-to-harm coeff. | 0.172 | 0.076 |
| q — support quality | 0.111 | 0.195 |
| θ_H — churn harm weight | 0.084 | 0.027 |
| κ — social influence | 0.037 | 0.038 |
| α — exposure-to-trust coeff. | 0.012 | 0.004 |

<div class="callout">Intensity's effect is <strong>3.2–3.4× larger</strong> than any other parameter — and every signed effect points the expected direction across all 7 parameters tested simultaneously.</div>

---

<!-- _class: figure -->

## Robust across simultaneous parameter perturbation

![w:700](images/fig_morris.png)

<p class="fig-cap">μ* vs. σ for cumulative churn (circles) and mean trust (squares). Points far right = most influential; above the diagonal = interaction-dominated.</p>

---

<!-- _class: divider -->
<!-- _footer: '' -->

<div class="kicker">Part 4</div>

# Discussion

---

## The self-reinforcing destruction loop

<div class="flow">
<div class="flow-box">Dark Pattern Intensity</div>
<div class="flow-arrow">→</div>
<div class="flow-box">Exposure</div>
<div class="flow-arrow">→</div>
<div class="flow-box">Harm</div>
<div class="flow-arrow">→</div>
<div class="flow-box">Trust Erosion</div>
</div>
<div style="text-align:right; padding-right:6%; font-size:0.55em; color:var(--red); font-weight:800;">↓ social contagion feedback ↓</div>
<div class="flow">
<div class="flow-box">Revenue Loss</div>
<div class="flow-arrow">←</div>
<div class="flow-box">Reputation</div>
<div class="flow-arrow">←</div>
<div class="flow-box">Churn</div>
<div class="flow-arrow">←</div>
<div class="flow-box loop">Negative WOM</div>
</div>

<div class="callout warn" style="margin-top:0.7em;">
Negative WOM feeds back and erodes trust even among <strong>unexposed</strong> users (dashed loop) — accelerating every downstream stage. A strategy that looks profitable early destroys more value than it captures over the long run.
</div>

---

## Heterogeneous vulnerability and lock-in

<div class="columns">
<div>

**Who is harmed most is not who leaves.**

- Naive users accumulate the **most cumulative harm** — precisely because high switching costs trap them
- Activists churn fastest but **amplify harm via WOM** before exiting
- As savvy users leave, aggregate complaint volume can **fall** — even as remaining users suffer more

</div>
<div>

<div class="callout">
A regulator watching aggregate complaint rates or reputation scores could see an <strong>apparent improvement</strong> at the exact moment the most vulnerable users are experiencing the worst conditions.
</div>

<div class="callout warn">
Vulnerability here is <strong>situational</strong>, not demographic — invisible to standard protected-group frameworks.
</div>

</div>
</div>

---

## Policy implications

**1. Regulate intensity, not just presence.**
Non-linear, threshold-dependent harm favors graduated limits (like emission caps) over binary bans — intensity monitoring over incident-by-incident adjudication.

**2. Treat dark patterns as a public harm.**
Negative WOM damages users never directly exposed — an externality that individual-consent/redress frameworks aren't built to address.

**3. Mandate Extractive Divergence disclosure.**
A platform-economics metric platforms already track internally — a candidate "leverage ratio" for systemic-risk monitoring, ahead of reputational collapse.

---

## Limitations

- Parameters are **literature-informed, not empirically fitted** — results are directional/qualitative, not point forecasts
- **Single platform, no competition** — a deliberate scoping choice; likely a **conservative lower bound** on real-world churn
- Does **not model** regulatory intervention, media coverage, or legal consequences
- **Static network structure** across the simulation horizon

<div class="callout">Claims are conditional: they describe what follows <em>given</em> the modeled mechanisms — the robust part is the direction, ordering, and relative magnitude of effects, confirmed under Morris screening and alternate network topologies.</div>

---

## Conclusion

<div class="callout warn">
<strong>No safe deployment level exists within the modeled regime.</strong> Even low-intensity dark patterns cross qualitative regime boundaries and inflict persistent trust damage that is nearly invisible on a revenue dashboard.
</div>

- Harm is not contained to individual moments of manipulation — it **propagates through social networks** and **destabilizes platform economics**
- Trust Collapse triggers first and consistently → candidate **early-warning indicator**
- Extractive Divergence grounds regulatory monitoring in **economics platforms already track**

**Future work:** empirical calibration · multi-platform competition · adaptive regulatory dynamics (media, penalties)

---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _footer: '' -->

# Thank you

## Questions & discussion

<div class="authors">
Darko Etinger · darko.etinger@unipu.hr<br/>
Dejana Pivac · dpivac@unipu.hr
</div>
<div class="affil">
Faculty of Informatics, Juraj Dobrila University of Pula, Croatia<br/>
Code, data & replication package: github.com/detinger/dark-patterns-ABM
</div>
