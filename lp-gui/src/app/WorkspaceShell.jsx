import React from "react";

function WorkspaceShell({ title, description, onBack, children }) {
  return (
    <div className="page">
      <div className="card-header" style={{ padding: 0 }}>
        <div>
          <h1 className="heading-1">{title}</h1>
          <div className="helper">{description}</div>
        </div>
        <button className="btn btn-ghost" onClick={onBack}>
          Back
        </button>
      </div>
      {children}
    </div>
  );
}

export default WorkspaceShell;
