import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { Navbar } from "@/components/Navbar";

const audiences = [
  "Auteur — Écrivez avec l'IA sans perdre le fil de votre roman.",
  "Scénariste — Faites évoluer votre scénario sans casser sa continuité.",
  "Game Master — Faites vivre une campagne évolutive sans perdre la mémoire de votre monde."
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <Navbar />
      <main>
        <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-16 pb-20 md:pt-24 md:pb-28">
          <div className="max-w-4xl mx-auto text-center space-y-6">
            <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Le moteur de cohérence narrative</p>
            <h1 className="font-playfair text-5xl sm:text-6xl md:text-7xl font-bold text-[#0b1c30] tracking-tight">Écrivez avec l&apos;IA. Gardez votre histoire cohérente.</h1>
            <p className="max-w-2xl mx-auto text-base sm:text-lg text-[#45464d] leading-relaxed">Book Loop aide les auteurs, scénaristes et game masters à faire évoluer leur univers sans perdre le fil.</p>
            <p className="max-w-2xl mx-auto text-sm sm:text-base font-semibold text-[#0b1c30]">Votre univers grandit. Book Loop veille à ce qu&apos;il reste cohérent.</p>
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
              <h2 className="font-playfair text-3xl sm:text-4xl font-bold text-[#0b1c30]">Plus votre histoire grandit, plus il devient difficile de tout garder en tête.</h2>
              <p className="text-sm text-[#45464d] leading-relaxed">Personnages, lieux, événements, relations, règles de votre monde. L&apos;IA peut vous aider à écrire, mais elle ne sait pas toujours ce qui est réellement établi dans votre univers — ni ce qui vient de changer.</p>
            </div>
            <div className="rounded-2xl bg-[#f8f5f0] p-7 border border-[#c6c6cd]/40 space-y-4">
              {["Une contradiction peut passer inaperçue.", "Un détail peut être oublié.", "Une nouvelle version peut casser la continuité d&apos;une ancienne."].map((item) => <div key={item} className="flex gap-3 text-sm text-[#45464d]"><span className="mt-1 h-2 w-2 rounded-full bg-[#b87500] shrink-0" />{item}</div>)}
            </div>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-20">
          <div className="max-w-3xl mx-auto text-center space-y-5">
            <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">La promesse</p>
            <h2 className="font-playfair text-3xl sm:text-4xl font-bold text-[#0b1c30]">Book Loop transforme votre univers en une référence vivante.</h2>
            <p className="text-sm text-[#45464d] leading-relaxed">Chaque nouvelle création s&apos;appuie sur ce qui est déjà établi. Book Loop distingue ce qui est proposé par l&apos;IA, observé dans vos textes, validé par vous ou potentiellement contradictoire.</p>
            <p className="font-semibold text-[#0b1c30]">L&apos;IA propose. Vous décidez. Book Loop garde la cohérence.</p>
          </div>
        </section>

        <section className="bg-[#0b1c30] text-white">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-20">
            <div className="max-w-3xl mx-auto text-center space-y-4 mb-12">
              <p className="text-xs font-mono font-bold text-[#ffddb8] uppercase tracking-wider">Le cycle</p>
              <h2 className="font-playfair text-3xl sm:text-4xl font-bold">Créer. Vérifier. Décider. Continuer.</h2>
            </div>
            <div className="grid md:grid-cols-4 gap-6">
              {["Écrivez — créez un chapitre, une scène ou un nouvel élément.", "Vérifiez — confrontez le nouveau contenu à ce qui est établi.", "Décidez — acceptez, corrigez ou rejetez les propositions.", "Continuez — votre univers validé devient la base des prochaines créations."].map((item, index) => <div key={item} className="rounded-xl border border-white/10 p-5"><div className="text-[#ffddb8] font-mono text-xs mb-3">0{index + 1}</div><p className="text-sm leading-relaxed text-[#eaf1ff]">{item}</p></div>)}
            </div>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-20">
          <div className="text-center space-y-4 mb-10">
            <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Pour qui ?</p>
            <h2 className="font-playfair text-3xl sm:text-4xl font-bold text-[#0b1c30]">Un même problème, trois façons de créer.</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {audiences.map((item) => <div key={item} className="bg-white rounded-2xl border border-[#c6c6cd]/40 p-6"><Check className="w-5 h-5 text-[#b87500] mb-4" /><p className="text-sm text-[#45464d] leading-relaxed">{item}</p></div>)}
          </div>
        </section>

        <section className="bg-white border-t border-[#c6c6cd]/40">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 py-16 text-center space-y-5">
            <h2 className="font-playfair text-3xl sm:text-4xl font-bold text-[#0b1c30]">Les autres outils vous aident à créer ou à stocker votre univers.</h2>
            <p className="text-lg font-semibold text-[#0b1c30]">Book Loop vous aide à le faire évoluer sans le casser.</p>
            <Link href="/register" className="inline-flex px-6 py-3 rounded bg-[#0b1c30] text-white text-sm font-bold items-center gap-2">Commencer gratuitement <ArrowRight className="w-4 h-4" /></Link>
          </div>
        </section>
      </main>
    </div>
  );
}
