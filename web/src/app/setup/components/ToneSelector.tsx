import { Check, Feather, Heart, Moon, Smile, Sparkles, Theater, Zap } from "lucide-react";

const options = [
  { value: "Sombre", label: "Sombre", description: "Une atmosphère grave, inquiétante ou mélancolique.", icon: Moon },
  { value: "Tendu", label: "Tendu", description: "Une tension qui maintient le lecteur en alerte.", icon: Zap },
  { value: "Intime", label: "Intime", description: "Une narration proche des personnages et de leurs émotions.", icon: Heart },
  { value: "Léger", label: "Léger", description: "Une atmosphère accessible, douce ou divertissante.", icon: Smile },
  { value: "Drôle", label: "Drôle", description: "Une place importante donnée à l’humour et à la légèreté.", icon: Theater },
  { value: "Contemplatif", label: "Contemplatif", description: "Un rythme posé, attentif aux sensations et aux idées.", icon: Feather },
  { value: "Épique", label: "Épique", description: "Une narration ample, spectaculaire ou aventureuse.", icon: Sparkles },
  { value: "Je ne sais pas encore", label: "Je ne sais pas encore", description: "Vous pourrez laisser la tonalité émerger pendant l’écriture.", icon: Feather },
];

export function ToneSelector({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  return (
    <fieldset>
      <legend className="label mb-1">Quelle tonalité imaginez-vous ?</legend>
      <p className="hint mb-3">Choisissez l’ambiance générale que vous aimeriez donner à votre récit.</p>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2" role="radiogroup" aria-label="Tonalité du récit">
        {options.map((option) => {
          const selected = value === option.value;
          const Icon = option.icon;
          return (
            <button
              key={option.value}
              type="button"
              role="radio"
              aria-checked={selected}
              onClick={() => onChange(option.value)}
              className={`group relative rounded-xl border p-3 text-left transition-all ${selected ? "border-[#0b1c30] bg-[#f4f7fb] shadow-sm" : "border-[#c6c6cd]/60 bg-white hover:border-[#b87500]/70 hover:bg-[#fffdfa]"}`}
            >
              <span className={`absolute right-2.5 top-2.5 flex h-4.5 w-4.5 items-center justify-center rounded-full border ${selected ? "border-[#0b1c30] bg-[#0b1c30] text-white" : "border-[#c6c6cd] text-transparent"}`} aria-hidden="true">
                {selected ? <Check className="h-2.5 w-2.5" /> : null}
              </span>
              <Icon className={`mb-2 h-4 w-4 ${selected ? "text-[#b87500]" : "text-[#76777d]"}`} aria-hidden="true" />
              <span className="block pr-4 text-xs font-semibold text-[#0b1c30]">{option.label}</span>
              <span className="mt-1 block text-[10px] leading-relaxed text-[#5f5e5b]">{option.description}</span>
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}
