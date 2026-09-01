import {
  ProjectState,
  Character,
  LoreItem,
  Chapter,
  Scene,
  CreativeConstraint,
  SceneReview,
  UserProfile,
  ApiResponse
} from "@/types";
import { initialProjectData } from "@/lib/mockData";

const STORAGE_KEY = "manuscript_studio_project";

export function loadProjectFromStorage(): ProjectState {
  if (typeof window === "undefined") return initialProjectData;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : initialProjectData;
  } catch {
    return initialProjectData;
  }
}

export function saveProjectToStorage(state: ProjectState): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }
}

export const mockApiClient = {
  fetchProject(id: string = "proj-001"): ApiResponse<ProjectState> {
    const proj = loadProjectFromStorage();
    return { success: true, data: proj };
  },

  updateProject(
    id: string,
    updates: Partial<ProjectState>
  ): ApiResponse<ProjectState> {
    const proj = loadProjectFromStorage();
    const updated = { ...proj, ...updates };
    saveProjectToStorage(updated);
    return { success: true, data: updated };
  },

  createCharacter(
    projId: string,
    charData: Omit<Character, "id">
  ): ApiResponse<Character> {
    const proj = loadProjectFromStorage();
    const newChar: Character = {
      ...charData,
      id: `char-${Date.now()}`
    };
    proj.characters.push(newChar);
    proj.graphNodes.push({ id: newChar.id, label: newChar.name, type: "character" });
    saveProjectToStorage(proj);
    return { success: true, data: newChar };
  },

  deleteCharacter(projId: string, charId: string): ApiResponse<void> {
    const proj = loadProjectFromStorage();
    proj.characters = proj.characters.filter((c) => c.id !== charId);
    proj.graphNodes = proj.graphNodes.filter((n) => n.id !== charId);
    proj.graphEdges = proj.graphEdges.filter(
      (e) => e.source !== charId && e.target !== charId
    );
    saveProjectToStorage(proj);
    return { success: true };
  },

  createLoreItem(
    projId: string,
    loreData: Omit<LoreItem, "id">
  ): ApiResponse<LoreItem> {
    const proj = loadProjectFromStorage();
    const newItem: LoreItem = {
      ...loreData,
      id: `lore-${Date.now()}`
    };
    proj.loreItems.push(newItem);
    proj.graphNodes.push({ id: newItem.id, label: newItem.title, type: newItem.category });
    saveProjectToStorage(proj);
    return { success: true, data: newItem };
  },

  deleteLoreItem(projId: string, loreId: string): ApiResponse<void> {
    const proj = loadProjectFromStorage();
    proj.loreItems = proj.loreItems.filter((l) => l.id !== loreId);
    proj.graphNodes = proj.graphNodes.filter((n) => n.id !== loreId);
    proj.graphEdges = proj.graphEdges.filter(
      (e) => e.source !== loreId && e.target !== loreId
    );
    saveProjectToStorage(proj);
    return { success: true };
  },

  createChapter(
    projId: string,
    title: string,
    summary: string
  ): ApiResponse<Chapter> {
    const proj = loadProjectFromStorage();
    const newChap: Chapter = {
      id: `chap-${Date.now()}`,
      number: proj.chapters.length + 1,
      title,
      summary,
      status: "pending",
      scenes: []
    };
    proj.chapters.push(newChap);
    saveProjectToStorage(proj);
    return { success: true, data: newChap };
  },

  createScene(
    projId: string,
    chapterId: string,
    title: string,
    summary: string
  ): ApiResponse<Scene> {
    const proj = loadProjectFromStorage();
    const chapter = proj.chapters.find((c) => c.id === chapterId);
    if (!chapter) {
      return { success: false, error: "Chapter not found" };
    }
    const newScene: Scene = {
      id: `sc-${Date.now()}`,
      title,
      summary,
      status: "draft",
      content: ""
    };
    chapter.scenes.push(newScene);
    saveProjectToStorage(proj);
    return { success: true, data: newScene };
  },

  runSceneReview(
    projId: string,
    sceneId: string,
    content: string
  ): ApiResponse<SceneReview> {
    const proj = loadProjectFromStorage();

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

    proj.reviews.unshift(review);
    proj.chapters.forEach((chap) => {
      chap.scenes.forEach((sc) => {
        if (sc.id === sceneId) {
          sc.status = approved ? "validated" : "rejected";
          sc.scoreStyle = scoreStyle;
          sc.scoreCoherence = scoreCoherence;
        }
      });
    });

    saveProjectToStorage(proj);
    return { success: true, data: review };
  },

  loginUser(email: string, pass: string): ApiResponse<UserProfile> {
    return {
      success: true,
      data: {
        id: "usr-001",
        email,
        name: "Valerius de Cendres",
        plan: "pro"
      }
    };
  }
};
