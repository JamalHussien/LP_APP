import React from "react";

import WorkspaceShell from "../app/WorkspaceShell";
import Card from "../components/Card";
import LoadingState from "../components/LoadingState";
import GoldenSectionForm from "../services/gss/GoldenSectionForm";
import GoldenSectionResults from "../services/gss/GoldenSectionResults";
import useGoldenSectionForm from "../services/gss/useGoldenSectionForm";

function GSSWorkspace({ onBack }) {
  const gss = useGoldenSectionForm();
  const state = { ...gss, form: gss.form, loading: gss.loading, error: gss.error, result: gss.result };

  return (
    <WorkspaceShell
      title="Golden Section Search"
      description="Bracket a unimodal 1D optimum and shrink the interval until the tolerance is met."
      onBack={onBack}
    >
      <Card title="Configuration">
        <GoldenSectionForm state={state} actions={gss} />
      </Card>

      <Card title="Results and Convergence">
        {gss.loading && <LoadingState label="Running..." />}
        <GoldenSectionResults result={gss.result} />
      </Card>
    </WorkspaceShell>
  );
}

export default GSSWorkspace;
