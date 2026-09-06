import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Écrire un roman avec l’IA : méthode complète",
  description: "Méthode pratique pour écrire un roman avec l’IA tout en conservant la cohérence des personnages, des événements et de l’univers.",
  alternates: { canonical: "/guides/ecrire-un-roman-avec-ia" },
};

export default function GuidePage() {
  return (
    <main className="min-h-screen bg-[#f8f5f0] text-[#0f172a]"><article className="max-w-3xl mx-auto px-4 sm:px-6 py-16 md:py-24">
      <Link href="/guides" className="text-sm font-semibold text-[#b87500]">← Tous les guides</Link>
      <p className="mt-10 text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Écriture IA</p>
      <h1 className="mt-4 font-playfair text-4xl sm:text-5xl font-bold text-[#0b1c30]">Écrire un roman avec l’IA : méthode complète pour garder la cohérence</h1>
      <p className="mt-6 text-lg text-[#45464d] leading-relaxed">L’IA peut accélérer l’écriture d’un roman, mais générer chapitre après chapitre ne suffit pas. Plus l’histoire devient longue, plus il faut une référence stable qui permette de vérifier les nouveaux textes.</p>
      <div className="mt-12 space-y-10 text-[#30323a] leading-relaxed">
        <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">1. Définissez l’intention de l’histoire</h2><p className="mt-3">Commencez par le genre, le ton, les thèmes, le conflit central et les contraintes que vous ne voulez pas perdre. L’IA doit servir ces choix, pas les remplacer.</p></section>
        <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">2. Construisez une référence durable</h2><p className="mt-3">Listez les personnages, lieux, relations, événements, règles du monde et faits déjà établis. Cette référence joue le rôle d’une bible narrative : elle permet de distinguer ce qui est vrai dans l’histoire de ce qui n’est encore qu’une proposition.</p></section>
        <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">3. Travaillez par chapitres</h2><p className="mt-3">Pour chaque chapitre, donnez à l’IA le contexte pertinent et demandez une production vérifiable. Évitez de considérer chaque génération comme une vérité définitive.</p></section>
        <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">4. Vérifiez avant de poursuivre</h2><p className="mt-3">Comparez le nouveau chapitre aux faits établis. Un personnage qui change soudainement de métier, un âge incohérent ou un événement placé dans le mauvais ordre sont des signaux à traiter avant de continuer.</p></section>
        <section><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">5. Gardez la décision humaine</h2><p className="mt-3">Une détection de contradiction n’est pas toujours une erreur : vous pouvez volontairement modifier le Canon. L’important est de décider explicitement ce qui devient la nouvelle référence.</p></section>
        <section className="bg-white rounded-2xl border border-[#c6c6cd]/40 p-6"><h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">Le principe à retenir</h2><p className="mt-3">Pour écrire un roman avec l’IA sur la durée, pensez en boucle : <strong>écrire → vérifier → décider → continuer</strong>. C’est cette boucle qui transforme une suite de générations en véritable processus d’écriture.</p><p className="mt-3">Book Loop applique ce principe avec un Canon narratif qui conserve la référence de votre histoire et vous laisse l’autorité finale.</p></section>
      </div>
    </article></main>
  );
}
