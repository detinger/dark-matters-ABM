# Dark Patterns ABM simulation web app

A full-stack research prototype for exploring **agent-based simulations of dark patterns and long-term user trust erosion**.

This repository implements a complete simulation stack:

- **Mesa** handles the simulation model in Python
- **FastAPI** exposes the simulation through REST endpoints plus a live WebSocket stream
- **React + TypeScript + Vite** provide a modern dashboard UI
- **Mesa + SolaraViz** are available as an optional Mesa-native frontend
- **Recharts** renders time-series charts
- **react-force-graph** visualizes the full user network plus the platform node

---

## What is included

### Backend
- Mesa-based ABM for trust erosion under dark patterns
- Beta-distributed user trait sampling for bounded behavioral parameters
- In-memory simulation session manager
- Formal tipping-point detection with persistent trigger rules
- FastAPI endpoints for:
  - creating simulations
  - stepping simulations forward and backward
  - resetting simulations
  - fetching current state
  - fetching time-series results
  - exporting run data to CSV
  - deleting simulations
- Batch experiment runner

### Frontend
- Modern React dashboard
- Simulation creation form with view/edit mode state machine (form locks when viewing a loaded simulation, unlocks for creating new ones)
- Auto-zero intensity slider when all dark patterns are unchecked
- KPI cards
- Tipping-point status panel
- Time-series charts (trust, users, WOM, churn, reputation, per-step economics, cumulative economics, cost of dark patterns)
- Full-network visualization with platform node, live legend, colored trust states, and always-on animated interaction effects
- Live run mode with speed slider and selectable `WebSocket` or `Polling` transport
- CSV export button for the active simulation
- Session list for loading/deleting in-memory runs

---

