import { useEffect, useMemo, useState } from "react";

import { postBlob, postJson } from "../api/client";
import { coerceNumber, normalizeInput } from "../utils/numberInput";

const emptyConstraint = (n) => ({
  coefficients: Array(n).fill(""),
  type: "<=",
  rhs: "",
});

export default function useLPForm() {
  const [mode, setMode] = useState("numerical");
  const [numVars, setNumVars] = useState(2);
  const [sense, setSense] = useState("maximize");
  const [objective, setObjective] = useState(Array(2).fill(""));
  const [constraints, setConstraints] = useState([]);
  const [nonNegative, setNonNegative] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [plotUrl, setPlotUrl] = useState(null);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});

  useEffect(() => {
    return () => {
      if (plotUrl) {
        URL.revokeObjectURL(plotUrl);
      }
    };
  }, [plotUrl]);

  // resizing numVars with safeguards
  const changeNumVars = (n) => {
    const newN = Math.max(1, n || 1);
    if (newN < numVars) {
      const ok = window.confirm("Reducing variables will drop extra coefficients. Continue?");
      if (!ok) return;
    }
    setNumVars(newN);
    setObjective((prev) => {
      const next = Array(newN).fill("");
      prev.forEach((v, i) => {
        if (i < newN) next[i] = normalizeInput(v);
      });
      return next;
    });
    setConstraints((prev) =>
      prev.map((c) => {
        const coeffs = Array(newN).fill("");
        c.coefficients.forEach((v, i) => {
          if (i < newN) coeffs[i] = normalizeInput(v);
        });
        return { ...c, coefficients: coeffs };
      })
    );
  };

  const addConstraint = () => setConstraints((prev) => [...prev, emptyConstraint(numVars)]);
  const removeConstraint = (idx) =>
    setConstraints((prev) => prev.filter((_, i) => i !== idx));

  const updateObjective = (i, val) =>
    setObjective((prev) => prev.map((v, idx) => (idx === i ? val : v)));

  const updateConstraintCoeff = (cIdx, vIdx, val) =>
    setConstraints((prev) =>
      prev.map((c, i) =>
        i === cIdx
          ? { ...c, coefficients: c.coefficients.map((cv, j) => (j === vIdx ? val : cv)) }
          : c
      )
    );

  const updateConstraintSense = (cIdx, senseVal) =>
    setConstraints((prev) => prev.map((c, i) => (i === cIdx ? { ...c, type: senseVal } : c)));

  const updateConstraintRhs = (cIdx, val) =>
    setConstraints((prev) => prev.map((c, i) => (i === cIdx ? { ...c, rhs: val } : c)));

  const validate = () => {
    const errors = {};
    objective.forEach((s, i) => {
      const { value, error } = coerceNumber(s);
      if (value === null) errors[`obj-${i}`] = error || "Required";
    });
    constraints.forEach((c, ci) => {
      const cErr = {};
      c.coefficients.forEach((s, vi) => {
        const { value, error } = coerceNumber(s);
        if (value === null) cErr[`a-${vi}`] = error || "Required";
      });
      const rhs = coerceNumber(c.rhs);
      if (rhs.value === null) cErr.b = rhs.error || "Required";
      if (Object.keys(cErr).length) errors[`c-${ci}`] = cErr;
    });
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const buildPayload = () => {
    const parseArr = (arr) => arr.map((s) => coerceNumber(s).value);
    return {
      mode,
      kind: "linear",
      n: Number(numVars),
      c: parseArr(objective),
      sense,
      constraints: constraints.map((c) => ({
        a: parseArr(c.coefficients),
        sense: c.type,
        b: coerceNumber(c.rhs).value,
      })),
      nonneg: Boolean(nonNegative),
    };
  };

  const submit = async () => {
    setError(null);
    if (!validate()) return;
    const payload = buildPayload();
    setLoading(true);
    try {
      if (mode === "graphical") {
        const blob = await postBlob("/solve", payload);
        setPlotUrl(URL.createObjectURL(blob));
        setResult(null);
      } else {
        const data = await postJson("/solve", payload);
        setResult(data);
        setPlotUrl(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const setModeSafely = (m) => {
    if (m === "graphical" && numVars > 3) {
      changeNumVars(3);
    }
    setMode(m);
  };

  const fieldErrorForConstraint = useMemo(() => {
    const map = [];
    constraints.forEach((_, idx) => {
      map[idx] = fieldErrors[`c-${idx}`] || {};
    });
    return map;
  }, [constraints, fieldErrors]);

  const objectiveErrors = useMemo(() => {
    return objective.map((_, idx) => fieldErrors[`obj-${idx}`] || null);
  }, [objective, fieldErrors]);

  return {
    state: {
      mode,
      numVars,
      sense,
      objective,
      constraints,
      nonNegative,
      loading,
      result,
      plotUrl,
      error,
      fieldErrors,
      objectiveErrors,
      constraintErrors: fieldErrorForConstraint,
    },
    actions: {
      changeNumVars,
      setMode: setModeSafely,
      setSense,
      setNonNegative,
      addConstraint,
      removeConstraint,
      updateObjective,
      updateConstraintCoeff,
      updateConstraintSense,
      updateConstraintRhs,
      submit,
    },
  };
}
