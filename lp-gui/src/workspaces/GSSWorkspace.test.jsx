import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import GSSWorkspace from "./GSSWorkspace";


describe("GSSWorkspace", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        x_star: 2,
        fx_star: 0,
        iterations: 1,
        termination_reason: "Interval width below tolerance.",
        history: [
          {
            iteration: 0,
            xl: 0,
            xu: 5,
            x1: 3.0901699437494745,
            x2: 1.9098300562505255,
            fx1: 1.1884705062547325,
            fx2: 0.008130618755783399,
            intervalWidth: 5,
            currentBestX: 1.9098300562505255,
            currentBestFx: 0.008130618755783399,
          },
        ],
        success: true,
        plot: null,
        variable: "x",
      }),
    });
  });

  it("submits golden section search and renders the summary", async () => {
    render(<GSSWorkspace onBack={() => {}} />);

    fireEvent.click(screen.getByRole("button", { name: /Run Golden Section Search/i }));

    expect(await screen.findByText(/Estimated optimum x\*/i)).toBeInTheDocument();
    expect(screen.getByText(/Converged:/i)).toBeInTheDocument();
  });
});
