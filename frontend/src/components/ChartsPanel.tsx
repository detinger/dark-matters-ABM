import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TippingPointState } from '../types'

type Props = {
  series: Array<Record<string, number>>
  tippingPoints: Record<string, TippingPointState>
}

const tippingPointColors: Record<string, string> = {
  trust_collapse: '#2563eb',
  social_contagion: '#059669',
  churn_cascade: '#dc2626',
  extractive_divergence: '#d97706',
}

function renderTippingLines(tippingPoints: Record<string, TippingPointState>) {
  return Object.entries(tippingPoints)
    .filter(([, point]) => point.triggered && point.step !== null)
    .map(([key, point]) => {
      const step = point.step as number
      return (
        <ReferenceLine
          key={key}
          x={step}
          stroke={tippingPointColors[key] ?? '#64748b'}
          strokeDasharray="6 4"
          strokeWidth={2}
          ifOverflow="extendDomain"
          label={{
            value: point.label,
            position: 'insideTopRight',
            fill: tippingPointColors[key] ?? '#64748b',
            fontSize: 11,
          }}
        />
      )
    })
}

export function ChartsPanel({ series, tippingPoints }: Props) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Simulation charts</h2>
        <p>Time series collected from Mesa DataCollector. Dashed vertical markers show triggered tipping points.</p>
      </div>
      <div className="chart-grid">
        <div className="chart-card">
          <h3>Trust and reputation</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={series}>
              <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 3" />
              <XAxis dataKey="step" stroke="var(--chart-axis)" tick={{ fill: 'var(--chart-axis)' }} />
              <YAxis domain={[0, 1]} stroke="var(--chart-axis)" tick={{ fill: 'var(--chart-axis)' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--chart-tooltip-bg)',
                  border: '1px solid var(--chart-tooltip-border)',
                  borderRadius: '12px',
                  color: 'var(--text-main)',
                }}
                labelStyle={{ color: 'var(--text-main)' }}
              />
              <Legend wrapperStyle={{ color: 'var(--text-main)' }} />
              {renderTippingLines(tippingPoints)}
              <Line type="monotone" dataKey="mean_trust" stroke="#2563eb" dot={false} />
              <Line type="monotone" dataKey="reputation" stroke="#9333ea" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Churn and negative WOM</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={series}>
              <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 3" />
              <XAxis dataKey="step" stroke="var(--chart-axis)" tick={{ fill: 'var(--chart-axis)' }} />
              <YAxis domain={[0, 1]} stroke="var(--chart-axis)" tick={{ fill: 'var(--chart-axis)' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--chart-tooltip-bg)',
                  border: '1px solid var(--chart-tooltip-border)',
                  borderRadius: '12px',
                  color: 'var(--text-main)',
                }}
                labelStyle={{ color: 'var(--text-main)' }}
              />
              <Legend wrapperStyle={{ color: 'var(--text-main)' }} />
              {renderTippingLines(tippingPoints)}
              <Line type="monotone" dataKey="churn_rate" stroke="#ef4444" dot={false} />
              <Line type="monotone" dataKey="cumulative_churn" stroke="#f97316" dot={false} />
              <Line type="monotone" dataKey="negative_wom_rate" stroke="#059669" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}
