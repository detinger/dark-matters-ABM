import { useState } from 'react'
import type { SimulationCreateRequest } from '../types'
import { defaultCreatePayload } from '../hooks/useSimulation'

type Props = {
  onCreate: (payload: SimulationCreateRequest) => Promise<void>
  onStep: (count: number) => Promise<void>
  onReset: () => Promise<void>
  onToggleLive: () => Promise<void>
  onExport: () => Promise<void>
  onLiveSpeedChange: (value: number) => void
  disabled?: boolean
  hasSimulation: boolean
  liveRunning: boolean
  liveSpeed: number
}

export function ControlPanel({
  onCreate,
  onStep,
  onReset,
  onToggleLive,
  onExport,
  onLiveSpeedChange,
  disabled,
  hasSimulation,
  liveRunning,
  liveSpeed,
}: Props) {
  const [form, setForm] = useState<SimulationCreateRequest>(defaultCreatePayload)

  const updateField = <K extends keyof SimulationCreateRequest>(key: K, value: SimulationCreateRequest[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Create simulation</h2>
        <p>Configure Mesa parameters and create a new backend session.</p>
      </div>

      <div className="grid grid-2 control-group">
        <label>
          Users
          <input type="number" value={form.num_users} min={50} max={5000} onChange={(e) => updateField('num_users', Number(e.target.value))} />
        </label>
        <label>
          Max steps
          <input type="number" value={form.max_steps} min={1} max={500} onChange={(e) => updateField('max_steps', Number(e.target.value))} />
        </label>
        <label>
          Network type
          <select value={form.network_type} onChange={(e) => updateField('network_type', e.target.value as SimulationCreateRequest['network_type'])}>
            <option value="small_world">Small-world</option>
            <option value="scale_free">Scale-free</option>
            <option value="random">Random</option>
          </select>
        </label>
        <label>
          Avg degree
          <input type="number" value={form.avg_degree} min={2} max={50} onChange={(e) => updateField('avg_degree', Number(e.target.value))} />
        </label>
      </div>

      <div className="grid grid-2 control-group">
        <label>
          Dark pattern intensity
          <input type="range" min={0} max={1} step={0.01} value={form.dark_pattern_intensity} onChange={(e) => updateField('dark_pattern_intensity', Number(e.target.value))} />
          <span>{form.dark_pattern_intensity.toFixed(2)}</span>
        </label>
        <label>
          Customer support quality
          <input type="range" min={0} max={1} step={0.01} value={form.customer_support_quality} onChange={(e) => updateField('customer_support_quality', Number(e.target.value))} />
          <span>{form.customer_support_quality.toFixed(2)}</span>
        </label>
        <label>
          Social influence strength
          <input type="range" min={0} max={1} step={0.01} value={form.social_influence_strength} onChange={(e) => updateField('social_influence_strength', Number(e.target.value))} />
          <span>{form.social_influence_strength.toFixed(2)}</span>
        </label>
        <label>
          Review visibility
          <input type="range" min={0} max={1} step={0.01} value={form.review_visibility} onChange={(e) => updateField('review_visibility', Number(e.target.value))} />
          <span>{form.review_visibility.toFixed(2)}</span>
        </label>
      </div>

      <div className="grid grid-3 checkboxes control-group">
        <label><input type="checkbox" checked={form.pattern_forced_trial} onChange={(e) => updateField('pattern_forced_trial', e.target.checked)} /> Forced trial</label>
        <label><input type="checkbox" checked={form.pattern_hard_cancel} onChange={(e) => updateField('pattern_hard_cancel', e.target.checked)} /> Hard cancel</label>
        <label><input type="checkbox" checked={form.pattern_drip_pricing} onChange={(e) => updateField('pattern_drip_pricing', e.target.checked)} /> Drip pricing</label>
        <label><input type="checkbox" checked={form.adaptive_platform} onChange={(e) => updateField('adaptive_platform', e.target.checked)} /> Adaptive platform</label>
      </div>

      <div className="button-row">
        <button disabled={disabled || liveRunning} onClick={() => onCreate(form)}>Create simulation</button>
        <button disabled={disabled || liveRunning || !hasSimulation} onClick={() => onStep(-1)}>Step -1</button>
        <button disabled={disabled || liveRunning || !hasSimulation} onClick={() => onStep(1)}>Step +1</button>
        <button disabled={disabled || liveRunning || !hasSimulation} onClick={() => onStep(-10)}>Run -10</button>
        <button disabled={disabled || liveRunning || !hasSimulation} onClick={() => onStep(10)}>Run +10</button>
        <button disabled={disabled || liveRunning || !hasSimulation} onClick={onReset}>Reset</button>
        <button disabled={liveRunning ? false : disabled || !hasSimulation} onClick={onToggleLive}>
          {liveRunning ? 'Stop Live' : 'Run Live'}
        </button>
        <button className="secondary" disabled={disabled || liveRunning || !hasSimulation} onClick={onExport}>Export CSV</button>
      </div>

      <div className="control-group live-speed-control">
        <label>
          Live speed
          <input
            type="range"
            min={1}
            max={10}
            step={1}
            value={liveSpeed}
            onChange={(e) => onLiveSpeedChange(Number(e.target.value))}
          />
          <div className="range-meta">
            <span>Slower</span>
            <strong>{liveSpeed}/10</strong>
            <span>Faster</span>
          </div>
        </label>
      </div>
    </section>
  )
}
