import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SDWorkspace from "./SDWorkspace";


describe("SDWorkspace", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        points: [[0, 0], [0.5, 0.5]],
        f_values: [2, 0.5],
        grad_norms: [2, 1],
        grads: [[2, 2], [1, 1]],
        alphas: [0.25],
        step_modes: ["constant"],
        fallback_reasons: [null],
        success: true,
        message: "Gradient tolerance reached",
        plot: null,
        variables: ["x", "y"],
      }),
    });
  });

  it("submits steepest descent and renders the convergence state", async () => {
    render(<SDWorkspace onBack={() => {}} />);

    expect(screen.getByRole("button", { name: /Minimize/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Run Gradient Search/i }));

    expect(await screen.findByText(/Converged:/i)).toBeInTheDocument();
    expect(screen.getByText(/Gradient tolerance reached/i)).toBeInTheDocument();
  });

  it("submits the selected maximize sense", async () => {
    render(<SDWorkspace onBack={() => {}} />);

    fireEvent.click(screen.getByRole("button", { name: /Maximize/i }));
    fireEvent.click(screen.getByRole("button", { name: /Run Gradient Search/i }));

    await screen.findByText(/Converged:/i);

    const [, request] = globalThis.fetch.mock.calls[0];
    const payload = JSON.parse(request.body);
    expect(payload.sense).toBe("maximize");
  });
});
