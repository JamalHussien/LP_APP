import { useState } from "react";
import axios from "axios";
import ObjectiveForm from "./components/ObjectiveForm";
import ConstraintsForm from "./components/ConstraintsForm";
import ResultPanel from "./components/ResultPanel";

function App() {
  const [mode, setMode] = useState("numerical");
  const [nVars, setNVars] = useState(2);
  const [objective, setObjective] = useState(Array(2).fill(""));
  const [sense, setSense] = useState("maximize");
  const [constraints, setConstraints] = useState([]);
  const [nonneg, setNonneg] = useState(true);
  const [result, setResult] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [htmlContent, setHtmlContent] = useState(null);

  const solve = async () => {
    if (mode === "graphical" && nVars !== 2 && nVars !== 3) {
      alert("Graphical mode supports 2 or 3 variables (3 for interactive).");
      return;
    }

    const payload = {
      mode,
      n: nVars,
      c: objective,
      sense,
      constraints,
      nonneg,
    };

    try {
      if (mode === "numerical") {
        const res = await axios.post("http://127.0.0.1:8000/solve", payload);
        setResult(res.data);
        setImageUrl(null);
        setHtmlContent(null);
      } else {
        const res = await axios.post(
          "http://127.0.0.1:8000/solve",
          payload,
          { responseType: "arraybuffer" }
        );
        const contentType = res.headers["content-type"] || "";
        if (contentType.includes("text/html")) {
          const html = new TextDecoder().decode(res.data);
          setHtmlContent(html);
          setImageUrl(null);
          setResult(null);
        } else {
          const blob = new Blob([res.data], { type: contentType || "image/png" });
          setImageUrl(URL.createObjectURL(blob));
          setHtmlContent(null);
          setResult(null);
        }
      }
    } catch (err) {
      alert("Error solving LP");
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", backgroundColor: "#90EE90", padding: "20px", borderRadius: "8px" }}>
      <h2>Linear Programming Solver</h2>

      <div>
        <label>Mode: </label>
        <select value={mode} onChange={e => setMode(e.target.value)}>
          <option value="numerical">Numerical</option>
          <option value="graphical">Graphical (2 variables)</option>
        </select>
      </div>

      <div>
        <label>Number of Variables: </label>
        <input
          type="number"
          value={nVars}
          min="1"
          onChange={e => {
            const n = parseInt(e.target.value);
            setNVars(n);
            setObjective(Array(n).fill(""));
            setConstraints([]);
          }}
        />
      </div>

      <ObjectiveForm
        nVars={nVars}
        objective={objective}
        setObjective={setObjective}
        sense={sense}
        setSense={setSense}
      />

      <ConstraintsForm
        nVars={nVars}
        constraints={constraints}
        setConstraints={setConstraints}
        nonneg={nonneg}
        setNonneg={setNonneg}
      />

      <button onClick={solve}>Solve</button>

      <ResultPanel result={result} imageUrl={imageUrl} />
    </div>
  );
}

export default App;
