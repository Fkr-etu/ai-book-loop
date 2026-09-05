"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import {
  Sparkles,
  Check,
  Feather,
  BookOpen,
  Zap,
  HelpCircle,
  ArrowRight,
  ShieldCheck
} from "lucide-react";

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("yearly");

  const plans = [
    {
      id: "standard",
      name: "Auteur Indépendant",
      subtitle: "Pour les écrivains qui découvrent l'assistance IA",
      monthlyPrice: 24,
      yearlyPrice: 19,
      popular: false,
      features: [
        "Jusqu'à 1 projet de livre actif",
        "50 000 mots générés par mois",
        "Agent Critique Standard",
        "Bible du Monde (15 fiches max)",
        "Export Markdown & Plain Text",
        "Support e-mail"
      ]
    },
    {
      id: "pro",
      name: "Architecte Littéraire",
      subtitle: "Pour les auteurs chevronnés exigeant une continuité stricte",
      monthlyPrice: 59,
      yearlyPrice: 49,
      popular: true,
      features: [
        "Projets de livres illimités",
        "Génération de mots illimitée",
        "Agents Multiples (Writer, Reviewer, Summarizer)",
        "Graphe de Relations Lore Interactif",
        "Linter Déterministe Personnalisé",
        "Génération de Chapitre séquentiel sous contrôle",
        "Export EPUB, PDF & Markdown Studio",
        "Support Prioritaire Auteur"
      ]
    },
    {
      id: "elite",
      name: "Maison d'Édition",
      subtitle: "Pour les studios de création et équipes d'édition",
      monthlyPrice: 179,
      yearlyPrice: 149,
      popular: false,
      features: [
        "Tout l'accès Pro Architecte",
        "Multi-utilisateurs & Co-écriture",
        "Entraînement sur le style de votre Maison",
        "Modèles LLM dédiés à faible latence",
        "Garantie de Confidentialité Stricte (No Train)",
        "Accompagnement par un Ingénieur Prompt Littéraire"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter selection:bg-[#ffddb8] selection:text-[#0f172a]">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 md:py-12 space-y-8 md:space-y-12">
        {/* Header Hero */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider inline-flex items-center gap-1.5 px-3 py-1 bg-[#ffddb8]/40 rounded-full border border-[#b87500]/30">
            <Sparkles className="w-3.5 h-3.5 text-[#b87500]" /> Offres & Abonnements
          </span>
          <h1 className="font-playfair text-3xl sm:text-4xl md:text-5xl font-bold text-[#0b1c30] tracking-tight">
            Investissez dans la clarté de vos récits
          </h1>
          <p className="text-xs sm:text-sm md:text-base text-[#45464d] leading-relaxed">
            Profitez de la puissance de l'IA sans compromettre la noblesse de votre prose. Sans engagement, annulez à tout moment.
          </p>

          {/* Billing Cycle Toggle */}
          <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
            <span
              className={`text-xs font-semibold ${
                billingCycle === "monthly" ? "text-[#0b1c30]" : "text-[#76777d]"
              }`}
            >
              Facturation Mensuelle
            </span>
            <button
              type="button"
              onClick={() =>
                setBillingCycle(billingCycle === "monthly" ? "yearly" : "monthly")
              }
              className="w-12 h-6 bg-[#0b1c30] rounded-full p-1 transition-colors relative cursor-pointer"
            >
              <div
                className={`w-4 h-4 bg-[#ffddb8] rounded-full transition-transform ${
                  billingCycle === "yearly" ? "translate-x-6" : "translate-x-0"
                }`}
              />
            </button>
            <span
              className={`text-xs font-semibold flex items-center gap-1.5 ${
                billingCycle === "yearly" ? "text-[#0b1c30]" : "text-[#76777d]"
              }`}
            >
              Facturation Annuelle
              <span className="text-[10px] font-mono bg-[#ffddb8] text-[#2a1700] font-bold px-1.5 py-0.5 rounded">
                -20% Réduction
              </span>
            </span>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 items-stretch">
          {plans.map((plan) => {
            const price = billingCycle === "yearly" ? plan.yearlyPrice : plan.monthlyPrice;
            return (
              <div
                key={plan.id}
                className={`rounded-2xl p-6 sm:p-8 flex flex-col justify-between transition-all relative ${
                  plan.popular
                    ? "bg-[#0b1c30] text-white shadow-xl ring-2 ring-[#b87500]"
                    : "bg-white text-[#0b1c30] border border-[#c6c6cd]/40 shadow-xs hover:border-[#b87500]/50"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-[#ffddb8] text-[#2a1700] text-[11px] font-mono font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-xs whitespace-nowrap">
                    Recommandé par les Auteurs
                  </div>
                )}

                <div>
                  <div className="mb-6">
                    <h2
                      className={`font-playfair text-xl sm:text-2xl font-bold ${
                        plan.popular ? "text-white" : "text-[#0b1c30]"
                      }`}
                    >
                      {plan.name}
                    </h2>
                    <p
                      className={`text-xs mt-1 leading-relaxed ${
                        plan.popular ? "text-[#7c839b]" : "text-[#5f5e5b]"
                      }`}
                    >
                      {plan.subtitle}
                    </p>
                  </div>

                  <div className="mb-6 pb-6 border-b border-[#c6c6cd]/20">
                    <div className="flex items-baseline gap-1">
                      <span className="font-playfair text-3xl sm:text-4xl font-bold">
                        {price}€
                      </span>
                      <span
                        className={`text-xs font-mono ${
                          plan.popular ? "text-[#7c839b]" : "text-[#76777d]"
                        }`}
                      >
                        /mois
                      </span>
                    </div>
                    {billingCycle === "yearly" && (
                      <span className="text-[10px] font-mono text-[#b87500] mt-1 block">
                        Facturé annuellement ({price * 12}€/an)
                      </span>
                    )}
                  </div>

                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feat, idx) => (
                      <li key={idx} className="flex items-start gap-2.5 text-xs leading-normal">
                        <Check
                          className={`w-4 h-4 shrink-0 mt-0.5 ${
                            plan.popular ? "text-[#ffddb8]" : "text-[#b87500]"
                          }`}
                        />
                        <span className={plan.popular ? "text-[#eaf1ff]" : "text-[#45464d]"}>
                          {feat}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                <Link
                  href="/register"
                  className={`w-full py-3 rounded text-xs font-bold flex items-center justify-center gap-2 transition-colors ${
                    plan.popular
                      ? "bg-[#ffddb8] text-[#2a1700] hover:bg-[#ffb95e]"
                      : "bg-[#0b1c30] text-white hover:bg-[#131b2e]"
                  }`}
                >
                  <span>S'abonner Maintenant</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            );
          })}
        </div>

        {/* Guarantee Banner */}
        <div className="p-5 sm:p-6 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-4">
            <div className="w-12 h-12 rounded-full bg-[#eff4ff] text-[#0b1c30] flex items-center justify-center shrink-0">
              <ShieldCheck className="w-6 h-6 text-[#b87500]" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#0b1c30]">
                Garantie de Propriété Littéraire à 100%
              </h3>
              <p className="text-xs text-[#45464d] mt-0.5">
                Vous conservez l'intégralité des droits d'auteur sur les textes générés et vos univers canoniques. Vos données ne sont jamais revendues.
              </p>
            </div>
          </div>
          <Link
            href="/studio"
            className="w-full sm:w-auto px-4 py-2 border border-[#0b1c30] text-[#0b1c30] rounded text-xs font-semibold hover:bg-[#eff4ff] shrink-0 text-center"
          >
            Tester l'Atelier Gratuitement
          </Link>
        </div>
      </main>
    </div>
  );
}
