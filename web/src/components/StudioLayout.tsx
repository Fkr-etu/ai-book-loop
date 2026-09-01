"use client";

import React from "react";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { ProjectProvider } from "@/lib/useProjectStore";

export function StudioLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProjectProvider>
      <div className="min-h-screen bg-[#f8f9ff] flex flex-col font-inter">
        <Navbar />
        <div className="flex-1 flex">
          <Sidebar />
          <main className="flex-1 overflow-x-hidden min-h-[calc(100vh-61px)]">
            {children}
          </main>
        </div>
      </div>
    </ProjectProvider>
  );
}
