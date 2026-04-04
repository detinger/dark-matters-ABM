import type { TippingPointState } from '../types'

type Props = {
  tippingPoints: Record<string, TippingPointState>
}

export function TippingPointsPanel({ tippingPoints }: Props) {
  const items = Object.entries(tippingPoints)

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Tipping Points</h2>
        <p>Formalized threshold detection for persistent trust, contagion, churn, and revenue divergence shifts.</p>
      </div>
      <div className="tipping-grid">
        {items.map(([key, point]) => (
          <article className={`tipping-card ${point.triggered ? 'triggered' : ''}`} key={key}>
            <div className="tipping-card-header">
              <strong>{point.label}</strong>
              <span className={`tipping-badge ${point.triggered ? 'on' : 'off'}`}>
                {point.triggered ? `Triggered at step ${point.step}` : 'Not triggered'}
              </span>
            </div>
            <p>{point.description}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
