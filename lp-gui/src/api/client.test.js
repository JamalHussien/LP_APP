import { describe, expect, it, vi } from "vitest";

import { API_BASE_URL, extractApiError, postJson } from "./client";


describe("api client", () => {
  it("posts JSON to the configured API base URL", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ success: true }),
    });

    const result = await postJson("/solve", { n: 2 });

    expect(result).toEqual({ success: true });
    expect(globalThis.fetch).toHaveBeenCalledWith(
      `${API_BASE_URL}/solve`,
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
    );
  });

  it("extracts error details from JSON responses", async () => {
    const message = await extractApiError({
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({ detail: "bad request" }),
      text: async () => "",
      status: 400,
    });

    expect(message).toBe("bad request");
  });
});
