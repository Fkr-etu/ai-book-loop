"use client";

import React, { Suspense, useState } from "react";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { StudioErrorNotice } from "./StudioErrorNotice";
import { StudioBookSelector } from "./StudioBookSelector";
import { AuthGuard } from "./AuthGuard";

export function StudioLayout({ children }: { children: React.ReactNode }) {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#f8f9ff] flex flex-col font-inter">
        <Suspense fallback={null}>
          <StudioBookSelector />
        </Suspense>
        <Navbar
          showSidebarToggle={true}
          onToggleSidebar={() => setMobileSidebarOpen(!mobileSidebarOpen)}
        />
        <StudioErrorNotice />
        <div className="flex-1 flex relative">
          <div className="hidden md:block w-[280px] shrink-0 bg-[#eff4ff]/60 border-r border-[#c6c6cd]/30 h-[calc(100vh-61px)] sticky top-[61px]">
            <Sidebar />
          </div>

          {mobileSidebarOpen && (
            <div className="fixed inset-0 z-50 flex md:hidden">
              <div
                className="fixed inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
                onClick={() => setMobileSidebarOpen(false)}
              />
              <div className="relative w-[280px] max-w-[80vw] bg-[#f8f9ff] h-full shadow-2xl z-10 border-r border-[#c6c6cd]/40">
                <Sidebar onCloseMobile={() => setMobileSidebarOpen(false)} />
              </div>
            </div>
          )}

          <main className="flex-1 min-w-0 overflow-x-hidden min-h-[calc(100vh-61px)]">
            {children}
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
