const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const buildUrl = (path) => `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;

export async function extractApiError(response) {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    const data = await response.json().catch(() => null);
    const message = data?.detail || data?.message;
    if (typeof message === "string" && message.trim()) {
      return message;
    }
    if (data) {
      return JSON.stringify(data);
    }
  }

  const text = await response.text().catch(() => "");
  return text || `HTTP ${response.status}`;
}

async function post(path, payload) {
  const response = await fetch(buildUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await extractApiError(response));
  }

  return response;
}

export async function postJson(path, payload) {
  const response = await post(path, payload);
  return response.json();
}

export async function postBlob(path, payload) {
  const response = await post(path, payload);
  return response.blob();
}

export { API_BASE_URL };
