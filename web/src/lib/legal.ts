export const LEGAL_CONTENT_VERSION = "draft-micro-entreprise-2026-09";

export type LegalStatus = "draft" | "ready";

/**
 * Book Loop launch profile: French individual entrepreneur (micro-entreprise).
 * Business facts stay configurable until the operator supplies the definitive
 * information and validates the final legal texts.
 */
export const legal: {
  status: LegalStatus;
  operator: {
    legalForm: string;
    name: string;
    commercialName: string;
    address: string;
    siren: string;
    siret: string;
    ape: string;
    vat: string;
    contact: string;
  };
  hosting: { name: string; address: string };
  mediation: { name: string; contact: string };
  effectiveDate: string;
} = {
  status: "draft",
  operator: {
    legalForm: "Entrepreneur individuel — régime micro-entreprise",
    name: "À COMPLÉTER — prénom et nom de l'exploitant",
    commercialName: "Book Loop",
    address: "À COMPLÉTER — adresse professionnelle",
    siren: "À COMPLÉTER — numéro SIREN",
    siret: "À COMPLÉTER — numéro SIRET de l'établissement",
    ape: "À COMPLÉTER — code APE/NAF attribué",
    vat: "À COMPLÉTER — numéro de TVA intracommunautaire, le cas échéant",
    contact: "À COMPLÉTER — adresse e-mail de contact",
  },
  hosting: {
    name: "À COMPLÉTER — identité légale de l'hébergeur",
    address: "À COMPLÉTER — adresse de l'hébergeur",
  },
  mediation: {
    name: "À COMPLÉTER — médiateur de la consommation compétent",
    contact: "À COMPLÉTER — modalités de saisine",
  },
  effectiveDate: "À COMPLÉTER — date d'entrée en vigueur",
};

export const LEGAL_PLACEHOLDER_PREFIX = "À COMPLÉTER";

export function isLegalReady(): boolean {
  return legal.status === "ready" && !JSON.stringify(legal).includes(LEGAL_PLACEHOLDER_PREFIX);
}

export const legalPages = {
  mentions: {
    title: "Mentions légales",
    description: "Informations relatives à l'éditeur, entrepreneur individuel exploitant Book Loop, et à l'hébergement.",
  },
  privacy: {
    title: "Politique de confidentialité",
    description: "Informations sur les données personnelles traitées par Book Loop.",
  },
  terms: {
    title: "Conditions générales de vente",
    description: "Cadre contractuel applicable aux offres payantes de Book Loop.",
  },
} as const;
