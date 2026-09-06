import { LegalPage, Placeholder, legal } from "@/components/LegalPage";

export const metadata = { title: "Politique de confidentialité" };

export default function PrivacyPage() {
  return (
    <LegalPage title="Politique de confidentialité" description="Base de publication pour l'information des utilisateurs sur les données personnelles traitées par Book Loop.">
      <section><h2 className="font-playfair text-2xl font-bold">Responsable du traitement</h2><p className="mt-4"><Placeholder>{legal.publisher.name}</Placeholder> · <Placeholder>{legal.publisher.contact}</Placeholder></p></section>
      <section><h2 className="font-playfair text-2xl font-bold">Données et finalités</h2><p className="mt-4">Book Loop doit documenter, pour chaque traitement effectivement activé, les données collectées, la finalité, la base légale, les destinataires, les durées de conservation et les droits applicables. Cette matrice sera finalisée avec le fonctionnement réel de l'API, de l'authentification, de la facturation et des services d'IA.</p></section>
      <section><h2 className="font-playfair text-2xl font-bold">Vos droits</h2><p className="mt-4">Les modalités permettant d'exercer les droits d'accès, rectification, effacement, limitation, opposition et, lorsque applicable, portabilité doivent être précisées ici avec le canal de contact opérationnel.</p></section>
      <section><h2 className="font-playfair text-2xl font-bold">Sous-traitants et transferts</h2><p className="mt-4">La liste des prestataires réellement utilisés et les éventuels transferts hors de l'Espace économique européen doivent être documentés avant mise en production commerciale.</p></section>
      <section><h2 className="font-playfair text-2xl font-bold">Cookies et traceurs</h2><p className="mt-4">Book Loop n'active pas ici de technologie de suivi non nécessaire. Tout ajout d'outil d'analytics, publicité ou autre traceur devra être déclaré et relié au mécanisme de consentement approprié.</p></section>
    </LegalPage>
  );
}
