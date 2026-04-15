import React from "react";

import WorkspaceShell from "../app/WorkspaceShell";
import Card from "../components/Card";
import ConstraintList from "../components/ConstraintList";
import ObjectiveEditor from "../components/ObjectiveEditor";
import ResultPanel from "../components/ResultPanel";
import useLPForm from "../hooks/useLPForm";

function LPWorkspace({ onBack }) {
  const { state, actions } = useLPForm();

  return (
    <WorkspaceShell
      title="Linear Programming"
      description="Set up your LP, then solve numerically or graphically."
      onBack={onBack}
    >
      <Card title="Problem Setup">
        <div className="form-grid" style={{ gap: "16px" }}>
          <div>
            <div className="label">Mode</div>
            <select className="select" value={state.mode} onChange={(e) => actions.setMode(e.target.value)}>
              <option value="numerical">Numerical</option>
              <option value="graphical">Graphical (2 or 3 vars)</option>
            </select>
            <div className="helper">Graphical is limited to 3 variables.</div>
          </div>

          <div>
            <div className="label">Number of Variables</div>
            <input
              type="number"
              min="1"
              value={state.numVars}
              className="input"
              onChange={(e) => actions.changeNumVars(parseInt(e.target.value, 10))}
            />
            <div className="helper">Adjusts the objective and constraint dimensions.</div>
          </div>

          <label className="label" style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input
              type="checkbox"
              checked={state.nonNegative}
              onChange={() => actions.setNonNegative(!state.nonNegative)}
              style={{ width: 16, height: 16 }}
            />
            Variables &gt;= 0
          </label>
        </div>
      </Card>

      <Card title="Objective Function">
        <ObjectiveEditor
          coeffs={state.objective}
          onChangeCoeff={actions.updateObjective}
          sense={state.sense}
          onSenseChange={actions.setSense}
          errors={state.objectiveErrors}
        />
      </Card>

      <Card
        title="Constraints"
        action={
          <button type="button" className="btn btn-ghost" onClick={actions.addConstraint}>
            Add Constraint
          </button>
        }
      >
        <ConstraintList
          constraints={state.constraints}
          onRemove={(idx) => actions.removeConstraint(idx)}
          onChangeCoeff={actions.updateConstraintCoeff}
          onChangeSense={actions.updateConstraintSense}
          onChangeRhs={actions.updateConstraintRhs}
          errors={state.constraintErrors}
        />
      </Card>

      <Card title="Solve and Results">
        <div className="form-grid" style={{ gap: "16px" }}>
          <button onClick={actions.submit} className="btn btn-primary" disabled={state.loading}>
            {state.loading ? "Solving..." : "Solve"}
          </button>
          <ResultPanel state={state} />
        </div>
      </Card>
    </WorkspaceShell>
  );
}

export default LPWorkspace;
