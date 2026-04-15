import { lazy } from "react";

const LPWorkspace = lazy(() => import("../workspaces/LPWorkspace"));
const SDWorkspace = lazy(() => import("../workspaces/SDWorkspace"));
const GSSWorkspace = lazy(() => import("../workspaces/GSSWorkspace"));

export const serviceRegistry = [
  {
    id: "lp",
    title: "Linear Programming",
    description: "Solve LPs numerically or with graphical visualization.",
    component: LPWorkspace,
  },
  {
    id: "sd",
    title: "Steepest Descent / Ascent",
    description: "Gradient-based minimization or maximization with constant or optimal step selection.",
    component: SDWorkspace,
  },
  {
    id: "gss",
    title: "Golden Section Search",
    description: "Unimodal 1D optimization with interval reduction and convergence tracking.",
    component: GSSWorkspace,
  },
];

export function getServiceById(serviceId) {
  return serviceRegistry.find((service) => service.id === serviceId) || null;
}
