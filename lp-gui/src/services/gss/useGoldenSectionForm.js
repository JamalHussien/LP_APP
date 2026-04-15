import { useState } from "react";

import { postJson } from "../../api/client";
import { coerceNumber } from "../../utils/numberInput";

export default function useGoldenSectionForm() {
  const [form, setForm] = useState({
    expression: "(x - 2)^2",
    a: "0",
    b: "5",
    sense: "minimize",
    epsilon: "1e-5",
    max_iters: "100",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const setField = (key, val) => setForm((prev) => ({ ...prev, [key]: val }));

  const parseRequiredNumber = (value, label) => {
    const parsed = coerceNumber(value);
    if (parsed.value === null) {
      return { value: null, error: `${label} must be a number.` };
    }
    return { value: parsed.value, error: null };
  };

  const validate = () => {
    if (!form.expression || !form.expression.trim()) {
      return { error: "Expression is required.", payload: null };
    }

    const a = parseRequiredNumber(form.a, "Lower bound");
    if (a.error) return { error: a.error, payload: null };

    const b = parseRequiredNumber(form.b, "Upper bound");
    if (b.error) return { error: b.error, payload: null };

    const epsilon = parseRequiredNumber(form.epsilon, "Tolerance");
    if (epsilon.error) return { error: epsilon.error, payload: null };
    if (epsilon.value <= 0) return { error: "Tolerance must be positive.", payload: null };

    const maxIterations = parseRequiredNumber(form.max_iters, "Max iterations");
    if (maxIterations.error) return { error: maxIterations.error, payload: null };
    if (!Number.isInteger(maxIterations.value) || maxIterations.value <= 0) {
      return { error: "Max iterations must be a positive integer.", payload: null };
    }

    if (a.value >= b.value) {
      return { error: "Lower bound must be less than upper bound.", payload: null };
    }

    return {
      error: null,
      payload: {
        expression: form.expression,
        a: a.value,
        b: b.value,
        sense: form.sense,
        epsilon: epsilon.value,
        max_iters: maxIterations.value,
      },
    };
  };

  const submit = async () => {
    const { error: validationError, payload } = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await postJson("/optimize/golden-section", payload);
      setResult(data);
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
    setField,
    setExpression: (expr) => setField("expression", expr),
    submit,
  };
}
