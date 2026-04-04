import type { Metrics, PlatformState } from '../types'

type Props = {
  metrics: Metrics
  platform: PlatformState
  steps: number
  maxSteps: number
}

const format = (value: number) => value.toFixed(3)

export function KpiCards({ metrics, platform, steps, maxSteps }: Props) {
  const items = [
    ['Step', `${steps} / ${maxSteps}`],
    ['Mean trust', format(metrics.mean_trust)],
    ['Mean harm', format(metrics.mean_harm)],
    ['Weekly churn', format(metrics.churn_rate)],
    ['Cumulative churn', format(metrics.cumulative_churn)],
    ['Negative WOM', format(metrics.negative_wom_rate)],
    ['Reputation', format(platform.reputation)],
    ['Short-term revenue', format(platform.short_term_revenue)],
    ['Long-term revenue', format(platform.long_term_revenue)],
  ]

  return (
    <section className="kpi-grid">
      {items.map(([label, value]) => (
        <article className="kpi-card" key={label}>
          <span className="kpi-label">{label}</span>
          <strong className="kpi-value">{value}</strong>
        </article>
      ))}
    </section>
  )
}
