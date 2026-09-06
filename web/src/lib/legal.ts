export const LEGAL_CONTENT_VERSION = "draft-2026-09";

/**
 * Business/legal facts intentionally remain placeholders until the operator
 * supplies the definitive information and validates the final legal text.
 */
export const legal = {
  publisher: {
    name: "À COMPLÉTER — raison sociale / nom de l'éditeur",
    address: "À COMPLÉTER — adresse du siège",
    registration: "À COMPLÉTER — SIREN / SIRET / RCS",
    vat: "À COMPLÉTER — numéro de TVA intracommunautaire, le cas échéant",
    contact: "À COMPLÉTER — adresse e-mail de contact",
    hosting: "À COMPLÉTER — informations légales de l'hébergeur",
  },
  mediation: {
    name: "À COMPLÉTER — médiateur de la consommation",
    contact: "À COMPLÉTER — modalités de saisine",
  },
  effectiveDate: "À COMPLÉTER — date d'entrée en vigueur",
} as const;

export const legalPages = {
  mentions: {
    title: "Mentions légales",
    description: "Informations relatives à l'éditeur et à l'hébergement de Book Loop.",
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
