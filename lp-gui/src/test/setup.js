import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

vi.mock("react-plotly.js", () => ({
  default: function Plot() {
    return null;
  },
}));

if (!globalThis.URL.createObjectURL) {
  globalThis.URL.createObjectURL = vi.fn(() => "blob:mock");
}

if (!globalThis.URL.revokeObjectURL) {
  globalThis.URL.revokeObjectURL = vi.fn();
}

if (!globalThis.confirm) {
  globalThis.confirm = () => true;
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
