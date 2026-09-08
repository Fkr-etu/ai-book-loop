"use client";

import { useEffect, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { realApiClient } from "@/services/realApiClient";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    let cancelled = false;

    void realApiClient.getCurrentUser().then((user) => {
      if (cancelled) return;
      if (user) {
        setAuthorized(true);
        return;
      }

      const query = searchParams.toString();
      const destination = query ? `${pathname}?${query}` : pathname;
      window.location.assign(`/login?next=${encodeURIComponent(destination)}`);
    }).catch(() => {
      if (!cancelled) {
        window.location.assign(`/login?next=${encodeURIComponent(pathname)}`);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [pathname, searchParams]);

  if (!authorized) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f8f5f0] px-4">
        <p className="text-sm text-[#76777d]">Vérification de votre session…</p>
      </main>
    );
  }

  return <>{children}</>;
}
