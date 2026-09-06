import Link from "next/link";

export const metadata = {
  title: "Comment éviter les contradictions dans un roman ?",
  description:
    "Méthode pour détecter et corriger les contradictions d’un roman : personnages, chronologie, lieux, relations et règles du monde.",
};

export default function GuidePage() {
  return (
    <main className="min-h-screen bg-[#f8f5f0] text-[#0f172a]">
      <article className="max-w-3xl mx-auto px-4 sm:px-6 py-16 md:py-24">
        <Link href="/guides" className="text-sm font-semibold text-[#b87500]">← Tous les guides</Link>
        <p className="mt-10 text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Cohérence</p>
        <h1 className="mt-4 font-playfair text-4xl sm:text-5xl font-bold text-[#0b1c30]">Comment éviter les contradictions dans un roman ?</h1>
        <p className="mt-6 text-lg text-[#45464d] leading-relaxed">Les contradictions apparaissent souvent quand une histoire s’allonge : un détail change, une date ne correspond plus ou un personnage agit contre ce qui a été établi. Elles sont plus faciles à prévenir qu’à réparer après plusieurs chapitres.</p>
        <div className="mt-12 space-y-10 text-[#30323a] leading-relaxed">
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Commencez par les faits critiques</h2><p className="mt-3">Identifiez les informations dont dépend la continuité : âge, apparence, métier, relations, lieux, dates, événements passés et règles de l’univers. Tout n’a pas besoin d’être mémorisé avec le même niveau de priorité.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Vérifiez chaque nouveau chapitre</h2><p className="mt-3">Une relecture de cohérence doit chercher les incompatibilités avec les faits établis, pas seulement les fautes de style. Cette vérification peut être assistée par l’IA, mais ses résultats restent des propositions à examiner.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Distinguez erreur et changement volontaire</h2><p className="mt-3">Si un personnage change de situation ou si une règle de l’univers évolue, ce n’est pas nécessairement une erreur. La question est de savoir si cette nouvelle version a été décidée par l’auteur et doit remplacer l’ancienne référence.</p></section>
          <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Évitez les corrections en cascade</h2><p className="mt-3">Lorsqu’un fait est modifié, vérifiez les passages qui en dépendent. Une référence centralisée et versionnée permet de savoir quelle décision est actuelle et de réduire les incohérences secondaires.</p></section>
          <section className="bg-white rounded-2xl border border-[#c6c6cd]/40 p-6"><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Une référence de vérité</h2><p className="mt-3">Le Canon de Book Loop sert précisément à conserver cette référence. L’IA peut signaler un conflit et proposer une correction ; l’auteur décide ce qui devient canon avant de poursuivre l’écriture.</p></section>
        </div>
      </article>
    </main>
  );
}
