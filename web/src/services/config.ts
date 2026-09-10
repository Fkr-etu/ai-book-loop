const DEFAULT_API_URL = "http://localhost:8000";

function normalizeBaseUrl(value: string): string {
  return value.replace(/\/+$/, "");
}

// Browser requests stay on the web origin so session cookies do not need
// cross-origin delivery. Server-side callers can still use the direct API URL.
export const API_BASE_URL =
  typeof window === "undefined"
    ? normalizeBaseUrl(process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL)
    : "";

// Real API is the safe default. CI explicitly opts into the deterministic mock API.
export const USE_REAL_API = process.env.NEXT_PUBLIC_USE_REAL_API !== "false";
