import React from "react";
import ConstraintRow from "./ConstraintRow";

function ConstraintList({
  constraints,
  onChangeCoeff,
  onChangeSense,
  onChangeRhs,
  onRemove,
  errors = [],
}) {
  return (
    <div className="form-grid" style={{ gap: "12px" }}>
      {constraints.length === 0 && (
        <p className="helper">No constraints yet. Add one.</p>
      )}
      {constraints.map((c, idx) => (
        <ConstraintRow
          key={idx}
          coeffs={c.coefficients}
          sense={c.type}
          rhs={c.rhs}
          onChangeCoeff={(i, v) => onChangeCoeff(idx, i, v)}
          onChangeSense={(v) => onChangeSense(idx, v)}
          onChangeRhs={(v) => onChangeRhs(idx, v)}
          onRemove={() => onRemove(idx)}
          errors={errors[idx] || {}}
        />
      ))}
    </div>
  );
}

export default ConstraintList;
