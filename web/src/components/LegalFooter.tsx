import Link from "next/link";

export function LegalFooter() {
  return (
    <footer className="border-t border-[#c6c6cd]/30 mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex flex-col md:flex-row gap-4 items-center justify-between text-xs text-[#5f5e5b]">
        <p>© {new Date().getFullYear()} Book Loop — Tous droits réservés.</p>
        <nav aria-label="Informations légales" className="flex flex-wrap justify-center gap-x-5 gap-y-2">
          <Link className="hover:text-[#0b1c30] underline-offset-2 hover:underline" href="/mentions-legales">Mentions légales</Link>
          <Link className="hover:text-[#0b1c30] underline-offset-2 hover:underline" href="/politique-confidentialite">Confidentialité</Link>
          <Link className="hover:text-[#0b1c30] underline-offset-2 hover:underline" href="/cgv">CGV</Link>
          <Link className="hover:text-[#0b1c30] underline-offset-2 hover:underline" href="/parametres/abonnement">Abonnement</Link>
        </nav>
      </div>
    </footer>
  );
}
