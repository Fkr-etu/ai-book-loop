import { LegalPage, Placeholder, legal } from "@/components/LegalPage";

export const metadata = { title: "Conditions générales de vente" };

export default function TermsPage() {
  return (
    <LegalPage title="Conditions générales de vente" description="Structure des conditions applicables aux offres payantes de Book Loop, exploité par un entrepreneur individuel.">
      <section><h2 className="font-playfair text-2xl font-bold">1. Vendeur et objet</h2><p className="mt-4">Les présentes conditions encadrent l'accès aux offres payantes de Book Loop. Le vendeur est l'entrepreneur individuel exploitant Book Loop :</p><p className="mt-2"><Placeholder>{legal.operator.name}</Placeholder>, entrepreneur individuel sous régime micro-entreprise, <Placeholder>{legal.operator.address}</Placeholder>, SIREN <Placeholder>{legal.operator.siren}</Placeholder>.</p></section>
      <section><h2 className="font-playfair text-2xl font-bold">2. Prix et facturation</h2><p className="mt-4">Les prix, taxes applicables, périodicité de facturation, renouvellement et modalités de paiement seront affichés de manière définitive avant la souscription. Aucun prix affiché dans cette base ne vaut engagement contractuel.</p></section>
      <section><h2 className="font-playfair text-2xl font-bold">3. Abonnement et résiliation</h2><p className="mt-4">L'interface d'abonnement doit permettre au consommateur d'accéder à la résiliation électronique lorsque celle-ci est applicable. Les effets de la résiliation, la date de fin d'accès et les éventuels remboursements seront définis dans la version finale des CGV.</p></section>
      <section><h2 className="font-playfair text-2xl font-bold">4. Droit de rétractation</h2><p className="mt-4">Le parcours de souscription doit présenter l'information applicable au droit de rétractation pour un service numérique et recueillir, lorsque nécessaire, les choix et demandes du consommateur selon le cadre légal applicable. Le formulaire et les conditions définitifs seront validés avant commercialisation.</p></section>
      <section><h2 className="font-playfair text-2xl font-bold">5. Médiation de la consommation</h2><p className="mt-4">Médiateur désigné : <Placeholder>{legal.mediation.name}</Placeholder>. Modalités de saisine : <Placeholder>{legal.mediation.contact}</Placeholder>.</p></section>
      <section><h2 className="font-playfair text-2xl font-bold">6. Version applicable</h2><p className="mt-4">Date d'entrée en vigueur : <Placeholder>{legal.effectiveDate}</Placeholder>. La version contractuelle définitive devra être conservée avec sa date d'effet.</p></section>
    </LegalPage>
  );
}
