import { LegalPage, Placeholder, legal } from "@/components/LegalPage";

export const metadata = { title: "Mentions légales" };

export default function MentionsLegalesPage() {
  return (
    <LegalPage title="Mentions légales" description="Informations relatives à l'entrepreneur individuel exploitant Book Loop et à l'hébergement.">
      <section>
        <h2 className="font-playfair text-2xl font-bold">Éditeur</h2>
        <dl className="mt-4 grid gap-3">
          <div><dt className="font-semibold">Nom de l'exploitant</dt><dd><Placeholder>{legal.operator.name}</Placeholder></dd></div>
          <div><dt className="font-semibold">Statut</dt><dd>{legal.operator.legalForm}</dd></div>
          <div><dt className="font-semibold">Nom commercial</dt><dd>{legal.operator.commercialName}</dd></div>
          <div><dt className="font-semibold">Adresse professionnelle</dt><dd><Placeholder>{legal.operator.address}</Placeholder></dd></div>
          <div><dt className="font-semibold">SIREN</dt><dd><Placeholder>{legal.operator.siren}</Placeholder></dd></div>
          <div><dt className="font-semibold">SIRET</dt><dd><Placeholder>{legal.operator.siret}</Placeholder></dd></div>
          <div><dt className="font-semibold">Code APE/NAF</dt><dd><Placeholder>{legal.operator.ape}</Placeholder></dd></div>
          <div><dt className="font-semibold">TVA</dt><dd><Placeholder>{legal.operator.vat}</Placeholder></dd></div>
          <div><dt className="font-semibold">Contact</dt><dd><Placeholder>{legal.operator.contact}</Placeholder></dd></div>
        </dl>
      </section>
      <section><h2 className="font-playfair text-2xl font-bold">Hébergement</h2><dl className="mt-4 grid gap-3"><div><dt className="font-semibold">Hébergeur</dt><dd><Placeholder>{legal.hosting.name}</Placeholder></dd></div><div><dt className="font-semibold">Adresse</dt><dd><Placeholder>{legal.hosting.address}</Placeholder></dd></div></dl></section>
      <section><h2 className="font-playfair text-2xl font-bold">Propriété intellectuelle</h2><p className="mt-4">Les éléments du site et de l'application doivent faire l'objet d'une information et de mentions adaptées à l'exploitation effective de Book Loop. Le périmètre définitif sera validé avant publication commerciale.</p></section>
    </LegalPage>
  );
}
