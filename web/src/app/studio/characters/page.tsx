"use client";

import React, { useEffect, useMemo, useState } from "react";
import { GitFork, Plus, Save, Trash2, Users, X } from "lucide-react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import { realApiClient, RealApiError } from "@/services/realApiClient";
import type { BackendCharacter, BackendCharacterRelation } from "@/types/api";

const EMPTY_FORM = { name: "", summary: "", aliases: "", attributes: "" };
function message(error: unknown) { return error instanceof RealApiError ? error.message : "Impossible de charger les personnages."; }
function attributesToText(attributes: Record<string, string>) { return Object.entries(attributes).map(([key, value]) => `${key}: ${value}`).join("\n"); }
function parseAttributes(value: string): Record<string, string> { return Object.fromEntries(value.split("\n").map((line) => line.trim()).filter(Boolean).map((line) => { const i = line.indexOf(":"); return i > 0 ? [line.slice(0, i).trim(), line.slice(i + 1).trim()] : [line, ""]; }).filter(([key]) => key)); }

export default function CharactersPage() {
  const { project } = useProjectStore();
  const bookId = project.id;
  const [characters, setCharacters] = useState<BackendCharacter[]>([]);
  const [relations, setRelations] = useState<BackendCharacterRelation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [relationTarget, setRelationTarget] = useState("");
  const [relationType, setRelationType] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const selected = useMemo(() => characters.find((character) => character.id === selectedId) ?? null, [characters, selectedId]);

  const refresh = async () => {
    if (!bookId) return;
    setLoading(true); setError(null);
    try {
      const [nextCharacters, nextRelations] = await Promise.all([realApiClient.listCharacters(bookId), realApiClient.listCharacterRelations(bookId)]);
      setCharacters(nextCharacters); setRelations(nextRelations);
      setSelectedId((current) => current && nextCharacters.some((character) => character.id === current) ? current : nextCharacters[0]?.id ?? null);
    } catch (err) { setError(message(err)); } finally { setLoading(false); }
  };
  useEffect(() => { void refresh(); }, [bookId]);
  useEffect(() => { setForm(selected ? { name: selected.name, summary: selected.summary, aliases: selected.aliases.join(", "), attributes: attributesToText(selected.attributes) } : EMPTY_FORM); }, [selected]);

  const createCharacter = async () => {
    if (!bookId || !form.name.trim()) return;
    setSaving(true); setError(null);
    try {
      const character = await realApiClient.createCharacter(bookId, { name: form.name.trim(), aliases: form.aliases.split(",").map((v) => v.trim()).filter(Boolean), summary: form.summary.trim(), attributes: parseAttributes(form.attributes), assertion_ids: [] });
      setCharacters((current) => [...current, character]); setSelectedId(character.id);
    } catch (err) { setError(message(err)); } finally { setSaving(false); }
  };
  const saveCharacter = async () => {
    if (!bookId || !selected) return;
    setSaving(true); setError(null);
    try {
      const updated = await realApiClient.updateCharacter(bookId, selected.id, { name: form.name.trim(), aliases: form.aliases.split(",").map((v) => v.trim()).filter(Boolean), summary: form.summary.trim(), attributes: parseAttributes(form.attributes) });
      setCharacters((current) => current.map((character) => character.id === updated.id ? updated : character));
    } catch (err) { setError(message(err)); } finally { setSaving(false); }
  };
  const deleteCharacter = async () => {
    if (!bookId || !selected || !window.confirm(`Supprimer « ${selected.name} » ?`)) return;
    setSaving(true); setError(null);
    try { await realApiClient.deleteCharacter(bookId, selected.id); await refresh(); } catch (err) { setError(message(err)); } finally { setSaving(false); }
  };
  const createRelation = async () => {
    if (!bookId || !selected || !relationTarget || !relationType.trim()) return;
    setSaving(true); setError(null);
    try { const relation = await realApiClient.createCharacterRelation(bookId, selected.id, relationTarget, relationType.trim()); setRelations((current) => [...current, relation]); setRelationTarget(""); setRelationType(""); } catch (err) { setError(message(err)); } finally { setSaving(false); }
  };
  const deleteRelation = async (relationId: string) => {
    if (!bookId) return;
    setSaving(true); setError(null);
    try { await realApiClient.deleteCharacterRelation(bookId, relationId); setRelations((current) => current.filter((relation) => relation.id !== relationId)); } catch (err) { setError(message(err)); } finally { setSaving(false); }
  };
  const nameFor = (id: string) => characters.find((character) => character.id === id)?.name ?? "Personnage inconnu";
  const selectedRelations = selected ? relations.filter((relation) => relation.source_character_id === selected.id || relation.target_character_id === selected.id) : [];

  return <StudioLayout><div className="p-4 sm:p-6 md:p-10 max-w-6xl mx-auto space-y-6">
    <header className="border-b border-[#c6c6cd]/30 pb-6"><span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider flex items-center gap-1.5"><Users className="w-4 h-4" /> Personnages</span><h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30] mt-1">Les personnages de votre histoire</h1><p className="text-xs text-[#45464d] mt-1">Construisez les identités narratives sans imposer de fiche-type. Les informations proposées restent révisables.</p></header>
    {error && <div role="alert" className="p-4 rounded-xl border border-red-200 bg-white text-xs text-[#ba1a1a] flex items-center justify-between gap-4"><span>{error}</span><button type="button" onClick={() => setError(null)} aria-label="Fermer"><X className="w-4 h-4" /></button></div>}
    {loading ? <div className="bg-white rounded-xl border border-[#c6c6cd]/40 p-10 text-center text-xs text-[#5f5e5b]">Chargement des personnages…</div> : <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-5">
      <section className="bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs overflow-hidden"><div className="p-4 border-b border-[#c6c6cd]/20 flex items-center justify-between"><span className="text-xs font-mono font-bold uppercase text-[#0b1c30]">Personnages ({characters.length})</span><button type="button" onClick={() => { setSelectedId(null); setForm(EMPTY_FORM); }} className="p-1.5 rounded bg-[#0b1c30] text-white" aria-label="Nouveau personnage"><Plus className="w-4 h-4" /></button></div>{characters.length === 0 ? <div className="p-6 text-xs text-[#76777d]">Aucun personnage pour le moment.</div> : <div className="divide-y divide-[#c6c6cd]/20">{characters.map((character) => <button key={character.id} type="button" onClick={() => setSelectedId(character.id)} className={`w-full text-left p-4 transition-colors ${selectedId === character.id ? "bg-[#eff4ff]" : "hover:bg-[#f8f9ff]"}`}><div className="font-semibold text-sm text-[#0b1c30] truncate">{character.name}</div><div className="text-[10px] font-mono uppercase text-[#76777d] mt-1">{character.status}</div></button>)}</div>}</section>
      <div className="space-y-5"><section className="bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs p-5 sm:p-6 space-y-5"><div className="flex items-center justify-between gap-3"><h2 className="font-playfair text-xl font-bold text-[#0b1c30]">{selected ? "Modifier le personnage" : "Nouveau personnage"}</h2>{selected && <button type="button" onClick={deleteCharacter} disabled={saving} className="text-xs font-semibold text-[#ba1a1a] flex items-center gap-1 disabled:opacity-50"><Trash2 className="w-3.5 h-3.5" /> Supprimer</button>}</div><label className="block text-xs font-semibold text-[#45464d]">Nom<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 w-full px-3 py-2.5 border border-[#c6c6cd] rounded bg-[#f8f9ff] text-sm" placeholder="Ex. Jeanne" /></label><label className="block text-xs font-semibold text-[#45464d]">Résumé<textarea value={form.summary} onChange={(e) => setForm({ ...form, summary: e.target.value })} rows={4} className="mt-1 w-full px-3 py-2.5 border border-[#c6c6cd] rounded bg-[#f8f9ff] text-sm" placeholder="Ce qui définit ce personnage dans votre histoire…" /></label><label className="block text-xs font-semibold text-[#45464d]">Alias <span className="font-normal text-[#76777d]">(séparés par des virgules)</span><input value={form.aliases} onChange={(e) => setForm({ ...form, aliases: e.target.value })} className="mt-1 w-full px-3 py-2.5 border border-[#c6c6cd] rounded bg-[#f8f9ff] text-sm" /></label><label className="block text-xs font-semibold text-[#45464d]">Attributs <span className="font-normal text-[#76777d]">(un par ligne, format clé: valeur)</span><textarea value={form.attributes} onChange={(e) => setForm({ ...form, attributes: e.target.value })} rows={5} className="mt-1 w-full px-3 py-2.5 border border-[#c6c6cd] rounded bg-[#f8f9ff] text-sm font-mono" placeholder="métier: détective\nâge: 42" /></label><div className="flex justify-end"><button type="button" onClick={selected ? saveCharacter : createCharacter} disabled={saving || !form.name.trim()} className="px-4 py-2.5 bg-[#0b1c30] text-white rounded text-xs font-bold flex items-center gap-2 disabled:opacity-50"><Save className="w-4 h-4" /> {saving ? "Enregistrement…" : selected ? "Enregistrer" : "Créer le personnage"}</button></div>{selected && <div className="pt-3 border-t border-[#c6c6cd]/20 text-[11px] text-[#76777d]">Statut : <strong className="text-[#0b1c30]">{selected.status}</strong> · Les faits provenant de sources sont reliés par des assertions plutôt que dupliqués ici.</div>}</section>
      {selected && <section className="bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs p-5 sm:p-6 space-y-4"><h2 className="font-playfair text-lg font-bold text-[#0b1c30] flex items-center gap-2"><GitFork className="w-4 h-4 text-[#b87500]" /> Relations</h2><div className="grid grid-cols-1 sm:grid-cols-[1fr_1fr_auto] gap-2"><select value={relationTarget} onChange={(e) => setRelationTarget(e.target.value)} className="px-3 py-2 border border-[#c6c6cd] rounded bg-[#f8f9ff] text-xs"><option value="">Personnage cible…</option>{characters.filter((character) => character.id !== selected.id).map((character) => <option key={character.id} value={character.id}>{character.name}</option>)}</select><input value={relationType} onChange={(e) => setRelationType(e.target.value)} placeholder="Type de relation (ex. rivalité)" className="px-3 py-2 border border-[#c6c6cd] rounded bg-[#f8f9ff] text-xs" /><button type="button" onClick={createRelation} disabled={saving || !relationTarget || !relationType.trim()} className="px-3 py-2 bg-[#0b1c30] text-white rounded text-xs font-bold disabled:opacity-50">Ajouter</button></div><div className="divide-y divide-[#c6c6cd]/20">{selectedRelations.map((relation) => <div key={relation.id} className="py-3 flex items-center justify-between gap-3 text-xs"><div><strong className="text-[#0b1c30]">{nameFor(relation.source_character_id)}</strong><span className="mx-2 text-[#76777d]">— {relation.relation_type} →</span><strong className="text-[#0b1c30]">{nameFor(relation.target_character_id)}</strong><div className="text-[10px] font-mono uppercase text-[#76777d] mt-1">{relation.status}</div></div><button type="button" onClick={() => deleteRelation(relation.id)} disabled={saving} aria-label="Supprimer la relation" className="text-[#ba1a1a] disabled:opacity-50"><Trash2 className="w-3.5 h-3.5" /></button></div>)}{selectedRelations.length === 0 && <p className="py-3 text-xs text-[#76777d]">Aucune relation définie.</p>}</div></section>}</div>
    </div>}
    <p className="text-[11px] text-[#76777d] font-mono">L’IA peut proposer des personnages et des faits ; leur statut reste proposé jusqu’à décision éditoriale.</p>
  </div></StudioLayout>;
}
