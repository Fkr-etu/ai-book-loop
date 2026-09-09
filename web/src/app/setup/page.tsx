"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, BookOpen, Check, Feather, Lightbulb, MapPin, Plus, Sparkles, Trash2, UserRound } from "lucide-react";
import { realApiClient, RealApiError } from "@/services/realApiClient";
import { getApiErrorMessage } from "@/services/apiErrorMessages";
import { track } from "@/lib/analytics";

type ElementType = "Personnage" | "Lieu" | "Époque / contexte" | "Organisation" | "Objet" | "Règle" | "Événement" | "Autre";
type SetupElement = { id: number; type: ElementType; name: string; description: string };

const genres = ["Roman", "Policier", "Thriller", "Romance", "Fantasy", "Science-fiction", "Historique", "Littérature générale", "Jeunesse", "Autre"];
const audiences = ["Adultes", "Adolescents", "Jeunesse", "Grand public", "Je ne sais pas encore"];
const tones = ["Sombre", "Tendu", "Intime", "Léger", "Drôle", "Contemplatif", "Épique", "Je ne sais pas encore"];
const elementTypes: { type: ElementType; icon: typeof UserRound }[] = [
  { type: "Personnage", icon: UserRound }, { type: "Lieu", icon: MapPin }, { type: "Époque / contexte", icon: BookOpen },
  { type: "Organisation", icon: Sparkles }, { type: "Objet", icon: BookOpen }, { type: "Règle", icon: Lightbulb }, { type: "Événement", icon: Sparkles }, { type: "Autre", icon: Plus },
];

function apiError(error: unknown): string {
  return error instanceof RealApiError ? getApiErrorMessage(error, error.message) : "Impossible de créer votre projet pour le moment.";
}
function chip(selected: boolean): string {
  return selected ? "border-[#0b1c30] bg-[#0b1c30] text-white" : "border-[#c6c6cd]/70 bg-white text-[#45464d] hover:border-[#b87500]/70";
}

