import { Check, Users } from "lucide-react";

type AudienceOption = {
  value: string;
  title: string;
  description: string;
};

const options: AudienceOption[] = [
  { value: "Adultes", title: "Adultes", description: "Romans et récits destinés principalement aux adultes." },
  { value: "Adolescents", title: "Adolescents / Young Adult", description: "Pour des lecteurs adolescents et jeunes adultes." },
  { value: "Jeunesse", title: "Enfants / Jeunesse", description: "Des histoires pensées pour les enfants et les jeunes lecteurs." },
  { value: "Grand public", title: "Tout public", description: "Une histoire qui peut s’adresser à un lectorat large." },
  { value: "Je ne sais pas encore", title: "Je ne sais pas encore", description: "Aucun problème : votre public pourra se préciser plus tard." },
];

export function AudienceSelector({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  return (
    <fieldset>
      <legend className="label mb-1">À quels lecteurs pensez-vous ?</legend>
      <p className="hint mb-3">Vous n’avez pas besoin de connaître précisément votre public. Choisissez ce qui s’en approche le plus.</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2" role="radiogroup" aria-label="Public cible">
        {options.map((option) => {
          const selected = value === option.value;
          return (
            <button
              key={option.value}
              type="button"
              role="radio"
              aria-checked={selected}
              onClick={() => onChange(option.value)}
              className={`group relative rounded-xl border p-4 text-left transition-all ${selected ? "border-[#0b1c30] bg-[#f4f7fb] shadow-sm" : "border-[#c6c6cd]/60 bg-white hover:border-[#b87500]/70 hover:bg-[#fffdfa]"}`}
            >
              <span className={`absolute right-3 top-3 flex h-5 w-5 items-center justify-center rounded-full border ${selected ? "border-[#0b1c30] bg-[#0b1c30] text-white" : "border-[#c6c6cd] text-transparent"}`} aria-hidden="true">
                {selected ? <Check className="h-3 w-3" /> : null}
              </span>
              <span className="flex items-start gap-3 pr-6">
                <span className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${selected ? "bg-white text-[#b87500]" : "bg-[#faf9f6] text-[#76777d]"}`} aria-hidden="true">
                  <Users className="h-4 w-4" />
                </span>
                <span>
                  <span className="block text-xs font-semibold text-[#0b1c30]">{option.title}</span>
                  <span className="mt-1 block text-[11px] leading-relaxed text-[#5f5e5b]">{option.description}</span>
                </span>
              </span>
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}
