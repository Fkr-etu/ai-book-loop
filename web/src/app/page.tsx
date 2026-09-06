import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
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
  "Auteur — Écrivez avec l’IA sans perdre le fil de votre roman.",
  "Scénariste — Faites évoluer votre scénario sans casser sa continuité.",
  "Game Master — Faites vivre une campagne évolutive sans perdre la mémoire de votre monde.",
];

const principles = [
  "Le Canon rassemble ce qui est établi dans votre histoire.",
  "Chaque nouvelle création est confrontée à ce qui existe déjà.",
  "L’IA propose des corrections ; vous restez l’autorité finale.",
  "Ce que vous validez devient la base des prochaines créations.",
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />
      <Navbar />
      <main>
        <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-16 pb-20 md:pt-24 md:pb-28">
          <div className="max-w-4xl mx-auto text-center space-y-6">
            <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">L’atelier d’écriture IA pour les histoires longues</p>
            <h1 className="font-playfair text-5xl sm:text-6xl md:text-7xl font-bold text-[#0b1c30] tracking-tight">Écrivez avec l’IA. Gardez votre histoire cohérente.</h1>
            <p className="max-w-2xl mx-auto text-base sm:text-lg text-[#45464d] leading-relaxed">Book Loop vous accompagne pour écrire et faire évoluer votre histoire avec l’IA, sans perdre la mémoire de votre univers.</p>
            <p className="max-w-2xl mx-auto text-sm sm:text-base font-semibold text-[#0b1c30]">Votre Canon garde la référence. L’IA propose. Vous décidez ce qui devient canon.</p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-3">
              <Link href="/register" className="w-full sm:w-auto px-6 py-3 rounded bg-[#0b1c30] text-white text-sm font-bold flex items-center justify-center gap-2 hover:bg-[#131b2e]">Commencer gratuitement <ArrowRight className="w-4 h-4" /></Link>
              <Link href="/pricing" className="w-full sm:w-auto px-6 py-3 rounded border border-[#0b1c30] text-[#0b1c30] text-sm font-semibold">Voir les tarifs</Link>
            </div>
          </div>
        </section>

        <section className="bg-white border-y border-[#c6c6cd]/40">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-20 grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-5">
              <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Le problème</p>
              <h2 className="font-playfair text-3xl sm:text-4xl font-bold text-[#0b1c30]">Plus votre histoire grandit, plus sa cohérence devient difficile à préserver.</h2>
              <p className="text-sm text-[#45464d] leading-relaxed">Personnages, lieux, événements, relations, règles de votre monde et intentions d’auteur s’accumulent. Une IA peut générer un chapitre convaincant tout en oubliant un détail établi plusieurs chapitres plus tôt.</p>
            </div>
            <div className="rounded-2xl bg-[#f8f5f0] p-7 border border-[#c6c6cd]/40 space-y-4">
              {["Une contradiction peut passer inaperçue.", "Un détail important peut être oublié.", "Une nouvelle version peut casser la continuité d’une ancienne."].map((item) => <div key={item} className="flex gap-3 text-sm text-[#45464d]"><span className="mt-1 h-2 w-2 rounded-full bg-[#b87500] shrink-0" />{item}</div>)}
            </div>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-20">
          <div className="max-w-3xl mx-auto text-center space-y-5">
            <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Le Canon</p>
            <h2 className="font-playfair text-3xl sm:text-4xl font-bold text-[#0b1c30]">L’IA oublie. Votre Canon, non.</h2>
            <p className="text-sm text-[#45464d] leading-relaxed">Book Loop construit une référence vivante de votre histoire : ce qui est établi, ce qui a été observé dans vos textes, ce qui est proposé et ce que vous avez validé. Le Canon devient la mémoire de référence utilisée pour faire évoluer votre univers.</p>
            <p className="font-semibold text-[#0b1c30]">L’IA ne décide pas de votre histoire. Elle vous aide à la construire sans la casser.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-4 max-w-4xl mx-auto mt-10">
            {principles.map((item, index) => <div key={item} className="bg-white rounded-xl border border-[#c6c6cd]/40 p-5 flex gap-4"><span className="font-mono text-xs text-[#b87500] mt-1">0{index + 1}</span><p className="text-sm text-[#45464d] leading-relaxed">{item}</p></div>)}
          </div>
        </section>

        <section className="bg-[#0b1c30] text-white">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-20">
            <div className="max-w-3xl mx-auto text-center space-y-4 mb-12">
              <p className="text-xs font-mono font-bold text-[#ffddb8] uppercase tracking-wider">Le cycle Book Loop</p>
              <h2 className="font-playfair text-3xl sm:text-4xl font-bold">Créer. Vérifier. Décider. Continuer.</h2>
              <p className="text-sm text-[#eaf1ff] leading-relaxed">Chaque chapitre s’inscrit dans une boucle où la génération, la vérification et la validation humaine renforcent progressivement la cohérence de votre histoire.</p>
            </div>
            <div className="grid md:grid-cols-4 gap-6">
              {["Écrivez — créez un chapitre, une scène ou un nouvel élément.", "Vérifiez — confrontez le nouveau contenu à ce qui est établi.", "Décidez — acceptez, corrigez ou rejetez les propositions.", "Continuez — votre univers validé devient la base des prochaines créations."].map((item, index) => <div key={item} className="rounded-xl border border-white/10 p-5"><div className="text-[#ffddb8] font-mono text-xs mb-3">0{index + 1}</div><p className="text-sm leading-relaxed text-[#eaf1ff]">{item}</p></div>)}
            </div>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-20">
          <div className="text-center space-y-4 mb-10">
            <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Pour qui ?</p>
            <h2 className="font-playfair text-3xl sm:text-4xl font-bold text-[#0b1c30]">Pour celles et ceux qui font évoluer des histoires complexes.</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {audiences.map((item) => <div key={item} className="bg-white rounded-2xl border border-[#c6c6cd]/40 p-6"><Check className="w-5 h-5 text-[#b87500] mb-4" /><p className="text-sm text-[#45464d] leading-relaxed">{item}</p></div>)}
          </div>
        </section>

        <section className="bg-white border-t border-[#c6c6cd]/40">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 py-16 text-center space-y-5">
            <h2 className="font-playfair text-3xl sm:text-4xl font-bold text-[#0b1c30]">Votre histoire mérite mieux qu’un contexte oublié.</h2>
            <p className="text-lg font-semibold text-[#0b1c30]">Book Loop garde votre univers en mémoire pour que vous puissiez continuer à créer.</p>
            <Link href="/register" className="inline-flex px-6 py-3 rounded bg-[#0b1c30] text-white text-sm font-bold items-center gap-2">Commencer gratuitement <ArrowRight className="w-4 h-4" /></Link>
          </div>
        </section>
      </main>
    </div>
  );
}
