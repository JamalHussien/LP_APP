import React from "react";
import Plot from "react-plotly.js";

import Banner from "../../components/Banner";

function IterTable({ points, fValues, gradNorms, grads, alphas, showAlpha }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr>
            <th align="left">k</th>
            <th align="left">x</th>
            <th align="left">grad f(x)</th>
            <th align="left">f(x)</th>
            <th align="left">||g||</th>
            {showAlpha && <th align="left">alpha_k</th>}
            <th align="left">x_next</th>
          </tr>
        </thead>
        <tbody>
          {points.map((point, index) => (
            <tr key={index}>
              <td>{index}</td>
              <td>[{point.map((value) => (value.toFixed ? value.toFixed(4) : value)).join(", ")}]</td>
              <td>
                {grads && grads[index]
                  ? `[${grads[index].map((value) => (value.toFixed ? value.toFixed(4) : value)).join(", ")}]`
                  : "-"}
              </td>
              <td>{fValues[index]?.toFixed ? fValues[index].toFixed(6) : fValues[index]}</td>
              <td>{gradNorms[index]?.toExponential ? gradNorms[index].toExponential(2) : gradNorms[index]}</td>
              {showAlpha && <td>{alphas[index] !== undefined ? (alphas[index].toPrecision ? alphas[index].toPrecision(3) : alphas[index]) : ""}</td>}
              <td>
                {points[index + 1]
                  ? `[${points[index + 1].map((value) => (value.toFixed ? value.toFixed(4) : value)).join(", ")}]`
                  : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SteepestDescentResults({ result }) {
  if (!result) return null;

  const { points, f_values, grad_norms, success, message, plot, alphas = [] } = result;
  const showAlpha = Array.isArray(alphas) && alphas.length > 0;

  return (
    <div className="form-grid" style={{ gap: "12px" }}>
      <Banner tone={success ? "success" : "error"}>
        {success ? "Converged: " : "Status: "}
        {message}
      </Banner>
      {plot && (
        <Plot
          data={plot.data}
          layout={{ ...plot.layout, autosize: true }}
          config={{ responsive: true }}
          style={{ width: "100%", height: "400px" }}
        />
      )}
      <IterTable
        points={points}
        fValues={f_values}
        gradNorms={grad_norms}
        grads={result.grads || []}
        alphas={alphas}
        showAlpha={showAlpha}
      />
    </div>
  );
}

export default SteepestDescentResults;
