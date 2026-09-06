"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { track } from "@/lib/analytics";

export function AnalyticsBootstrap() {
  const pathname = usePathname();

  useEffect(() => {
    track("page_viewed");
  }, [pathname]);

  return null;
}
