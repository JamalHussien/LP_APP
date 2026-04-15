import React from "react";

function SegmentedControl({ options, value, onChange }) {
  return (
    <div
      style={{
        display: "inline-flex",
        border: "1px solid var(--color-border)",
        borderRadius: 12,
        overflow: "hidden",
      }}
    >
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className="btn"
          style={{
            borderRadius: 0,
            border: "none",
            background: value === opt.value ? "var(--color-primary)" : "transparent",
            color: value === opt.value ? "#fff" : "var(--color-text)",
          }}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export default SegmentedControl;
