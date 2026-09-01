"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  BookState,
  Character,
  LoreItem,
  Chapter,
  Scene,
  CreativeConstraint,
  SceneReview,
  CanonicalContextResponse
} from "@/types";
import { initialProjectData } from "@/lib/mockData";
import { getApiClient } from "@/services/api";

interface ProjectContextType {
  project: BookState;
  loading: boolean;
  error: string | null;
  clearError: () => void;
  selectedChapterNumber: number;
  setSelectedChapterNumber: (num: number) => void;
  selectedVersionNumber: number;
  setSelectedVersionNumber: (num: number) => void;

  // Domain Actions (delegated to API)
  refreshProject: () => Promise<void>;
  updateProjectInfo: (info: Partial<BookState>) => Promise<void>;
  generateOutline: () => Promise<void>;
  approveOutline: () => Promise<void>;
  addChapter: (title: string, objective: string) => Promise<void>;
  generateChapter: (chapterNumber: number) => Promise<void>;
  reviewChapter: (chapterNumber: number, versionNumber?: number, draftText?: string) => Promise<SceneReview>;
  approveChapter: (chapterNumber: number) => Promise<void>;
  rejectChapter: (chapterNumber: number) => Promise<void>;
  getCanonicalContext: (chapterNumber: number) => Promise<CanonicalContextResponse>;

  // Character & Lore Actions
  addCharacter: (char: Omit<Character, "id">) => Promise<void>;
  updateCharacter: (id: string, updates: Partial<Character>) => Promise<void>;
  deleteCharacter: (id: string) => Promise<void>;
  addLoreItem: (item: Omit<LoreItem, "id">) => Promise<void>;
  updateLoreItem: (id: string, updates: Partial<LoreItem>) => Promise<void>;
  deleteLoreItem: (id: string) => Promise<void>;

