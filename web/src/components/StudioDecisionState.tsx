import { Check, Clock3, X } from "lucide-react";

export type StudioDecisionStateValue =
  | "approved"
  | "canonical"
  | "rejected"
  | "needs_review"
  | "proposed"
  | "draft"
  | "in_progress"
  | "pending";

type StateDefinition = {
  label: string;
  detail: string;
  className: string;
  icon: typeof Check;
};

const STATES: Record<StudioDecisionStateValue, StateDefinition> = {
  approved: {
    label: "Canon approuvé",
    detail: "Cette version est la référence pour la suite du récit.",
    className: "bg-[#f3e7cb] text-[#76500f] border-[#d8b36e]",
    icon: Check,
  },
  canonical: {
    label: "Canon approuvé",
    detail: "Cette version est la référence pour la suite du récit.",
    className: "bg-[#f3e7cb] text-[#76500f] border-[#d8b36e]",
    icon: Check,
  },
  rejected: {
    label: "Rejetée",
    detail: "Cette proposition reste dans l'historique et ne modifie pas le Canon.",
    className: "bg-[#ffdad6] text-[#a33b32] border-[#e8aaa3]",
    icon: X,
  },
  needs_review: {
    label: "À votre décision",
    detail: "Vérifiez les points signalés avant de décider si cette version rejoint le Canon.",
    className: "bg-[#dcebf3] text-[#24536d] border-[#9bbfd3]",
    icon: Clock3,
  },
  proposed: {
    label: "Proposition de l'IA",
    detail: "L'IA propose cette version. Elle ne devient pas canonique sans décision de l'auteur.",
    className: "bg-[#dcebf3] text-[#24536d] border-[#9bbfd3]",
    icon: Clock3,
  },
  draft: {
    label: "Brouillon",
    detail: "Cette version n'est pas encore une décision canonique.",
    className: "bg-[#eef0f2] text-[#506070] border-[#c8d0d8]",
    icon: Clock3,
  },
  in_progress: {
    label: "En cours",
    detail: "Le workflow est en cours. Cet état est fourni par le backend.",
    className: "bg-[#eef0f2] text-[#506070] border-[#c8d0d8]",
    icon: Clock3,
  },
  pending: {
    label: "En attente",
    detail: "Cette version attend une étape du workflow.",
    className: "bg-[#eef0f2] text-[#506070] border-[#c8d0d8]",
    icon: Clock3,
  },
};

export function StudioDecisionState({ status }: { status?: string | null }) {
  const value = (status && status in STATES ? status : "draft") as StudioDecisionStateValue;
  const state = STATES[value];
  const Icon = state.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full border text-[11px] font-semibold ${state.className}`}
      title={state.detail}
      aria-label={`${state.label}. ${state.detail}`}
    >
      <Icon className="w-3.5 h-3.5" aria-hidden="true" />
      {state.label}
    </span>
  );
}
