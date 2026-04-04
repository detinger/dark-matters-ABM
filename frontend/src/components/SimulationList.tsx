import type { SimulationSummary } from '../types'

type Props = {
  simulations: SimulationSummary[]
  currentSimulationId: string | null
  onSelect: (simulationId: string) => Promise<void>
  onDelete: (simulationId: string) => Promise<void>
}

export function SimulationList({ simulations, currentSimulationId, onSelect, onDelete }: Props) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Saved sessions</h2>
        <p>In-memory backend sessions available in the current API process.</p>
      </div>
      <div className="simulation-list">
        {simulations.length === 0 ? (
          <p className="muted">No sessions yet.</p>
        ) : (
          simulations.map((simulation) => (
            <article className={`simulation-item ${simulation.simulation_id === currentSimulationId ? 'active' : ''}`} key={simulation.simulation_id}>
              <div>
                <strong>{simulation.simulation_id.slice(0, 8)}</strong>
                <p>Steps: {simulation.steps} / {simulation.max_steps}</p>
              </div>
              <div className="button-row compact">
                <button onClick={() => onSelect(simulation.simulation_id)}>Load</button>
                <button className="secondary" onClick={() => onDelete(simulation.simulation_id)}>Delete</button>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  )
}
