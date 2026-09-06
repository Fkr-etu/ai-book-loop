"use client";

import Link from "next/link";
import { ArrowRight, Check, FileCheck2, GitPullRequest, ShieldCheck } from "lucide-react";
import { BrandMark } from "@/components/BrandMark";
import { Navbar } from "@/components/Navbar";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://book-loop-web-nddyzebo7a-od.a.run.app";

const structuredData = {
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "SoftwareApplication", name: "Book Loop", applicationCategory: "WritingApplication", operatingSystem: "Web", url: SITE_URL, inLanguage: "fr-FR", description: "Atelier d’écriture IA pour les histoires longues, avec un Canon narratif pour préserver la cohérence de l’univers au fil des chapitres." },
    { "@type": "WebSite", name: "Book Loop", url: SITE_URL, inLanguage: "fr-FR" },
  ],
};

const audiences = [
  ["Romanciers", "Faites avancer un récit long sans abandonner un détail important en chemin."],
  ["Scénaristes", "Suivez personnages, révélations et chronologie d'une version à l'autre."],
  ["Game Masters", "Préservez les conséquences de chaque session dans un monde vivant."],
];

const loopSteps = [
  ["Proposition", "Vous écrivez ou demandez une nouvelle version. Rien n'est encore une vérité.", FileCheck2],
  ["Vérification", "Les règles, le Canon et les points d'attention restent visibles avant la décision.", GitPullRequest],
  ["Décision", "Vous approuvez, faites réviser ou rejetez. Votre décision laisse une trace.", ShieldCheck],
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f7f2e9] text-[#13243a] font-inter">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />
      <Navbar />
      <main>
        <section className="relative overflow-hidden border-b border-[#d9d0c4]">
          <div className="max-w-6xl mx-auto px-5 sm:px-8 py-14 md:py-24 grid lg:grid-cols-[minmax(0,1fr)_25rem] gap-12 lg:gap-20 items-center">
            <div className="max-w-2xl">
              <div className="flex items-center gap-3 text-[#506070] text-sm mb-7">
                <BrandMark className="w-9 h-9 text-[#13243a] shrink-0" />
                <span>Le bureau de continuité pour les histoires qui durent.</span>
              </div>
              <h1 className="font-playfair text-[2.8rem] sm:text-6xl md:text-7xl font-bold tracking-[-0.045em] leading-[0.98] text-[#13243a]">
                Gardez le fil.<br />Gardez la main.
              </h1>
              <p className="mt-7 max-w-xl text-base sm:text-lg text-[#506070] leading-relaxed">
                Book Loop vous aide à écrire avec l’IA sans laisser une proposition devenir vérité par accident. Votre Canon conserve ce qui est établi. Vous décidez de la suite.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <Link href="/register" className="inline-flex min-h-11 px-5 py-3 rounded-md bg-[#13243a] text-white text-sm font-semibold items-center justify-center gap-2 hover:bg-[#203b5b]">
                  Créer mon premier projet <ArrowRight className="w-4 h-4" />
                </Link>
                <Link href="#la-boucle" className="inline-flex min-h-11 px-4 py-3 rounded-md text-[#13243a] text-sm font-semibold items-center justify-center underline underline-offset-4 decoration-[#9a6617]">
                  Voir comment fonctionne la boucle
                </Link>
              </div>
            </div>

            <aside className="bg-[#fffdfc] border border-[#d9d0c4] shadow-[8px_8px_0_#e8dfd2] p-5 sm:p-6">
              <div className="flex items-center justify-between pb-4 border-b border-[#e6ddd2]">
                <span className="font-mono text-[11px] text-[#506070]">CHAPITRE 12 · VERSION 3</span>
                <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full border border-[#9bbfd3] bg-[#dcebf3] text-[#24536d] text-[11px] font-semibold">
                  À votre décision
                </span>
              </div>
              <p className="font-playfair text-xl font-bold mt-5">La porte de l’observatoire</p>
              <p className="font-merriweather text-sm leading-6 text-[#506070] mt-2">« Élise revient à la tour avant l’aube. »</p>
              <div className="mt-5 border-l-2 border-[#9a6617] pl-3">
                <p className="text-xs font-semibold text-[#13243a]">Le Canon indique</p>
                <p className="text-xs leading-5 text-[#506070] mt-1">Élise a quitté la ville à la fin du chapitre 10. Vérifiez le trajet ou modifiez la proposition.</p>
              </div>
              <div className="mt-6 flex gap-2">
                <span className="px-2.5 py-1.5 rounded bg-[#9a6617] text-white text-[11px] font-semibold">Réviser</span>
                <span className="px-2.5 py-1.5 rounded border border-[#d9d0c4] text-[#506070] text-[11px]">Voir la preuve</span>
              </div>
            </aside>
          </div>
        </section>

        <section id="la-boucle" className="max-w-6xl mx-auto px-5 sm:px-8 py-16 md:py-24">
          <div className="max-w-2xl">
            <p className="text-sm text-[#9a6617] font-semibold">Une boucle qui protège votre univers</p>
            <h2 className="font-playfair text-3xl sm:text-5xl font-bold tracking-[-0.03em] mt-3">L’IA peut proposer. Elle ne peut pas décider à votre place.</h2>
            <p className="text-[#506070] leading-relaxed mt-5">Book Loop rend visible le passage entre un texte en cours, une vérification et une information approuvée. C’est ce qui permet au prochain chapitre de partir sur une base fiable.</p>
          </div>
          <ol className="mt-12 grid md:grid-cols-3 border-t border-[#d9d0c4]">
            {loopSteps.map(([title, description, Icon], index) => {
              const StepIcon = Icon as typeof FileCheck2;
              return (
                <li key={title as string} className="py-7 md:py-9 md:pr-8 md:border-r last:border-r-0 border-b md:border-b-0 border-[#d9d0c4]">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-[#9a6617]">0{index + 1}</span>
                    <StepIcon className="w-5 h-5 text-[#13243a]" />
                  </div>
                  <h3 className="font-playfair text-2xl font-bold mt-5">{title as string}</h3>
                  <p className="max-w-xs text-sm leading-6 text-[#506070] mt-2">{description as string}</p>
                </li>
              );
            })}
          </ol>
        </section>

        <section className="bg-[#13243a] text-[#fffdfc]">
          <div className="max-w-6xl mx-auto px-5 sm:px-8 py-16 md:py-20 grid lg:grid-cols-[0.85fr_1.15fr] gap-12 items-start">
            <div>
              <p className="text-[#e1b45d] text-sm font-semibold">Le Canon est une frontière de confiance</p>
              <h2 className="font-playfair text-3xl sm:text-5xl font-bold leading-tight mt-3">Ce qui est validé guide la suite. Le reste demeure une proposition.</h2>
            </div>
            <div className="space-y-0 border-t border-white/20">
              {[
                "Les faits approuvés gardent leur provenance.",
                "Les contradictions restent explicites jusqu’à votre décision.",
                "Les versions et les revues restent dans l’historique.",
                "Une IA ne modifie jamais silencieusement votre Canon.",
              ].map((item) => (
                <div key={item} className="py-4 border-b border-white/20 flex gap-3 text-sm leading-6 text-[#e4e9ef]">
                  <Check className="w-4 h-4 text-[#e1b45d] shrink-0 mt-1" />
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-5 sm:px-8 py-16 md:py-24">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 border-b border-[#d9d0c4] pb-8">
            <div className="max-w-2xl">
              <p className="text-sm text-[#9a6617] font-semibold">Conçu pour les univers qui évoluent</p>
              <h2 className="font-playfair text-3xl sm:text-5xl font-bold mt-3">Une mémoire qui suit votre récit, pas un chat qui oublie.</h2>
            </div>
            <Link href="/pricing" className="text-sm font-semibold underline underline-offset-4 decoration-[#9a6617]">Découvrir les offres</Link>
          </div>
          <div className="grid md:grid-cols-3 gap-x-10">
            {audiences.map(([title, description]) => (
              <article key={title} className="py-8 border-b border-[#d9d0c4]">
                <h3 className="font-playfair text-2xl font-bold">{title}</h3>
                <p className="text-sm text-[#506070] leading-6 mt-2">{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="bg-[#fffdfc] border-y border-[#d9d0c4]">
          <div className="max-w-4xl mx-auto px-5 sm:px-8 py-16 md:py-20 text-center">
            <BrandMark className="w-11 h-11 text-[#13243a] mx-auto" />
            <h2 className="font-playfair text-3xl sm:text-5xl font-bold tracking-[-0.03em] mt-6">Votre histoire mérite plus qu’un contexte oublié.</h2>
            <p className="text-[#506070] text-base leading-relaxed max-w-xl mx-auto mt-4">Commencez un projet, posez vos fondations, puis faites évoluer chaque chapitre en gardant une trace claire de ce qui devient vrai.</p>
            <Link href="/register" className="inline-flex min-h-11 px-5 py-3 rounded-md bg-[#13243a] text-white text-sm font-semibold items-center gap-2 mt-8 hover:bg-[#203b5b]">
              Commencer gratuitement <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
