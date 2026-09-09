"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  Feather,
  Lightbulb,
  MapPin,
  Plus,
  Sparkles,
  Trash2,
  UserRound,
} from "lucide-react";
import { realApiClient, RealApiError } from "@/services/realApiClient";
import { getApiErrorMessage } from "@/services/apiErrorMessages";
import { track } from "@/lib/analytics";

type SetupElementType = "Personnage" | "Lieu" | "Époque / contexte" | "Organisation" | "Objet" | "Règle" | "Événement" | "Autre";

type SetupElement = { id: number; type: SetupElementType; name: string; description: string };

const genres = ["Roman", "Policier", "Thriller", "Romance", "Fantasy", "Science-fiction", "Historique", "Littérature générale", "Jeunesse", "Autre"];
const audiences = ["Adultes", "Adolescents", "Jeunesse", "Grand public", "Je ne sais pas encore"];
const tones = ["Sombre", "Tendu", "Intime", "Léger", "Drôle", "Contemplatif", "Épique", "Je ne sais pas encore"];
const elementTypes: { type: SetupElementType; icon: typeof UserRound }[] = [
  { type: "Personnage", icon: UserRound },
  { type: "Lieu", icon: MapPin },
  { type: "Époque / contexte", icon: BookOpen },
  { type: "Organisation", icon: Sparkles },
  { type: "Objet", icon: BookOpen },
  { type: "Règle", icon: Lightbulb },
  { type: "Événement", icon: Sparkles },
  { type: "Autre", icon: Plus },
];

function errorMessage(error: unknown): string {
  if (error instanceof RealApiError) return getApiErrorMessage(error, error.message);
  return "Impossible de créer votre projet pour le moment.";
}

function chipClass(selected: boolean): string {
  return selected
    ? "border-[#0b1c30] bg-[#0b1c30] text-white shadow-xs"
    : "border-[#c6c6cd]/70 bg-white text-[#45464d] hover:border-[#b87500]/70 hover:text-[#0b1c30]";
}

