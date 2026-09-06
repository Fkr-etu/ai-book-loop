"use client";

export const ANALYTICS_CONSENT_KEY = "book-loop-cookie-consent";

export type AnalyticsPlan = "free" | "creator" | "pro";

export type AnalyticsEvent =
  | "page_viewed"
  | "signup_started"
  | "signup_completed"
  | "book_created"
  | "canon_configured"
  | "chapter_generation_started"
  | "chapter_generation_completed"
  | "chapter_reviewed"
  | "chapter_approved"
  | "chapter_correction_requested"
  | "subscription_checkout_started"
  | "subscription_started"
  | "subscription_cancelled";

type EventProperties = {
  plan?: AnalyticsPlan;
  chapter_number?: number;
  generation_status?: "success" | "failure";
};

const PLAUSIBLE_ENDPOINT = process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT;
const PLAUSIBLE_DOMAIN = process.env.NEXT_PUBLIC_ANALYTICS_DOMAIN;

function hasAnalyticsConsent(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(ANALYTICS_CONSENT_KEY) === "accepted";
}

export function track(event: AnalyticsEvent, properties: EventProperties = {}): void {
  if (!hasAnalyticsConsent() || !PLAUSIBLE_ENDPOINT || !PLAUSIBLE_DOMAIN) return;

  const payload = {
    name: event,
    domain: PLAUSIBLE_DOMAIN,
    url: window.location.href,
    props: properties,
  };

  void fetch(PLAUSIBLE_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    keepalive: true,
  }).catch(() => {
    // Analytics must never affect the product flow.
  });
}

export function isAnalyticsConfigured(): boolean {
  return Boolean(PLAUSIBLE_ENDPOINT && PLAUSIBLE_DOMAIN);
}
