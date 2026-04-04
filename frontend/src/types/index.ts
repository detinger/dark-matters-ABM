export type NetworkType = 'small_world' | 'scale_free' | 'random'

export interface SimulationCreateRequest {
  num_users: number
  network_type: NetworkType
  avg_degree: number
  rewire_prob: number
  max_steps: number
  seed?: number | null
  dark_pattern_intensity: number
  pattern_forced_trial: boolean
  pattern_hard_cancel: boolean
  pattern_drip_pricing: boolean
  customer_support_quality: number
  adaptive_platform: boolean
  social_influence_strength: number
  review_visibility: number
}

export interface Metrics {
  active_users: number
  mean_trust: number
  mean_harm: number
  churn_rate: number
  cumulative_churn: number
  reputation: number
  negative_wom_rate: number
  short_term_revenue: number
  long_term_revenue: number
}

export interface NetworkNode {
  nodeId: number | string
  id: number
  nodeType: 'user' | 'platform'
  label?: string
  trust: number
  perceived_fairness: number
  harm: number
  negative_wom: number
  active: boolean
  last_exposure: number
  last_churn_probability: number
  reputation?: number
  dark_pattern_intensity?: number
  customer_support_quality?: number
}

export interface NetworkEdge {
  source: number | string
  target: number | string
}

export interface NetworkSnapshot {
  nodes: NetworkNode[]
  edges: NetworkEdge[]
}

export interface PlatformState {
  dark_pattern_intensity: number
  customer_support_quality: number
  adaptive_platform: boolean
  reputation: number
  short_term_revenue: number
  long_term_revenue: number
}

export interface TippingPointState {
  label: string
  description: string
  triggered: boolean
  step: number | null
}

export interface SimulationState {
  simulation_id: string
  steps: number
  max_steps: number
  params: Record<string, unknown>
  metrics: Metrics
  network_snapshot: NetworkSnapshot
  platform: PlatformState
  tipping_points: Record<string, TippingPointState>
}

export interface SimulationSummary {
  simulation_id: string
  steps: number
  max_steps: number
  params: Record<string, unknown>
}

export interface TimeseriesResponse {
  simulation_id: string
  series: Array<Record<string, number>>
}
