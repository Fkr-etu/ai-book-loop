"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useProjectStore } from "@/lib/useProjectStore";
import { getApiClient } from "@/services/api";
import { CanonicalContextResponse, ChapterVersion, GrillMessage, GrillResponse } from "@/types";

export const GRILL_IDLE_DELAY_MS = 8000;

export function useStudioChapter() {
  const store = useProjectStore();
  const project = store.project;
  const chapters = project.chapters || [];
  const reviews = project.reviews || [];
  const [activeTab, setActiveTab] = useState<"manuscript" | "history" | "context">("manuscript");
  const [selectedChapterNumber, setSelectedChapterNumber] = useState<number | null>(null);
  const [selectedVersionNumber, setSelectedVersionNumber] = useState<number | null>(null);
  const [canonicalContext, setCanonicalContext] = useState<CanonicalContextResponse | null>(null);
  const [contextError, setContextError] = useState<string | null>(null);
  const [editorContent, setEditorContent] = useState("");
  const [isWorking, setIsWorking] = useState(false);
  const [editorEngaged, setEditorEngaged] = useState(false);
  const [grillMessages, setGrillMessages] = useState<GrillMessage[]>([]);
  const [grillResponse, setGrillResponse] = useState<GrillResponse | null>(null);
  const [grillOpen, setGrillOpen] = useState(false);
  const [grillLoading, setGrillLoading] = useState(false);
  const [grillError, setGrillError] = useState<string | null>(null);
  const [grillDismissed, setGrillDismissed] = useState(false);
  const [grillNudge, setGrillNudge] = useState(false);
  const grillTurn = useRef(0);

  const activeChapter = useMemo(() => { if (!chapters.length) return undefined; return chapters.find((chapter) => chapter.number === selectedChapterNumber) || chapters[0]; }, [chapters, selectedChapterNumber]);
  const versions = activeChapter?.versions || [];
  const activeVersion: ChapterVersion | undefined = useMemo(() => {
    if (!versions.length) return undefined;
    return versions.find((version) => version.versionNumber === selectedVersionNumber) || versions.find((version) => version.versionNumber === activeChapter?.currentVersion) || versions[versions.length - 1];
  }, [versions, selectedVersionNumber, activeChapter?.currentVersion]);

  useEffect(() => { setSelectedChapterNumber((current) => current !== null && chapters.some((chapter) => chapter.number === current) ? current : chapters[0]?.number ?? null); }, [chapters]);
  useEffect(() => { setSelectedVersionNumber(activeVersion?.versionNumber ?? null); setEditorContent(activeVersion?.content || activeChapter?.scenes?.[0]?.content || ""); }, [activeChapter?.id, activeVersion?.id]);
  useEffect(() => {
    let cancelled = false;
    if (!activeChapter) { setCanonicalContext(null); setContextError(null); return; }
    setContextError(null);
    store.getCanonicalContext(activeChapter.number).then((context) => { if (!cancelled) setCanonicalContext(context); }).catch((error: unknown) => { if (!cancelled) { console.error("Unable to load canonical context", error); setCanonicalContext(null); setContextError("Impossible de charger les repères de votre histoire."); } });
    return () => { cancelled = true; };
  }, [activeChapter?.number, store]);
  useEffect(() => { setGrillMessages([]); setGrillResponse(null); setGrillOpen(false); setGrillError(null); setGrillNudge(false); setGrillDismissed(false); setEditorEngaged(false); grillTurn.current = 0; }, [project.id, activeChapter?.id]);
  useEffect(() => {
    if (!activeChapter || !editorEngaged || grillOpen || grillDismissed || grillNudge || grillResponse || isWorking) return;
    const timer = window.setTimeout(() => setGrillNudge(true), GRILL_IDLE_DELAY_MS);
    return () => window.clearTimeout(timer);
  }, [editorContent, editorEngaged, activeChapter?.id, grillOpen, grillDismissed, grillNudge, grillResponse, isWorking]);

  const handleEditorFocus = () => setEditorEngaged(true);
  const handleEditorChange = (content: string) => { setEditorContent(content); setGrillNudge(false); };
  const askGrill = async (messages: GrillMessage[]) => {
    if (!project.id || grillLoading) return;
    const nextTurn = grillTurn.current + 1;
    setGrillLoading(true); setGrillError(null); setGrillOpen(true); setGrillNudge(false);
    try {
      const response = await getApiClient().grill(project.id, messages, nextTurn);
      grillTurn.current = nextTurn;
      setGrillResponse(response);
      setGrillMessages([...messages, { role: "assistant", content: [response.reply, response.question].filter(Boolean).join("\n") }]);
    } catch (error) { console.error("Critical Eye request failed", error); setGrillError("Impossible de faire intervenir votre Œil critique pour le moment."); }
    finally { setGrillLoading(false); }
  };
  const startGrill = () => askGrill([]);
  const answerGrill = async (answer: string) => {
    const content = answer.trim();
    if (!content || grillLoading || grillResponse?.done) return;
    const messages = [...grillMessages, { role: "user" as const, content }];
    setGrillResponse(null);
    await askGrill(messages);
  };
  const dismissGrill = () => { setGrillDismissed(true); setGrillNudge(false); };
  const handleGenerateVersion = async () => { if (!activeChapter) return; setIsWorking(true); try { await store.generateChapter(activeChapter.number); } catch (error) { console.error("Chapter generation failed", error); } finally { setIsWorking(false); } };
  const handleReview = async () => { if (!activeChapter) return; setIsWorking(true); try { await store.reviewChapter(activeChapter.number, activeVersion?.versionNumber, editorContent); } catch (error) { console.error("Chapter review failed", error); } finally { setIsWorking(false); } };
  const handleApprove = async () => { if (activeChapter) await store.approveChapter(activeChapter.number); };
  const handleReject = async () => { if (activeChapter) await store.rejectChapter(activeChapter.number); };

  return { project, chapters, reviews, activeTab, setActiveTab, selectedChapterNumber, setSelectedChapterNumber, setSelectedVersionNumber, canonicalContext, contextError, editorContent, setEditorContent: handleEditorChange, handleEditorFocus, isWorking, activeChapter, versions, activeVersion, handleGenerateVersion, handleReview, handleApprove, handleReject, canDecide: activeChapter?.status === "needs_review", wordCount: editorContent.trim() ? editorContent.trim().split(/\s+/).length : 0, latestReview: reviews[0], grillMessages, grillResponse, grillOpen, grillLoading, grillError, grillNudge, startGrill, answerGrill, dismissGrill, closeGrill: () => setGrillOpen(false) };
}

export type StudioChapterController = ReturnType<typeof useStudioChapter>;
