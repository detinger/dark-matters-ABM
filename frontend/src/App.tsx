import './styles.css'
import { ChartsPanel } from './components/ChartsPanel'
import { ControlPanel } from './components/ControlPanel'
import { KpiCards } from './components/KpiCards'
import { NetworkGraphPanel } from './components/NetworkGraphPanel'
import { SimulationList } from './components/SimulationList'
import { useSimulation } from './hooks/useSimulation'

export default function App() {
  const {
    simulations,
    currentSimulationId,
    state,
    timeseries,
    loading,
    liveRunning,
    liveSpeed,
    error,
    derived,
    createSimulation,
    loadSimulation,
    stepSimulation,
    resetSimulation,
    setLiveSpeed,
    toggleLiveSimulation,
    exportSimulation,
    deleteSimulation,
  } = useSimulation()

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Mesa + FastAPI + React</p>
          <h1>Dark Patterns ABM Dashboard</h1>
          <p className="hero-copy">
            A starter dashboard for exploring long-term trust erosion under dark patterns with a Python Mesa backend.
          </p>
        </div>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <div className="layout-grid">
        <div className="sidebar">
          <ControlPanel
            onCreate={createSimulation}
            onStep={stepSimulation}
            onReset={resetSimulation}
            onToggleLive={toggleLiveSimulation}
            onExport={exportSimulation}
            onLiveSpeedChange={setLiveSpeed}
            disabled={loading}
            hasSimulation={derived.hasSimulation}
            liveRunning={liveRunning}
            liveSpeed={liveSpeed}
          />
          <SimulationList
            simulations={simulations}
            currentSimulationId={currentSimulationId}
            onSelect={loadSimulation}
            onDelete={deleteSimulation}
          />
        </div>

        <div className="content">
          {state ? (
            <>
              <KpiCards metrics={state.metrics} platform={state.platform} steps={state.steps} maxSteps={state.max_steps} />
              <ChartsPanel series={timeseries} />
              <NetworkGraphPanel snapshot={state.network_snapshot} />
            </>
          ) : (
            <section className="panel empty-state">
              <h2>No simulation loaded</h2>
              <p>Create a simulation from the left panel to begin.</p>
            </section>
          )}
        </div>
      </div>
    </main>
  )
}
