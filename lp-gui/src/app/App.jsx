import React, { Suspense, useMemo, useState } from "react";

import LoadingState from "../components/LoadingState";
import SelectionScreen from "./SelectionScreen";
import { getServiceById, serviceRegistry } from "./serviceRegistry";

function App() {
  const [serviceId, setServiceId] = useState(null);
  const activeService = useMemo(() => getServiceById(serviceId), [serviceId]);

  if (!activeService) {
    return <SelectionScreen services={serviceRegistry} onSelect={setServiceId} />;
  }

  const Workspace = activeService.component;

  return (
    <Suspense
      fallback={
        <div className="page">
          <LoadingState label="Loading workspace..." />
        </div>
      }
    >
      <Workspace onBack={() => setServiceId(null)} />
    </Suspense>
  );
}

export default App;
