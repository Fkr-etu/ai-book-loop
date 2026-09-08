"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { realApiClient } from "@/services/realApiClient";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    let cancelled = false;

    void realApiClient.getCurrentUser().then((user) => {
      if (cancelled) return;
      if (user) {
        setAuthorized(true);
        return;
      }

      const query = window.location.search;
      const destination = `${pathname}${query}`;
      window.location.assign(`/login?next=${encodeURIComponent(destination)}`);
    }).catch(() => {
      if (!cancelled) {
        const destination = `${pathname}${window.location.search}`;
        window.location.assign(`/login?next=${encodeURIComponent(destination)}`);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [pathname]);

  if (!authorized) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f8f5f0] px-4">
        <p className="text-sm text-[#76777d]">Vérification de votre session…</p>
      </main>
    );
  }

  return <>{children}</>;
}
