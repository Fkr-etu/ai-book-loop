"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { ArrowRight, Check } from "lucide-react";

const plans = [
  { id: "free", name: "Free", subtitle: "Pour découvrir Book Loop sur un premier projet.", monthlyPrice: 0, yearlyPrice: 0, features: ["1 projet", "Création avec IA limitée", "Vérification de cohérence limitée", "Canon et univers persistant", "Historique limité"], popular: false },
  { id: "creator", name: "Creator", subtitle: "Pour les créateurs qui veulent travailler sérieusement avec l'IA.", monthlyPrice: 19, yearlyPrice: 190, features: ["Jusqu'à 3 projets", "Création avec IA", "Vérification de cohérence", "Canon et univers persistant", "Historique et versions", "Revue et corrections"], popular: true },
  { id: "pro", name: "Pro", subtitle: "Pour les projets ambitieux et les univers qui évoluent beaucoup.", monthlyPrice: 39, yearlyPrice: 390, features: ["Jusqu'à 10 projets", "Création avec IA", "Vérification de cohérence renforcée", "Canon et univers persistant", "Historique et versions complet", "Revue et corrections", "Priorité de traitement", "Support prioritaire"], popular: false }
];

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-12 md:py-16 space-y-12">
        <header className="text-center max-w-3xl mx-auto space-y-4">
          <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Tarifs simples, sans compteur de tokens</p>
          <h1 className="font-playfair text-4xl sm:text-5xl font-bold text-[#0b1c30] tracking-tight">Payez pour créer. Pas pour compter les tokens.</h1>
          <p className="text-sm sm:text-base text-[#45464d] leading-relaxed">Des limites d'utilisation équitables nous permettent de garder Book Loop rapide, prévisible et abordable. Vous pouvez changer ou arrêter votre abonnement à tout moment.</p>
          <div className="inline-flex items-center gap-1 rounded-full bg-white border border-[#c6c6cd]/50 p-1 text-xs font-semibold">
            <button type="button" onClick={() => setBillingCycle("monthly")} className={`px-4 py-2 rounded-full ${billingCycle === "monthly" ? "bg-[#0b1c30] text-white" : "text-[#45464d]"}`}>Mensuel</button>
            <button type="button" onClick={() => setBillingCycle("yearly")} className={`px-4 py-2 rounded-full ${billingCycle === "yearly" ? "bg-[#0b1c30] text-white" : "text-[#45464d]"}`}>Annuel <span className="text-[#b87500]">~2 mois offerts</span></button>
          </div>
        </header>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 items-stretch">
          {plans.map((plan) => {
            const price = billingCycle === "monthly" ? plan.monthlyPrice : plan.yearlyPrice;
            const monthlyEquivalent = plan.yearlyPrice > 0 ? Math.round(plan.yearlyPrice / 12) : 0;
            return (
              <article key={plan.id} className={`rounded-2xl p-6 sm:p-8 flex flex-col justify-between relative ${plan.popular ? "bg-[#0b1c30] text-white shadow-xl ring-2 ring-[#b87500]" : "bg-white text-[#0b1c30] border border-[#c6c6cd]/40 shadow-xs"}`}>
                {plan.popular && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#ffddb8] text-[#2a1700] text-[11px] font-mono font-bold px-3 py-1 rounded-full uppercase tracking-wider whitespace-nowrap">Le plus populaire</div>}
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
                <Link href="/register" className={`w-full py-3 rounded text-xs font-bold flex items-center justify-center gap-2 ${plan.popular ? "bg-[#ffddb8] text-[#2a1700] hover:bg-[#ffb95e]" : "bg-[#0b1c30] text-white hover:bg-[#131b2e]"}`}>
                  {plan.id === "free" ? "Commencer gratuitement" : "Commencer"}<ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </article>
            );
          })}
        </section>
        <p className="text-center text-xs text-[#5f5e5b] max-w-2xl mx-auto">Les fonctionnalités et limites exactes peuvent évoluer pendant la phase bêta. Les conditions commerciales définitives seront affichées avant toute souscription payante.</p>
      </main>
    </div>
  );
}
