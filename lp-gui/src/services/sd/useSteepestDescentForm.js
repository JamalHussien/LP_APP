import { useState } from "react";

import { postJson } from "../../api/client";

export default function useSteepestDescentForm() {
  const [form, setForm] = useState({
    expression: "x^2 + 4xy + 5y^2",
    start: ["0", "0"],
    sense: "minimize",
    mode: "constant",
    alpha: "0.1",
    max_iters: "200",
    grad_tol: "1e-6",
    delta_f_tol: "1e-8",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [varsDetected, setVarsDetected] = useState(["x1", "x2"]);

  const setField = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  const resizeStart = (vars) => {
    setVarsDetected(vars);
    setForm((f) => {
      const next = [...f.start];
      if (next.length < vars.length) {
        while (next.length < vars.length) next.push("0");
      } else if (next.length > vars.length) {
        next.length = vars.length;
      }
      return { ...f, start: next };
    });
  };

  const parseNumber = (s) => {
    const n = Number(s);
    return Number.isFinite(n) ? n : null;
  };

  const validate = () => {
    if (!form.expression || !form.expression.trim()) return "Expression is required";
    if (!form.start.length) return "Start point is required";
    return null;
  };

  const submit = async () => {
    const err = validate();
    if (err) {
      setError(err);
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    const payload = {
      expression: form.expression,
      start: form.start.map(parseNumber),
      sense: form.sense,
      mode: form.mode,
      alpha: parseNumber(form.alpha) ?? 0.1,
      max_iters: parseInt(form.max_iters, 10) || 200,
      grad_tol: parseNumber(form.grad_tol) ?? 1e-6,
      delta_f_tol: parseNumber(form.delta_f_tol) ?? 1e-8,
    };
    try {
      const data = await postJson("/optimize/steepest-descent", payload);
      setResult(data);
      if (data.variables) {
        resizeStart(data.variables);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return {
    form,
    loading,
    error,
    result,
    varsDetected,
    setField,
    setExpression: (expr) => {
      setField("expression", expr);
    },
    updateStart: (idx, val) =>
      setForm((f) => {
        const v = [...f.start];
        v[idx] = val;
        return { ...f, start: v };
      }),
    setVariablesFromServer: resizeStart,
    submit,
  };
}
