import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";


describe("App", () => {
  it("renders the service selector and loads a workspace on selection", async () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: /Golden Section Search/i }));

    expect(await screen.findByRole("heading", { name: /Golden Section Search/i })).toBeInTheDocument();
  });
});
