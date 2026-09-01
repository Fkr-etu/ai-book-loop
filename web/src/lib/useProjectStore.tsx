"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import {
  ProjectState,
  initialProjectData,
  Character,
  LoreItem,
  Chapter,
  Scene,
  CreativeConstraint,
  SceneReview
} from "./mockData";

interface ProjectContextType {
  project: ProjectState;
  updateProjectInfo: (info: Partial<ProjectState>) => void;
  addCharacter: (char: Omit<Character, "id">) => void;
  updateCharacter: (id: string, char: Partial<Character>) => void;
  deleteCharacter: (id: string) => void;
  addLoreItem: (item: Omit<LoreItem, "id">) => void;
  updateLoreItem: (id: string, item: Partial<LoreItem>) => void;
  deleteLoreItem: (id: string) => void;
  addChapter: (title: string, summary: string) => void;
  addScene: (chapterId: string, title: string, summary: string) => void;
  updateSceneContent: (chapterId: string, sceneId: string, content: string) => void;
  runAiValidation: (sceneId: string, content: string) => Promise<SceneReview>;
  toggleConstraint: (id: string) => void;
  addConstraint: (type: CreativeConstraint["type"], description: string) => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [project, setProject] = useState<ProjectState>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("manuscript_studio_project");
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch {
          // fallback
        }
      }
    }
    return initialProjectData;
  });

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("manuscript_studio_project", JSON.stringify(project));
    }
  }, [project]);

  const updateProjectInfo = (info: Partial<ProjectState>) => {
    setProject((prev) => ({ ...prev, ...info }));
  };

  const addCharacter = (char: Omit<Character, "id">) => {
    const newChar: Character = {
      ...char,
      id: `char-${Date.now()}`
    };
    setProject((prev) => ({
      ...prev,
      characters: [...prev.characters, newChar],
      graphNodes: [
        ...prev.graphNodes,
        { id: newChar.id, label: newChar.name, type: "character" }
      ]
    }));
  };

  const updateCharacter = (id: string, updated: Partial<Character>) => {
    setProject((prev) => ({
      ...prev,
      characters: prev.characters.map((c) => (c.id === id ? { ...c, ...updated } : c))
    }));
  };

  const deleteCharacter = (id: string) => {
    setProject((prev) => ({
      ...prev,
      characters: prev.characters.filter((c) => c.id !== id),
      graphNodes: prev.graphNodes.filter((n) => n.id !== id),
      graphEdges: prev.graphEdges.filter((e) => e.source !== id && e.target !== id)
    }));
  };

  const addLoreItem = (item: Omit<LoreItem, "id">) => {
    const newItem: LoreItem = {
      ...item,
      id: `lore-${Date.now()}`
    };
    setProject((prev) => ({
      ...prev,
      loreItems: [...prev.loreItems, newItem],
      graphNodes: [
        ...prev.graphNodes,
        { id: newItem.id, label: newItem.title, type: newItem.category as any }
      ]
    }));
  };

  const updateLoreItem = (id: string, updated: Partial<LoreItem>) => {
    setProject((prev) => ({
      ...prev,
      loreItems: prev.loreItems.map((l) => (l.id === id ? { ...l, ...updated } : l))
    }));
  };

  const deleteLoreItem = (id: string) => {
    setProject((prev) => ({
      ...prev,
      loreItems: prev.loreItems.filter((l) => l.id !== id),
      graphNodes: prev.graphNodes.filter((n) => n.id !== id),
      graphEdges: prev.graphEdges.filter((e) => e.source !== id && e.target !== id)
    }));
  };

  const addChapter = (title: string, summary: string) => {
    setProject((prev) => {
      const nextNum = prev.chapters.length + 1;
      const newChap: Chapter = {
        id: `chap-${Date.now()}`,
        number: nextNum,
        title,
        summary,
        status: "pending",
        scenes: []
      };
      return { ...prev, chapters: [...prev.chapters, newChap] };
    });
  };

  const addScene = (chapterId: string, title: string, summary: string) => {
    setProject((prev) => ({
      ...prev,
      chapters: prev.chapters.map((chap) => {
        if (chap.id === chapterId) {
          const newScene: Scene = {
            id: `sc-${Date.now()}`,
            title,
            summary,
            status: "draft",
            content: ""
          };
          return { ...chap, scenes: [...chap.scenes, newScene] };
        }
        return chap;
      })
    }));
  };

  const updateSceneContent = (chapterId: string, sceneId: string, content: string) => {
    setProject((prev) => ({
      ...prev,
      chapters: prev.chapters.map((chap) => {
        if (chap.id === chapterId) {
          return {
            ...chap,
            scenes: chap.scenes.map((sc) => (sc.id === sceneId ? { ...sc, content } : sc))
          };
        }
        return chap;
      })
    }));
  };

  const runAiValidation = async (sceneId: string, content: string): Promise<SceneReview> => {
    // Simulate LLM review process latency
    await new Promise((resolve) => setTimeout(resolve, 1200));

    // Simple deterministic check logic simulation
    const hasModernism = /ordinateur|robot|telephone|internet|wifi|voiture/i.test(content);
    const scoreStyle = hasModernism ? 5 : Math.floor(Math.random() * 2) + 8; // 8 or 9
    const scoreCoherence = hasModernism ? 6 : Math.floor(Math.random() * 2) + 8; // 8 or 9
    const forbiddenFound = hasModernism ? ["Mots modernes détectés"] : [];
    const approved = scoreStyle >= 7 && scoreCoherence >= 7 && forbiddenFound.length === 0;

    const review: SceneReview = {
      id: `rev-${Date.now()}`,
      sceneId,
      scoreStyle,
      scoreCoherence,
      forbiddenPatternsFound: forbiddenFound,
      critique: approved
        ? "Excellente qualité stylistique et parfaite cohérence avec la Bible du Monde. Le rythme est soutenu et les détails tactiles enrichissent le récit."
        : "Présence de termes anachroniques et déviation par rapport aux contraintes établies.",
      approved,
      timestamp: "À l'instant"
    };

    setProject((prev) => ({
      ...prev,
      reviews: [review, ...prev.reviews],
      chapters: prev.chapters.map((chap) => ({
        ...chap,
        scenes: chap.scenes.map((sc) =>
          sc.id === sceneId
            ? {
                ...sc,
                status: approved ? "validated" : "rejected",
                scoreStyle,
                scoreCoherence
              }
            : sc
        )
      }))
    }));

    return review;
  };

  const toggleConstraint = (id: string) => {
    setProject((prev) => ({
      ...prev,
      constraints: prev.constraints.map((c) =>
        c.id === id ? { ...c, active: !c.active } : c
      )
    }));
  };

  const addConstraint = (type: CreativeConstraint["type"], description: string) => {
    const newC: CreativeConstraint = {
      id: `c-${Date.now()}`,
      type,
      description,
      active: true
    };
    setProject((prev) => ({
      ...prev,
      constraints: [...prev.constraints, newC]
    }));
  };

  return (
    <ProjectContext.Provider
      value={{
        project,
        updateProjectInfo,
        addCharacter,
        updateCharacter,
        deleteCharacter,
        addLoreItem,
        updateLoreItem,
        deleteLoreItem,
        addChapter,
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
