import React from "react";

import Banner from "../../components/Banner";
import Card from "../../components/Card";
import NumericField from "../../components/NumericField";
import SegmentedControl from "../../components/SegmentedControl";

function SteepestDescentForm({ state, actions }) {
  const { form, loading, error, varsDetected } = state;
  const { setField, setExpression, updateStart, submit } = actions;

  return (
    <div className="form-grid" style={{ gap: "16px" }}>
      {error && <Banner tone="error">{error}</Banner>}
      <Card title="Objective f(x)">
        <div className="form-grid" style={{ gap: "8px" }}>
          <div className="label">Enter objective (differentiable)</div>
          <textarea
            rows={3}
            className="input"
            style={{ width: "100%", fontFamily: "monospace" }}
            value={form.expression}
            onChange={(e) => setExpression(e.target.value)}
            placeholder="Example: x^2 + 4xy + 5y^2 + 2x - 3y + 1"
          />
          <div className="helper">
            Use ^ for powers, implicit multiplication allowed (for example 4xy). Any differentiable
            expression is accepted. The solver can minimize or maximize: quadratics use the exact
            line search step when curvature supports the chosen goal, and other objectives use
            adaptive 1-D line search with backtracking only as a fallback.
          </div>
        </div>
      </Card>

      <div>
        <div className="label">Goal</div>
        <SegmentedControl
          value={form.sense}
          onChange={(value) => setField("sense", value)}
          options={[
            { value: "minimize", label: "Minimize" },
            { value: "maximize", label: "Maximize" },
          ]}
        />
      </div>

      <div>
        <div className="label">Mode</div>
        <SegmentedControl
          value={form.mode}
          onChange={(value) => setField("mode", value)}
          options={[
            { value: "constant", label: "Constant LR" },
            { value: "optimal", label: "Optimal (exact quadratic or line search)" },
          ]}
        />
        {form.mode === "constant" && (
          <div style={{ marginTop: 8, maxWidth: 180 }}>
            <NumericField
              label="Learning Rate"
              value={form.alpha}
              onChange={(value) => setField("alpha", value)}
              placeholder="0.1"
            />
          </div>
        )}
      </div>

      <Card title="Start and Criteria">
        <div className="form-grid grid-auto">
          {form.start.map((value, index) => (
            <NumericField
              key={index}
              label={`x0 (${varsDetected[index] || `x${index + 1}`})`}
              value={value}
              onChange={(nextValue) => updateStart(index, nextValue)}
              placeholder="0"
            />
          ))}
        </div>
        <div className="form-grid grid-auto" style={{ marginTop: 12 }}>
          <NumericField label="Max iterations" value={form.max_iters} onChange={(value) => setField("max_iters", value)} />
          <NumericField label="Grad norm tol" value={form.grad_tol} onChange={(value) => setField("grad_tol", value)} />
          <NumericField label="Delta f tol" value={form.delta_f_tol} onChange={(value) => setField("delta_f_tol", value)} />
        </div>
      </Card>

      <div>
        <button className="btn btn-primary" onClick={submit} disabled={loading}>
          {loading ? "Running..." : "Run Gradient Search"}
        </button>
      </div>
    </div>
  );
}

export default SteepestDescentForm;