## Project structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── schemas/
│   │   │   └── simulation.py
│   │   ├── simulation/
│   │   │   ├── agents.py
│   │   │   ├── config.py
│   │   │   ├── metrics.py
│   │   │   ├── model.py
│   │   │   └── service.py
│   │   ├── experiments.py
│   │   ├── main.py
│   │   └── solara_app.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── dark-patterns-ABM-COLAB.ipynb
├── CALIBRATION_PLAN.md
├── .gitignore
└── README.md
```

---

## Architecture

```text
Option A: React + TypeScript -> FastAPI -> Mesa model
Option B: Mesa + SolaraViz -> Mesa model
```

### Responsibilities by layer

#### Mesa / simulation layer
Responsible for:
- agents
- state transitions
- network effects
- trust updates
- churn logic
- revenue and reputation proxies
- tipping-point detection
- time-series collection

#### FastAPI layer
Responsible for:
- creating simulation sessions
- storing in-memory model instances
- stepping or resetting simulations
- serializing state for the UI
- streaming live ticks to the dashboard over WebSocket

#### React layer
Responsible for:
- parameter input
- scenario control
- visualizing metrics
- live stepping controls
- CSV export
- visualizing full network state and animated interaction events
- interacting with the API

---

## Domain model overview

### UserAgent
Represents one application user with traits such as:
- digital literacy
- manipulation sensitivity
- social activity
- complaint propensity
- switching cost
- trust baseline
- trust resilience (type-dependent dampening of trust loss)

Traits are sampled from Beta(5,5) distributions scaled to per-type ranges, producing realistic bell-shaped variation around type midpoints.

Dynamic state includes:
- current trust
- perceived fairness
- cumulative harm (saturates logistically at 1.0)
- negative WOM
- active vs churned status
- per-pattern exposure count (drives exposure buildup ramp)

### PlatformAgent
Represents the platform/provider with variables such as:
- dark pattern intensity
- support quality
- adaptive strategy flag
- reputation
- short-term revenue
- long-term revenue

### Environment
The simulation uses a user network rather than a 2D grid. The backend supports:
- `small_world`
- `scale_free`
- `random`

The dashboard visualizes the full user graph, includes the platform as a distinct graph node, and maintains a stable per-simulation layout so interaction animations play without node positions shifting on every tick.

---

## Main simulation mechanics

Each simulation step follows this order:

1. **Direct exposure**
   - each active user is exposed to each active dark pattern
   - the first 3 encounters deliver partial harm (exposure buildup ramp)
2. **Trust and harm update**
   - trust declines (dampened by trust resilience for naive users)
   - harm accumulates with logistic saturation (slows as harm approaches 1.0)
3. **Social diffusion**
   - harm-gated negative word-of-mouth spreads through the network
   - WOM requires a cooldown (harm ≥ 0.08) then ramps up gradually with accumulated harm
   - per-step spread capped at 3 neighbors, with 0.35 global damping factor
   - receivers experience diminishing returns (repeated messages discount) and trust-shielding (high-trust users are more skeptical of complaints)
4. **Recovery**
   - support quality partially repairs trust (harm-dampened effectiveness)
   - partial recovery operates during exposure, scaled proportionally to exposure severity
   - natural passive recovery: trust drifts slowly toward a harm-adjusted ceiling each step
   - recovery ceiling = `baseline × (1 − harm)` — accumulated harm permanently depresses maximum recoverable trust
   - both recovery mechanisms are weakened by active dark-pattern intensity: multiplied by `(1 − intensity)`
5. **Positive WOM**
   - only users with zero harm and zero cumulative exposure spread positive sentiment
   - positive WOM trust boost capped at the harm-adjusted ceiling, not full baseline
6. **Churn decision**
   - logistic churn model with a trust-deficit dead zone: users whose trust is above ~0.70 experience no trust-driven churn pressure
   - only when trust drops below the dead zone threshold does the trust deficit contribute to churn probability
   - harm, negative WOM, and switching cost remain independent churn drivers
7. **Natural attrition**
   - small background churn unrelated to dark patterns (~0.01%/step)
8. **Platform update**
   - reputation updated (floor at 2.0, cap at 92.0)
   - economics: subscription revenue + dark-pattern extraction (undetected exposures earn 1.5×), both scaled by reputation factor `(reputation/100)^0.5`
   - opportunity cost tracked: projected no-DP revenue vs actual revenue
9. **Optional adaptation**
   - the platform reduces dark pattern intensity when churn or reputation cross adaptation thresholds

### Formal tipping-point detection

A tipping point is recorded only when a rule remains true for **5 consecutive steps**.

- **Trust Collapse**
  - `mean_trust <= 0.50`
- **Social Contagion**
  - `negative_wom_rate >= 0.22`
- **Churn Cascade**
  - `cumulative_churn >= 0.35`
- **Extractive Divergence**
  - revenue gap is at least `20%` of short-term revenue while `cumulative_churn >= 0.15`

---

## API overview

Base URL:

```text
http://localhost:8000/api
```

### Health
`GET /health`

### Simulations
`GET /simulations`

Returns all in-memory sessions currently stored in the backend process.

### Create simulation
`POST /simulations`

Example request body:

```json
{
  "num_users": 500,
  "network_type": "small_world",
  "avg_degree": 8,
  "rewire_prob": 0.08,
  "max_steps": 312,
  "seed": 42,
  "dark_pattern_intensity": 0.4,
  "pattern_forced_trial": true,
  "pattern_hard_cancel": true,
  "pattern_drip_pricing": true,
  "customer_support_quality": 0.3,
  "adaptive_platform": false,
  "social_influence_strength": 0.18,
  "review_visibility": 0.35
}
```

### Get simulation state
`GET /simulations/{simulation_id}`

Returns:
- parameters
- current step
- latest metrics
- full network snapshot
- recent interaction events for animated network rendering
- platform state
- tipping-point status

### Step simulation
`POST /simulations/{simulation_id}/step`

Request body:

```json
{ "count": 10 }
```

This advances the model by the requested number of steps or until `max_steps` is reached.

Negative values rewind the simulation deterministically by rebuilding from the original seed and replaying to the target step.

### Reset simulation
`POST /simulations/{simulation_id}/reset`

Resets the existing session using its original parameters.

### Get time series
`GET /simulations/{simulation_id}/timeseries`

Returns a list of data points from Mesa `DataCollector`.

### Live simulation stream
`WS /simulations/{simulation_id}/live?interval_ms=280`

Streams live updates for the selected simulation. Each message includes:
- event type such as `snapshot`, `tick`, `complete`, or `error`
- current simulation state
- full time-series data
- updated simulation list metadata

The React dashboard uses this endpoint when `WebSocket` is selected as the live transport. `Polling` is available as a fallback transport.

### Export CSV
`GET /simulations/{simulation_id}/export.csv`

Downloads a CSV containing:
- one row per step
- all collected model metrics
- tipping-point trigger flags and trigger steps
- the full parameter set repeated on each row for analysis portability

### Delete simulation
`DELETE /simulations/{simulation_id}`

Removes the simulation from in-memory storage.

---

## Running the project

### Prerequisites

Requirements:
- **Python 3.11+**
- **Node.js 20+**
- **npm**

---

## Quick Local Script

The cross-platform helper script (`dev.py`) provides the fastest setup and launch path from the repository root. It runs identically on Windows, macOS, and Linux:

```bash
python dev.py setup
python dev.py run
```

What it does:

- `python dev.py setup`
  - creates `backend/.venv`
  - installs backend dependencies
  - installs frontend dependencies
  - creates `frontend/.env` from `.env.example` if needed
  - sets `VITE_API_BASE=http://localhost:8000/api`
