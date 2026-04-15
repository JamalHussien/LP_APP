import React from "react";

function LoadingState({ label = "Loading..." }) {
  return (
    <div className="state-loading">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export default LoadingState;
