import Link from "next/link";
import { LegalFooter } from "@/components/LegalFooter";

export const metadata = { title: "Gérer mon abonnement" };

export default function SubscriptionSettingsPage() {
  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-12 md:py-16">
        <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider mb-3">Compte · Abonnement</p>
        <h1 className="font-playfair text-4xl font-bold text-[#0b1c30]">Gérer mon abonnement</h1>
        <section className="mt-8 bg-white border border-[#c6c6cd]/40 rounded-2xl p-6 sm:p-8 space-y-6">
          <div>
            <h2 className="font-playfair text-xl font-bold">Gestion de l’abonnement</h2>
            <p className="mt-2 text-sm text-[#5f5e5b]">Les abonnements payants sont gérés par le parcours de facturation intégré et le portail client du prestataire de paiement lorsque cette option est disponible pour votre compte.</p>
          </div>
          <div className="rounded-lg border border-dashed border-[#c6c6cd] p-4 text-xs text-[#5f5e5b]">La disponibilité des actions de gestion dépend de l’état de votre abonnement et des fonctionnalités exposées par le portail de facturation. Aucun changement n’est simulé par cette page.</div>
          <div className="flex flex-wrap gap-3">
            <Link href="/cgv" className="rounded bg-[#0b1c30] px-4 py-2 text-xs font-semibold text-white">Consulter les CGV</Link>
            <Link href="/politique-confidentialite" className="rounded border border-[#c6c6cd] px-4 py-2 text-xs font-semibold text-[#45464d]">Confidentialité</Link>
          </div>
        </section>
      </main>
      <LegalFooter />
    </div>
  );
}