  // UI Legacy Helpers
  addScene?: (chapterId: string, title: string, summary: string) => void;
  updateSceneContent?: (chapterId: string, sceneId: string, content: string) => void;
  runAiValidation?: (sceneId: string, content: string) => SceneReview;
  toggleConstraint?: (id: string) => void;
  addConstraint?: (type: CreativeConstraint["type"], description: string) => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [project, setProject] = useState<BookState>(initialProjectData);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedChapterNumber, setSelectedChapterNumber] = useState<number>(1);
  const [selectedVersionNumber, setSelectedVersionNumber] = useState<number>(1);

  const clearError = () => setError(null);

  const refreshProject = useCallback(async () => {
    try {
      const data = await getApiClient().getBook(project.id || "proj-001");
      setProject(data);
    } catch (err: any) {
      console.error("Error refreshing project:", err);
      setError(err.message || "Erreur de chargement du projet.");
    }
  }, [project.id]);

  useEffect(() => {
    refreshProject();
  }, [refreshProject]);

  const updateProjectInfo = async (info: Partial<BookState>) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().updateBook(project.id, info);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Impossible de mettre à jour le livre.");
    } finally {
      setLoading(false);
    }
  };

  const generateOutline = async () => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().generateOutline(project.id);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la génération du plan.");
    } finally {
      setLoading(false);
    }
  };

  const approveOutline = async () => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().approveOutline(project.id);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de l'approbation du plan.");
    } finally {
      setLoading(false);
    }
  };

  const addChapter = async (title: string, objective: string) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().addChapter(project.id, title, objective);
      setProject(updated);
      const newNum = updated.chapters.length;
      setSelectedChapterNumber(newNum);
      setSelectedVersionNumber(1);
    } catch (err: any) {
      setError(err.message || "Impossible d'ajouter le chapitre.");
    } finally {
      setLoading(false);
    }
  };

  const generateChapter = async (chapterNumber: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getApiClient().generateChapter(project.id, chapterNumber);
      setProject(res.book);
      setSelectedVersionNumber(res.versionNumber);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la génération du chapitre.");
    } finally {
      setLoading(false);
    }
  };

  const reviewChapter = async (
    chapterNumber: number,
    versionNumber?: number,
    draftText?: string
  ): Promise<SceneReview> => {
    setLoading(true);
    setError(null);
    try {
      const res = await getApiClient().reviewChapter(project.id, chapterNumber, versionNumber, draftText);
      setProject(res.book);
      return res.review;
    } catch (err: any) {
      setError(err.message || "Erreur lors de la critique du chapitre.");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const approveChapter = async (chapterNumber: number) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().approveChapter(project.id, chapterNumber);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de l'approbation du chapitre.");
    } finally {
      setLoading(false);
    }
  };

  const rejectChapter = async (chapterNumber: number) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().rejectChapter(project.id, chapterNumber);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors du rejet du chapitre.");
    } finally {
      setLoading(false);
    }
  };

  const getCanonicalContext = async (chapterNumber: number): Promise<CanonicalContextResponse> => {
    return getApiClient().getCanonicalContext(project.id, chapterNumber);
  };

  const addCharacter = async (char: Omit<Character, "id">) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().createCharacter(project.id, char);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la création du personnage.");
    } finally {
      setLoading(false);
    }
  };

  const updateCharacter = async (id: string, updates: Partial<Character>) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().updateCharacter(project.id, id, updates);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la mise à jour du personnage.");
    } finally {
      setLoading(false);
    }
  };

  const deleteCharacter = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().deleteCharacter(project.id, id);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la suppression du personnage.");
    } finally {
      setLoading(false);
    }
  };

  const addLoreItem = async (item: Omit<LoreItem, "id">) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().createLoreItem(project.id, item);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de l'ajout au lore.");
    } finally {
      setLoading(false);
    }
  };

  const updateLoreItem = async (id: string, updates: Partial<LoreItem>) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().updateLoreItem(project.id, id, updates);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la mise à jour du lore.");
    } finally {
      setLoading(false);
    }
  };

  const deleteLoreItem = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await getApiClient().deleteLoreItem(project.id, id);
      setProject(updated);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la suppression de l'élément.");
    } finally {
      setLoading(false);
    }
  };

  // Legacy scene UI helper
  const addScene = (chapterId: string, title: string, summary: string) => {
    const newScene: Scene = { id: `sc-${Date.now()}`, title, summary, status: "draft", content: "" };
    setProject((prev) => ({
      ...prev,
      chapters: prev.chapters.map((chap) =>
        chap.id === chapterId ? { ...chap, scenes: [...(chap.scenes || []), newScene] } : chap
      )
    }));
  };

  const updateSceneContent = (chapterId: string, sceneId: string, content: string) => {
    setProject((prev) => ({
      ...prev,
      chapters: prev.chapters.map((chap) =>
        chap.id === chapterId
          ? {
              ...chap,
              scenes: (chap.scenes || []).map((sc) => (sc.id === sceneId ? { ...sc, content } : sc))
            }
          : chap
      )
    }));
  };

  const runAiValidation = (sceneId: string, content: string): SceneReview => {
    const review: SceneReview = {
      id: `rev-${Date.now()}`,
      score: 8,
      approved: true,
      issues: [],
      suggestions: ["Conforme."],
      scoreStyle: 8,
      scoreCoherence: 8,
      timestamp: "À l'instant"
    };
    return review;
  };

  const toggleConstraint = (id: string) => {
    setProject((prev) => ({
      ...prev,
      creativeConstraints: (prev.creativeConstraints || []).map((c) =>
        c.id === id ? { ...c, active: !c.active } : c
      )
    }));
  };

  const addConstraint = (type: CreativeConstraint["type"], description: string) => {
    const newC: CreativeConstraint = { id: `c-${Date.now()}`, type, description, active: true };
    setProject((prev) => ({
      ...prev,
      creativeConstraints: [...(prev.creativeConstraints || []), newC],
      constraints: [...(prev.constraints || []), description]
    }));
  };

  return (
    <ProjectContext.Provider
      value={{
        project,
        loading,
        error,
        clearError,
        selectedChapterNumber,
        setSelectedChapterNumber,
        selectedVersionNumber,
        setSelectedVersionNumber,
        refreshProject,
        updateProjectInfo,
        generateOutline,
        approveOutline,
        addChapter,
        generateChapter,
        reviewChapter,
        approveChapter,
        rejectChapter,
        getCanonicalContext,
        addCharacter,
        updateCharacter,
        deleteCharacter,
        addLoreItem,
        updateLoreItem,
        deleteLoreItem,
        addScene,
        updateSceneContent,
        runAiValidation,
        toggleConstraint,
        addConstraint
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
};

export const useProjectStore = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error("useProjectStore must be used within a ProjectProvider");
  }
  return context;
};
