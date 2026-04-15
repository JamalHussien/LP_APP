import React from "react";
import Plot from "react-plotly.js";

import Banner from "../../components/Banner";

function formatNumber(value, digits = 6) {
  if (typeof value !== "number" || !Number.isFinite(value)) return String(value ?? "");
  return Math.abs(value) >= 1e4 || (Math.abs(value) > 0 && Math.abs(value) < 1e-3)
    ? value.toExponential(3)
    : value.toFixed(digits);
}

function Summary({ result }) {
  return (
    <div
      className="results-surface"
      style={{ display: "grid", gap: "12px", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}
    >
      <div>
        <div className="label">Variable</div>
        <div>{result.variable || "x"}</div>
      </div>
      <div>
        <div className="label">Estimated optimum x*</div>
        <div>{formatNumber(result.x_star)}</div>
      </div>
      <div>
        <div className="label">Objective value f(x*)</div>
        <div>{formatNumber(result.fx_star)}</div>
      </div>
      <div>
        <div className="label">Iterations</div>
        <div>{result.iterations}</div>
      </div>
      <div>
        <div className="label">Termination</div>
        <div>{result.termination_reason}</div>
      </div>
    </div>
  );
}

function IterationTable({ history = [] }) {
  if (!history.length) {
    return <Banner>No interval reductions were needed because the starting interval already met the tolerance.</Banner>;
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr>
            <th align="left">k</th>
            <th align="left">xl</th>
            <th align="left">xu</th>
            <th align="left">x1</th>
            <th align="left">x2</th>
            <th align="left">f(x1)</th>
            <th align="left">f(x2)</th>
            <th align="left">Width</th>
            <th align="left">Best x</th>
            <th align="left">Best f(x)</th>
          </tr>
        </thead>
        <tbody>
          {history.map((row) => (
            <tr key={row.iteration}>
              <td>{row.iteration}</td>
              <td>{formatNumber(row.xl, 5)}</td>
              <td>{formatNumber(row.xu, 5)}</td>
              <td>{formatNumber(row.x1, 5)}</td>
              <td>{formatNumber(row.x2, 5)}</td>
              <td>{formatNumber(row.fx1, 6)}</td>
              <td>{formatNumber(row.fx2, 6)}</td>
              <td>{formatNumber(row.intervalWidth, 6)}</td>
              <td>{formatNumber(row.currentBestX, 6)}</td>
              <td>{formatNumber(row.currentBestFx, 6)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GoldenSectionResults({ result }) {
  if (!result) return null;

  const tone = result.success ? "success" : "info";
  const prefix = result.success ? "Converged: " : "Stopped: ";

  return (
    <div className="form-grid" style={{ gap: "12px" }}>
      <Banner tone={tone}>
        {prefix}
        {result.termination_reason}
      </Banner>
      <Summary result={result} />
      {result.plot && (
        <Plot
          data={result.plot.data}
          layout={{ ...result.plot.layout, autosize: true }}
          config={{ responsive: true }}
          style={{ width: "100%", height: "400px" }}
        />
      )}
      <IterationTable history={result.history} />
    </div>
  );
}

export default GoldenSectionResults;