- `python dev.py run`
  - starts the backend with `python -m app.dev_server`
  - starts the frontend with `npm run dev`
  - stops both services (and frees ports 8000/5173) when you press `Ctrl+C`

---

## 1. Manual setup

Open a terminal in `backend/`.

### Create and activate a virtual environment

#### macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Choose a frontend

The project runs in two configurations:

- **React dashboard + FastAPI** — the full custom web application
- **Mesa SolaraViz** — the Mesa-native interactive frontend

### Option A. Run the existing React dashboard

#### Run the API

From the `backend/` folder:

```bash
python -m app.dev_server
```

The backend is available at:

```text
http://localhost:8000
```

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

#### Start the React frontend

Open a second terminal in `frontend/`.

### Install dependencies

```bash
npm install
```

### Optional environment file

Copy the example file to override the default API base URL.

#### macOS / Linux
```bash
cp .env.example .env
```

#### Windows PowerShell
```powershell
Copy-Item .env.example .env
```

### Start the frontend

```bash
npm run dev
```

The React app is available at:

```text
http://localhost:5173
```

### Option B. Run the Mesa SolaraViz frontend

From the `backend/` folder:

```bash
solara run app/solara_app.py --production --port 8765
```

The Mesa frontend is available at:

```text
http://localhost:8765
```

This mode reuses the same `DarkPatternTrustModel`, keeps the platform visible in the network view, and provides Mesa's built-in play, pause, step, and reset controls without requiring the React app or FastAPI server.

---

## First run workflow

### React dashboard path

1. Start the backend
2. Start the frontend
3. Open the dashboard in your browser
4. Configure parameters and create a simulation using the left-hand form
5. Use the run controls below the form:
   - `Step +1` / `Step -1` for single-step navigation
   - `Run +10` / `Run -10` for batch steps
   - `Run Live` for continuous streaming
6. Choose the live transport in the control panel:
   - `WebSocket` for the default low-overhead live stream
   - `Polling` as a fallback transport
7. Load a saved simulation from the session list — the form updates to show that simulation's parameters (locked). Click `New simulation` to configure and create another run.

### Mesa SolaraViz path

1. Start the Solara app
2. Open `http://localhost:8765`
3. Adjust parameters in the Mesa controls
4. Use `Step`, `Play/Pause`, and `Reset`
5. Inspect the network overview, summary tables, and Mesa plots

---

## Running batch experiments

The repository includes a batch experiment runner in:

```text
backend/app/experiments.py
```

The backend virtual environment must exist and Python dependencies must be installed before running batch experiments. Without this step, Python raises `ModuleNotFoundError: No module named 'pandas'` and related import errors.

Run it from the `backend/` folder:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.experiments
```

If the virtual environment is already set up:

```bash
cd backend
source .venv/bin/activate
python -m app.experiments
```

To run without activating the environment:

```bash
cd backend
.venv/bin/python -m app.experiments
```

The script writes results to:

```text
backend/results/batch_results.csv
```

---

## Default parameters

### Population and network
- `num_users = 500`
- `network_type = small_world`
- `avg_degree = 8`
- `rewire_prob = 0.08`
- `max_steps = 312` (6 years at 1 step/week)

### Platform
- `dark_pattern_intensity = 0.40`
- `pattern_forced_trial = true`
- `pattern_hard_cancel = true`
- `pattern_drip_pricing = true`
- `customer_support_quality = 0.30`
- `adaptive_platform = false`

### Social diffusion
- `social_influence_strength = 0.18`
- `review_visibility = 0.35`

---

## Development status

### 1. Scientific model

Implemented:
- Beta(5,5) trait sampling calibrated to per-type ranges [DONE]
- parameter calibration from literature and behavioral constraints [DONE]
- formal tipping-point detection [DONE]
- three discrete user types with per-type trait distributions [DONE]
- revenue model: hidden-extraction premium, reputation-discounted revenue, opportunity cost tracking [DONE]
- trust resilience per user type [DONE]
- logistic harm saturation [DONE]
- exposure buildup ramp [DONE]
- harm-dampened recovery [DONE]
- WOM spread dynamics: cooldown threshold, logistic ramp-up, global damping, receiver trust shield [DONE]
- partial recovery during exposure and natural passive recovery [DONE]
- harm-adjusted trust ceiling [DONE]
- trust-deficit dead zone in churn model [DONE]

### 2. Backend architecture

Implemented:
- in-memory session management [DONE]
- deterministic backward stepping via seeded replay [DONE]
- WebSocket live streaming [DONE]
- batch experiment runner [DONE]

Planned extensions:
- persistent storage for simulation sessions
- background job processing for long experiments
- authentication layer

### 3. Frontend

Implemented:
- scenario comparison: single active simulation [DONE]
- CSV export [DONE]
- dark mode and polished layout [DONE]
- form view/edit state machine [DONE]
- auto-zero intensity when no patterns selected [DONE]
- form sync from loaded simulation parameters [DONE]

Planned extensions:
- side-by-side scenario comparison view
- multiple saved chart overlays
- richer network interaction controls

### 4. Research workflows

Implemented:
- Colab notebook analysis pipeline [DONE]
- CSV export for downstream analysis [DONE]

Planned extensions:
- sensitivity analysis dashboards
- experiment registry

## Calibration reference

For a parameter-by-parameter calibration plan linked to literature, surveys, audits, and behavioral data, see:

- `CALIBRATION_PLAN.md`

---

## Known limitations

- Simulation sessions are stored **in memory only**; restarting the backend clears all sessions.
- Backward stepping works by deterministic replay, so large rewinds are more computationally expensive than forward steps.
- Parameter values are calibrated to behavioral plausibility constraints documented in `CALIBRATION_PLAN.md`; fitting against real-world platform telemetry is outside the scope of the current implementation.
- There is no authentication or persistence layer.
- Long experiment execution is synchronous.
- Live WebSocket updates send full state payloads on each tick rather than incremental diffs.
- The animated network visualization becomes computationally demanding at large population sizes.

---

## Problem framing

> A stochastic, network-based agent-based simulation of long-term trust erosion caused by dark patterns in digital applications, exposed through a modern web interface for scenario exploration and comparative analysis.

The architecture separates:
- **Mesa** as the scientific model core
- **FastAPI** as the delivery layer
- **React** as the presentation layer

---

## Troubleshooting

### Backend import errors
Make sure you are in the `backend/` folder when starting Uvicorn:

```bash
python -m app.dev_server
```

### CORS errors in the browser
Make sure:
- backend runs on `http://localhost:8000`
- frontend runs on `http://localhost:5173`
- you did not change ports without updating CORS or `VITE_API_BASE`

