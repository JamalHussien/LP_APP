import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import LPWorkspace from "./LPWorkspace";


describe("LPWorkspace", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, x: [1, 2], objective: 11 }),
    });
  });

  it("submits a numerical LP solve and renders the result", async () => {
    render(<LPWorkspace onBack={() => {}} />);

    fireEvent.change(screen.getByLabelText("c1"), { target: { value: "3" } });
    fireEvent.change(screen.getByLabelText("c2"), { target: { value: "5" } });
    fireEvent.click(screen.getByRole("button", { name: /^Solve$/i }));

    expect(await screen.findByText(/Numerical Result/i)).toBeInTheDocument();
    expect(screen.getByText(/"success": true/i)).toBeInTheDocument();
  });
});
