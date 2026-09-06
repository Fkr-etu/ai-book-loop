"use client";

import { AlertTriangle, RefreshCw, X } from "lucide-react";
import { useProjectStore } from "@/lib/useProjectStore";

export function StudioErrorNotice() {
  const { error, clearError, refreshProject } = useProjectStore();

  if (!error) return null;

  const retry = async () => {
    clearError();
    await refreshProject();
  };

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="border-b border-[#d9aaaa] bg-[#fff4f4] px-4 py-3 text-[#5c2020]"
    >
      <div className="mx-auto flex max-w-7xl items-start gap-3 text-xs">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        <p className="min-w-0 flex-1 leading-relaxed">{error}</p>
        <div className="flex shrink-0 items-center gap-1">
          <button
            type="button"
            onClick={() => void retry()}
            className="inline-flex items-center gap-1.5 rounded border border-[#d9aaaa] bg-white px-2.5 py-1.5 font-semibold hover:bg-[#fffafa] focus:outline-none focus:ring-2 focus:ring-[#5c2020]/30 disabled:opacity-50"
            aria-label="Réessayer le chargement du projet"
          >
            <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
            Réessayer
          </button>
          <button
            type="button"
            onClick={clearError}
            className="rounded p-1.5 hover:bg-[#f9dddd] focus:outline-none focus:ring-2 focus:ring-[#5c2020]/30"
            aria-label="Fermer le message d'erreur"
          >
            <X className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
