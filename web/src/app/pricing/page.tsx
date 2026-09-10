"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { ArrowRight, Check, Loader2 } from "lucide-react";
import { getApiClient } from "@/services/api";
import type { BackendSubscriptionPlan } from "@/types/api";

const plans = [
  { id: "free", name: "Free", subtitle: "Pour commencer une première histoire.", monthlyPrice: 0, yearlyPrice: 0, features: ["1 projet", "Création limitée", "Relire votre texte", "Votre univers conservé", "Historique limité"], popular: false },
  { id: "creator", name: "Creator", subtitle: "Pour écrire régulièrement et faire grandir vos histoires.", monthlyPrice: 19, yearlyPrice: 190, features: ["Jusqu'à 3 projets", "Création sans limite de projet", "Relire et améliorer vos textes", "Votre univers conservé", "Historique et versions", "Relecture et corrections"], popular: true },
  { id: "pro", name: "Pro", subtitle: "Pour les projets ambitieux et les univers qui évoluent beaucoup.", monthlyPrice: 39, yearlyPrice: 390, features: ["Jusqu'à 10 projets", "Création sans limite de projet", "Relecture renforcée", "Votre univers conservé", "Historique complet", "Relecture et corrections", "Traitement prioritaire", "Support prioritaire"], popular: false }
];

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");
  const [currentPlan, setCurrentPlan] = useState<BackendSubscriptionPlan | null>(null);
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    let active = true;
    void getApiClient().getCurrentUser().then((user) => {
      if (active) setCurrentPlan(user?.plan ?? null);
    }).catch(() => {
      if (active) setCurrentPlan(null);
    });
    return () => { active = false; };
  }, []);

  async function startCheckout(planId: string) {
    if (planId === "free") {
      if (currentPlan === "free") return;
      router.push("/register");
      return;
    }
    if (planId === currentPlan) return;
    setLoadingPlan(planId);
    setError(null);
    try {
      const api = getApiClient();
      const user = await api.getCurrentUser();
      if (!user) {
        router.push(`/register?plan=${planId}&billing=${billingCycle}`);
        return;
      }
      const url = await api.createCheckout(planId as "creator" | "pro", billingCycle);
      window.location.assign(url);
    } catch (checkoutError) {
      setError(checkoutError instanceof Error ? checkoutError.message : "Impossible de démarrer le paiement.");
    } finally {
      setLoadingPlan(null);
    }
  }

  const currentPlanName = plans.find((plan) => plan.id === currentPlan)?.name;

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-12 md:py-16 space-y-10">
        <header className="text-center max-w-3xl mx-auto space-y-4">
          <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Votre offre</p>
          <h1 className="font-playfair text-4xl sm:text-5xl font-bold text-[#0b1c30] tracking-tight">Une offre qui suit votre façon d’écrire.</h1>
          {currentPlanName ? (
            <div className="mx-auto max-w-xl rounded-xl bg-white border border-[#c6c6cd]/40 px-5 py-4 text-left shadow-xs">
              <p className="text-sm text-[#0b1c30] font-semibold">Vous bénéficiez actuellement de l’offre {currentPlanName}.</p>
              <p className="text-xs text-[#5f5e5b] mt-1">Vous pouvez passer à une offre supérieure quand votre projet le demande.</p>
            </div>
          ) : (
            <p className="text-sm sm:text-base text-[#45464d] leading-relaxed">Commencez gratuitement. Quand votre projet prend de l’ampleur, choisissez l’offre qui vous convient.</p>
          )}
          <div className="inline-flex items-center gap-1 rounded-full bg-white border border-[#c6c6cd]/50 p-1 text-xs font-semibold">
            <button type="button" onClick={() => setBillingCycle("monthly")} className={`px-4 py-2 rounded-full ${billingCycle === "monthly" ? "bg-[#0b1c30] text-white" : "text-[#45464d]"}`}>Mensuel</button>
            <button type="button" onClick={() => setBillingCycle("yearly")} className={`px-4 py-2 rounded-full ${billingCycle === "yearly" ? "bg-[#0b1c30] text-white" : "text-[#45464d]"}`}>Annuel <span className="text-[#b87500]">~2 mois offerts</span></button>
          </div>
          {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        </header>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 items-stretch">
          {plans.map((plan) => {
            const price = billingCycle === "monthly" ? plan.monthlyPrice : plan.yearlyPrice;
            const monthlyEquivalent = plan.yearlyPrice > 0 ? Math.round(plan.yearlyPrice / 12) : 0;
            const loading = loadingPlan === plan.id;
            const isCurrent = currentPlan === plan.id;
            const actionLabel = isCurrent ? "Offre actuelle" : plan.id === "free" ? "Commencer gratuitement" : `Passer à ${plan.name}`;
            return (
              <article key={plan.id} className={`rounded-2xl p-6 sm:p-8 flex flex-col justify-between relative ${plan.popular ? "bg-[#0b1c30] text-white shadow-xl ring-2 ring-[#b87500]" : "bg-white text-[#0b1c30] border border-[#c6c6cd]/40 shadow-xs"}`}>
                {plan.popular && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#ffddb8] text-[#2a1700] text-[11px] font-mono font-bold px-3 py-1 rounded-full uppercase tracking-wider whitespace-nowrap">Le plus populaire</div>}
                {isCurrent && <div className={`absolute top-4 right-4 text-[10px] font-mono font-bold uppercase tracking-wider ${plan.popular ? "text-[#ffddb8]" : "text-[#b87500]"}`}>Votre offre</div>}
                <div>
                  <h2 className="font-playfair text-2xl font-bold">{plan.name}</h2>
                  <p className={`text-xs mt-2 leading-relaxed ${plan.popular ? "text-[#cbd3e5]" : "text-[#5f5e5b]"}`}>{plan.subtitle}</p>
                  <div className="my-6 pb-6 border-b border-current/10">
                    {price === 0 ? <span className="font-playfair text-4xl font-bold">0 €</span> : billingCycle === "monthly" ? <><span className="font-playfair text-4xl font-bold">{price} €</span><span className="text-xs ml-1">/mois</span></> : <><span className="font-playfair text-4xl font-bold">{monthlyEquivalent} €</span><span className="text-xs ml-1">/mois</span><span className="block text-[10px] font-mono text-[#b87500] mt-1">{price} € facturés par an</span></>}
                  </div>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature) => <li key={feature} className="flex items-start gap-2.5 text-xs leading-normal"><Check className={`w-4 h-4 shrink-0 mt-0.5 ${plan.popular ? "text-[#ffddb8]" : "text-[#b87500]"}`} /><span className={plan.popular ? "text-[#eaf1ff]" : "text-[#45464d]"}>{feature}</span></li>)}
                  </ul>
                </div>
                <button type="button" onClick={() => void startCheckout(plan.id)} disabled={loading || isCurrent} className={`w-full py-3 rounded text-xs font-bold flex items-center justify-center gap-2 disabled:opacity-60 ${isCurrent ? "bg-[#e8e5df] text-[#5f5e5b] cursor-default" : plan.popular ? "bg-[#ffddb8] text-[#2a1700] hover:bg-[#ffb95e]" : "bg-[#0b1c30] text-white hover:bg-[#131b2e]"}`}>
                  {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : actionLabel}
                  {!loading && !isCurrent && <ArrowRight className="w-3.5 h-3.5" />}
                </button>
              </article>
            );
          })}
        </section>
        <p className="text-center text-xs text-[#5f5e5b] max-w-2xl mx-auto">Les fonctionnalités et limites exactes peuvent évoluer pendant la phase bêta. Les conditions commerciales définitives seront affichées avant toute souscription payante.</p>
      </main>
    </div>
  );
}
