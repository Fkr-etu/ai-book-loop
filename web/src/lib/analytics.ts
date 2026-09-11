"use client";

export const ANALYTICS_CONSENT_KEY = "book-loop-cookie-consent";
export const ANALYTICS_CONSENT_EVENT = "book-loop-analytics-consent-changed";

export type AnalyticsPlan = "free" | "creator" | "pro";

export type AnalyticsEvent =
  | "landing_viewed"
  | "signup_started"
  | "signup_completed"
  | "book_created"
  | "manuscript_import_started"
  | "document_ingested"
  | "canon_configured"
  | "analysis_started"
  | "analysis_completed"
  | "analysis_result_viewed"
  | "critical_eye_opened"
  | "critical_eye_message_sent"
  | "critical_eye_completed"
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
  issue_count?: number;
};

const GA4_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA4_MEASUREMENT_ID;

export function hasAnalyticsConsent(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(ANALYTICS_CONSENT_KEY) === "accepted";
}

export function isAnalyticsConfigured(): boolean {
  return Boolean(GA4_MEASUREMENT_ID);
}

export function canTrack(): boolean {
  return hasAnalyticsConsent() && isAnalyticsConfigured();
}

export function track(event: AnalyticsEvent, properties: EventProperties = {}): void {
  if (!canTrack() || typeof window.gtag !== "function") return;

  window.gtag("event", event, properties);
}

export function getGa4MeasurementId(): string | undefined {
  return GA4_MEASUREMENT_ID;
}
