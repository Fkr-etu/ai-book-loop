"use client";

import { useEffect, useMemo, useState } from "react";
import { useProjectStore } from "@/lib/useProjectStore";
import { CanonicalContextResponse, ChapterVersion } from "@/types";

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

  const activeChapter = useMemo(() => {
    if (!chapters.length) return undefined;
    return chapters.find((chapter) => chapter.number === selectedChapterNumber) || chapters[0];
  }, [chapters, selectedChapterNumber]);

  const versions = activeChapter?.versions || [];
  const activeVersion: ChapterVersion | undefined = useMemo(() => {
    if (!versions.length) return undefined;
    return versions.find((version) => version.versionNumber === selectedVersionNumber) ||
      versions.find((version) => version.versionNumber === activeChapter?.currentVersion) ||
      versions[versions.length - 1];
  }, [versions, selectedVersionNumber, activeChapter?.currentVersion]);

  useEffect(() => {
    setSelectedChapterNumber((current) => {
      if (current !== null && chapters.some((chapter) => chapter.number === current)) return current;
      return chapters[0]?.number ?? null;
    });
  }, [chapters]);

  useEffect(() => {
    setSelectedVersionNumber(activeVersion?.versionNumber ?? null);
    setEditorContent(activeVersion?.content || activeChapter?.scenes?.[0]?.content || "");
  }, [activeChapter?.id, activeVersion?.id]);

  useEffect(() => {
    let cancelled = false;
    if (!activeChapter) {
      setCanonicalContext(null);
      setContextError(null);
      return;
    }
    setContextError(null);
    store.getCanonicalContext(activeChapter.number)
      .then((context) => {
        if (!cancelled) setCanonicalContext(context);
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          console.error("Unable to load canonical context", error);
          setCanonicalContext(null);
          setContextError("Impossible de charger les repères de votre histoire.");
        }
      });
    return () => { cancelled = true; };
  }, [activeChapter?.number, store]);

  const handleGenerateVersion = async () => {
    if (!activeChapter) return;
    setIsWorking(true);
    try { await store.generateChapter(activeChapter.number); }
    catch (error) { console.error("Chapter generation failed", error); }
    finally { setIsWorking(false); }
  };

  const handleReview = async () => {
    if (!activeChapter) return;
    setIsWorking(true);
    try { await store.reviewChapter(activeChapter.number, activeVersion?.versionNumber, editorContent); }
    catch (error) { console.error("Chapter review failed", error); }
    finally { setIsWorking(false); }
  };

  const handleApprove = async () => {
    if (activeChapter) await store.approveChapter(activeChapter.number);
  };

  const handleReject = async () => {
    if (activeChapter) await store.rejectChapter(activeChapter.number);
  };

  return {
    project,
    chapters,
    reviews,
    activeTab,
    setActiveTab,
    selectedChapterNumber,
    setSelectedChapterNumber,
    setSelectedVersionNumber,
    canonicalContext,
    contextError,
    editorContent,
    setEditorContent,
    isWorking,
    activeChapter,
    versions,
    activeVersion,
    handleGenerateVersion,
    handleReview,
    handleApprove,
    handleReject,
    canDecide: activeChapter?.status === "needs_review",
    wordCount: editorContent.trim() ? editorContent.trim().split(/\s+/).length : 0,
    latestReview: reviews[0],
  };
}

export type StudioChapterController = ReturnType<typeof useStudioChapter>;
