"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, CreditCard, Loader2 } from "lucide-react";
import { realApiClient } from "@/services/realApiClient";
import type { BackendBillingState, BackendUser } from "@/types/api";

const planLabels: Record<BackendBillingState["plan"], string> = {
  free: "Free",
  creator: "Creator",
  pro: "Pro",
};

export default function AccountPage() {
  const [user, setUser] = useState<BackendUser | null>(null);
  const [billing, setBilling] = useState<BackendBillingState | null>(null);
  const [loading, setLoading] = useState(true);
  const [openingPortal, setOpeningPortal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([realApiClient.getCurrentUser(), realApiClient.getBillingState()])
      .then(([currentUser, state]) => {
        if (!currentUser) {
          window.location.assign("/login");
          return;
        }
        setUser(currentUser);
        setBilling(state);
      })
      .catch((err: unknown) => {
        console.error("Unable to load account", err);
        setError("Impossible de charger votre abonnement.");
      })
      .finally(() => setLoading(false));
  }, []);

  const handlePortal = async () => {
    setOpeningPortal(true);
    setError(null);
    try {
      const { url } = await realApiClient.createBillingPortal();
      window.location.assign(url);
    } catch (err) {
      console.error("Unable to open billing portal", err);
      setError("Impossible d’ouvrir la gestion de l’abonnement.");
      setOpeningPortal(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#f8f5f0] px-4 py-10 sm:px-6">
      <div className="mx-auto max-w-2xl">
        <Link href="/dashboard" className="mb-8 inline-flex items-center gap-2 text-xs font-semibold text-[#0b1c30] hover:underline">
          <ArrowLeft className="h-3.5 w-3.5" /> Retour à mes livres
        </Link>

        <div className="rounded-2xl border border-[#c6c6cd]/40 bg-white p-6 shadow-xs sm:p-8">
          <p className="font-mono text-[10px] font-bold uppercase tracking-widest text-[#76777d]">Compte</p>
          <h1 className="mt-2 font-playfair text-3xl font-bold text-[#0b1c30]">Mon abonnement</h1>
          <p className="mt-2 text-sm text-[#5f5e5b]">Gérez votre formule et votre facturation depuis Stripe.</p>

          {loading ? (
            <div className="mt-8 flex items-center gap-2 text-sm text-[#76777d]"><Loader2 className="h-4 w-4 animate-spin" /> Chargement…</div>
          ) : billing ? (
            <section className="mt-8 rounded-xl border border-[#c6c6cd]/30 bg-[#f8f9ff] p-5">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-mono uppercase tracking-wider text-[#76777d]">Formule actuelle</p>
                  <p className="mt-1 text-xl font-bold text-[#0b1c30]">{planLabels[billing.plan]}</p>
                  {user && <p className="mt-1 text-xs text-[#5f5e5b]">{user.email}</p>}
                </div>
                <span className="rounded-full border border-[#c6c6cd]/40 bg-white px-3 py-1 text-xs font-semibold text-[#0b1c30]">
                  {billing.subscription_status === "active" ? "Active" : billing.subscription_status === "trialing" ? "Essai" : billing.subscription_status}
                </span>
              </div>

              {billing.subscription_current_period_end && (
                <p className="mt-4 text-xs text-[#5f5e5b]">
                  {billing.subscription_cancel_at_period_end ? "Fin de l’abonnement le " : "Prochaine échéance le "}
                  {new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(new Date(billing.subscription_current_period_end))}.
                </p>
              )}

              <div className="mt-5 flex flex-col gap-2 sm:flex-row">
                {billing.plan !== "free" ? (
                  <button type="button" onClick={handlePortal} disabled={openingPortal} className="inline-flex items-center justify-center gap-2 rounded bg-[#0b1c30] px-4 py-2.5 text-xs font-bold text-white disabled:opacity-50">
                    {openingPortal ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CreditCard className="h-3.5 w-3.5" />}
                    Gérer mon abonnement
                  </button>
                ) : (
                  <Link href="/pricing" className="inline-flex items-center justify-center gap-2 rounded bg-[#0b1c30] px-4 py-2.5 text-xs font-bold text-white">
                    <CreditCard className="h-3.5 w-3.5" /> Choisir une formule
                  </Link>
                )}
              </div>
            </section>
          ) : null}

          {error && <p role="alert" className="mt-4 rounded border border-[#d98980] bg-[#fff5f3] p-3 text-xs text-[#a33b32]">{error}</p>}
        </div>
      </div>
    </main>
  );
}
