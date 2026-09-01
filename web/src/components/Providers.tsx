"use client";

import React from "react";
import { ProjectProvider } from "@/lib/useProjectStore";

export function Providers({ children }: { children: React.ReactNode }) {
  return <ProjectProvider>{children}</ProjectProvider>;
}
