import Link from "next/link";

export const metadata = {
  title: "Guides d’écriture IA et cohérence narrative",
  description:
    "Guides pratiques pour écrire avec l’IA, construire une bible narrative et préserver la cohérence d’une histoire longue.",
};

const guides = [
  {
    slug: "ecrire-un-roman-avec-ia",
    title: "Écrire un roman avec l’IA : méthode complète pour garder la cohérence",
    description:
      "Une méthode concrète pour passer de l’idée au manuscrit sans laisser l’IA perdre les faits importants de votre histoire.",
  },
  {
    slug: "garder-coherence-roman-ia",
    title: "Comment garder la cohérence d’un roman écrit avec l’IA ?",
    description:
      "Personnages, chronologie, lieux et règles : les bonnes pratiques pour éviter les contradictions au fil des chapitres.",
  },
  {
    slug: "bible-narrative",
    title: "Qu’est-ce qu’une bible narrative ?",
    description:
      "Comprendre le rôle d’une bible narrative et pourquoi elle devient essentielle quand une histoire évolue sur la durée.",
  },
  {
    slug: "eviter-contradictions-roman",
    title: "Comment éviter les contradictions dans un roman ?",
    description:
      "Une approche simple pour repérer, vérifier et décider quoi faire lorsqu’un nouveau passage contredit l’histoire établie.",
  },
];

export default function GuidesPage() {
  return (
    <main className="min-h-screen bg-[#f8f5f0] text-[#0f172a]">
      <section className="max-w-5xl mx-auto px-4 sm:px-6 py-16 md:py-24">
        <Link href="/" className="text-sm font-semibold text-[#b87500]">← Book Loop</Link>
        <div className="max-w-3xl mt-10 space-y-5">
          <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Guides</p>
          <h1 className="font-playfair text-4xl sm:text-5xl font-bold text-[#0b1c30]">Écrire avec l’IA sans perdre le fil de votre histoire.</h1>
          <p className="text-lg text-[#45464d] leading-relaxed">Des méthodes pratiques pour écrire des histoires longues, préserver leur continuité et garder l’auteur aux commandes.</p>
        </div>
        <div className="grid md:grid-cols-2 gap-6 mt-14">
          {guides.map((guide) => (
            <article key={guide.slug} className="bg-white rounded-2xl border border-[#c6c6cd]/40 p-6">
              <h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">{guide.title}</h2>
              <p className="mt-3 text-sm text-[#45464d] leading-relaxed">{guide.description}</p>
              <Link href={`/guides/${guide.slug}`} className="inline-flex mt-5 text-sm font-bold text-[#0b1c30]">Lire le guide →</Link>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
