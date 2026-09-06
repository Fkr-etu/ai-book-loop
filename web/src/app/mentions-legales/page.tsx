import { LegalPage, Placeholder, legal } from "@/components/LegalPage";

export const metadata = { title: "Mentions légales" };

export default function MentionsLegalesPage() {
  return (
    <LegalPage title="Mentions légales" description="Informations relatives à l'éditeur, au contact et à l'hébergement de Book Loop.">
      <section><h2 className="font-playfair text-2xl font-bold">Éditeur</h2><dl className="mt-4 grid gap-3"><div><dt className="font-semibold">Nom</dt><dd><Placeholder>{legal.publisher.name}</Placeholder></dd></div><div><dt className="font-semibold">Adresse</dt><dd><Placeholder>{legal.publisher.address}</Placeholder></dd></div><div><dt className="font-semibold">Immatriculation</dt><dd><Placeholder>{legal.publisher.registration}</Placeholder></dd></div><div><dt className="font-semibold">TVA</dt><dd><Placeholder>{legal.publisher.vat}</Placeholder></dd></div><div><dt className="font-semibold">Contact</dt><dd><Placeholder>{legal.publisher.contact}</Placeholder></dd></div></dl></section>
      <section><h2 className="font-playfair text-2xl font-bold">Hébergement</h2><p className="mt-4"><Placeholder>{legal.publisher.hosting}</Placeholder></p></section>
      <section><h2 className="font-playfair text-2xl font-bold">Propriété intellectuelle</h2><p className="mt-4">Les éléments du site et de l'application doivent faire l'objet d'une information et de mentions adaptées à l'exploitation effective de Book Loop. Le périmètre définitif sera validé avant publication commerciale.</p></section>
    </LegalPage>
  );
}
