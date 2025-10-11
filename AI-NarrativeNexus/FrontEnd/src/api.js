const API_BASE = "http://127.0.0.1:8000/api"; // FastAPI backend

export async function fetchAPI(endpoint, method = "POST", body = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return await res.json();
}

// Specific wrappers
export const preprocessText = (text) =>
  fetchAPI("/preprocess", "POST", { text });

export const analyzeSentiment = (text) =>
  fetchAPI("/sentiment", "POST", { text });

export const runTopicModeling = (docs) =>
  fetchAPI("/topic", "POST", { docs });

export const summarizeText = (text) =>
  fetchAPI("/summarize", "POST", { text });
