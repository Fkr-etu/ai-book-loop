"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import {
  ANALYTICS_CONSENT_EVENT,
  ANALYTICS_CONSENT_KEY,
  canTrack,
  getGa4MeasurementId,
  track,
} from "@/lib/analytics";

const GA_SCRIPT_ID = "book-loop-ga4-script";

function loadGa4(): void {
  const measurementId = getGa4MeasurementId();
  if (!measurementId || !canTrack() || document.getElementById(GA_SCRIPT_ID)) return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag(...args: unknown[]) {
    window.dataLayer.push(args);
  };
  window.gtag("js", new Date());
  window.gtag("config", measurementId, { send_page_view: false });

  const script = document.createElement("script");
  script.id = GA_SCRIPT_ID;
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
  document.head.appendChild(script);
}

export function AnalyticsBootstrap() {
  const pathname = usePathname();

  useEffect(() => {
    const onConsentChange = () => {
      loadGa4();
      if (pathname === "/") track("landing_viewed");
    };

    if (window.localStorage.getItem(ANALYTICS_CONSENT_KEY) === "accepted") {
      loadGa4();
    }

    window.addEventListener(ANALYTICS_CONSENT_EVENT, onConsentChange);
    return () => window.removeEventListener(ANALYTICS_CONSENT_EVENT, onConsentChange);
  }, [pathname]);

  useEffect(() => {
    if (pathname === "/") {
      track("landing_viewed");
    }
  }, [pathname]);

  return null;
}
