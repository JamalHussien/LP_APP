import React from "react";

function NumericField({
  label,
  value,
  onChange,
  placeholder = "e.g. 3.5",
  error,
  widthClass = "w-24",
}) {
  return (
    <label className={widthClass} style={{ minWidth: 120 }}>
      <div className="label">{label}</div>
      <input
        type="text"
        inputMode="decimal"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="input"
        aria-invalid={!!error}
      />
      {error && <div className="helper" style={{ color: "#ef4444" }}>{error}</div>}
    </label>
  );
}

export default NumericField;
