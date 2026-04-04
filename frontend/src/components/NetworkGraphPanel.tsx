import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { NetworkSnapshot, RecentEventsState } from '../types'

type Props = {
  simulationId: string
  steps: number
  snapshot: NetworkSnapshot
  recentEvents: RecentEventsState
}

type GraphNode = NetworkSnapshot['nodes'][number] & {
  x?: number
  y?: number
  vx?: number
  vy?: number
  fx?: number
  fy?: number
}

type GraphLink = NetworkSnapshot['edges'][number] & {
  eventType?: 'platform_exposure' | 'social_signal'
  eventIntensity?: number
  particleCount?: number
}

function hashToUnitInterval(value: string) {
  let hash = 2166136261
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }
  return ((hash >>> 0) % 1000000) / 1000000
}

function getStableRandomPosition(key: string, radiusLimit: number) {
  const angle = hashToUnitInterval(`${key}:angle`) * Math.PI * 2
  const radiusFactor = Math.sqrt(hashToUnitInterval(`${key}:radius`))
  const radius = 32 + radiusFactor * radiusLimit

  return {
    x: Math.cos(angle) * radius,
    y: Math.sin(angle) * radius,
  }
}

function trustToColor(trust: number, active: boolean) {
  if (!active) return '#475569'
  if (trust > 0.85) return '#16a34a'
  if (trust > 0.65) return '#0ea5e9'
  if (trust > 0.45) return '#7c3aed'
  if (trust > 0.25) return '#f97316'
  return '#dc2626'
}

