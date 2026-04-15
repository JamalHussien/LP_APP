import React from "react";

import WorkspaceShell from "../app/WorkspaceShell";
import Card from "../components/Card";
import LoadingState from "../components/LoadingState";
import SteepestDescentForm from "../services/sd/SteepestDescentForm";
import SteepestDescentResults from "../services/sd/SteepestDescentResults";
import useSteepestDescentForm from "../services/sd/useSteepestDescentForm";

function SDWorkspace({ onBack }) {
  const sd = useSteepestDescentForm();
  const state = { ...sd, form: sd.form, loading: sd.loading, error: sd.error, result: sd.result };

  return (
    <WorkspaceShell
      title="Steepest Descent / Ascent"
      description="Run gradient-based minimization or maximization with constant or optimal step selection."
      onBack={onBack}
    >
      <Card title="Configuration">
        <SteepestDescentForm state={state} actions={sd} />
      </Card>

      <Card title="Results and Trajectory">
        {sd.loading && <LoadingState label="Running..." />}
        <SteepestDescentResults result={sd.result} />
      </Card>
    </WorkspaceShell>
  );
}

export default SDWorkspace;
