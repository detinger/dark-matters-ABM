import ForceGraph2D from 'react-force-graph-2d'
import type { NetworkSnapshot } from '../types'

type Props = {
  snapshot: NetworkSnapshot
}

function trustToColor(trust: number, active: boolean) {
  if (!active) return '#475569'
  if (trust > 0.85) return '#16a34a'
  if (trust > 0.65) return '#0ea5e9'
  if (trust > 0.45) return '#7c3aed'
  if (trust > 0.25) return '#f97316'
  return '#dc2626'
}

export function NetworkGraphPanel({ snapshot }: Props) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Network snapshot</h2>
        <p>Full user graph for the active simulation. Node color reflects trust and active status.</p>
        <div className="network-legend">
          <span className="legend-item"><span className="legend-dot platform" /> Platform</span>
          <span className="legend-item"><span className="legend-dot trust-high" /> Very high trust</span>
          <span className="legend-item"><span className="legend-dot trust-good" /> High trust</span>
          <span className="legend-item"><span className="legend-dot trust-mid" /> Mid trust</span>
          <span className="legend-item"><span className="legend-dot trust-low" /> Lower trust</span>
          <span className="legend-item"><span className="legend-dot trust-critical" /> Low trust</span>
          <span className="legend-item"><span className="legend-dot inactive" /> Inactive user</span>
        </div>
      </div>
      <div className="network-card">
        <ForceGraph2D
          graphData={{ nodes: snapshot.nodes, links: snapshot.edges }}
          nodeId="nodeId"
          nodeLabel={(node: object) => {
            const typed = node as {
              id: number
              nodeId: number | string
              nodeType: 'user' | 'platform'
              label?: string
              trust: number
              harm: number
              active: boolean
              reputation?: number
              dark_pattern_intensity?: number
            }
            if (typed.nodeType === 'platform') {
              return `${typed.label ?? 'Platform'} | reputation=${typed.reputation?.toFixed(2) ?? typed.trust.toFixed(2)} | intensity=${typed.dark_pattern_intensity?.toFixed(2) ?? 0}`
            }
            return `Agent ${typed.id} | node=${typed.nodeId} | trust=${typed.trust.toFixed(2)} | harm=${typed.harm.toFixed(2)} | active=${typed.active}`
          }}
          linkColor={() => 'rgba(100, 116, 139, 0.35)'}
          linkWidth={0.8}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const typed = node as unknown as {
              x: number
              y: number
              trust: number
              active: boolean
              nodeType: 'user' | 'platform'
            }
            const label = ''
            const fontSize = 8 / globalScale
            const radius = typed.nodeType === 'platform' ? 7.5 : 4.5
            ctx.beginPath()
            ctx.arc(typed.x, typed.y, radius, 0, 2 * Math.PI, false)
            ctx.fillStyle = typed.nodeType === 'platform' ? '#facc15' : trustToColor(typed.trust, typed.active)
            ctx.fill()
            ctx.lineWidth = typed.nodeType === 'platform' ? 1.6 / globalScale : 1.1 / globalScale
            ctx.strokeStyle = typed.nodeType === 'platform' ? 'rgba(120, 53, 15, 0.95)' : 'rgba(248, 250, 252, 0.95)'
            ctx.stroke()
            ctx.font = `${fontSize}px Sans-Serif`
            ctx.fillStyle = '#111827'
            ctx.fillText(label, typed.x + 6, typed.y + 6)
          }}
          nodeRelSize={4}
          cooldownTicks={80}
        />
      </div>
    </section>
  )
}