export function NetworkGraphPanel({ simulationId, steps, snapshot, recentEvents }: Props) {
  const [graphInstanceKey, setGraphInstanceKey] = useState(0)
  const [graphSize, setGraphSize] = useState({ width: 720, height: 720 })
  const graphRef = useRef<any>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const pendingViewportFitRef = useRef(true)
  const fixedNodePositionsRef = useRef<Map<string, { x: number; y: number }> | null>(null)
  const previousGraphRef = useRef<{ nodes: GraphNode[] } | null>(null)
  const previousSimulationIdRef = useRef(simulationId)
  const previousStepsRef = useRef(steps)
  const smoothAnimationEnabled = true

  useEffect(() => {
    const element = containerRef.current
    if (!element) return

    const updateSize = () => {
      const nextWidth = Math.max(320, Math.round(element.clientWidth))
      const nextHeight = Math.max(320, Math.round(element.clientHeight || element.clientWidth))
      pendingViewportFitRef.current = true
      setGraphSize((current) =>
        current.width === nextWidth && current.height === nextHeight
          ? current
          : { width: nextWidth, height: nextHeight },
      )
    }

    updateSize()
    const observer = new ResizeObserver(updateSize)
    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [])

  useEffect(() => {
    const simulationChanged = previousSimulationIdRef.current !== simulationId
    const resetDetected = previousStepsRef.current > 0 && steps === 0

    if (simulationChanged || resetDetected) {
      previousGraphRef.current = null
      fixedNodePositionsRef.current = null
      pendingViewportFitRef.current = true
      setGraphInstanceKey((current) => current + 1)
    }

    previousSimulationIdRef.current = simulationId
    previousStepsRef.current = steps
  }, [simulationId, steps])

  const fitViewport = () => {
    graphRef.current?.zoomToFit?.(
      350,
      Math.max(48, Math.round(Math.min(graphSize.width, graphSize.height) * 0.08)),
    )
    pendingViewportFitRef.current = false
  }

  useEffect(() => {
    if (!pendingViewportFitRef.current) {
      return
    }

    const timeoutId = window.setTimeout(() => {
      fitViewport()
    }, 180)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [graphInstanceKey, graphSize.height, graphSize.width, smoothAnimationEnabled])

  const graphData = useMemo(() => {
    const previousNodeMap = new Map<string, GraphNode>()
    if (previousGraphRef.current) {
      for (const node of previousGraphRef.current.nodes) {
        previousNodeMap.set(String(node.nodeId), node)
      }
    }

    const highlightedExposureTargets = new Set(recentEvents.direct_exposures.map(String))
    const highlightedSocialEdges = recentEvents.social_edges.slice(0, 260)
    const highlightedSocialEdgeMap = new Map<string, number>()
    for (const edge of highlightedSocialEdges) {
      highlightedSocialEdgeMap.set(`${edge.source}->${edge.target}`, edge.intensity)
      highlightedSocialEdgeMap.set(`${edge.target}->${edge.source}`, edge.intensity)
    }

    const totalUsers = snapshot.nodes.filter((node) => node.nodeType === 'user').length
    const radiusLimit = Math.max(80, Math.min(graphSize.width, graphSize.height) * 0.42)
    let fixedNodePositions = fixedNodePositionsRef.current
    if (!fixedNodePositions) {
      fixedNodePositions = new Map<string, { x: number; y: number }>()
      for (const node of snapshot.nodes) {
        if (node.nodeType !== 'user') {
          continue
        }
        const position = getStableRandomPosition(`${simulationId}:${node.nodeId}`, radiusLimit)
        fixedNodePositions.set(String(node.nodeId), position)
      }
      fixedNodePositionsRef.current = fixedNodePositions
    }
    let userIndex = 0
    const nodes: GraphNode[] = snapshot.nodes.map((node) => {
      const previousNode = previousNodeMap.get(String(node.nodeId))
      if (node.nodeType === 'platform') {
        return {
          ...node,
          x: 0,
          y: 0,
          fx: 0,
          fy: 0,
          vx: 0,
          vy: 0,
        }
      }
      const centeredPosition = getStableRandomPosition(`${simulationId}:${node.nodeId}`, radiusLimit)
      const fixedPosition = fixedNodePositions?.get(String(node.nodeId))
      userIndex += 1
      if (smoothAnimationEnabled && fixedPosition) {
        return {
          ...node,
          x: fixedPosition.x,
          y: fixedPosition.y,
          fx: fixedPosition.x,
          fy: fixedPosition.y,
          vx: 0,
          vy: 0,
        }
      }
      if (!smoothAnimationEnabled || !previousNode) {
        return {
          ...node,
          x: centeredPosition.x,
          y: centeredPosition.y,
        }
      }
      return {
        ...node,
        x: previousNode.x,
        y: previousNode.y,
        vx: previousNode.vx,
        vy: previousNode.vy,
        fx: previousNode.fx,
        fy: previousNode.fy,
      }
    })

    const links: GraphLink[] = snapshot.edges.map((edge) => {
      if (edge.source === 'platform' && highlightedExposureTargets.has(String(edge.target))) {
        return {
          ...edge,
          eventType: 'platform_exposure',
          eventIntensity: 1,
          particleCount: 3,
        }
      }

      const socialIntensity = highlightedSocialEdgeMap.get(`${edge.source}->${edge.target}`)
      if (socialIntensity !== undefined) {
        return {
          ...edge,
          eventType: 'social_signal',
          eventIntensity: socialIntensity,
          particleCount: 2,
        }
      }

      return { ...edge, particleCount: 0 }
    })

    const nextGraph = { nodes, links }
    previousGraphRef.current = nextGraph
    return nextGraph
  }, [graphSize.height, graphSize.width, recentEvents, smoothAnimationEnabled, snapshot])

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
      <div className="network-card" ref={containerRef}>
        <ForceGraph2D
          key={`${simulationId}-${graphInstanceKey}`}
          ref={graphRef}
          graphData={graphData}
          width={graphSize.width}
          height={graphSize.height}
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
          linkColor={(link) => {
            const typed = link as GraphLink
            if (typed.eventType === 'platform_exposure') return 'rgba(250, 204, 21, 0.65)'
            if (typed.eventType === 'social_signal') return 'rgba(14, 165, 233, 0.7)'
            return 'rgba(100, 116, 139, 0.35)'
          }}
          linkWidth={(link) => {
            const typed = link as GraphLink
            if (typed.eventType === 'platform_exposure') return 1.8
            if (typed.eventType === 'social_signal') return 1.3
            return 0.8
          }}
          linkDirectionalParticles={(link) => {
            const typed = link as GraphLink
            return smoothAnimationEnabled ? typed.particleCount ?? 0 : 0
          }}
          linkDirectionalParticleColor={(link) => {
            const typed = link as GraphLink
            if (typed.eventType === 'platform_exposure') return '#fde68a'
            if (typed.eventType === 'social_signal') return '#7dd3fc'
            return '#94a3b8'
          }}
          linkDirectionalParticleWidth={(link) => {
            const typed = link as GraphLink
            if (typed.eventType === 'platform_exposure') return 2.6
            if (typed.eventType === 'social_signal') return 2
            return 0
          }}
          linkDirectionalParticleSpeed={(link) => {
            const typed = link as GraphLink
            if (typed.eventType === 'platform_exposure') return 0.01
            if (typed.eventType === 'social_signal') return 0.008 + (typed.eventIntensity ?? 0) * 0.03
            return 0
          }}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const typed = node as unknown as {
              x: number
              y: number
              trust: number
              active: boolean
              nodeType: 'user' | 'platform'
              nodeId: number | string
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
            if (recentEvents.churned_nodes.includes(Number(typed.nodeId))) {
              ctx.beginPath()
              ctx.arc(typed.x, typed.y, radius + 2.8, 0, 2 * Math.PI, false)
              ctx.strokeStyle = 'rgba(248, 113, 113, 0.85)'
              ctx.lineWidth = 1.4 / globalScale
              ctx.stroke()
            }
            ctx.font = `${fontSize}px Sans-Serif`
            ctx.fillStyle = '#111827'
            ctx.fillText(label, typed.x + 6, typed.y + 6)
          }}
          nodeRelSize={4}
          warmupTicks={smoothAnimationEnabled ? 0 : 0}
          cooldownTicks={smoothAnimationEnabled ? 0 : 80}
          onEngineStop={() => {
            if (pendingViewportFitRef.current) {
              fitViewport()
            }
          }}
        />
      </div>
    </section>
  )
}
