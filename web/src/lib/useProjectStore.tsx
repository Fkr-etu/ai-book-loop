"use client";

import React, { createContext, useContext, useState } from "react";
import {
  ProjectState,
  Character,
  LoreItem,
  Chapter,
  Scene,
  CreativeConstraint,
  SceneReview
} from "@/types";
import { initialProjectData } from "@/lib/mockData";

const STORAGE_KEY = "manuscript_studio_project";

function loadFromStorage(): ProjectState {
  if (typeof window === "undefined") return initialProjectData;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : initialProjectData;
  } catch {
    return initialProjectData;
  }
}

function saveToStorage(data: ProjectState): void {
  if (typeof window !== "undefined") {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {
      // ignore
    }
  }
}

interface ProjectContextType {
  project: ProjectState;
  updateProjectInfo: (info: Partial<ProjectState>) => void;
  addCharacter: (char: Omit<Character, "id">) => void;
  updateCharacter: (id: string, char: Partial<Character>) => void;
  deleteCharacter: (id: string) => void;
  addLoreItem: (item: Omit<LoreItem, "id">) => void;
  deleteLoreItem: (id: string) => void;
  addChapter: (title: string, summary: string) => void;
  addScene: (chapterId: string, title: string, summary: string) => void;
  updateSceneContent: (chapterId: string, sceneId: string, content: string) => void;
  runAiValidation: (sceneId: string, content: string) => SceneReview;
  toggleConstraint: (id: string) => void;
  addConstraint: (type: CreativeConstraint["type"], description: string) => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [project, setProject] = useState<ProjectState>(() => loadFromStorage());

  const updateProjectInfo = (info: Partial<ProjectState>) => {
    setProject((prev) => {
      const next = { ...prev, ...info };
      saveToStorage(next);
      return next;
    });
  };

  const addCharacter = (char: Omit<Character, "id">) => {
    const newChar: Character = {
      ...char,
      id: `char-${Date.now()}`
    };
    setProject((prev) => {
      const next = {
        ...prev,
        characters: [...prev.characters, newChar],
        graphNodes: [
          ...prev.graphNodes,
          { id: newChar.id, label: newChar.name, type: "character" as const }
        ]
      };
      saveToStorage(next);
      return next;
    });
  };

  const updateCharacter = (id: string, updated: Partial<Character>) => {
    setProject((prev) => {
      const next = {
        ...prev,
        characters: prev.characters.map((c) => (c.id === id ? { ...c, ...updated } : c))
      };
      saveToStorage(next);
      return next;
    });
  };

  const deleteCharacter = (id: string) => {
    setProject((prev) => {
      const next = {
        ...prev,
        characters: prev.characters.filter((c) => c.id !== id),
        graphNodes: prev.graphNodes.filter((n) => n.id !== id),
        graphEdges: prev.graphEdges.filter((e) => e.source !== id && e.target !== id)
      };
      saveToStorage(next);
      return next;
    });
  };

  const addLoreItem = (item: Omit<LoreItem, "id">) => {
    const newItem: LoreItem = {
      ...item,
      id: `lore-${Date.now()}`
    };
    setProject((prev) => {
      const next = {
        ...prev,
        loreItems: [...prev.loreItems, newItem],
        graphNodes: [
          ...prev.graphNodes,
          { id: newItem.id, label: newItem.title, type: newItem.category }
        ]
      };
      saveToStorage(next);
      return next;
    });
  };

  const deleteLoreItem = (id: string) => {
    setProject((prev) => {
      const next = {
        ...prev,
        loreItems: prev.loreItems.filter((l) => l.id !== id),
        graphNodes: prev.graphNodes.filter((n) => n.id !== id),
        graphEdges: prev.graphEdges.filter((e) => e.source !== id && e.target !== id)
      };
      saveToStorage(next);
      return next;
    });
  };

  const addChapter = (title: string, summary: string) => {
    setProject((prev) => {
      const next = {
        ...prev,
        chapters: [
          ...prev.chapters,
          {
            id: `chap-${Date.now()}`,
            number: prev.chapters.length + 1,
            title,
            summary,
            status: "pending" as const,
            scenes: []
          }
        ]
      };
      saveToStorage(next);
      return next;
    });
  };

  const addScene = (chapterId: string, title: string, summary: string) => {
    setProject((prev) => {
      const next = {
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
      };
      saveToStorage(next);
      return next;
    });
  };

  const updateSceneContent = (chapterId: string, sceneId: string, content: string) => {
    setProject((prev) => {
      const next = {
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
      };
      saveToStorage(next);
      return next;
    });
  };

  const runAiValidation = (sceneId: string, content: string): SceneReview => {
    const hasForbiddenWord = /ordinateur|robot|telephone|internet|wifi|voiture/i.test(
      content
    );
    const scoreStyle = hasForbiddenWord ? 5 : 9;
    const scoreCoherence = hasForbiddenWord ? 5 : 9;
    const forbiddenFound = hasForbiddenWord ? ["Mots modernes anachroniques détectés"] : [];
    const approved = scoreStyle >= 7 && scoreCoherence >= 7 && forbiddenFound.length === 0;

    const review: SceneReview = {
      id: `rev-${Date.now()}`,
      sceneId,
      scoreStyle,
      scoreCoherence,
      forbiddenPatternsFound: forbiddenFound,
      critique: approved
        ? "Texte conforme au ton scholastique et à la Bible du Monde. Excellente précision sensorielle."
        : "Presence de termes modernes violant les directives du Linter IA.",
      approved,
      timestamp: "À l'instant"
    };

    setProject((prev) => {
      const next = {
        ...prev,
        reviews: [review, ...prev.reviews],
        chapters: prev.chapters.map((chap) => ({
          ...chap,
          scenes: chap.scenes.map((sc) =>
            sc.id === sceneId
              ? {
                  ...sc,
                  status: approved ? ("validated" as const) : ("rejected" as const),
                  scoreStyle,
                  scoreCoherence
                }
              : sc
          )
        }))
      };
      saveToStorage(next);
      return next;
    });

    return review;
  };

  const toggleConstraint = (id: string) => {
    setProject((prev) => {
      const next = {
        ...prev,
        constraints: prev.constraints.map((c) =>
          c.id === id ? { ...c, active: !c.active } : c
        )
      };
      saveToStorage(next);
      return next;
    });
  };

  const addConstraint = (type: CreativeConstraint["type"], description: string) => {
    const newC: CreativeConstraint = {
      id: `c-${Date.now()}`,
      type,
      description,
      active: true
    };
    setProject((prev) => {
      const next = {
        ...prev,
        constraints: [...prev.constraints, newC]
      };
      saveToStorage(next);
      return next;
    });
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
