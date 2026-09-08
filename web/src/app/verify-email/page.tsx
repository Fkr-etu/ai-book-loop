"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { getApiClient } from "@/services/api";

export default function VerifyEmailPage() {
  const params = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    const token = params.get("token");
    if (!token) {
      setStatus("error");
      return;
    }
    getApiClient()
      .verifyEmail(token)
      .then(() => setStatus("success"))
      .catch(() => setStatus("error"));
  }, [params]);

  return (
    <main className="min-h-screen bg-[#f8f5f0] text-[#0f172a] flex items-center justify-center p-6">
      <section className="w-full max-w-md bg-white rounded-xl shadow-sm border border-[#c6c6cd]/30 p-8 text-center">
        {status === "loading" && <><h1 className="font-playfair text-2xl font-bold mb-3">Vérification en cours</h1><p className="text-sm text-[#45464d]">Nous confirmons votre adresse e-mail…</p></>}
        {status === "success" && <><h1 className="font-playfair text-2xl font-bold mb-3">Adresse e-mail vérifiée</h1><p className="text-sm text-[#45464d] mb-6">Votre compte est maintenant confirmé.</p><Link href="/studio" className="inline-flex bg-[#0f172a] text-white font-semibold text-sm px-5 py-3 rounded">Accéder à mon espace</Link></>}
        {status === "error" && <><h1 className="font-playfair text-2xl font-bold mb-3">Lien invalide ou expiré</h1><p className="text-sm text-[#45464d] mb-6">Demandez un nouveau lien de vérification depuis votre compte.</p><Link href="/login" className="font-semibold text-[#0f172a] hover:underline">Retour à la connexion</Link></>}
      </section>
    </main>
  );
}
