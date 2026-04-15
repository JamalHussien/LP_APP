// Helpers to keep UI values as strings while allowing interim states like "-" or "."
export const coerceNumber = (s) => {
  if (s === "" || s === "-" || s === "." || s === "-.") return { value: null, error: null };
  const n = Number(s);
  if (Number.isFinite(n)) return { value: n, error: null };
  return { value: null, error: "Not a number" };
};

export const normalizeInput = (s) => (s === undefined || s === null ? "" : String(s));
