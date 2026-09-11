"use client";

import { FormEvent, useState } from "react";
import { Eye, Loader2, Send, X } from "lucide-react";
import type { GrillPersonality } from "@/types";
import type { StudioChapterController } from "../hooks/useStudioChapter";

const PERSONALITY_LABELS: Record<GrillPersonality, string> = {
  challenger: "Le Challenger",
  editor: "L’Éditeur",
  devils_advocate: "L’Avocat du diable",
  demanding_kind: "Le Bienveillant exigeant",
};

export function CriticalEye({ controller }: { controller: StudioChapterController }) {
  const { project, grillNudge, grillOpen, grillResponse, grillLoading, grillError, grillMessages, startGrill, answerGrill, dismissGrill, closeGrill } = controller;
  const [answer, setAnswer] = useState("");
  const personality = project.grillPersonality || "challenger";

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!answer.trim()) return;
    const value = answer;
    setAnswer("");
    await answerGrill(value);
  };

  if (!grillOpen && !grillNudge) return null;

  if (!grillOpen) return (
    <section className="mb-4 rounded-xl border border-[#b87500]/30 bg-[#fffaf2] p-4 shadow-xs" aria-live="polite">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#0b1c30] text-[#ffddb8]"><Eye className="h-4 w-4" /></div>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-bold text-[#0b1c30]">Vous cherchez la suite ?</p>
          <p className="mt-1 text-[11px] leading-relaxed text-[#5f5e5b]">Votre Œil critique peut vous poser une question pour débloquer votre réflexion, sans écrire à votre place.</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button type="button" onClick={startGrill} className="inline-flex items-center gap-1.5 rounded bg-[#0b1c30] px-3 py-2 text-[11px] font-bold text-white">Faire intervenir mon Œil critique <Eye className="h-3 w-3" /></button>
            <button type="button" onClick={dismissGrill} className="px-2 py-2 text-[11px] text-[#76777d] hover:text-[#0b1c30]">Pas maintenant</button>
          </div>
        </div>
      </div>
    </section>
  );

  return (
    <section className="mb-4 overflow-hidden rounded-xl border border-[#0b1c30]/15 bg-white shadow-xs" aria-label="Œil critique">
      <header className="flex items-center justify-between gap-3 border-b border-[#c6c6cd]/30 bg-[#0b1c30] px-4 py-3 text-white">
        <div className="flex items-center gap-2.5"><div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#ffddb8] text-[#0b1c30]"><Eye className="h-3.5 w-3.5" /></div><div><p className="text-xs font-bold">Votre Œil critique</p><p className="text-[10px] text-white/60">{PERSONALITY_LABELS[personality]}</p></div></div>
        <button type="button" onClick={closeGrill} aria-label="Fermer l’Œil critique" className="text-white/60 hover:text-white"><X className="h-4 w-4" /></button>
      </header>
      <div className="space-y-3 p-4">
        {grillMessages.length === 0 && grillLoading ? <div className="flex items-center gap-2 text-xs text-[#76777d]"><Loader2 className="h-3.5 w-3.5 animate-spin" /> Il cherche le point à mettre à l’épreuve…</div> : null}
        {grillResponse && <div className="rounded-lg bg-[#f8f5f0] p-3.5"><p className="text-xs leading-relaxed text-[#45464d]">{grillResponse.reply}</p>{grillResponse.question && <p className="mt-2 font-playfair text-base font-bold leading-snug text-[#0b1c30]">{grillResponse.question}</p>}</div>}
        {grillError && <p className="rounded-lg bg-[#ffdad6] p-3 text-xs text-[#a33b32]">{grillError}</p>}
        {grillResponse?.done ? <p className="text-[11px] text-[#76777d]">La session est terminée. Gardez ces questions comme pistes de réflexion.</p> : <form onSubmit={submit} className="flex gap-2"><input value={answer} onChange={(event) => setAnswer(event.target.value)} disabled={grillLoading} placeholder="Votre réponse…" aria-label="Votre réponse à l’Œil critique" className="min-w-0 flex-1 rounded-lg border border-[#c6c6cd]/50 bg-white px-3 py-2.5 text-xs text-[#0b1c30] outline-none focus:border-[#0b1c30]" /><button type="submit" disabled={grillLoading || !answer.trim()} aria-label="Répondre à l’Œil critique" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#0b1c30] text-white disabled:opacity-40"><Send className="h-3.5 w-3.5" /></button></form>}
      </div>
    </section>
  );
}
