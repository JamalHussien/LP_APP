import React from "react";
import NumericField from "./NumericField";

function ObjectiveEditor({ coeffs, onChangeCoeff, sense, onSenseChange, errors = [] }) {
  return (
    <div className="form-grid" style={{ gap: "12px" }}>
      <div className="card-header" style={{ padding: 0, marginBottom: 0 }}>
        <span className="card-title" style={{ fontSize: "16px" }}>Objective</span>
        <select
          value={sense}
          onChange={(e) => onSenseChange(e.target.value)}
          className="select"
        >
          <option value="maximize">Maximize</option>
          <option value="minimize">Minimize</option>
        </select>
      </div>
      <div className="form-grid grid-auto">
        {coeffs.map((val, i) => (
          <NumericField
            key={i}
            label={`c${i + 1}`}
            value={val}
            onChange={(v) => onChangeCoeff(i, v)}
            placeholder="e.g. 3"
            error={errors[i]}
            widthClass="w-24"
          />
        ))}
      </div>
    </div>
  );
}

export default ObjectiveEditor;
