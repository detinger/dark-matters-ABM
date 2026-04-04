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
      </div>
      <div className="network-card">
        <ForceGraph2D
          graphData={{ nodes: snapshot.nodes, links: snapshot.edges }}
          nodeId="nodeId"
          nodeLabel={(node: object) => {
            const typed = node as { id: number; nodeId: number; trust: number; harm: number; active: boolean }
            return `Agent ${typed.id} | node=${typed.nodeId} | trust=${typed.trust.toFixed(2)} | harm=${typed.harm.toFixed(2)} | active=${typed.active}`
          }}
          linkColor={() => 'rgba(100, 116, 139, 0.35)'}
          linkWidth={0.8}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const typed = node as unknown as { x: number; y: number; trust: number; active: boolean }
            const label = ''
            const fontSize = 8 / globalScale
            const radius = 4.5
            ctx.beginPath()
            ctx.arc(typed.x, typed.y, radius, 0, 2 * Math.PI, false)
            ctx.fillStyle = trustToColor(typed.trust, typed.active)
            ctx.fill()
            ctx.lineWidth = 1.1 / globalScale
            ctx.strokeStyle = 'rgba(248, 250, 252, 0.95)'
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
