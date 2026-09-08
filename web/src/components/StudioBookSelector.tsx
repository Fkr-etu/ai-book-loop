"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useProjectStore } from "@/lib/useProjectStore";

export function StudioBookSelector() {
  const searchParams = useSearchParams();
  const { project, selectBook, refreshProject } = useProjectStore();
  const bookId = searchParams.get("bookId");

  useEffect(() => {
    if (bookId) {
      if (bookId !== project.id) void selectBook(bookId).catch(() => undefined);
      return;
    }
    if (!project.chapters.length && project.id) void refreshProject();
  }, [bookId, project.id, project.chapters.length, refreshProject, selectBook]);

  return null;
}
