# Optimization Toolkit

A full-stack optimization app built with FastAPI and React/Vite. It began as a Linear Programming solver and now supports three workflows from a single service-selection screen:

1. Linear Programming (LP)
2. Steepest Descent / Steepest Ascent
3. Golden Section Search

All workspaces share the same UI shell, API client, validation style, and result presentation patterns.

## Contents

- `optimization/` - canonical backend package for domain models, algorithms, parsers, plotting utilities, application services, and API wiring.
- `optimization/app/api.py` - thin FastAPI endpoints for LP, steepest descent/ascent, and golden section search.
- `lp-gui/` - React UI with one workspace per optimization method.
- `tests/` - pytest coverage for algorithm cores, application services, and API behavior.

## Architecture Map

- `optimization/` is the backend source of truth. New backend code should live here, not in legacy top-level modules.
- `optimization/algorithms/` contains pure solver logic and result dataclasses. These modules do not depend on FastAPI, React, DTOs, or plotting payloads.
- `optimization/app/` contains application services, DTOs, dependency wiring, and the thin HTTP adapter in `api.py`.
- `optimization/infrastructure/` contains parsing, plotting, and logging helpers used by the application layer.
- `main.py` and the other top-level Python modules are compatibility shims only. Internal imports should target `optimization.*`.
- `lp-gui/src/app/` contains the app shell, service registry, selection screen, and workspace loading.
- `lp-gui/src/workspaces/` contains one workspace per optimization method.
- `lp-gui/src/services/` contains feature-local hooks, forms, and results components.
- `lp-gui/src/api/client.js` is the shared browser-to-backend HTTP client.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Recommended: a virtual environment

## Backend Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with:

```bash
source .venv/bin/activate
```

### Run API

```bash
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`, with docs at `http://127.0.0.1:8000/docs`.

### Backend Tests

```bash
python -m pytest -q
```

## Frontend Setup

```bash
cd lp-gui
npm install
npm run dev
```

The frontend dev server runs at `http://localhost:5173`.

### Frontend Validation

```bash
cd lp-gui
npm run lint
npm run test
npm run build
```

## UI Flow

1. Service selection: choose LP, Steepest Descent, or Golden Section Search.
2. Workspace:
   - LP: configure objective coefficients, constraints, solve mode, and non-negativity.
   - Steepest Descent: choose minimize or maximize, enter a differentiable objective or quadratic data, start point, step mode, and stopping criteria.
   - Golden Section Search: enter a one-variable objective, choose minimize or maximize, set `[a, b]`, tolerance, and max iterations.
3. Results:
   - LP shows the numerical solution or graphical output.
   - Steepest Descent shows the optimization path, objective history, step sizes, and diagnostics.
   - Golden Section Search shows the estimated optimum, interval history, and convergence chart.

## API Endpoints

### `POST /solve`

Solves LP problems numerically or graphically.

```json
{
  "mode": "numerical",
  "n": 2,
  "c": [2, 3],
  "sense": "maximize",
  "constraints": [
    {"a": [1, 1], "sense": "<=", "b": 4}
  ],
  "nonneg": true
}
```

### `POST /optimize/steepest-descent`

Runs the generalized gradient search. `sense` defaults to `"minimize"` for backward compatibility and can also be `"maximize"` for steepest ascent.

### `POST /optimize/golden-section`

Runs one-dimensional Golden Section Search on a closed interval.

```json
{
  "expression": "(x - 2)^2",
  "a": 0,
  "b": 5,
  "sense": "minimize",
  "epsilon": 1e-5,
  "max_iters": 100
}
```

## Golden Section Search

Golden Section Search is a derivative-free method for unimodal one-dimensional optimization on a closed interval `[a, b]`. It is useful when:

- the objective depends on exactly one variable
- the optimum is bracketed by a reliable interval
- the function is unimodal on that interval

### Assumptions and Limitations

- The objective should be unimodal on `[a, b]`.
- If the interval contains multiple local optima, the reported result may be misleading.
- The method only supports one-variable expressions in this app.
- Objective evaluations must remain finite inside the interval.

### Inputs

- `expression`: one-variable objective such as `(x - 2)^2`
- `a`: lower bound
- `b`: upper bound with `a < b`
- `sense`: `"minimize"` or `"maximize"`
- `epsilon`: stop when interval width is below this tolerance
- `max_iters`: maximum number of interval-reduction steps

### Outputs

- `x_star`: estimated optimum
- `fx_star`: objective value at the estimated optimum
- `iterations`: number of interval-reduction steps performed
- `termination_reason`: why the algorithm stopped
- `history`: full iteration history with interval bounds, interior points, objective values, width, and current best estimate

### Interior-Point Convention

This app uses:

- `d = phi * (xu - xl)`
- `x1 = xl + d`
- `x2 = xu - d`

Because `phi ~= 0.618`, `x1` is usually to the right of `x2`.

Example on `[0, 2]`:

- width = `2`
- `d0 = phi * 2 = 1.236067...`
- `x1 = 1.236067...`
- `x2 = 0.763932...`

## Steepest Descent / Ascent

The steepest-descent endpoint is now a generalized gradient-search flow:

- `sense = "minimize"` uses the steepest descent direction.
- `sense = "maximize"` uses the steepest ascent direction.
- `mode = "constant"` uses a fixed step size.
- `mode = "optimal"` uses the exact quadratic step when curvature supports the chosen sense, otherwise an adaptive one-dimensional line search with backtracking fallback.

The endpoint name remains `/optimize/steepest-descent` for compatibility.

## Linear Programming

LP supports:

- numerical solving through SciPy HiGHS
- maximize and minimize objectives
- `<=`, `>=`, and `=` constraints
- optional non-negativity constraints
- graphical solving for supported 2D/3D cases

## Adding A New Algorithm

1. Add the pure algorithm and result types under `optimization/algorithms/`.
2. Add parser or plotting helpers under `optimization/infrastructure/` only if the algorithm needs them.
3. Add an application service under `optimization/app/` that parses inputs, runs the algorithm, and prepares presentation data without doing HTTP work.
4. Add DTO mapping in `optimization/app/mappers.py` and keep the endpoint in `optimization/app/api.py` thin.
5. Add a workspace under `lp-gui/src/workspaces/`, feature-local form/results under `lp-gui/src/services/`, and register it in `lp-gui/src/app/serviceRegistry.js`.
6. Add backend tests in `tests/` and frontend tests in `lp-gui/src/` so the feature is covered at service, API, and UI boundaries.

## Validation Commands

```bash
python -m pytest -q
cd lp-gui
npm run lint
npm run test
npm run build
```

## Notes

- Generated Python bytecode, pytest caches, frontend build output, and `node_modules` are ignored by Git.
- Keep root-level Python modules as compatibility shims only.
- Prefer small focused modules over large all-in-one files.
