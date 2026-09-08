"use client";

import { StudioChapterController } from "../hooks/useStudioChapter";

export function StudioSidebar({ controller }: { controller: StudioChapterController }) {
  const { activeTab, setActiveTab, versions, activeVersion, latestReview, project, contextError, canonicalContext, setSelectedVersionNumber } = controller;
  return (
    <aside className="w-full shrink-0 overflow-y-auto border-t border-[#c6c6cd]/30 bg-[#f8f9ff] p-4 lg:w-[360px] lg:border-l lg:border-t-0">
      <div className="mb-4 flex gap-1 rounded-lg border border-[#c6c6cd]/30 bg-[#e5eeff] p-1 text-xs font-mono font-bold text-[#0b1c30]">
        {(["manuscript", "history", "context"] as const).map((tab) => <button key={tab} type="button" onClick={() => setActiveTab(tab)} className={`flex-1 rounded py-1.5 ${activeTab === tab ? "bg-white shadow-xs" : "text-[#76777d]"}`}>{tab === "manuscript" ? "Relire" : tab === "history" ? `Versions (${versions.length})` : "Repères"}</button>)}
      </div>

      {activeTab === "manuscript" && <div className="space-y-4">
        {latestReview ? <section className="rounded-xl border border-[#c6c6cd]/30 bg-white p-4 shadow-xs">
          <div className="mb-3 flex items-center justify-between"><span className="text-xs font-bold text-[#0b1c30]">Dernière relecture</span>{latestReview.timestamp && <span className="text-[10px] font-mono text-[#76777d]">{latestReview.timestamp}</span>}</div>
          <div className="grid grid-cols-2 gap-2 text-center">
            <div className="rounded border border-[#c6c6cd]/20 bg-[#f8f9ff] p-2"><div className="text-[10px] text-[#45464d]">Style</div><div className="text-sm font-bold">{latestReview.scoreStyle ?? "—"}{latestReview.scoreStyle !== undefined ? "/10" : ""}</div></div>
            <div className="rounded border border-[#c6c6cd]/20 bg-[#f8f9ff] p-2"><div className="text-[10px] text-[#45464d]">Cohérence</div><div className="text-sm font-bold">{latestReview.scoreCoherence ?? "—"}{latestReview.scoreCoherence !== undefined ? "/10" : ""}</div></div>
          </div>
          {latestReview.critique && <p className="mt-3 text-xs italic text-[#45464d]">{latestReview.critique}</p>}
        </section> : <div className="rounded-xl border border-dashed border-[#c6c6cd]/50 p-5 text-xs text-[#76777d]">Aucune relecture disponible.</div>}
        {project.characters?.length ? <section className="rounded-xl border border-[#c6c6cd]/30 bg-white p-4"><span className="mb-2 block text-[11px] font-mono font-bold uppercase text-[#76777d]">Personnages du livre</span><div className="space-y-2">{project.characters.slice(0, 5).map((character) => <div key={character.id} className="flex items-center gap-2"><div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#0b1c30] text-xs font-bold text-[#ffddb8]">{character.name.charAt(0)}</div><div><div className="text-xs font-bold text-[#0b1c30]">{character.name}</div><div className="text-[10px] text-[#45464d]">{character.role}</div></div></div>)}</div></section> : null}
      </div>}

      {activeTab === "history" && <div className="space-y-3">
        <span className="block text-xs font-mono font-bold uppercase tracking-wider text-[#76777d]">Versions précédentes</span>
        {versions.length ? versions.map((version) => { const selected = version.versionNumber === activeVersion?.versionNumber; return <button key={version.id || version.versionNumber} type="button" onClick={() => setSelectedVersionNumber(version.versionNumber)} className={`w-full rounded-xl border p-3.5 text-left ${selected ? "border-[#0b1c30] bg-[#0b1c30] text-white" : "border-[#c6c6cd]/40 bg-white text-[#0b1c30]"}`}><div className="flex items-center justify-between gap-2 text-xs font-mono font-bold"><span>v{version.versionNumber}</span><span>{version.status}</span></div><p className={`mt-2 line-clamp-3 text-xs font-merriweather ${selected ? "text-[#c6c6cd]" : "text-[#5f5e5b]"}`}>{version.content}</p></button>; }) : <div className="rounded border border-dashed border-[#c6c6cd]/50 p-4 text-xs text-[#76777d]">Aucune version précédente.</div>}
      </div>}

      {activeTab === "context" && <div className="space-y-3">
        <span className="block text-xs font-mono font-bold uppercase tracking-wider text-[#76777d]">Repères de l’histoire</span>
        {contextError ? <div className="rounded border border-[#e8aaa3] bg-[#ffdad6] p-3 text-xs text-[#a33b32]">{contextError}</div> : canonicalContext ? <div className="space-y-3 text-xs">
          <div className="rounded-lg border border-[#c6c6cd]/30 bg-white p-3"><strong>Votre intention</strong><p className="mt-1 text-[#45464d]">{canonicalContext.authorIdea}</p></div>
          <div className="rounded-lg border border-[#c6c6cd]/30 bg-white p-3"><strong>Votre univers</strong><p className="mt-1 text-[#45464d]">{canonicalContext.lore}</p></div>
          <div className="rounded-lg border border-[#c6c6cd]/30 bg-white p-3"><strong>Vos règles d’écriture</strong><ul className="mt-1 list-disc pl-4 text-[#45464d]">{canonicalContext.constraints.map((constraint, index) => <li key={index}>{constraint}</li>)}</ul></div>
          <div className="rounded-lg border border-[#c6c6cd]/30 bg-white p-3"><strong>Ce qui s’est passé avant</strong><p className="mt-1 whitespace-pre-wrap text-[#45464d]">{canonicalContext.previousSummaries || "Aucun chapitre précédent approuvé."}</p></div>
        </div> : <div className="rounded border border-dashed border-[#c6c6cd]/50 p-4 text-xs text-[#76777d]">Aucun repère disponible pour ce chapitre.</div>}
      </div>}
    </aside>
  );
}
