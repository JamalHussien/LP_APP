import React from "react";

function ServiceCard({ title, description, onSelect }) {
  return (
    <button type="button" className="card" style={{ cursor: "pointer", textAlign: "left" }} onClick={onSelect}>
      <h2 className="card-title">{title}</h2>
      <div className="helper">{description}</div>
    </button>
  );
}

function SelectionScreen({ services, onSelect }) {
  return (
    <div className="page">
      <h1 className="heading-1">Optimization Toolkit</h1>
      <div className="helper">Choose a service to begin</div>
      <div className="form-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px" }}>
        {services.map((service) => (
          <ServiceCard
            key={service.id}
            title={service.title}
            description={service.description}
            onSelect={() => onSelect(service.id)}
          />
        ))}
      </div>
    </div>
  );
}

export default SelectionScreen;