### Frontend cannot reach API
Check:
- backend is running
- `frontend/.env` has the correct `VITE_API_BASE`
- browser console and FastAPI logs for errors

### WebSocket live mode disconnects
Check:
- backend is running on `http://localhost:8000`
- the browser can reach `ws://localhost:8000/api/...`
- switch the live transport to `Polling` as a fallback if the socket is interrupted

### Simulation disappears
Expected behavior when the backend restarts, because sessions are stored in memory.

### Network visualization performance
The dashboard renders the full network plus a platform node and animated interaction events. Large populations increase browser rendering load, particularly near the upper limit of the supported user count.

---

## Deploying on Railway

This repository is an isolated monorepo, so deploy the frontend and backend as two Railway services connected to the same GitHub repository.

### 1. Create the services

Create two services named `backend` and `frontend`. For each service, open **Settings** and configure:

| Service | Root Directory | Railway Config File | Watch Path |
| --- | --- | --- | --- |
| `backend` | `/backend` | `/backend/railway.toml` | `/backend/**` |
| `frontend` | `/frontend` | `/frontend/railway.toml` | `/frontend/**` |

The config-file paths are repository-absolute because Railway does not resolve them relative to the service Root Directory.

### 2. Generate public domains

Under **Settings -> Networking**, generate a Railway domain for both services.

### 3. Connect the services

Open the backend's generated domain directly and confirm that `/api/health` returns `{"status":"ok"}`. Then add this runtime variable to the `frontend` service using the actual backend domain shown under **Settings -> Networking**:

```env
API_UPSTREAM=https://your-backend.up.railway.app
```

Enter the value without surrounding quotes or a trailing `/api`. A Railway reference variable also works when the backend service is named exactly `backend`:

```env
API_UPSTREAM=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

The deployed frontend sends browser requests to its own `/api` path, and Caddy forwards them to `API_UPSTREAM`. This avoids cross-origin browser requests and allows the upstream to be changed at runtime. Remove any old `VITE_API_BASE` variable from the frontend service, deploy the staged variable change, and redeploy the frontend. The frontend health check uses the proxied backend health endpoint, so Railway rejects a deployment when `API_UPSTREAM` is missing or unreachable.

### 4. Verify the deployment

- Backend health: `https://<backend-domain>/api/health`
- Backend API docs: `https://<backend-domain>/docs`
- Frontend: `https://<frontend-domain>/`
- Proxied health check: `https://<frontend-domain>/api/health`

The backend Railway config starts Uvicorn on Railway's injected `PORT`. The frontend Dockerfile builds the Vite app and serves it with Caddy on the same injected port.

If the proxied health check returns `502`, Caddy cannot reach `API_UPSTREAM`. Confirm that the variable is attached to the `frontend` service in the same environment, that its staged change was deployed, and that the direct backend health URL works.

---

## Version history

See `VERSION_NOTES.md` for a concise changelog.
