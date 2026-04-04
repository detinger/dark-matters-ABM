import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

type Props = {
  series: Array<Record<string, number>>
}

export function ChartsPanel({ series }: Props) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Simulation charts</h2>
        <p>Time series collected from Mesa DataCollector.</p>
      </div>
      <div className="chart-grid">
        <div className="chart-card">
          <h3>Trust and reputation</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={series}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="step" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="mean_trust" stroke="#2563eb" dot={false} />
              <Line type="monotone" dataKey="reputation" stroke="#9333ea" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Churn and negative WOM</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={series}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="step" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Legend />
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
