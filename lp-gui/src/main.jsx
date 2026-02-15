import React, { useState } from "react";
import { createRoot } from "react-dom/client";

function App() {
  const [mode, setMode] = useState("numerical");
  const [numVars, setNumVars] = useState(2);
  const [sense, setSense] = useState("maximize"); // 'maximize' | 'minimize'
  const [objective, setObjective] = useState(Array(2).fill(""));
  const [constraints, setConstraints] = useState([]);
  const [nonNegative, setNonNegative] = useState(true);
  const [result, setResult] = useState(null);
  const [plotUrl, setPlotUrl] = useState(null);

  const parseNumOrZero = (v) => {
    if (v === "" || v === null || v === undefined) return 0;
    const n = Number(v);
    return Number.isNaN(n) ? 0 : n;
  };

  const updateObjective = (index, value) => {
    const copy = [...objective];
    copy[index] = parseFloat("" + value) || 0; // treat empty/invalid as 0
    setObjective(copy);
  };

  const addConstraint = () => {
    setConstraints([
      ...constraints,
      {
        coefficients: Array(numVars).fill(""),
        type: "<=",
        rhs: ""
      }
    ]);
  };

  const updateConstraintCoeff = (cIndex, vIndex, value) => {
    const copy = [...constraints];
    const parsed = parseNumOrZero(value);
    copy[cIndex] = {
      ...copy[cIndex],
      coefficients: copy[cIndex].coefficients.map((x, i) =>
        i === vIndex ? parsed : x
      )
    };
    setConstraints(copy);
  };

  const updateConstraintMeta = (cIndex, field, value) => {
    const copy = [...constraints];
    if (field === "rhs") {
      copy[cIndex][field] = parseNumOrZero(value);
    } else {
      copy[cIndex][field] = value;
    }
    setConstraints(copy);
  };
  const submit = async () => {
    const mappedConstraints = constraints.map((c) => ({
      a: c.coefficients.map((v) => parseNumOrZero(v)),
      sense: c.type,
      b: parseNumOrZero(c.rhs)
    }));

    const payload = {
      mode,
      n: Number(numVars),
      c: objective.map((v) => parseNumOrZero(v)),
      sense, // 'maximize' | 'minimize'
      constraints: mappedConstraints,
      nonneg: Boolean(nonNegative)
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `HTTP ${response.status}`);
      }

      if (mode === "graphical") {
        const blob = await response.blob();
        setPlotUrl(URL.createObjectURL(blob));
        setResult(null);
      } else {
        const data = await response.json();
        setResult(data);
        setPlotUrl(null);
      }
    } catch (err) {
      // surface error to user
      setResult({ success: false, error: err.message });
      setPlotUrl(null);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Linear Programming Solver</h1>

      <div className="space-y-2">
        <label>Mode:</label>
        <select
          className="border p-2 rounded"
          value={mode}
          onChange={(e) => setMode(e.target.value)}
        >
          <option value="numerical">Numerical</option>
          <option value="graphical">Graphical (2 vars only)</option>
        </select>
      </div>

      <div>
        <label>Number of Variables:</label>
        <input
          type="number"
          min="1"
          value={numVars}
          className="border p-2 rounded ml-2 w-20"
          onChange={(e) => {
            const n = Math.max(1, parseInt(e.target.value) || 1);
            setNumVars(n);
            setObjective(Array(n).fill(0));
            setConstraints((prev) =>
              prev.map((c) => ({
                ...c,
                coefficients: Array(n)
                  .fill(0)
                  .map((_, i) => c.coefficients[i] ?? 0)
              }))
            );
          }}
        />
      </div>

      <div>
        <h2 className="text-xl font-semibold">Objective Function</h2>

        {/* Objective type selector */}
        <div style={{ marginTop: 8, marginBottom: 8 }}>
          <label style={{ marginRight: 8 }}>Objective:</label>
          <select
            value={sense}
            onChange={(e) => setSense(e.target.value)}
            className="border p-2 rounded"
          >
            <option value="maximize">Maximize</option>
            <option value="minimize">Minimize</option>
          </select>
        </div>

        <div className="flex flex-wrap gap-4 mt-2">
          {objective.map((val, i) => (
            <input
              key={i}
              type="number"
              className="border p-2 rounded w-24"
              placeholder={`c${i + 1}`}
              value={val}
              onChange={(e) => updateObjective(i, e.target.value)}
            />
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold">Constraints</h2>
        <button
          onClick={addConstraint}
          className="bg-blue-500 text-white px-4 py-2 rounded mt-2"
        >
          Add Constraint
        </button>

        {constraints.map((c, ci) => (
          <div key={ci} className="flex flex-wrap gap-2 mt-4 items-center">
            {c.coefficients.map((coef, vi) => (
              <input
                key={vi}
                type="number"
                className="border p-2 rounded w-20"
                placeholder={`x${vi + 1}`}
                value={c.coefficients[vi]}
                onChange={(e) => updateConstraintCoeff(ci, vi, e.target.value)}
              />
            ))}

            <select
              className="border p-2 rounded"
              value={c.type}
              onChange={(e) => updateConstraintMeta(ci, "type", e.target.value)}
            >
              <option value="<=">≤</option>
              <option value=">=">≥</option>
              <option value="=">=</option>
            </select>

            <input
              type="number"
              className="border p-2 rounded w-24"
              placeholder="RHS"
              value={c.rhs}
              onChange={(e) => updateConstraintMeta(ci, "rhs", e.target.value)}
            />
          </div>
        ))}
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={nonNegative}
            onChange={() => setNonNegative(!nonNegative)}
          />
          Variables ≥ 0
        </label>
      </div>

      <button
        onClick={submit}
        className="bg-green-600 text-white px-6 py-2 rounded"
      >
        Solve
      </button>

      {result && (
        <div className="mt-6 p-4 border rounded">
          <h3 className="font-semibold">Solution / Status</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      {plotUrl && (
        <div className="mt-6">
          <img src={plotUrl} alt="Graphical Solution" style={{ maxWidth: "100%" }} />
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
