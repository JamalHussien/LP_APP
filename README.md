# Linear Programming Solver

A full-stack application for solving linear programming (LP) problems using numerical and graphical methods. Built with FastAPI backend and React/Vite frontend.

## 🎯 Features

- **Numerical Solving**: Optimized solutions using SciPy's `linprog`
- **Graphical Visualization**: 
  - 2D constraint plots with feasible region shading
  - Interactive 3D plots for 3-variable problems
- **Flexible Problem Definition**:
  - Support for maximize/minimize objectives
  - Multiple constraint types (≤, ≥, =)
  - Optional non-negativity constraints
- **REST API**: CORS-enabled endpoints for easy integration
- **Responsive UI**: Modern React interface with real-time form updates

## 🏗️ Architecture

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | FastAPI + Uvicorn |
| **Optimization Engine** | SciPy (linprog with HiGHS solver) |
| **Visualization** | Matplotlib, Plotly |
| **Frontend Framework** | React 19 |
| **Build Tool** | Vite |
| **HTTP Client** | Axios |

### Project Structure

```
LP_APP/
├── Backend (Python)
│   ├── main.py              # FastAPI application & /solve endpoint
│   ├── models.py            # Pydantic data models (LPRequest, LPSolution)
│   ├── interfaces.py        # Abstract base classes (ISolver, IRenderer)
│   ├── solvers.py           # SciPySolver implementation
│   ├── renderers.py         # MatplotlibRenderer for graphical output
│   ├── requirements.txt     # Python dependencies
│   └── venv/                # Virtual environment
│
├── lp-gui/                  # React Frontend
│   ├── src/
│   │   ├── main.jsx         # Monolithic App component
│   │   ├── App.jsx          # Modular App (component-based)
│   │   ├── index.css        # Global styles
│   │   ├── App.css          # App-specific styles
│   │   └── components/
│   │       ├── ObjectiveForm.jsx
│   │       ├── ConstraintsForm.jsx
│   │       └── ResultPanel.jsx
│   ├── package.json         # Node dependencies & scripts
│   ├── vite.config.js       # Vite configuration
│   └── index.html           # HTML entry point
│
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- pip & npm

### Backend Setup

```bash
# Navigate to project root
cd c:\Users\HP\projects\LP_APP

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn scipy numpy matplotlib plotly pydantic

# Run server
uvicorn main:app --reload
```

Backend runs at: **http://127.0.0.1:8000**

API docs: **http://127.0.0.1:8000/docs**

### Frontend Setup

```bash
# Navigate to frontend directory
cd lp-gui

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: **http://localhost:5173**

## 📖 API Documentation

### Endpoint: `POST /solve`

**Request Body** (`LPRequest`):
```json
{
  "mode": "numerical",
  "n": 2,
  "c": [2, 3],
  "sense": "maximize",
  "constraints": [
    {
      "a": [1, 1],
      "sense": "<=",
      "b": 4
    }
  ],
  "nonneg": true
}
```

**Response** (`LPSolution` - Numerical Mode):
```json
{
  "x": [0.0, 4.0],
  "objective": 12.0,
  "success": true,
  "message": null
}
```

**Response** (Graphical Mode):
- 2D: PNG image bytes
- 3D: HTML with interactive Plotly visualization

### Request Fields

| Field | Type | Description |
|-------|------|-------------|
| `mode` | `"numerical"` \| `"graphical"` | Solving method |
| `n` | `integer` | Number of decision variables |
| `c` | `array[float]` | Objective function coefficients |
| `sense` | `"maximize"` \| `"minimize"` | Optimization direction |
| `constraints` | `array[Constraint]` | List of constraints |
| `nonneg` | `boolean` | Apply non-negativity constraints (x ≥ 0) |

### Constraint Object

| Field | Type | Description |
|-------|------|-------------|
| `a` | `array[float]` | Constraint coefficients |
| `sense` | `"<="` \| `">="` \| `"="` | Constraint type |
| `b` | `float` | Right-hand side value |

### Example: Solve a 2D LP Problem

**Problem**: Maximize $2x_1 + 3x_2$ subject to:
- $x_1 + x_2 \leq 4$
- $x_1 \geq 0, x_2 \geq 0$

**Request**:
```bash
curl -X POST "http://127.0.0.1:8000/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "numerical",
    "n": 2,
    "c": [2, 3],
    "sense": "maximize",
    "constraints": [
      {"a": [1, 1], "sense": "<=", "b": 4}
    ],
    "nonneg": true
  }'
```

**Response**:
```json
{
  "x": [0.0, 4.0],
  "objective": 12.0,
  "success": true,
  "message": null
}
```

## 🎨 Frontend Usage

### Running the App

1. **Select Mode**: Choose between "Numerical" (for exact solution) or "Graphical" (for visualization)

2. **Specify Variables**: Enter the number of decision variables (2 or 3)

3. **Define Objective**:
   - Toggle between "Maximize" and "Minimize"
   - Enter coefficient for each variable

4. **Add Constraints**:
   - Click "Add Constraint" button
   - Enter coefficients, select constraint type (≤, ≥, =), enter RHS value
   - Repeat for additional constraints

5. **Optional Settings**:
   - Check/uncheck "Non-negativity constraints" for $x \geq 0$

6. **Solve**:
   - Click "Solve" button
   - View results below

### Component Architecture (App.jsx)

The modular version uses reusable components:

- **ObjectiveForm**: Handles objective function input
- **ConstraintsForm**: Manages constraints and non-negativity toggle
- **ResultPanel**: Displays numerical results or images

## 🔧 Development Guide

### Backend Structure

**[models.py](models.py)** - Data Models
- `Constraint`: Single linear constraint
- `LPRequest`: HTTP request payload
- `LPSolution`: Solver output DTO

**[interfaces.py](interfaces.py)** - Abstractions
- `ISolver`: Solver interface for extensibility
- `IRenderer`: Renderer interface for visualization

**[solvers.py](solvers.py)** - Solver Implementation
- `SciPySolver`: Uses `scipy.optimize.linprog` with HiGHS algorithm
- Handles constraint conversion to standard form
- Adjusts for maximization vs. minimization

**[renderers.py](renderers.py)** - Visualization
- `MatplotlibRenderer`: 2D/3D graphical rendering
- 2D: Computes feasible region vertices, plots constraint lines and shading
- 3D: Uses Plotly for interactive visualization
- Returns PNG (2D) or HTML (3D)

**[main.py](main.py)** - FastAPI Application
- Configures CORS for React dev server
- Dependency injection for solvers/renderers
- Single endpoint: `POST /solve`

### Frontend Structure

**[main.jsx](lp-gui/src/main.jsx)** - Monolithic App
- Single component with all state management
- Direct HTTP calls with `fetch`
- Suitable for simple use cases

**[App.jsx](lp-gui/src/App.jsx)** - Component-Based App
- Modular architecture with child components
- Uses `axios` for HTTP requests
- Supports HTML (Plotly) response handling

**[components/](lp-gui/src/components/)** - Reusable UI Components
- `ObjectiveForm.jsx`: Objective input
- `ConstraintsForm.jsx`: Constraint management
- `ResultPanel.jsx`: Results display

### Running Tests

```bash
# Frontend linting
cd lp-gui
npm run lint

# Backend (manual testing with API docs)
# Visit: http://127.0.0.1:8000/docs
```

## 📊 Data Flow

```
User Input (React UI)
    ↓
Form State Management
    ↓
POST /solve → JSON Payload
    ↓
FastAPI Endpoint
    ↓
Choose Solver Path
    ├─ Numerical: SciPySolver.solve()
    │   ↓
    │   scipy.optimize.linprog
    │   ↓
    │   LPSolution (JSON)
    │
    └─ Graphical: MatplotlibRenderer.render_graph()
        ↓
        Compute feasible vertices (2D) / planes (3D)
        ↓
        [2D: PNG] or [3D: HTML with Plotly]
    ↓
HTTP Response (JSON/Binary/HTML)
    ↓
React Component Displays Results
```

## 🧮 Mathematical Details

### Standard Form Conversion

The solver converts LP problems to SciPy's standard form:

$$\min c^T x$$
$$\text{subject to:}$$
$$A_{ub} x \leq b_{ub}$$
$$A_{eq} x = b_{eq}$$
$$x_{\text{bounds}}$$

**Constraint Handling**:
- $a·x \leq b$ → `A_ub, b_ub`
- $a·x \geq b$ → Transform to $-a·x \leq -b$
- $a·x = b$ → `A_eq, b_eq`

**Objective**:
- Maximize: Negate coefficients, solve, negate result
- Minimize: Solve directly

**Bounds**:
- With non-negativity: $x \in [0, \infty)$
- Without: $x \in (-\infty, \infty)$

### 2D Graphical Solution

1. Extract constraint lines: $a_1 x_1 + a_2 x_2 = b$
2. Find intersections (solve 2×2 linear systems)
3. Include axis intersections if applicable
4. Filter feasible points (satisfy all constraints)
5. Order vertices by angle around centroid
6. Shade feasible region (polygon)
7. Mark optimal vertex

## 🐛 Error Handling

| Scenario | Status | Message |
|----------|--------|---------|
| Invalid constraints | 400 | Validation error detail |
| Graphical mode with n ≠ 2,3 | 400 | "Graphical mode only supports 2 or 3 variables" |
| Solve failure | 400 | SciPy error message |
| Server error | 500 | Internal error detail |

## 🔌 CORS Configuration

The backend allows requests from:
- `http://localhost:5173`
- `http://127.0.0.1:5173`

For production, update CORS origins in `main.py`.

## 📦 Dependencies

### Backend
```
fastapi>=0.104.0
uvicorn>=0.24.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.8.0
plotly>=5.18.0
pydantic>=2.5.0
```

### Frontend
```
react@19.2.0
axios@1.13.5
plotly.js-dist-min@3.3.1
react-plotly.js@2.6.0
vite@5.0.0
```

## 🚢 Production Deployment

### Backend

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend

```bash
# Build production bundle
cd lp-gui
npm run build

# Output in: lp-gui/dist/
# Serve with any static server (nginx, Apache, etc.)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🎓 Future Enhancements

- [ ] Parametric sensitivity analysis
- [ ] Integer/binary programming support
- [ ] Export results to CSV/PDF
- [ ] Comprehensive unit test suite
- [ ] Drag-and-drop constraint builder
- [ ] Unbounded/infeasible problem detection
- [ ] Problem history/save functionality
- [ ] Dark mode UI theme

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Current Version**: 1.0  
**Status**: Active Development
**this doc was generated by github copilot in February 2026** 