export default function SetupPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [title, setTitle] = useState("");
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [premise, setPremise] = useState("");
  const [intent, setIntent] = useState("");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState("");
  const [constraints, setConstraints] = useState<string[]>([]);
  const [constraintDraft, setConstraintDraft] = useState("");
  const [elements, setElements] = useState<SetupElement[]>([]);
  const [elementType, setElementType] = useState<ElementType | null>(null);
  const [elementName, setElementName] = useState("");
  const [elementDescription, setElementDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const lore = useMemo(() => elements.map((e) => `${e.type}: ${e.name.trim()}${e.description.trim() ? ` — ${e.description.trim()}` : ""}`).join("\n"), [elements]);
  const premisePlaceholder = selectedGenres.includes("Policier") || selectedGenres.includes("Thriller")
    ? "Une inspectrice enquête sur une série de meurtres qui semblent reproduire des affaires non résolues vingt ans auparavant…"
    : selectedGenres.includes("Fantasy")
      ? "Dans un royaume où les souvenirs peuvent être échangés, une jeune femme découvre qu’une partie de son enfance lui a été retirée…"
      : "Une femme revient dans sa ville natale après quinze ans d’absence et découvre que quelqu’un connaît un secret qu’elle n’a jamais raconté…";

  const addConstraint = () => {
    const value = constraintDraft.trim();
    if (!value || constraints.includes(value)) return;
    setConstraints((items) => [...items, value]);
    setConstraintDraft("");
  };
  const addElement = () => {
    if (!elementType || (!elementName.trim() && !elementDescription.trim())) return;
    setElements((items) => [...items, { id: Date.now(), type: elementType, name: elementName.trim(), description: elementDescription.trim() }]);
    setElementType(null); setElementName(""); setElementDescription("");
  };
  const finish = async () => {
    setCreating(true); setError(null);
    try {
      const book = await realApiClient.createBook({
        title: title.trim() || "Projet sans titre",
        theme: selectedGenres.length ? selectedGenres.join(" · ") : "Projet narratif",
        author_idea: premise.trim(), lore, constraints,
        creative_brief: { premise: premise.trim(), audience, tone, themes: intent.trim() ? [intent.trim()] : [], must_include: [], must_avoid: [] },
      });
      track("book_created");
      router.push(`/studio?bookId=${encodeURIComponent(book.id)}`);
    } catch (err) { setError(apiError(err)); } finally { setCreating(false); }
  };

  const stepTitles = ["Votre histoire", "Votre direction", "Ce que vous avez déjà imaginé"];
  const isReview = step === 4;

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter selection:bg-[#ffddb8]">
      <header className="sticky top-0 z-20 border-b border-[#c6c6cd]/30 bg-white/90 backdrop-blur">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2.5" aria-label="Retour à la bibliothèque"><div className="w-8 h-8 rounded bg-[#0b1c30] text-[#ffddb8] flex items-center justify-center"><Feather className="w-4 h-4" /></div><span className="font-playfair font-bold text-lg text-[#0b1c30] hidden sm:block">Book Loop</span></Link>
          <span className="text-[11px] text-[#76777d]">{isReview ? "Synthèse" : `${step} / 3`}</span>
        </div>
        <div className="h-1 bg-[#e5eeff]"><div className="h-1 bg-[#0b1c30] transition-all duration-300" style={{ width: `${isReview ? 100 : (step / 3) * 100}%` }} /></div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 md:py-12">
        {!isReview ? <div className="grid lg:grid-cols-[1fr_280px] gap-8 items-start">
          <section className="bg-white rounded-2xl border border-[#c6c6cd]/40 shadow-xs p-5 sm:p-8">
            {step === 1 && <div className="space-y-7">
              <Header eyebrow="Votre histoire" title="Parlez-nous de votre histoire" text="Vous n’avez pas besoin d’avoir tout défini. Quelques éléments suffisent pour commencer." />
              <Field label="Comment appelez-vous votre projet ?" hint="Le titre peut être provisoire."><input id="setup-title" aria-label="Comment appelez-vous votre projet ?" value={title} onChange={(e) => setTitle(e.target.value)} className="field" placeholder="Le dernier hiver, Projet sans titre…" /></Field>
              <div><div className="flex justify-between mb-2"><span className="label">Quel type de récit écrivez-vous ?</span><span className="optional">Optionnel</span></div><div className="flex flex-wrap gap-2">{genres.map((g) => <button key={g} type="button" onClick={() => setSelectedGenres((items) => items.includes(g) ? items.filter((x) => x !== g) : [...items, g])} className={`pill ${chip(selectedGenres.includes(g))}`}>{g}</button>)}</div><p className="hint">Plusieurs choix sont possibles.</p></div>
              <Field label="De quoi parle votre histoire ?" hint="Parlez du point de départ, des personnages ou de l’idée qui vous donne envie d’écrire."><textarea id="setup-premise" aria-label="De quoi parle votre histoire ?" value={premise} onChange={(e) => setPremise(e.target.value)} rows={7} className="textarea" placeholder={premisePlaceholder} /></Field>
            </div>}

            {step === 2 && <div className="space-y-7">
              <Header eyebrow="Votre direction" title="Qu’avez-vous envie de raconter ?" text="Une émotion, une question, une idée ou simplement une envie d’écrire suffit." />
              <Field label="Qu’aimeriez-vous faire ressentir, raconter ou explorer ?"><textarea id="setup-intent" aria-label="Qu'aimeriez-vous faire ressentir, raconter ou explorer ?" value={intent} onChange={(e) => setIntent(e.target.value)} rows={5} className="textarea" placeholder="Créer une enquête où le lecteur doute constamment de la vérité…" /><div className="flex flex-wrap gap-2 mt-2">{["Créer du suspense", "Explorer la culpabilité", "Faire réfléchir", "Faire rire", "Créer de l’émotion"].map((x) => <button key={x} type="button" onClick={() => setIntent((v) => v ? `${v} ${x}.` : `${x}.`)} className="suggestion">{x}</button>)}</div></Field>
              <ChoiceGroup label="Pour qui écrivez-vous ?" values={audiences} value={audience} onChange={setAudience} />
              <ChoiceGroup label="Quelle tonalité imaginez-vous ?" values={tones} value={tone} onChange={setTone} />
              <div><div className="label mb-1">Y a-t-il des choses que nous devons absolument respecter ?</div><p className="hint mb-3">Rester réaliste, une époque précise, un secret à préserver, une règle de narration…</p><div className="flex gap-2"><input aria-label="Ajouter une contrainte" value={constraintDraft} onChange={(e) => setConstraintDraft(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addConstraint(); } }} className="field flex-1" placeholder="Ajouter une contrainte" /><button type="button" onClick={addConstraint} aria-label="Ajouter une contrainte" className="iconButton"><Plus className="w-4 h-4" /></button></div>{constraints.length > 0 && <div className="flex flex-wrap gap-2 mt-3">{constraints.map((c) => <span key={c} className="constraint">{c}<button type="button" aria-label={`Supprimer ${c}`} onClick={() => setConstraints((items) => items.filter((x) => x !== c))}><Trash2 className="w-3 h-3" /></button></span>)}</div>}</div>
            </div>}

            {step === 3 && <div className="space-y-7">
              <Header eyebrow="Ce que vous avez déjà imaginé" title="Quels éléments importants connaissez-vous déjà ?" text="Personnages, lieux, époque, organisations, objets, événements… Ajoutez uniquement ce que vous connaissez déjà." />
              <div className="rounded-xl border border-dashed border-[#c6c6cd] bg-[#faf9f6] p-4"><div className="grid grid-cols-2 sm:grid-cols-4 gap-2">{elementTypes.map(({ type, icon: Icon }) => <button key={type} type="button" onClick={() => setElementType(type)} className={`p-3 rounded-lg border text-left ${elementType === type ? "border-[#b87500] bg-white" : "border-transparent bg-white/70 hover:border-[#c6c6cd]"}`}><Icon className="w-4 h-4 text-[#b87500] mb-1.5" /><span className="text-[10px] font-semibold">{type}</span></button>)}</div>{elementType && <div className="mt-4 pt-4 border-t border-[#c6c6cd]/40 space-y-3"><span className="eyebrow">Nouvel élément · {elementType}</span><input value={elementName} onChange={(e) => setElementName(e.target.value)} className="field" placeholder={elementType === "Personnage" ? "Nom du personnage" : "Nom ou repère"} /><textarea value={elementDescription} onChange={(e) => setElementDescription(e.target.value)} rows={3} className="textarea" placeholder="Ce que vous savez déjà de cet élément…" /><button type="button" onClick={addElement} disabled={!elementName.trim() && !elementDescription.trim()} className="primaryButton disabled:opacity-40"><Plus className="w-3.5 h-3.5" /> Ajouter cet élément</button></div>}</div>
              {elements.length ? <div className="space-y-2">{elements.map((e) => <div key={e.id} className="flex justify-between gap-3 p-3 rounded-lg border border-[#c6c6cd]/40 bg-white"><div><span className="eyebrow">{e.type}</span><p className="text-xs font-semibold mt-1">{e.name || "Élément sans nom"}</p>{e.description && <p className="text-[11px] text-[#5f5e5b] mt-1">{e.description}</p>}</div><button type="button" aria-label={`Supprimer ${e.name || e.type}`} onClick={() => setElements((items) => items.filter((x) => x.id !== e.id))} className="text-[#76777d] hover:text-red-700"><Trash2 className="w-3.5 h-3.5" /></button></div>)}</div> : <div className="rounded-xl bg-[#eff4ff] p-4 text-xs text-[#45464d]"><strong className="text-[#0b1c30]">Rien de défini ?</strong> C’est parfaitement normal. Vous pourrez construire ces éléments dans l’Atelier.</div>}
            </div>}

            <div className="mt-9 pt-6 border-t border-[#c6c6cd]/30 flex justify-between gap-3">{step > 1 ? <button type="button" onClick={() => setStep((s) => s - 1)} className="secondaryButton"><ArrowLeft className="w-3.5 h-3.5" /> Précédent</button> : <Link href="/dashboard" className="text-xs text-[#76777d] self-center">Quitter</Link>}{step < 3 ? <button type="button" data-testid="next-step-btn" onClick={() => premise.trim() && setStep((s) => s + 1)} disabled={step === 1 && !premise.trim()} className="primaryButton disabled:opacity-40">Continuer <ArrowRight className="w-3.5 h-3.5" /></button> : <button type="button" onClick={() => setStep(4)} className="primaryButton">Voir la synthèse <ArrowRight className="w-3.5 h-3.5" /></button>}</div>
          </section>
          <aside className="hidden lg:block sticky top-24 space-y-3"><div className="rounded-xl bg-[#0b1c30] text-white p-5"><span className="eyebrow text-[#ffddb8]">Book Loop</span><p className="font-playfair text-lg mt-3">L’IA propose, vous décidez.</p><p className="text-[11px] text-white/70 mt-2 leading-relaxed">Laissez des zones ouvertes. Votre histoire n’a pas besoin d’être entièrement définie pour commencer.</p></div><div className="rounded-xl border border-[#c6c6cd]/40 bg-white p-4 space-y-3">{stepTitles.map((label, i) => <div key={label} className="flex items-center gap-2 text-[11px]"><span className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-mono font-bold ${step > i + 1 ? "bg-[#0b1c30] text-white" : step === i + 1 ? "bg-[#ffddb8] text-[#2a1700]" : "bg-[#eff4ff] text-[#76777d]"}`}>{step > i + 1 ? <Check className="w-3 h-3" /> : i + 1}</span><span className={step === i + 1 ? "font-semibold text-[#0b1c30]" : "text-[#76777d]"}>{label}</span></div>)}</div></aside>
        </div> : <section className="max-w-4xl mx-auto bg-white rounded-2xl border border-[#b87500]/40 shadow-xs p-5 sm:p-8">
          <Header eyebrow="Synthèse" title="Voici ce que nous avons compris" text="Relisez rapidement. Vous pourrez tout modifier ensuite dans l’Atelier." />
          <div className="grid md:grid-cols-2 gap-4 mt-7"><Summary title="Votre histoire"><h3 className="font-playfair text-lg font-bold">{title || "Projet sans titre"}</h3><div className="flex flex-wrap gap-1.5 mt-2">{selectedGenres.length ? selectedGenres.map((g) => <span key={g} className="constraint">{g}</span>) : <span className="hint">Genre encore ouvert</span>}</div><p className="summaryText">{premise}</p></Summary><Summary title="Votre direction"><p className="summaryText">{intent || "Vous n’avez pas encore défini de direction précise."}</p>{audience && <p className="meta">Public · {audience}</p>}{tone && <p className="meta">Tonalité · {tone}</p>}</Summary><Summary title="Éléments importants" wide>{elements.length ? <div className="grid sm:grid-cols-2 gap-2">{elements.map((e) => <div key={e.id} className="text-xs"><strong>{e.name || e.type}</strong><span className="meta"> · {e.type}</span></div>)}</div> : <p className="hint">Aucun élément défini pour l’instant.</p>}{constraints.length > 0 && <div className="mt-4 pt-3 border-t border-[#c6c6cd]/40"><span className="text-[10px] font-semibold">À respecter</span><div className="flex flex-wrap gap-1.5 mt-2">{constraints.map((c) => <span key={c} className="constraint">{c}</span>)}</div></div>}</Summary></div>
          {error && <p role="alert" className="mt-5 text-xs text-red-700">{error}</p>}
          <div className="mt-7 pt-6 border-t border-[#c6c6cd]/30 flex flex-col-reverse sm:flex-row justify-between gap-3"><button type="button" onClick={() => setStep(3)} className="secondaryButton justify-center"><ArrowLeft className="w-3.5 h-3.5" /> Modifier</button><button type="button" onClick={() => void finish()} disabled={creating} className="primaryButton justify-center disabled:opacity-50"><Check className="w-4 h-4" /> {creating ? "Création du projet…" : "C’est bien ça — commencer l’atelier"}</button></div>
        </section>}
      </main>
      <style jsx>{`.field{width:100%;padding:.75rem 1rem;font-size:.875rem;border:1px solid #c6c6cd;border-radius:.75rem;background:#faf9f6;outline:none}.field:focus,.textarea:focus{border-color:#b87500}.textarea{width:100%;padding:1rem;font-size:.875rem;border:1px solid #c6c6cd;border-radius:.75rem;background:#faf9f6;outline:none;font-family:inherit;line-height:1.7;resize:vertical}.label{font-size:.875rem;font-weight:600;color:#0b1c30}.hint,.optional{font-size:11px;color:#76777d}.pill{padding:.5rem .75rem;border-radius:9999px;border-width:1px;font-size:.75rem;font-weight:600;transition:all .15s}.suggestion{padding:.375rem .625rem;border-radius:9999px;background:#eff4ff;font-size:10px;color:#45464d}.constraint{display:inline-flex;align-items:center;gap:.4rem;padding:.375rem .625rem;border-radius:9999px;background:#ffddb8;color:#2a1700;font-size:10px;font-weight:600}.iconButton{padding:.65rem;border-radius:.5rem;background:#0b1c30;color:white}.primaryButton,.secondaryButton{display:inline-flex;align-items:center;gap:.4rem;padding:.625rem 1rem;border-radius:.5rem;font-size:.75rem;font-weight:600}.primaryButton{background:#0b1c30;color:white}.secondaryButton{border:1px solid #c6c6cd;color:#0b1c30;background:white}.eyebrow{display:block;font-size:10px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#b87500}.summaryText{font-size:.75rem;line-height:1.7;color:#45464d;margin-top:.75rem}.meta{font-size:10px;color:#76777d;margin-top:.5rem}`}</style>
    </div>
  );
}

function Header({ eyebrow, title, text }: { eyebrow: string; title: string; text: string }) {
  return <div className="max-w-2xl"><span className="eyebrow">{eyebrow}</span><h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30] mt-1">{title}</h1><p className="text-sm text-[#5f5e5b] mt-2 leading-relaxed">{text}</p></div>;
}
function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return <div><label className="label block mb-1">{label}</label>{hint && <p className="hint mb-2">{hint}</p>}{children}</div>;
}
function ChoiceGroup({ label, values, value, onChange }: { label: string; values: string[]; value: string; onChange: (value: string) => void }) {
  return <div><div className="label mb-2">{label} <span className="optional">Optionnel</span></div><div className="flex flex-wrap gap-2">{values.map((item) => <button key={item} type="button" onClick={() => onChange(item === value ? "" : item)} className={`pill ${chip(item === value)}`}>{item}</button>)}</div></div>;
}
function Summary({ title, children, wide = false }: { title: string; children: React.ReactNode; wide?: boolean }) {
  return <div className={`rounded-xl bg-[#faf9f6] border border-[#c6c6cd]/40 p-5 ${wide ? "md:col-span-2" : ""}`}><span className="eyebrow">{title}</span><div className="mt-2">{children}</div></div>;
}
