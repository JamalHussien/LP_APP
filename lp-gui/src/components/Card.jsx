import React from "react";

function Card({ title, action, children }) {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">{title}</h2>
        {action && <div className="card-action">{action}</div>}
      </div>
      {children}
    </div>
  );
}

export default Card;
