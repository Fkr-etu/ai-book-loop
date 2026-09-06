import Link from "next/link";

export const metadata = {
  title: "Qu’est-ce qu’une bible narrative ?",
  description:
    "Définition et méthode pour comprendre une bible narrative, ses éléments essentiels et son rôle dans une histoire longue.",
};

export default function GuidePage() {
  return (
    <main className="min-h-screen bg-[#f8f5f0] text-[#0f172a]">
      <article className="max-w-3xl mx-auto px-4 sm:px-6 py-16 md:py-24">
        <Link href="/guides" className="text-sm font-semibold text-[#b87500]">← Tous les guides</Link>
        <p className="mt-10 text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Bible narrative</p>
        <h1 className="mt-4 font-playfair text-4xl sm:text-5xl font-bold text-[#0b1c30]">Qu’est-ce qu’une bible narrative ?</h1>
        <p className="mt-6 text-lg text-[#45464d] leading-relaxed">Une bible narrative est une référence structurée qui rassemble les éléments importants d’une fiction afin de préserver sa continuité au fur et à mesure que l’histoire évolue.</p>
        <div className="mt-12 space-y-10 text-[#30323a] leading-relaxed">
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Que contient-elle ?</h2><p className="mt-3">Selon le projet, elle peut réunir les personnages, leurs relations, les lieux, les événements, la chronologie, les règles du monde, les objets importants, les arcs narratifs et les choix de ton ou de style.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Pourquoi est-elle utile ?</h2><p className="mt-3">Une histoire longue contient trop de dépendances pour être reconstruite parfaitement à partir du seul dernier chapitre. Une bible permet de conserver les décisions importantes et de limiter les contradictions.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Bible statique ou référence vivante ?</h2><p className="mt-3">Une bonne bible évolue avec le projet. Mais toutes les propositions ne doivent pas devenir des faits : l’auteur doit pouvoir distinguer ce qui est établi, observé, proposé et validé.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Avec l’IA</h2><p className="mt-3">La bible narrative devient particulièrement utile lorsque l’IA participe à l’écriture. Elle fournit une mémoire de référence et permet de confronter chaque nouvelle proposition aux décisions déjà prises.</p></section>
          <section className="bg-white rounded-2xl border border-[#c6c6cd]/40 p-6"><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Le Canon de Book Loop</h2><p className="mt-3">Book Loop pousse cette idée avec un Canon narratif : une référence durable de l’histoire, utilisée dans la boucle de génération et de vérification, avec une validation humaine comme autorité finale.</p></section>
        </div>
      </article>
    </main>
  );
}
