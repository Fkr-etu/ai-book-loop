import Link from "next/link";

export const metadata = {
  title: "Garder la cohérence d’un roman écrit avec l’IA",
  description:
    "Découvrez comment préserver personnages, chronologie, lieux et règles d’un roman lorsque l’IA génère de nouveaux chapitres.",
};

export default function GuidePage() {
  return (
    <main className="min-h-screen bg-[#f8f5f0] text-[#0f172a]">
      <article className="max-w-3xl mx-auto px-4 sm:px-6 py-16 md:py-24">
        <Link href="/guides" className="text-sm font-semibold text-[#b87500]">← Tous les guides</Link>
        <p className="mt-10 text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Continuité narrative</p>
        <h1 className="mt-4 font-playfair text-4xl sm:text-5xl font-bold text-[#0b1c30]">Comment garder la cohérence d’un roman écrit avec l’IA ?</h1>
        <p className="mt-6 text-lg text-[#45464d] leading-relaxed">Le principal défi d’un roman assisté par IA n’est pas seulement la qualité d’un passage isolé : c’est sa compatibilité avec tout ce qui a déjà été établi.</p>
        <div className="mt-12 space-y-10 text-[#30323a] leading-relaxed">
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Centralisez les faits importants</h2><p className="mt-3">Gardez une référence des informations qui ne doivent pas être réinventées à chaque chapitre : identité, apparence, relations, lieux, chronologie, règles et événements majeurs.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Ne confondez pas contexte et vérité</h2><p className="mt-3">Un résumé transmis à une IA est un contexte de travail. Il ne constitue pas forcément une source de vérité. Une référence durable permet de savoir quelles informations ont été validées.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Contrôlez les contradictions</h2><p className="mt-3">Avant de valider un chapitre, recherchez les écarts avec la référence : couleur des yeux, emplacement d’un lieu, ordre des événements, motivations ou relations. Les petites incohérences deviennent coûteuses lorsqu’elles se propagent.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Acceptez que le Canon puisse évoluer</h2><p className="mt-3">Une contradiction peut aussi révéler une décision créative. Si vous changez volontairement un fait, faites de ce changement une décision explicite afin que les prochaines générations utilisent la bonne version.</p></section>
          <section className="bg-white rounded-2xl border border-[#c6c6cd]/40 p-6"><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Une bonne boucle de continuité</h2><p className="mt-3">Écrivez le chapitre, vérifiez-le contre votre référence, décidez des changements, puis continuez avec cette version validée. C’est le principe du Canon dans Book Loop.</p></section>
        </div>
      </article>
    </main>
  );
}