export default function SetupPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [title, setTitle] = useState("");
  const [genresSelected, setGenresSelected] = useState<string[]>([]);
  const [premise, setPremise] = useState("");
  const [intent, setIntent] = useState("");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState("");
  const [constraints, setConstraints] = useState<string[]>([]);
  const [constraintDraft, setConstraintDraft] = useState("");
  const [elements, setElements] = useState<SetupElement[]>([]);
  const [elementType, setElementType] = useState<SetupElementType | null>(null);
  const [elementName, setElementName] = useState("");
  const [elementDescription, setElementDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canContinue = step === 1 ? premise.trim().length > 0 : true;

  const lore = useMemo(
    () => elements
      .filter((element) => element.name.trim() || element.description.trim())
      .map((element) => `${element.type}: ${element.name.trim()}${element.description.trim() ? ` — ${element.description.trim()}` : ""}`)
      .join("\n"),
    [elements],
  );

  const addConstraint = () => {
    const value = constraintDraft.trim();
    if (!value || constraints.includes(value)) return;
    setConstraints((current) => [...current, value]);
    setConstraintDraft("");
  };

  const addElement = () => {
    if (!elementType || (!elementName.trim() && !elementDescription.trim())) return;
    setElements((current) => [...current, { id: Date.now(), type: elementType, name: elementName.trim(), description: elementDescription.trim() }]);
    setElementType(null);
    setElementName("");
    setElementDescription("");
  };

  const handleFinish = async () => {
    setCreating(true);
    setError(null);
    try {
      const book = await realApiClient.createBook({
        title: title.trim() || "Projet sans titre",
        theme: genresSelected.length ? genresSelected.join(" · ") : "Projet narratif",
        author_idea: premise.trim(),
        lore,
        constraints,
        creative_brief: {
          premise: premise.trim(),
          audience,
          tone,
          themes: intent.trim() ? [intent.trim()] : [],
          must_include: [],
          must_avoid: [],
        },
      });
      track("book_created");
      router.push(`/studio?bookId=${encodeURIComponent(book.id)}`);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter selection:bg-[#ffddb8] selection:text-[#0f172a]">
      <header className="sticky top-0 z-20 border-b border-[#c6c6cd]/30 bg-white/90 backdrop-blur">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <Link href="/dashboard" className="flex items-center gap-2.5 shrink-0" aria-label="Retour à la bibliothèque">
            <div className="w-8 h-8 rounded bg-[#0b1c30] text-[#ffddb8] flex items-center justify-center"><Feather className="w-4 h-4" /></div>
            <span className="font-playfair font-bold text-lg text-[#0b1c30] hidden sm:block">Book Loop</span>
          </Link>
          <div className="flex items-center gap-3 text-[11px] text-[#76777d]">
            <span className="hidden sm:block">Votre projet</span>
            <span className="font-mono font-bold text-[#0b1c30]">{step} / 3</span>
          </div>
        </div>
        <div className="h-1 bg-[#e5eeff]"><div className="h-1 bg-[#0b1c30] transition-all duration-300" style={{ width: `${(step / 3) * 100}%` }} /></div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 md:py-12">
        <div className="grid lg:grid-cols-[1fr_280px] gap-8 items-start">
          <section className="bg-white rounded-2xl border border-[#c6c6cd]/40 shadow-xs p-5 sm:p-8">
            {step === 1 && (
              <div className="space-y-7 animate-fadeIn">
                <div className="max-w-2xl">
                  <span className="text-[10px] font-mono font-bold text-[#b87500] uppercase tracking-wider">Votre histoire</span>
                  <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30] mt-1">Parlez-nous de votre histoire</h1>
                  <p className="text-sm text-[#5f5e5b] mt-2 leading-relaxed">Vous n&apos;avez pas besoin d&apos;avoir tout défini. Quelques éléments suffisent pour commencer.</p>
                </div>

                <div>
                  <label htmlFor="setup-title" className="block text-sm font-semibold text-[#0b1c30] mb-1">Comment appelez-vous votre projet ?</label>
                  <p className="text-[11px] text-[#76777d] mb-2">Le titre peut être provisoire.</p>
                  <input id="setup-title" value={title} onChange={(event) => setTitle(event.target.value)} className="w-full px-4 py-3 text-sm border border-[#c6c6cd]/70 rounded-xl bg-[#faf9f6] focus:border-[#b87500] focus:outline-none" placeholder="Le dernier hiver, Projet sans titre…" />
                </div>

                <div>
                  <div className="flex items-baseline justify-between gap-4 mb-2"><span className="text-sm font-semibold text-[#0b1c30]">Quel type de récit écrivez-vous ?</span><span className="text-[10px] text-[#76777d]">Optionnel</span></div>
                  <div className="flex flex-wrap gap-2">
                    {genres.map((genre) => <button key={genre} type="button" onClick={() => setGenresSelected((current) => current.includes(genre) ? current.filter((item) => item !== genre) : [...current, genre])} className={`px-3 py-2 rounded-full border text-xs font-semibold transition-colors ${chipClass(genresSelected.includes(genre))}`}>{genre}</button>)}
                  </div>
                  <p className="text-[11px] text-[#76777d] mt-2">Vous pouvez en choisir plusieurs, ou ne rien choisir pour l&apos;instant.</p>
                </div>

                <div>
                  <label htmlFor="setup-premise" className="block text-sm font-semibold text-[#0b1c30] mb-1">De quoi parle votre histoire ?</label>
                  <p className="text-[11px] text-[#76777d] mb-2">Parlez du point de départ, des personnages ou de l&apos;idée qui vous donne envie d&apos;écrire.</p>
                  <textarea id="setup-premise" value={premise} onChange={(event) => setPremise(event.target.value)} rows={7} className="w-full p-4 text-sm border border-[#c6c6cd]/70 rounded-xl bg-[#faf9f6] focus:border-[#b87500] focus:outline-none font-merriweather leading-relaxed resize-y" placeholder={genresSelected.includes("Policier") || genresSelected.includes("Thriller") ? "Une inspectrice enquête sur une série de meurtres qui semblent reproduire des affaires non résolues vingt ans auparavant…" : genresSelected.includes("Fantasy") ? "Dans un royaume où les souvenirs peuvent être échangés, une jeune femme découvre qu’une partie de son enfance lui a été volontairement retirée…" : "Une femme revient dans sa ville natale après quinze ans d’absence et découvre que quelqu’un semble connaître un secret qu’elle n’a jamais raconté…"} />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-7 animate-fadeIn">
                <div className="max-w-2xl">
                  <span className="text-[10px] font-mono font-bold text-[#b87500] uppercase tracking-wider">Votre direction</span>
                  <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30] mt-1">Qu&apos;avez-vous envie de raconter ?</h1>
                  <p className="text-sm text-[#5f5e5b] mt-2 leading-relaxed">Il n&apos;y a pas de bonne réponse. Une émotion, une question, une idée ou simplement une envie d&apos;écrire suffit.</p>
                </div>

                <div>
                  <label htmlFor="setup-intent" className="block text-sm font-semibold text-[#0b1c30] mb-1">Qu&apos;aimeriez-vous faire ressentir, raconter ou explorer ?</label>
                  <textarea id="setup-intent" value={intent} onChange={(event) => setIntent(event.target.value)} rows={5} className="w-full p-4 text-sm border border-[#c6c6cd]/70 rounded-xl bg-[#faf9f6] focus:border-[#b87500] focus:outline-none font-merriweather leading-relaxed resize-y" placeholder="Créer une enquête où le lecteur doute constamment de la vérité…" />
                  <div className="mt-2 flex flex-wrap gap-2">
                    {["Créer du suspense", "Explorer la culpabilité", "Faire réfléchir", "Faire rire", "Créer de l’émotion"].map((example) => <button key={example} type="button" onClick={() => setIntent((current) => current ? `${current} ${example}.` : `${example}.`)} className="px-2.5 py-1.5 rounded-full bg-[#eff4ff] text-[10px] text-[#45464d] hover:text-[#0b1c30]">{example}</button>)}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-semibold text-[#0b1c30] mb-2">Pour qui écrivez-vous ? <span className="text-[10px] font-normal text-[#76777d]">Optionnel</span></div>
                  <div className="flex flex-wrap gap-2">{audiences.map((value) => <button key={value} type="button" onClick={() => setAudience(value === audience ? "" : value)} className={`px-3 py-2 rounded-full border text-xs font-semibold transition-colors ${chipClass(value === audience)}`}>{value}</button>)}</div>
                </div>

                <div>
                  <div className="text-sm font-semibold text-[#0b1c30] mb-2">Quelle tonalité imaginez-vous ? <span className="text-[10px] font-normal text-[#76777d]">Optionnel</span></div>
                  <div className="flex flex-wrap gap-2">{tones.map((value) => <button key={value} type="button" onClick={() => setTone(value === tone ? "" : value)} className={`px-3 py-2 rounded-full border text-xs font-semibold transition-colors ${chipClass(value === tone)}`}>{value}</button>)}</div>
                </div>

                <div className="pt-2">
                  <div className="text-sm font-semibold text-[#0b1c30] mb-1">Y a-t-il des choses que nous devons absolument respecter ?</div>
                  <p className="text-[11px] text-[#76777d] mb-3">Par exemple : rester réaliste, une époque précise, un secret à préserver, un public particulier…</p>
                  <div className="flex gap-2"><input value={constraintDraft} onChange={(event) => setConstraintDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); addConstraint(); } }} className="flex-1 px-3 py-2.5 text-xs border border-[#c6c6cd]/70 rounded-lg bg-[#faf9f6] focus:border-[#b87500] focus:outline-none" placeholder="Ajouter une contrainte" /><button type="button" onClick={addConstraint} className="px-3 py-2.5 rounded-lg bg-[#0b1c30] text-white text-xs font-semibold"><Plus className="w-3.5 h-3.5" /></button></div>
                  {constraints.length > 0 && <div className="mt-3 flex flex-wrap gap-2">{constraints.map((constraint) => <span key={constraint} className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-[#ffddb8] text-[#2a1700] text-[10px] font-semibold">{constraint}<button type="button" onClick={() => setConstraints((current) => current.filter((item) => item !== constraint))} aria-label={`Supprimer ${constraint}`}><Trash2 className="w-3 h-3" /></button></span>)}</div>}
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-7 animate-fadeIn">
                <div className="max-w-2xl">
                  <span className="text-[10px] font-mono font-bold text-[#b87500] uppercase tracking-wider">Ce que vous avez déjà imaginé</span>
                  <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30] mt-1">Quels éléments importants connaissez-vous déjà ?</h1>
                  <p className="text-sm text-[#5f5e5b] mt-2 leading-relaxed">Personnages, lieux, époque, organisations, objets, événements… Ajoutez uniquement ce que vous connaissez déjà.</p>
                </div>

                <div className="rounded-xl border border-dashed border-[#c6c6cd] bg-[#faf9f6] p-4 sm:p-5">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">{elementTypes.map(({ type, icon: Icon }) => <button key={type} type="button" onClick={() => setElementType(type)} className={`p-3 rounded-lg border text-left transition-colors ${elementType === type ? "border-[#b87500] bg-white" : "border-transparent bg-white/70 hover:border-[#c6c6cd]"}`}><Icon className="w-4 h-4 text-[#b87500] mb-1.5" /><span className="text-[10px] font-semibold text-[#0b1c30]">{type}</span></button>)}</div>
                  {elementType && <div className="mt-4 pt-4 border-t border-[#c6c6cd]/40 space-y-3">
                    <div className="text-[10px] font-mono font-bold uppercase text-[#b87500]">Nouvel élément · {elementType}</div>
                    <input value={elementName} onChange={(event) => setElementName(event.target.value)} className="w-full px-3 py-2.5 text-xs border border-[#c6c6cd]/70 rounded-lg bg-white focus:border-[#b87500] focus:outline-none" placeholder={elementType === "Personnage" ? "Nom du personnage" : "Nom ou repère"} />
                    <textarea value={elementDescription} onChange={(event) => setElementDescription(event.target.value)} rows={3} className="w-full p-3 text-xs border border-[#c6c6cd]/70 rounded-lg bg-white focus:border-[#b87500] focus:outline-none resize-y" placeholder="Ce que vous savez déjà de cet élément…" />
                    <button type="button" onClick={addElement} disabled={!elementName.trim() && !elementDescription.trim()} className="px-4 py-2 rounded-lg bg-[#0b1c30] text-white text-xs font-semibold disabled:opacity-40 flex items-center gap-1.5"><Plus className="w-3.5 h-3.5" /> Ajouter cet élément</button>
                  </div>}
                </div>

                {elements.length > 0 ? <div className="space-y-2">{elements.map((element) => <div key={element.id} className="flex items-start justify-between gap-3 p-3 rounded-lg border border-[#c6c6cd]/40 bg-white"><div className="min-w-0"><span className="text-[9px] font-mono uppercase text-[#b87500] font-bold">{element.type}</span><p className="text-xs font-semibold text-[#0b1c30] mt-0.5">{element.name || "Élément sans nom"}</p>{element.description && <p className="text-[11px] text-[#5f5e5b] mt-1 line-clamp-2">{element.description}</p>}</div><button type="button" onClick={() => setElements((current) => current.filter((item) => item.id !== element.id))} className="p-1.5 text-[#76777d] hover:text-red-700" aria-label={`Supprimer ${element.name || element.type}`}><Trash2 className="w-3.5 h-3.5" /></button></div>)}</div> : <div className="rounded-xl bg-[#eff4ff] p-4 text-xs text-[#45464d]"><strong className="text-[#0b1c30]">Rien de défini pour l&apos;instant ?</strong> C&apos;est parfaitement normal. Vous pourrez construire ces éléments dans l&apos;Atelier.</div>}
              </div>
            )}

            <div className="mt-9 pt-6 border-t border-[#c6c6cd]/30 flex items-center justify-between gap-3">
              {step > 1 ? <button type="button" onClick={() => { setError(null); setStep((current) => current - 1); }} className="px-4 py-2.5 text-xs font-semibold text-[#0b1c30] border border-[#c6c6cd] rounded-lg hover:bg-[#eff4ff] flex items-center gap-1.5"><ArrowLeft className="w-3.5 h-3.5" /> Précédent</button> : <Link href="/dashboard" className="text-xs text-[#76777d] hover:text-[#0b1c30]">Quitter</Link>}
              {step < 3 ? <button type="button" data-testid="next-step-btn" onClick={() => { if (canContinue) { setError(null); setStep((current) => current + 1); } }} disabled={!canContinue} className="px-5 py-2.5 text-xs font-semibold bg-[#0b1c30] text-white rounded-lg hover:bg-[#131b2e] disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5">Continuer <ArrowRight className="w-3.5 h-3.5 text-[#ffddb8]" /></button> : <button type="button" onClick={() => setStep(4)} className="px-5 py-2.5 text-xs font-semibold bg-[#0b1c30] text-white rounded-lg flex items-center gap-1.5"><span>Voir la synthèse</span><ArrowRight className="w-3.5 h-3.5 text-[#ffddb8]" /></button>}
            </div>
          </section>

          <aside className="hidden lg:block sticky top-24 space-y-3">
            <div className="rounded-xl bg-[#0b1c30] text-white p-5">
              <div className="text-[10px] font-mono uppercase tracking-wider text-[#ffddb8] font-bold mb-3">Book Loop</div>
              <p className="font-playfair text-lg leading-snug">L&apos;IA propose, vous décidez.</p>
              <p className="text-[11px] text-white/70 mt-2 leading-relaxed">Vous pouvez laisser des zones ouvertes. Book Loop n&apos;a pas besoin que votre histoire soit déjà entièrement définie.</p>
            </div>
            <div className="rounded-xl border border-[#c6c6cd]/40 bg-white p-4 space-y-3">
              {["Votre histoire", "Votre direction", "Ce que vous avez déjà imaginé"].map((label, index) => <div key={label} className="flex items-center gap-2 text-[11px]"><span className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-[9px] font-bold ${step > index + 1 ? "bg-[#0b1c30] text-white" : step === index + 1 ? "bg-[#ffddb8] text-[#2a1700]" : "bg-[#eff4ff] text-[#76777d]"}`}>{step > index + 1 ? <Check className="w-3 h-3" /> : index + 1}</span><span className={step === index + 1 ? "font-semibold text-[#0b1c30]" : "text-[#76777d]"}>{label}</span></div>)}
            </div>
          </aside>
        </div>

        {step === 4 && (
          <section className="mt-8 bg-white rounded-2xl border border-[#b87500]/40 shadow-xs p-5 sm:p-8 animate-fadeIn">
            <div className="max-w-2xl">
              <span className="text-[10px] font-mono font-bold text-[#b87500] uppercase tracking-wider">Synthèse</span>
              <h2 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30] mt-1">Voici ce que nous avons compris</h2>
              <p className="text-sm text-[#5f5e5b] mt-2">Relisez rapidement. Vous pourrez tout modifier ensuite dans l&apos;Atelier.</p>
            </div>
            <div className="mt-7 grid md:grid-cols-2 gap-4">
              <div className="rounded-xl bg-[#faf9f6] border border-[#c6c6cd]/40 p-5"><span className="text-[10px] font-mono uppercase text-[#b87500] font-bold">Votre histoire</span><h3 className="font-playfair text-lg font-bold text-[#0b1c30] mt-1">{title || "Projet sans titre"}</h3><div className="flex flex-wrap gap-1.5 mt-2">{genresSelected.length ? genresSelected.map((genre) => <span key={genre} className="px-2 py-1 rounded-full bg-[#ffddb8] text-[9px] font-semibold text-[#2a1700]">{genre}</span>) : <span className="text-[10px] text-[#76777d]">Genre encore ouvert</span>}</div><p className="text-xs text-[#45464d] mt-3 leading-relaxed">{premise}</p></div>
              <div className="rounded-xl bg-[#faf9f6] border border-[#c6c6cd]/40 p-5"><span className="text-[10px] font-mono uppercase text-[#b87500] font-bold">Votre direction</span><p className="text-xs text-[#45464d] mt-2 leading-relaxed">{intent || "Vous n&apos;avez pas encore défini de direction précise."}</p>{audience && <p className="text-[10px] text-[#76777d] mt-3">Public · {audience}</p>}{tone && <p className="text-[10px] text-[#76777d] mt-1">Tonalité · {tone}</p>}</div>
              <div className="rounded-xl bg-[#faf9f6] border border-[#c6c6cd]/40 p-5 md:col-span-2"><span className="text-[10px] font-mono uppercase text-[#b87500] font-bold">Éléments importants</span>{elements.length ? <div className="mt-3 grid sm:grid-cols-2 gap-2">{elements.map((element) => <div key={element.id} className="text-xs"><span className="font-semibold text-[#0b1c30]">{element.name || element.type}</span><span className="text-[#76777d]"> · {element.type}</span></div>)}</div> : <p className="text-xs text-[#76777d] mt-2">Aucun élément défini pour l&apos;instant.</p>}{constraints.length > 0 && <div className="mt-4 pt-3 border-t border-[#c6c6cd]/40"><span className="text-[10px] font-semibold text-[#0b1c30]">À respecter</span><div className="flex flex-wrap gap-1.5 mt-2">{constraints.map((constraint) => <span key={constraint} className="px-2 py-1 rounded-full bg-[#ffddb8] text-[9px] text-[#2a1700]">{constraint}</span>)}</div></div>}</div>
            </div>
            {error && <p role="alert" className="mt-5 text-xs text-red-700">{error}</p>}
            <div className="mt-7 pt-6 border-t border-[#c6c6cd]/30 flex flex-col-reverse sm:flex-row sm:items-center justify-between gap-3"><button type="button" onClick={() => setStep(3)} className="px-4 py-2.5 text-xs font-semibold text-[#0b1c30] border border-[#c6c6cd] rounded-lg flex items-center justify-center gap-1.5"><ArrowLeft className="w-3.5 h-3.5" /> Modifier</button><button type="button" onClick={() => void handleFinish()} disabled={creating} className="px-5 py-2.5 text-xs font-bold bg-[#0b1c30] text-[#ffddb8] rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"><Check className="w-4 h-4" />{creating ? "Création du projet…" : "C'est bien ça — commencer l'atelier"}</button></div>
          </section>
        )}
      </main>
    </div>
  );
}
