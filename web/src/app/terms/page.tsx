import Link from "next/link";

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-[#f8f5f0] px-6 py-12 text-[#0f172a]">
      <article className="mx-auto max-w-3xl rounded-xl border border-[#c6c6cd]/30 bg-white p-8 shadow-sm sm:p-10">
        <Link href="/register" className="text-xs font-semibold text-[#45464d] hover:underline">← Retour à l’inscription</Link>
        <h1 className="mt-6 font-playfair text-3xl font-bold">Conditions d’utilisation</h1>
        <p className="mt-2 text-xs text-[#76777d]">Version publiée le 8 septembre 2026</p>
        <div className="mt-8 space-y-6 text-sm leading-7 text-[#45464d]">
          <section><h2 className="font-bold text-[#0b1c30]">1. Objet</h2><p>AI Book Loop fournit un espace logiciel destiné à accompagner la création, l’organisation et la révision de projets de livres, notamment avec des fonctions d’assistance par intelligence artificielle.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">2. Compte</h2><p>Vous êtes responsable des informations fournies lors de votre inscription et de la confidentialité de vos moyens d’accès. Vous devez utiliser le service conformément aux lois applicables et ne pas tenter de compromettre son fonctionnement ou celui des autres comptes.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">3. Contenus et décisions éditoriales</h2><p>Vous conservez la responsabilité de vos contenus et de vos décisions éditoriales. Les suggestions générées par le service doivent être vérifiées par l’auteur avant utilisation. Le service ne garantit pas l’exactitude, l’originalité ou l’adéquation éditoriale d’une proposition générée.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">4. Abonnements</h2><p>Les fonctionnalités payantes et leur facturation sont présentées au moment de la souscription. La gestion du paiement et de l’abonnement est effectuée via le prestataire de paiement indiqué par le service.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">5. Évolution du service</h2><p>AI Book Loop peut faire évoluer ses fonctionnalités, notamment pour améliorer la sécurité, les performances et les capacités éditoriales du produit.</p></section>
          <section><h2 className="font-bold text-[#0b1c30]">6. Contact</h2><p>Pour toute question relative à ces conditions, utilisez le canal de support indiqué dans l’application.</p></section>
        </div>
        <Link href="/privacy" className="mt-8 inline-block text-xs font-semibold underline">Consulter la politique de confidentialité</Link>
      </article>
    </main>
  );
}
