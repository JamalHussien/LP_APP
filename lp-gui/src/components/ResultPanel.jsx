import React from "react";

import Banner from "./Banner";
import LoadingState from "./LoadingState";

function ResultPanel({ state }) {
  const { loading, error, result, plotUrl } = state;

  if (!loading && !result && !plotUrl && !error) {
    return <div className="helper">Results will appear here after solving.</div>;
  }

  return (
    <div className="results-surface form-grid" style={{ gap: "12px" }}>
      {loading && <LoadingState label="Solving..." />}
      {error && <Banner tone="error">Error: {error}</Banner>}
      {result && (
        <div>
          <div className="card-header" style={{ padding: 0 }}>
            <h3 className="card-title" style={{ fontSize: "16px" }}>
              Numerical Result
            </h3>
            {!loading && !error && <span className="pill-success">Solved</span>}
          </div>
          <pre
            style={{
              background: "#fff",
              border: "1px solid #e2e8f0",
              borderRadius: 10,
              padding: "10px",
              margin: 0,
            }}
          >
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
      {plotUrl && (
        <div>
          <div className="card-header" style={{ padding: 0 }}>
            <h3 className="card-title" style={{ fontSize: "16px" }}>
              Graphical Result
            </h3>
          </div>
          <img
            src={plotUrl}
            alt="LP Graph"
            style={{ maxWidth: "100%", borderRadius: 12, border: "1px solid #e2e8f0" }}
          />
        </div>
      )}
    </div>
  );
}

export default ResultPanel;
