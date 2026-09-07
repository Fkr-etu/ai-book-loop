"use client";

import { useEffect, useState } from "react";
import { ANALYTICS_CONSENT_EVENT, ANALYTICS_CONSENT_KEY } from "@/lib/analytics";

const STORAGE_KEY = ANALYTICS_CONSENT_KEY;

type Consent = "accepted" | "rejected";

export function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(localStorage.getItem(STORAGE_KEY) === null);
  }, []);

  const save = (consent: Consent) => {
    localStorage.setItem(STORAGE_KEY, consent);
    window.dispatchEvent(new Event(ANALYTICS_CONSENT_EVENT));
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <aside className="fixed inset-x-4 bottom-4 z-[60] mx-auto max-w-2xl rounded-xl border border-[#c6c6cd]/50 bg-white p-5 shadow-xl" aria-label="Préférences de cookies">
      <h2 className="font-playfair text-lg font-bold text-[#0b1c30]">Vos préférences de confidentialité</h2>
      <p className="mt-2 text-xs leading-relaxed text-[#5f5e5b]">
        Book Loop utilise Google Analytics uniquement si vous acceptez les traceurs non nécessaires. Nous mesurons l&apos;usage du produit avec des événements techniques (par exemple création d&apos;un livre) et n&apos;envoyons pas le contenu de vos livres, votre Canon, vos prompts ou les réponses de l&apos;IA à Google Analytics.
      </p>
      <div className="mt-4 flex flex-wrap gap-2 justify-end">
        <button type="button" onClick={() => save("rejected")} className="rounded border border-[#c6c6cd] px-4 py-2 text-xs font-semibold text-[#45464d] hover:bg-[#f8f5f0]">Refuser</button>
        <button type="button" onClick={() => save("accepted")} className="rounded bg-[#0b1c30] px-4 py-2 text-xs font-semibold text-white hover:bg-[#131b2e]">Accepter</button>
      </div>
    </aside>
  );
}
