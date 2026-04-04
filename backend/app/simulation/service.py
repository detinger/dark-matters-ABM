from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.simulation.config import DEFAULTS
from app.simulation.model import DarkPatternTrustModel


@dataclass
class SimulationSession:
    simulation_id: str
    model: DarkPatternTrustModel
    params: dict[str, Any] = field(default_factory=dict)


class SimulationService:
    def __init__(self):
        self.sessions: dict[str, SimulationSession] = {}

    def _build_model_at_step(self, params: dict[str, Any], steps: int) -> DarkPatternTrustModel:
        model = DarkPatternTrustModel(**params)
        for _ in range(max(0, steps)):
            if model.steps >= model.max_steps:
                break
            model.step()
        return model

    def create(self, overrides: dict[str, Any] | None = None) -> SimulationSession:
        params = {**DEFAULTS, **(overrides or {})}
        simulation_id = str(uuid4())
        model = self._build_model_at_step(params, 0)
        session = SimulationSession(simulation_id=simulation_id, model=model, params=params)
        self.sessions[simulation_id] = session
        return session

    def list_simulations(self) -> list[dict[str, Any]]:
        output = []
        for sim_id, session in self.sessions.items():
            output.append({
                "simulation_id": sim_id,
                "steps": session.model.steps,
                "max_steps": session.model.max_steps,
                "params": session.params,
            })
        return output

    def get(self, simulation_id: str) -> SimulationSession:
        if simulation_id not in self.sessions:
            raise KeyError(f"Simulation '{simulation_id}' not found")
        return self.sessions[simulation_id]

    def delete(self, simulation_id: str) -> None:
        if simulation_id not in self.sessions:
            raise KeyError(f"Simulation '{simulation_id}' not found")
        del self.sessions[simulation_id]

    def step(self, simulation_id: str, count: int = 1) -> SimulationSession:
        session = self.get(simulation_id)
        if count >= 0:
            for _ in range(count):
                if session.model.steps >= session.model.max_steps:
                    break
                session.model.step()
            return session

        target_step = max(0, session.model.steps + count)
        session.model = self._build_model_at_step(session.params, target_step)
        return session

    def reset(self, simulation_id: str) -> SimulationSession:
        session = self.get(simulation_id)
        session.model = self._build_model_at_step(session.params, 0)
        return session


simulation_service = SimulationService()
