import type {
  SimulationCreateRequest,
  SimulationState,
  SimulationSummary,
  TimeseriesResponse,
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
    ...options,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed with ${response.status}`)
  }

  return response.json() as Promise<T>
}

async function download(path: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}${path}`)

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed with ${response.status}`)
  }

  return response.blob()
}

export const api = {
  listSimulations: () => request<SimulationSummary[]>('/simulations'),
  createSimulation: (payload: SimulationCreateRequest) =>
    request<SimulationSummary>('/simulations', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getSimulation: (simulationId: string) => request<SimulationState>(`/simulations/${simulationId}`),
  stepSimulation: (simulationId: string, count: number) =>
    request<SimulationState>(`/simulations/${simulationId}/step`, {
      method: 'POST',
      body: JSON.stringify({ count }),
    }),
  resetSimulation: (simulationId: string) =>
    request<SimulationState>(`/simulations/${simulationId}/reset`, {
      method: 'POST',
    }),
  getTimeseries: (simulationId: string) =>
    request<TimeseriesResponse>(`/simulations/${simulationId}/timeseries`),
  downloadSimulationCsv: (simulationId: string) =>
    download(`/simulations/${simulationId}/export.csv`),
  deleteSimulation: (simulationId: string) =>
    request<{ message: string }>(`/simulations/${simulationId}`, {
      method: 'DELETE',
    }),
}
