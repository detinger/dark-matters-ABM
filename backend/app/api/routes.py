from __future__ import annotations

import asyncio
import csv
from io import StringIO

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from app.schemas.simulation import (
    SimulationCreateRequest,
    StepRequest,
    SimulationSummary,
    SimulationStateResponse,
    SimulationTimeseriesResponse,
    ApiMessage,
    HealthResponse,
)
from app.simulation.service import simulation_service

router = APIRouter()


def _serialize_simulation_summary(session, simulation_id: str) -> dict:
    return {
        "simulation_id": simulation_id,
        "steps": session.model.steps,
        "max_steps": session.model.max_steps,
        "params": session.params,
    }


def _serialize_simulation_state(session, simulation_id: str) -> dict:
    return {
        "simulation_id": simulation_id,
        "steps": session.model.steps,
        "max_steps": session.model.max_steps,
        "params": session.params,
        "metrics": session.model.get_latest_metrics(),
        "network_snapshot": session.model.get_network_snapshot(),
        "platform": {
            "dark_pattern_intensity": session.model.platform.dark_pattern_intensity,
            "customer_support_quality": session.model.platform.customer_support_quality,
            "adaptive_platform": session.model.platform.adaptive_platform,
            "reputation": session.model.platform.reputation,
            "short_term_revenue": session.model.platform.short_term_revenue,
            "long_term_revenue": session.model.platform.long_term_revenue,
        },
        "tipping_points": session.model.get_tipping_points(),
        "recent_events": session.model.get_recent_events(),
    }


def _serialize_live_payload(session, simulation_id: str, event: str) -> dict:
    return {
        "event": event,
        "state": _serialize_simulation_state(session, simulation_id),
        "series": session.model.get_timeseries(),
        "simulations": simulation_service.list_simulations(),
    }


@router.get("/health", response_model=HealthResponse)
def healthcheck():
    return {"status": "ok"}


@router.get("/simulations")
def list_simulations():
    return simulation_service.list_simulations()


@router.post("/simulations", response_model=SimulationSummary)
def create_simulation(payload: SimulationCreateRequest):
    session = simulation_service.create(payload.model_dump())
    return _serialize_simulation_summary(session, session.simulation_id)


@router.get("/simulations/{simulation_id}", response_model=SimulationStateResponse)
def get_simulation_state(simulation_id: str):
    try:
        session = simulation_service.get(simulation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _serialize_simulation_state(session, simulation_id)


@router.post("/simulations/{simulation_id}/step", response_model=SimulationStateResponse)
def step_simulation(simulation_id: str, payload: StepRequest):
    try:
        session = simulation_service.step(simulation_id, payload.count)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _serialize_simulation_state(session, simulation_id)


@router.post("/simulations/{simulation_id}/reset", response_model=SimulationStateResponse)
def reset_simulation(simulation_id: str):
    try:
        session = simulation_service.reset(simulation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _serialize_simulation_state(session, simulation_id)


@router.get("/simulations/{simulation_id}/timeseries", response_model=SimulationTimeseriesResponse)
def get_timeseries(simulation_id: str):
    try:
        session = simulation_service.get(simulation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"simulation_id": simulation_id, "series": session.model.get_timeseries()}


@router.get("/simulations/{simulation_id}/export.csv")
def export_simulation_csv(simulation_id: str):
    try:
        session = simulation_service.get(simulation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    timeseries = session.model.get_timeseries()
    param_keys = sorted(session.params.keys())
    metric_keys = sorted({key for row in timeseries for key in row.keys()})
    fieldnames = ["simulation_id", *param_keys, *metric_keys]

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()

    for row in timeseries:
        writer.writerow({
            "simulation_id": simulation_id,
            **session.params,
            **row,
        })

    filename = f"simulation-{simulation_id}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=buffer.getvalue(), media_type="text/csv", headers=headers)


@router.delete("/simulations/{simulation_id}", response_model=ApiMessage)
def delete_simulation(simulation_id: str):
    try:
        simulation_service.delete(simulation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": f"Simulation '{simulation_id}' deleted."}


@router.websocket("/simulations/{simulation_id}/live")
async def stream_simulation_live(
    websocket: WebSocket,
    simulation_id: str,
):
    await websocket.accept()

    try:
        session = simulation_service.get(simulation_id)
    except KeyError:
        await websocket.send_json({"event": "error", "message": f"Simulation '{simulation_id}' not found"})
        await websocket.close(code=1008)
        return

    try:
        raw_interval = websocket.query_params.get("interval_ms", "280")
        interval_ms = max(40, min(2000, int(raw_interval)))
    except ValueError:
        await websocket.send_json({"event": "error", "message": "interval_ms must be an integer"})
        await websocket.close(code=1008)
        return

    try:
        await websocket.send_json(_serialize_live_payload(session, simulation_id, "snapshot"))

        while True:
            if session.model.steps >= session.model.max_steps:
                await websocket.send_json(_serialize_live_payload(session, simulation_id, "complete"))
                await websocket.close(code=1000)
                return

            await asyncio.sleep(interval_ms / 1000)
            try:
                session = simulation_service.step(simulation_id, 1)
            except KeyError:
                await websocket.send_json({"event": "error", "message": f"Simulation '{simulation_id}' no longer exists"})
                await websocket.close(code=1008)
                return
            event = "complete" if session.model.steps >= session.model.max_steps else "tick"
            await websocket.send_json(_serialize_live_payload(session, simulation_id, event))

            if event == "complete":
                await websocket.close(code=1000)
                return
    except WebSocketDisconnect:
        return
