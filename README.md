# Dark Patterns ABM simulation web app

A full-stack  project for exploring **agent-based simulations of dark patterns and long-term user trust erosion**.

This repository gives you a clean foundation for a research prototype where:

- **Mesa** handles the simulation model in Python
- **FastAPI** exposes the simulation through a REST API
- **React + TypeScript + Vite** provide a modern dashboard UI
- **Recharts** renders time-series charts
- **react-force-graph** visualizes a sampled user network

The project is intentionally designed as a **starter**: it already runs, but it also leaves room for substantial research and engineering improvements.

---

## What is included

### Backend
- Mesa-based ABM for trust erosion under dark patterns
- In-memory simulation session manager
- FastAPI endpoints for:
  - creating simulations
  - stepping simulations
  - resetting simulations
  - fetching current state
  - fetching time-series results
  - deleting simulations
- Batch experiment runner scaffold

### Frontend
- Modern React dashboard
- Simulation creation form
- KPI cards
- Time-series charts
- Network snapshot visualization
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
│   │   └── main.py
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
├── .gitignore
└── README.md
```

---

## Architecture

```text
React + TypeScript (frontend)
        ↓ HTTP
FastAPI (backend API)
        ↓
Mesa model + simulation service
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
- time-series collection

#### FastAPI layer
Responsible for:
- creating simulation sessions
- storing in-memory model instances
- stepping or resetting simulations
- serializing state for the UI

#### React layer
Responsible for:
- parameter input
- scenario control
- visualizing metrics
- visualizing sampled network state
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

Dynamic state includes:
- current trust
- perceived fairness
- cumulative harm
- negative WOM
- active vs churned status

### PlatformAgent
Represents the platform/provider with variables such as:
- dark pattern intensity
- support quality
- adaptive strategy flag
- reputation
- short-term revenue
- long-term revenue

### Environment
The simulation uses a user network rather than a 2D grid. The backend currently supports:
- `small_world`
- `scale_free`
- `random`

---

## Main simulation mechanics

Each simulation step roughly follows this order:

1. **Direct exposure**
   - users may encounter active dark patterns
2. **Trust and harm update**
   - trust declines, harm accumulates
3. **Social diffusion**
   - negative word-of-mouth spreads through the network
4. **Recovery**
   - support quality can partially repair trust
5. **Churn decision**
   - users may leave based on trust, harm, WOM, switching cost
6. **Platform update**
   - reputation and revenue proxies are updated
7. **Optional adaptation**
   - platform may reduce dark pattern intensity if outcomes worsen

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
  "max_steps": 104,
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
- sampled network snapshot
- platform state

### Step simulation
`POST /simulations/{simulation_id}/step`

Request body:

```json
{ "count": 10 }
```

This advances the model by the requested number of steps or until `max_steps` is reached.

### Reset simulation
`POST /simulations/{simulation_id}/reset`

Resets the existing session using its original parameters.

### Get time series
`GET /simulations/{simulation_id}/timeseries`

Returns a list of data points from Mesa `DataCollector`.

### Delete simulation
`DELETE /simulations/{simulation_id}`

Removes the simulation from in-memory storage.

---

## Running the project

## Prerequisites

You should have installed:
- **Python 3.11+** recommended
- **Node.js 20+** recommended
- **npm**

---

## 1. Start the backend

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

### Run the API

From the `backend/` folder:

```bash
uvicorn app.main:app --reload
```

The backend should be available at:

```text
http://localhost:8000
```

Interactive docs will be available at:

```text
http://localhost:8000/docs
```

---

## 2. Start the frontend

Open a second terminal in `frontend/`.

### Install dependencies

```bash
npm install
```

### Optional environment file

Copy the example file if you want to customize the API base URL.

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

The frontend should be available at:

```text
http://localhost:5173
```

---

## First run workflow

1. Start the backend
2. Start the frontend
3. Open the dashboard in your browser
4. Create a simulation using the left-hand form
5. Click:
   - `Step +1`
   - `Run +10`
   - `Run +52`
6. Inspect KPI cards, charts, and the network snapshot

---

## Running batch experiments

The repository includes a starter batch runner in:

```text
backend/app/experiments.py
```

Run it from the `backend/` folder:

```bash
python -m app.experiments
```

The script writes results to:

```text
backend/results/batch_results.csv
```

You should treat this as a scaffold. For thesis use, you will likely want to:
- add more scenario families
- add parameter sweeps
- persist outputs in a more structured way
- generate figures automatically

---

## Default parameters

### Population and network
- `num_users = 500`
- `network_type = small_world`
- `avg_degree = 8`
- `rewire_prob = 0.08`
- `max_steps = 104`

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

## Suggested development roadmap

### 1. Strengthen the scientific model
Good next steps:
- replace bounded normal sampling with proper Beta distributions
- calibrate parameters from literature or survey data
- formalize tipping point detection
- store agent-type segments explicitly
- improve revenue model

### 2. Improve backend architecture
Possible upgrades:
- add persistent storage for simulation metadata
- save results to Postgres or Redis (I don't need that for now)
- add background jobs for long experiments
- add WebSocket streaming for live runs (only if it improves the app)
- add authentication if needed

### 3. Improve frontend UX
Possible upgrades:
- scenario comparison view
- multiple saved charts
- export to CSV/JSON/PNG
- parameter presets
- richer network controls
- dark mode and polished layout system

### 4. Improve research workflows
Possible upgrades:
- notebook analysis pipeline 
- automated report generation
- sensitivity analysis dashboards
- experiment registry

---

## Known limitations


Current limitations include:
- simulation sessions are stored **in memory only**
- restarting the backend clears all sessions
- network visualization uses only a sampled subset of nodes
- metrics are illustrative and not empirically calibrated
- there is no authentication or persistence layer
- long experiment execution is synchronous

These limitations are acceptable for a starter and often acceptable for a thesis prototype, but they should be acknowledged in a formal research write-up.

---

## Suggested thesis framing

This project supports a thesis framing like:

> A stochastic, network-based agent-based simulation of long-term trust erosion caused by dark patterns in digital applications, exposed through a modern web interface for scenario exploration and comparative analysis.

That framing keeps:
- **Mesa** as the scientific model core
- **FastAPI** as the delivery layer
- **React** as the presentation layer

---

## Troubleshooting

### Backend import errors
Make sure you are in the `backend/` folder when starting Uvicorn:

```bash
uvicorn app.main:app --reload
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

### Simulation disappears
That is expected if the backend restarts because sessions are stored in memory.

---

## Recommended next files to add

If you want to continue developing this seriously, the next high-value additions are:

- `backend/app/simulation/scenarios.py`
- `backend/app/simulation/serialization.py`
- `backend/app/analysis/`
- `backend/tests/`
- `frontend/src/pages/ComparisonPage.tsx`
- `frontend/src/components/ScenarioPresetCards.tsx`
- `frontend/src/components/ExportButtons.tsx`

---

## License

This starter is provided as a development scaffold. Add your preferred license before publishing or sharing widely.

---

## Final note

This repository is meant to get you from **research idea** to **running full-stack prototype** quickly.

The simulation is already separated cleanly enough that you can evolve it in three directions at once:
- scientific model refinement
- API hardening
- UI modernization

That makes it a very good base for a diploma thesis, internal demo, or later publication-oriented prototype.
