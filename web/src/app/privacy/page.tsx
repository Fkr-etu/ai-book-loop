import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-[#f8f5f0] px-6 py-12 text-[#0f172a]">
      <article className="mx-auto max-w-3xl rounded-xl border border-[#c6c6cd]/30 bg-white p-8 shadow-sm sm:p-10">
        <Link href="/register" className="text-xs font-semibold text-[#45464d] hover:underline">← Retour à l’inscription</Link>
        <h1 className="mt-6 font-playfair text-3xl font-bold">Politique de confidentialité</h1>
        <p className="mt-2 text-xs text-[#76777d]">Version publiée le 8 septembre 2026</p>
        <div className="mt-8 space-y-6 text-sm leading-7 text-[#45464d]">
          <section><h2 className="font-bold text-[#0b1c30]">1. Données traitées</h2><p>Le service traite notamment les informations nécessaires à la création et à la gestion du compte, ainsi que les données que vous choisissez d’ajouter à vos projets éditoriaux.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">2. Finalités</h2><p>Ces données sont utilisées pour fournir le service, sécuriser les comptes, gérer les abonnements, conserver les projets et améliorer l’expérience lorsque vous avez donné le consentement requis.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">3. Cookies et session</h2><p>Le service utilise un cookie de session nécessaire à l’authentification. Des mécanismes de mesure d’audience peuvent être activés selon vos choix de consentement.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">4. Prestataires</h2><p>Certaines fonctions peuvent nécessiter des prestataires techniques, notamment pour le paiement ou l’hébergement. Les données pertinentes sont alors transmises dans le cadre nécessaire à la fourniture de ces fonctions.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">5. Conservation et sécurité</h2><p>Des mesures techniques et organisationnelles sont mises en œuvre pour protéger les données contre les accès non autorisés, la perte ou l’altération. Les durées de conservation dépendent de la nature des données et des obligations applicables.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">6. Vos droits</h2><p>Selon votre situation et la législation applicable, vous pouvez disposer de droits d’accès, de rectification, d’effacement, de limitation, d’opposition ou de portabilité. Pour exercer un droit ou poser une question, utilisez le canal de support indiqué dans l’application.</p></section>
        </div>
        <Link href="/terms" className="mt-8 inline-block text-xs font-semibold underline">Consulter les conditions d’utilisation</Link>
      </article>
    </main>
  );
}
