import axios from 'axios';

// NEVER put GEMINI_API_KEY here. All AI calls happen in the Python backend.
const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export async function runAnalysis() {
  const response = await axios.get(`${BASE_URL}/api/analyze`);
  return response.data;
  // Returns: { ops: [...], business: {...}, caretaker: [...] }
}

export async function getHealth() {
  const response = await axios.get(`${BASE_URL}/health`);
  return response.data;
}

export async function getStatus() {
  // Pings Gemini with a tiny request to confirm AI is reachable
  const response = await axios.get(`${BASE_URL}/api/status`);
  return response.data;
}
