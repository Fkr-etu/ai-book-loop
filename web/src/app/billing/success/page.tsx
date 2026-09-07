"use client";

import Link from "next/link";
import { CheckCircle2 } from "lucide-react";
import { Navbar } from "@/components/Navbar";

export default function BillingSuccessPage() {
  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0b1c30]">
      <Navbar />
      <main className="max-w-xl mx-auto px-6 py-24 text-center space-y-6">
        <CheckCircle2 className="w-14 h-14 mx-auto text-[#b87500]" aria-hidden="true" />
        <h1 className="font-playfair text-4xl font-bold">Abonnement activé</h1>
        <p className="text-sm text-[#45464d] leading-relaxed">
          Merci. Stripe confirme votre paiement et Book Loop mettra à jour votre offre via son webhook. Vous pouvez revenir au Studio.
        </p>
        <Link href="/studio" className="inline-flex rounded px-5 py-3 bg-[#0b1c30] text-white text-sm font-bold">Retour au Studio</Link>
      </main>
    </div>
  );
}
