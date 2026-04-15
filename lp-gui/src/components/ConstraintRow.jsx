import React from "react";
import NumericField from "./NumericField";

function ConstraintRow({
  coeffs,
  sense,
  rhs,
  onChangeCoeff,
  onChangeSense,
  onChangeRhs,
  onRemove,
  errors = {},
}) {
  return (
    <div className="constraint-row">
      {coeffs.map((val, i) => (
        <NumericField
          key={i}
          label={`x${i + 1}`}
          value={val}
          onChange={(v) => onChangeCoeff(i, v)}
          placeholder="coef"
          error={errors[`a-${i}`]}
          widthClass="w-24"
        />
      ))}

      <label className="flex flex-col gap-1">
        <span className="label">Sense</span>
        <select
          value={sense}
          onChange={(e) => onChangeSense(e.target.value)}
          className="select"
        >
          <option value="<=">&lt;=</option>
          <option value=">=">&gt;=</option>
          <option value="=">=</option>
        </select>
      </label>

      <NumericField
        label="RHS"
        value={rhs}
        onChange={onChangeRhs}
        placeholder="e.g. 10"
        error={errors.b}
        widthClass="w-28"
      />

      <button
        type="button"
        onClick={onRemove}
        className="btn-text"
      >
        Remove
      </button>
    </div>
  );
}

export default ConstraintRow;
