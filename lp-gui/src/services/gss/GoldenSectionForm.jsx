import React from "react";

import Banner from "../../components/Banner";
import Card from "../../components/Card";
import NumericField from "../../components/NumericField";
import SegmentedControl from "../../components/SegmentedControl";

function GoldenSectionForm({ state, actions }) {
  const { form, loading, error } = state;
  const { setField, setExpression, submit } = actions;

  return (
    <div className="form-grid" style={{ gap: "16px" }}>
      <Banner>
        Golden Section Search assumes the objective is unimodal on the interval [a, b]. If the
        interval contains multiple local optima, the reported answer may be misleading.
      </Banner>
      {error && <Banner tone="error">{error}</Banner>}

      <Card title="Objective f(x)">
        <div className="form-grid" style={{ gap: "8px" }}>
          <div className="label">Enter a one-variable objective</div>
          <textarea
            rows={3}
            className="input"
            style={{ width: "100%", fontFamily: "monospace" }}
            value={form.expression}
            onChange={(e) => setExpression(e.target.value)}
            placeholder="Example: (x - 2)^2"
          />
          <div className="helper">
            Use ^ for powers, implicit multiplication is allowed, and only one variable should
            appear in the expression.
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

      <Card title="Interval and Stopping Criteria">
        <div className="form-grid grid-auto">
          <NumericField label="Lower bound a" value={form.a} onChange={(value) => setField("a", value)} placeholder="0" />
          <NumericField label="Upper bound b" value={form.b} onChange={(value) => setField("b", value)} placeholder="5" />
          <NumericField
            label="Tolerance epsilon"
            value={form.epsilon}
            onChange={(value) => setField("epsilon", value)}
            placeholder="1e-5"
          />
          <NumericField
            label="Max iterations"
            value={form.max_iters}
            onChange={(value) => setField("max_iters", value)}
            placeholder="100"
          />
        </div>
      </Card>

      <div>
        <button className="btn btn-primary" onClick={submit} disabled={loading}>
          {loading ? "Running..." : "Run Golden Section Search"}
        </button>
      </div>
    </div>
  );
}

export default GoldenSectionForm;
